from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import get_settings
from app.models.models import DOCUMENT_MODELS

settings = get_settings()

client: AsyncIOMotorClient = None

# ── Colección directa estilo tu database.py original ──────────────────────
# Útil para operaciones rápidas con insert_many / find sin usar Beanie
db         = None
collection = None   # equivalente a db["reactor_data"]


async def connect_db():
    global client, db, collection
    client = AsyncIOMotorClient(settings.mongo_uri)

    # Beanie (ODM completo para modelos tipados)
    await init_beanie(
        database=client[settings.mongo_db],
        document_models=DOCUMENT_MODELS,
    )

    # Acceso directo a la colección (como en tu código original)
    db         = client[settings.mongo_db]
    collection = db["reactor_data"]

    print(f"✅ MongoDB conectado → {settings.mongo_db}")


async def disconnect_db():
    global client
    if client:
        client.close()
        print("🔌 MongoDB desconectado")
