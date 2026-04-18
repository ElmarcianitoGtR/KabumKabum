from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import pandas as pd
import io

from app.models.models import (
    SensorReading, AnalysisResult, UploadedDocument,
    User, AlertLevel, OperatingState
)
from app.core.security import require_reader, require_operator, require_admin
from app.services.inference_pipeline import run_pipeline
from app.services.gemini_service import generate_recommendation, translate_all, summarize_all_langs

router = APIRouter(prefix="/api", tags=["Reactor"])

# Referencia al objeto de inferencia bayesiana (se inyecta al iniciar)
_bayesian_inference = None

def set_bayesian_inference(inference):
    global _bayesian_inference
    _bayesian_inference = inference


# ─────────────────────────────────────────────────
#  ANÁLISIS EN TIEMPO REAL (lectura manual)
# ─────────────────────────────────────────────────

class SensorInput(BaseModel):
    pc1: float; pc2: float; pc3: float; pc4: float; pc5: float
    spe_q: float; t2: float; health_index: float
    operating_state: OperatingState = OperatingState.STEADY_HIGH_LOAD
    estimated_remaining_useful_life_days: Optional[float] = None
    timestamp: Optional[datetime] = None


@router.post("/analyze")
async def analyze_sensor(
    data: SensorInput,
    current_user: User = Depends(require_reader),
):
    """Corre el pipeline bayesiano + Mamdani sobre una lectura de sensores."""
    sensor_dict = {
        "pc1": data.pc1, "pc2": data.pc2, "pc3": data.pc3,
        "pc4": data.pc4, "pc5": data.pc5,
        "spe_q": data.spe_q, "t2": data.t2,
        "health_index": data.health_index,
    }

    # 1) Pipeline Red Bayesiana → Mamdani
    result = run_pipeline(sensor_dict, _bayesian_inference)

    # 2) Generar recomendación con Gemini (en español)
    recommendation = await generate_recommendation(
        alert_level     = result["alert_level"],
        life_score      = result["life_score"],
        fault_prob      = result["fault_probability"],
        operating_state = data.operating_state.value,
        lang            = "es",
    )

    # 3) Guardar lectura en MongoDB
    reading = SensorReading(
        timestamp                            = data.timestamp or datetime.utcnow(),
        operating_state_label                = data.operating_state,
        estimated_remaining_useful_life_days = data.estimated_remaining_useful_life_days or 0,
        pc1=data.pc1, pc2=data.pc2, pc3=data.pc3, pc4=data.pc4, pc5=data.pc5,
        spe_q        = data.spe_q,
        t2           = data.t2,
        health_index = data.health_index,
        bayesian_fault_prob = result["fault_probability"],
        mamdani_life_score  = result["life_score"],
        alert_level         = AlertLevel(result["alert_level"]),
    )
    await reading.insert()

    # 4) Guardar resultado del análisis
    analysis = AnalysisResult(
        created_by           = str(current_user.id),
        reading_id           = str(reading.id),
        bayesian_fault_prob  = result["fault_probability"],
        mamdani_life_score   = result["life_score"],
        alert_level          = AlertLevel(result["alert_level"]),
        recommendation       = recommendation,
        recommendation_es    = recommendation,
    )
    await analysis.insert()

    return {
        "reading_id":          str(reading.id),
        "analysis_id":         str(analysis.id),
        "alert_level":         result["alert_level"],
        "life_score":          result["life_score"],
        "fault_probability":   result["fault_probability"],
        "recommendation_es":   recommendation,
    }


# ─────────────────────────────────────────────────
#  IMPORTAR CSV COMPLETO
# ─────────────────────────────────────────────────

