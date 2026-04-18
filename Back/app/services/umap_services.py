import pandas as pd
import joblib
import json

UMAP_CSV = "artifacts/reactor_umap_embedding.csv"
SCALER_PATH = "artifacts/umap_scaler.pkl"
MODEL_PATH = "artifacts/umap_model.pkl"
DIST_PATH = "artifacts/distributions.json"

umap_embedding = None
umap_model = None
umap_scaler = None
umap_metadata = None


def load_umap_artifacts():
    global umap_embedding
    global umap_model
    global umap_scaler
    global umap_metadata

    try:
        # Cargar embedding ya calculado
        df = pd.read_csv(UMAP_CSV)
        umap_embedding = df.to_dict(orient="records")

        # Cargar modelo y scaler
        umap_model = joblib.load(MODEL_PATH)
        umap_scaler = joblib.load(SCALER_PATH)

        # Cargar metadata
        with open(DIST_PATH, "r") as f:
            umap_metadata = json.load(f)

        print("✅ UMAP cargado correctamente")

    except Exception as e:
        print(f"⚠️ Error cargando UMAP: {e}")