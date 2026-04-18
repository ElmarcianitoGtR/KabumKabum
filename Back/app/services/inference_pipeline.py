"""
Pipeline de inferencia — usa el modelo entrenado por el equipo:
  artifacts/model.xmlbif       → Red Bayesiana (DiscreteBayesianNetwork)
  artifacts/discretizer.joblib → Discretizador de variables continuas
  artifacts/metadata.json      → Metadatos: features, clases de RUL, etc.

Flujo:
  Sensores (float)
      → Discretizador (joblib)
      → Red Bayesiana (pgmpy)  → P(RUL_class)
      → Motor Mamdani          → life_score 0-100 + alert_level
"""

import numpy as np
import pandas as pd
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from typing import Dict, Any

# ─────────────────────────────────────────────────
#  ESTADO GLOBAL — se llena en el startup de main.py
# ─────────────────────────────────────────────────
_model   = None   # DiscreteBayesianNetwork
_infer   = None   # VariableElimination
_disc    = None   # discretizer (joblib)
_meta    = None   # metadata.json
_mamdani = None   # sistema difuso Mamdani


def load_artifacts(model, infer, disc, meta):
    """Llamado desde main.py al iniciar la app."""
    global _model, _infer, _disc, _meta
    _model = model
    _infer = infer
    _disc  = disc
    _meta  = meta
    print("✅ Artefactos del modelo cargados en inference_pipeline")


# ═══════════════════════════════════════════════════════
#  PASO 1 — RED BAYESIANA: P(RUL_class | evidencia)
# ═══════════════════════════════════════════════════════

def run_bayesian(sensor_data: Dict[str, float]) -> Dict[str, Any]:
    """
    Recibe valores crudos de sensores, los discretiza con el joblib
    de tu compañera y consulta la red bayesiana.
    """
    if _infer is None or _disc is None or _meta is None:
        print("⚠️  Artefactos no cargados — bayesiana en modo simulado")
        return {
            "rul_distribution":     {"high": 0.5, "medium": 0.3, "low": 0.2},
            "predicted_class":      "medium",
            "fault_probability":    0.2,
            "evidence_discretized": {},
        }

    features = _meta["input_features"]

    # 1) Construir DataFrame con las features del modelo
    x      = pd.DataFrame([{f: sensor_data.get(f, 0.0) for f in features}])

    # 2) Discretizar con el joblib de tu compañera
    x_disc = _disc.transform(x[features])
    x_disc = pd.DataFrame(x_disc, columns=features).astype(int)

    # 3) Armar evidencia para la red bayesiana
    evidence = {col: int(x_disc.loc[0, col]) for col in features}

    # 4) Consultar la red bayesiana
    q                = _infer.query(variables=["RUL_class"], evidence=evidence)
    states           = q.state_names["RUL_class"]
    probs            = [float(v) for v in q.values]
    rul_distribution = dict(zip(states, probs))
    predicted_class  = max(rul_distribution, key=rul_distribution.get)

    # Probabilidad de fallo = prob de la clase "low" (menor vida útil)
    fault_probability = rul_distribution.get("low", min(rul_distribution.values()))

    return {
        "rul_distribution":     rul_distribution,
        "predicted_class":      predicted_class,
        "fault_probability":    round(float(fault_probability), 4),
        "evidence_discretized": evidence,
    }


# ═══════════════════════════════════════════════════════
#  PASO 2 — MOTOR MAMDANI: life_score + alert_level
# ═══════════════════════════════════════════════════════

