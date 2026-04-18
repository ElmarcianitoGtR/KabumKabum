import sys
import types

# --- MONKEY PATCH PRO PARA PYTHON 3.13 ---
if 'imp' not in sys.modules:
    fake_imp = types.ModuleType('imp')
    sys.modules['imp'] = fake_imp
    
    # Mockeamos find_module para que no truene
    def find_module(name, path=None):
        # Engañamos a skfuzzy diciéndole que no encontramos 'nose'
        # Esto es seguro porque 'nose' es solo para tests
        raise ImportError(f"No module named {name}")
    
    fake_imp.find_module = find_module
    print("🛠️  Patch Pro aplicado: 'imp.find_module' emulado.")
# -----------------------------------------
    


from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import pandas as pd
import json
import joblib

from app.core.config import get_settings
from app.core.database import connect_db, disconnect_db
from app.middleware.security import register_middlewares
from app.routes import auth, reactor, chat
from app.services.inference_pipeline import load_artifacts
from app.services.umap_service import load_umap_artifacts
from app.routes import umap

settings     = get_settings()
CSV_PATH     = "data/data_limpia.csv"
ARTIFACT_DIR = "artifacts"


# ─────────────────────────────────────────────────
#  CICLO DE VIDA: startup / shutdown
# ─────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando ReactorGuard API...")

    # 1) Conectar MongoDB
    await connect_db()

    # 2) Cargar artefactos del modelo de tu compañera
    try:
        from pgmpy.models import DiscreteBayesianNetwork
        from pgmpy.inference import VariableElimination

        model = DiscreteBayesianNetwork.load(
            f"{ARTIFACT_DIR}/model.xmlbif", filetype="xmlbif"
        )
        disc = joblib.load(f"{ARTIFACT_DIR}/discretizer.joblib")
        with open(f"{ARTIFACT_DIR}/metadata.json", "r", encoding="utf-8") as f:
            meta = json.load(f)

        infer = VariableElimination(model)
        load_artifacts(model=model, infer=infer, disc=disc, meta=meta)
        print("✅ Modelo bayesiano + discretizador + metadata cargados")

    except FileNotFoundError as e:
        print(f"⚠️  Artefacto no encontrado: {e} — pipeline en modo simulado")
        load_artifacts(model=None, infer=None, disc=None, meta=None)
    except Exception as e:
        print(f"⚠️  Error cargando artefactos: {e} — pipeline en modo simulado")
        load_artifacts(model=None, infer=None, disc=None, meta=None)

    yield

    # 3) Cargar UMAP
    try:
        load_umap_artifacts()
        print("✅ UMAP embedding cargado")
    except Exception as e:
        print(f"⚠️ Error cargando UMAP: {e}")

    # ── SHUTDOWN ──────────────────────────────────
    await disconnect_db()
    print("👋 ReactorGuard API detenida")


# ─────────────────────────────────────────────────
#  CREAR APP
# ─────────────────────────────────────────────────

app = FastAPI(
    title       = settings.app_name,
    version     = "1.0.0",
    description = "Backend de monitoreo de vida útil de reactores nucleares",
    docs_url    = "/docs" if settings.debug else None,
    redoc_url   = "/redoc" if settings.debug else None,
    lifespan    = lifespan,
)

register_middlewares(app)

app.include_router(auth.router)
app.include_router(reactor.router)
app.include_router(chat.router)
app.include_router(umap.router)


# ─────────────────────────────────────────────────
#  ENDPOINTS BÁSICOS (código original integrado)
# ─────────────────────────────────────────────────

@app.get("/", tags=["Sistema"])
def root():
    return {"message": "Reactor backend activo ⚛️"}


@app.get("/health", tags=["Sistema"])
async def health():
    return {"status": "ok", "app": settings.app_name}


@app.get("/data/preview", tags=["Datos CSV"])
def preview_data():
    """Previsualiza las primeras 5 filas del CSV."""
    try:
        df = pd.read_csv(CSV_PATH)
        return {
            "rows":    len(df),
            "columns": list(df.columns),
            "preview": df.head().to_dict(orient="records"),
        }
    except FileNotFoundError:
        raise HTTPException(404, f"CSV no encontrado en {CSV_PATH}")
    except Exception as e:
        raise HTTPException(500, f"Error leyendo CSV: {e}")


@app.post("/data/load", tags=["Datos CSV"])
async def load_data():
    """Carga el CSV completo a MongoDB evitando duplicados."""
    from app.core.database import collection
    try:
        df     = pd.read_csv(CSV_PATH)
        await collection.delete_many({})
        data   = df.to_dict(orient="records")
        result = await collection.insert_many(data)
        return {
            "message":          "Datos cargados a MongoDB",
            "records_inserted": len(result.inserted_ids),
            "columns":          list(df.columns),
        }
    except FileNotFoundError:
        raise HTTPException(404, f"CSV no encontrado en {CSV_PATH}")
    except Exception as e:
        raise HTTPException(500, f"Error cargando datos: {e}")


# ─────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host   = "0.0.0.0",
        port   = 8000,
        reload = settings.debug,
    )
