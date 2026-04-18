from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum


# ─────────────────────────────────────────────────
#  ENUMS
# ─────────────────────────────────────────────────

class UserRole(str, Enum):
    ADMIN    = "admin"      # acceso total
    OPERATOR = "operador"   # lectura + escritura datos reactor
    READER   = "lector"     # solo monitoreo


class OperatingState(str, Enum):
    STEADY_HIGH_LOAD      = "steady_high_load"
    LOAD_FOLLOWING        = "load_following"
    LOW_POWER_MAINTENANCE = "low_power_maintenance"
    CONTROLLED_TRANSIENT  = "controlled_transient"


class AlertLevel(str, Enum):
    NORMAL   = "normal"
    WARNING  = "warning"
    CRITICAL = "critical"


# ─────────────────────────────────────────────────
#  USUARIO
# ─────────────────────────────────────────────────

class User(Document):
    name:              str
    email:             Indexed(EmailStr, unique=True)
    hashed_password:   str                          # bcrypt — NUNCA en texto plano
    role:              UserRole = UserRole.READER
    solana_public_key: Optional[str] = None         # wallet / identidad on-chain
    is_active:         bool = True
    created_at:        datetime = Field(default_factory=datetime.utcnow)
    last_login:        Optional[datetime] = None

    class Settings:
        name = "users"


# ─────────────────────────────────────────────────
#  LECTURA DE SENSORES
# ─────────────────────────────────────────────────

class SensorReading(Document):
    timestamp:                         datetime
    operating_state_label:             OperatingState
    estimated_remaining_useful_life_days: float
    pc1: float
    pc2: float
    pc3: float
    pc4: float
    pc5: float
    spe_q:        float     # error de predicción cuadrado (detección anomalías)
    t2:           float     # estadístico Hotelling (anomalía multivariada)
    health_index: float     # índice de salud del reactor

    # Resultados del pipeline ML (se llenan después de procesar)
    bayesian_fault_prob:  Optional[float] = None   # P(fallo) de la red bayesiana
    mamdani_life_score:   Optional[float] = None   # salida difusa Mamdani
    alert_level:          Optional[AlertLevel] = None

    class Settings:
        name = "sensor_readings"


# ─────────────────────────────────────────────────
#  RESULTADO DEL ANÁLISIS (resumen por sesión)
# ─────────────────────────────────────────────────

class AnalysisResult(Document):
    created_at:           datetime = Field(default_factory=datetime.utcnow)
    created_by:           str                          # user id
    reading_id:           str                          # referencia a SensorReading
    bayesian_fault_prob:  float
    mamdani_life_score:   float
    alert_level:          AlertLevel
    recommendation:       str                          # texto generado por Gemini
    recommendation_es:    Optional[str] = None
    recommendation_en:    Optional[str] = None
    recommendation_nah:   Optional[str] = None        # náhuatl

    class Settings:
        name = "analysis_results"


# ─────────────────────────────────────────────────
#  DOCUMENTOS SUBIDOS
# ─────────────────────────────────────────────────

class UploadedDocument(Document):
    filename:    str
    content_type: str
    size_bytes:  int
    uploaded_by: str                                  # user id
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    summary_es:  Optional[str] = None
    summary_en:  Optional[str] = None
    summary_nah: Optional[str] = None
    file_path:   str                                  # ruta en servidor

    class Settings:
        name = "documents"


# ─────────────────────────────────────────────────
#  LOG DE ACCIONES (auditoría)
# ─────────────────────────────────────────────────

class ActionLog(Document):
    timestamp:  datetime = Field(default_factory=datetime.utcnow)
    user_id:    str
    user_email: str
    action:     str          # ej: "login", "upload_doc", "run_analysis"
    endpoint:   str
    ip_address: str
    success:    bool
    details:    Optional[str] = None

    class Settings:
        name = "action_logs"


# ─────────────────────────────────────────────────
#  LISTA DE MODELOS PARA INICIALIZAR BEANIE
# ─────────────────────────────────────────────────

DOCUMENT_MODELS = [
    User,
    SensorReading,
    AnalysisResult,
    UploadedDocument,
    ActionLog,
]