def _build_mamdani():
    fault_prob = ctrl.Antecedent(np.arange(0, 1.01, 0.01), "fault_prob")
    health     = ctrl.Antecedent(np.arange(0, 101,  1),    "health")
    spe_level  = ctrl.Antecedent(np.arange(0, 1.01, 0.01), "spe_level")
    life_score = ctrl.Consequent(np.arange(0, 101,  1),    "life_score")

    fault_prob["baja"]  = fuzz.trimf(fault_prob.universe, [0.0, 0.0,  0.35])
    fault_prob["media"] = fuzz.trimf(fault_prob.universe, [0.2, 0.5,  0.8 ])
    fault_prob["alta"]  = fuzz.trimf(fault_prob.universe, [0.65,1.0,  1.0 ])

    health["deteriorado"] = fuzz.trimf(health.universe, [0,  0,  40 ])
    health["moderado"]    = fuzz.trimf(health.universe, [20, 50, 80 ])
    health["bueno"]       = fuzz.trimf(health.universe, [60, 100,100])

    spe_level["normal"]  = fuzz.trimf(spe_level.universe, [0.0, 0.0, 0.4])
    spe_level["elevado"] = fuzz.trimf(spe_level.universe, [0.3, 0.6, 0.9])
    spe_level["critico"] = fuzz.trimf(spe_level.universe, [0.7, 1.0, 1.0])

    life_score["critica"] = fuzz.trimf(life_score.universe, [0,   0,  35 ])
    life_score["baja"]    = fuzz.trimf(life_score.universe, [15,  35, 55 ])
    life_score["media"]   = fuzz.trimf(life_score.universe, [40,  60, 80 ])
    life_score["alta"]    = fuzz.trimf(life_score.universe, [65, 100,100 ])

    rules = [
        ctrl.Rule(fault_prob["alta"]   & health["deteriorado"], life_score["critica"]),
        ctrl.Rule(fault_prob["alta"]   & spe_level["critico"],  life_score["critica"]),
        ctrl.Rule(spe_level["critico"] & health["deteriorado"], life_score["critica"]),
        ctrl.Rule(fault_prob["alta"]   & health["moderado"],    life_score["baja"]),
        ctrl.Rule(fault_prob["media"]  & health["deteriorado"], life_score["baja"]),
        ctrl.Rule(fault_prob["media"]  & spe_level["elevado"],  life_score["baja"]),
        ctrl.Rule(fault_prob["baja"]   & health["bueno"],       life_score["alta"]),
        ctrl.Rule(fault_prob["baja"]   & spe_level["normal"],   life_score["alta"]),
        ctrl.Rule(fault_prob["media"]  & health["bueno"],       life_score["media"]),
        ctrl.Rule(fault_prob["baja"]   & health["moderado"],    life_score["media"]),
    ]

    return ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))


def get_mamdani():
    global _mamdani
    if _mamdani is None:
        _mamdani = _build_mamdani()
    return _mamdani


def run_mamdani(fault_probability: float, health_index: float, spe_q: float) -> Dict[str, Any]:
    spe_norm    = float(np.clip(spe_q / (spe_q + 10), 0, 1))
    health_norm = float(np.clip(health_index, 0, 100))

    sim = get_mamdani()
    sim.input["fault_prob"] = float(np.clip(fault_probability, 0.001, 0.999))
    sim.input["health"]     = float(np.clip(health_norm, 0.001, 99.999))
    sim.input["spe_level"]  = float(np.clip(spe_norm, 0.001, 0.999))

    try:
        sim.compute()
        life_score = float(sim.output["life_score"])
    except Exception as e:
        print(f"⚠️  Mamdani error: {e}")
        life_score = 50.0

    if life_score < 25:   alert = "critical"
    elif life_score < 50: alert = "warning"
    else:                 alert = "normal"

    return {"life_score": round(life_score, 2), "alert_level": alert}


# ═══════════════════════════════════════════════════════
#  FUNCIÓN PRINCIPAL — Pipeline completo
# ═══════════════════════════════════════════════════════

def run_pipeline(sensor_data: Dict[str, float]) -> Dict[str, Any]:
    """
    Pipeline completo:
      sensor_data (floats) → Red Bayesiana → Mamdani → resultado
    """
    bayesian = run_bayesian(sensor_data)
    mamdani  = run_mamdani(
        fault_probability = bayesian["fault_probability"],
        health_index      = sensor_data.get("health_index", 50.0),
        spe_q             = sensor_data.get("SPE_Q", sensor_data.get("spe_q", 1.0)),
    )

    return {
        "rul_distribution":     bayesian["rul_distribution"],
        "predicted_rul_class":  bayesian["predicted_class"],
        "fault_probability":    bayesian["fault_probability"],
        "evidence_discretized": bayesian["evidence_discretized"],
        "life_score":           mamdani["life_score"],
        "alert_level":          mamdani["alert_level"],
    }