@router.post("/import-csv")
async def import_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(require_operator),
):
    """Importa el CSV de sensores y corre el pipeline en todos los registros."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Solo se aceptan archivos .csv")

    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    required = {"pc1","pc2","pc3","pc4","pc5","spe_q","t2","health_index"}
    missing  = required - set(df.columns.str.lower())
    if missing:
        raise HTTPException(400, f"Columnas faltantes: {missing}")

    df.columns = df.columns.str.lower()
    inserted = 0
    alerts   = {"normal": 0, "warning": 0, "critical": 0}

    for _, row in df.iterrows():
        sensor_dict = {k: float(row[k]) for k in ["pc1","pc2","pc3","pc4","pc5","spe_q","t2","health_index"]}
        result = run_pipeline(sensor_dict, _bayesian_inference)
        alerts[result["alert_level"]] += 1

        reading = SensorReading(
            timestamp                            = pd.to_datetime(row.get("timestamp", datetime.utcnow())),
            operating_state_label                = row.get("operating_state_label", "steady_high_load"),
            estimated_remaining_useful_life_days = float(row.get("estimated_remaining_useful_life_days", 0)),
            pc1=sensor_dict["pc1"], pc2=sensor_dict["pc2"],
            pc3=sensor_dict["pc3"], pc4=sensor_dict["pc4"],
            pc5=sensor_dict["pc5"],
            spe_q        = sensor_dict["spe_q"],
            t2           = sensor_dict["t2"],
            health_index = sensor_dict["health_index"],
            bayesian_fault_prob = result["fault_probability"],
            mamdani_life_score  = result["life_score"],
            alert_level         = AlertLevel(result["alert_level"]),
        )
        await reading.insert()
        inserted += 1

    return {
        "message":  f"{inserted} registros importados",
        "alerts":   alerts,
        "imported_by": current_user.email,
    }


# ─────────────────────────────────────────────────
#  HISTORIAL DE LECTURAS
# ─────────────────────────────────────────────────

@router.get("/readings")
async def get_readings(
    limit: int = 50,
    current_user: User = Depends(require_reader),
):
    readings = await SensorReading.find_all().sort("-timestamp").limit(limit).to_list()
    return readings


@router.get("/readings/{reading_id}")
async def get_reading(
    reading_id: str,
    current_user: User = Depends(require_reader),
):
    reading = await SensorReading.get(reading_id)
    if not reading:
        raise HTTPException(404, "Lectura no encontrada")
    return reading


# ─────────────────────────────────────────────────
#  SUBIR DOCUMENTOS
# ─────────────────────────────────────────────────

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(require_operator),
):
    """Sube un documento técnico y genera resumen en 3 idiomas con Gemini."""
    content = await file.read()
    text    = content.decode("utf-8", errors="ignore")

    summaries = await summarize_all_langs(text)

    doc = UploadedDocument(
        filename     = file.filename,
        content_type = file.content_type or "text/plain",
        size_bytes   = len(content),
        uploaded_by  = str(current_user.id),
        file_path    = f"uploads/{file.filename}",
        summary_es   = summaries["es"],
        summary_en   = summaries["en"],
        summary_nah  = summaries["nah"],
    )
    await doc.insert()

    return {
        "document_id": str(doc.id),
        "filename":    doc.filename,
        "summaries":   summaries,
    }


@router.get("/documents")
async def list_documents(current_user: User = Depends(require_reader)):
    return await UploadedDocument.find_all().to_list()


# ─────────────────────────────────────────────────
#  WEBSOCKET — MONITOREO EN TIEMPO REAL
# ─────────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, data: dict):
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                pass

ws_manager = ConnectionManager()


@router.websocket("/ws/monitor")
async def websocket_monitor(websocket: WebSocket):
    """
    WebSocket para monitoreo en tiempo real.
    El cliente envía lecturas de sensores en JSON y recibe
    el resultado del pipeline instantáneamente.
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            result = run_pipeline(data, _bayesian_inference)
            await websocket.send_json({
                "type":    "analysis",
                "result":  result,
                "ts":      datetime.utcnow().isoformat(),
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# ─────────────────────────────────────────────────
#  GESTIÓN DE USUARIOS (solo admin)
# ─────────────────────────────────────────────────

@router.get("/users")
async def list_users(current_user: User = Depends(require_admin)):
    users = await User.find_all().to_list()
    return [
        {"id": str(u.id), "name": u.name, "email": u.email,
         "role": u.role, "is_active": u.is_active}
        for u in users
    ]


@router.patch("/users/{user_id}/role")
async def update_role(
    user_id: str,
    new_role: str,
    current_user: User = Depends(require_admin),
):
    from app.models.models import UserRole
    user = await User.get(user_id)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    user.role = UserRole(new_role)
    await user.save()
    return {"message": f"Rol actualizado a {new_role}", "user": user.email}
