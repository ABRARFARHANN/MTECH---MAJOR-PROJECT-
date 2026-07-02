from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Dict, List

import joblib
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory

# Local project imports
import sys

ROOT = Path(__file__).resolve().parent

# Ensure we can import the mental-health and overall-risk helpers
sys.path.append(str(ROOT / "MENTAL_HEALTH_MODEL"))
sys.path.append(str(ROOT / "OVERALL_RISK_MODEL"))

from mental_health_service import predict_mental_health_risk_for_day  # type: ignore
from overall_risk_levels import (  # type: ignore
    overall_bp_and_diabetes,
    overall_bp_and_mental,
    overall_bp_diabetes_mental,
    overall_mental_and_diabetes,
)


def bp_risk_level(prob: float) -> str:
    """BP risk mapping.

    Adjusted so that moderately high probabilities are already classified
    as HIGH for demonstration/educational use.

    - LOW:    prob < 0.3
    - MEDIUM: 0.3 <= prob < 0.6
    - HIGH:   prob >= 0.6
    """
    if prob >= 0.6:
        return "HIGH"
    elif prob >= 0.3:
        return "MEDIUM"
    else:
        return "LOW"


def diabetes_risk_level(prob: float) -> str:
    """Diabetes risk mapping (same thresholds as notebooks)."""
    if prob >= 0.012:
        return "HIGH"
    elif prob >= 0.008:
        return "MEDIUM"
    else:
        return "LOW"


def load_models() -> Dict[str, Any]:
    """Load all trained models and feature lists once."""
    bp_model = joblib.load(ROOT / "BP_MODEL" / "bp_model.pkl")
    bp_scaler = joblib.load(ROOT / "BP_MODEL" / "diabetes_encoder.pkl")
    bp_features: List[str] = joblib.load(ROOT / "BP_MODEL" / "bp_features.pkl")

    diab_model = joblib.load(ROOT / "DIABETES_MODEL" / "diabetes_model.pkl")
    diab_scaler = joblib.load(ROOT / "DIABETES_MODEL" / "diabetes_scaler.pkl")
    diab_features: List[str] = joblib.load(ROOT / "DIABETES_MODEL" / "diabetes_features.pkl")

    fusion_model_path = str(
        ROOT
        / "MENTAL_HEALTH_MODEL"
        / "final_model"
        / "fusion_rf_model.pkl"
    )

    return {
        "bp_model": bp_model,
        "bp_scaler": bp_scaler,
        "bp_features": bp_features,
        "diab_model": diab_model,
        "diab_scaler": diab_scaler,
        "diab_features": diab_features,
        "fusion_model_path": fusion_model_path,
    }


MODELS = load_models()

app = Flask(__name__, static_folder="FRONT_END", static_url_path="")


# ---------------------- Static front-end routes ----------------------


@app.route("/")
def index() -> Any:
    """Serve the main front-end home page."""
    return send_from_directory("FRONT_END", "index.html")


# --------------------------- API endpoints ---------------------------


@app.post("/api/bp")
def api_bp() -> Any:
    data = request.get_json(force=True) or {}

    required_fields = [
        "Sex(M/F)",
        "Age(year)",
        "Height(cm)",
        "Weight(kg)",
        "Heart Rate(b/m)",
    ]

    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # Compute BMI on the server side to avoid duplication
    height_m = float(data["Height(cm)"]) / 100.0
    bmi = float(data["Weight(kg)"]) / (height_m ** 2)

    patient = {
        "Sex(M/F)": int(data["Sex(M/F)"]),
        "Age(year)": int(data["Age(year)"]),
        "Height(cm)": float(data["Height(cm)"]),
        "Weight(kg)": float(data["Weight(kg)"]),
        "Heart Rate(b/m)": float(data["Heart Rate(b/m)"]),
        "BMI(kg/m^2)": float(bmi),
    }

    X_bp = pd.DataFrame([patient])[MODELS["bp_features"]]
    X_bp_scaled = MODELS["bp_scaler"].transform(X_bp)
    prob = float(MODELS["bp_model"].predict_proba(X_bp_scaled)[:, 1][0])
    level = bp_risk_level(prob)

    return jsonify({"probability": prob, "risk_level": level})


@app.post("/api/diabetes")
def api_diabetes() -> Any:
    data = request.get_json(force=True) or {}

    required_fields = [
        "Pregnancies",
        "Glucose",
        "BloodPressure",
        "SkinThickness",
        "Insulin",
        "BMI",
        "DiabetesPedigreeFunction",
        "Age",
    ]

    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    patient = {
        "Pregnancies": int(data["Pregnancies"]),
        "Glucose": float(data["Glucose"]),
        "BloodPressure": float(data["BloodPressure"]),
        "SkinThickness": float(data["SkinThickness"]),
        "Insulin": float(data["Insulin"]),
        "BMI": float(data["BMI"]),
        "DiabetesPedigreeFunction": float(data["DiabetesPedigreeFunction"]),
        "Age": int(data["Age"]),
    }

    X_diab = pd.DataFrame([patient])[MODELS["diab_features"]]
    X_diab_scaled = MODELS["diab_scaler"].transform(X_diab)
    prob = float(MODELS["diab_model"].predict_proba(X_diab_scaled)[:, 1][0])
    level = diabetes_risk_level(prob)

    return jsonify({"probability": prob, "risk_level": level})


@app.post("/api/mental")
def api_mental() -> Any:
    data = request.get_json(force=True) or {}

    sleep_record = data.get("sleep_record") or {}
    activity_record = data.get("activity_record") or {}
    messages: List[str] = data.get("messages") or []

    # Basic validation
    sleep_required = [
        "time_in_bed_minutes",
        "total_sleep_minutes",
        "waso_minutes",
        "num_awakenings",
    ]
    activity_required = [
        "approx_steps",
        "walking_minutes",
        "sitting_hours",
        "went_outside_home",
        "num_outings",
        "visited_by_someone",
        "felt_unsteady_while_walking",
        "any_fall_or_near_fall",
        "needed_support_while_walking",
        "self_rated_energy",
        "pain_while_walking",
        "shortness_of_breath",
    ]

    missing_sleep = [f for f in sleep_required if f not in sleep_record]
    missing_act = [f for f in activity_required if f not in activity_record]

    if missing_sleep or missing_act:
        return (
            jsonify(
                {
                    "error": "Missing sleep/activity fields",
                    "missing_sleep": missing_sleep,
                    "missing_activity": missing_act,
                }
            ),
            400,
        )

    result = predict_mental_health_risk_for_day(
        user_id="web_user",
        day_date=date.today(),
        sleep_record=sleep_record,
        activity_record=activity_record,
        text_messages=messages,
        activity_history_before_today=[],
        fusion_model_path=MODELS["fusion_model_path"],
    )

    return jsonify(
        {
            "probability": float(result["fusion_probability"]),
            "risk_level": str(result["fusion_risk_level"]),
            "details": result,
        }
    )


@app.post("/api/overall")
def api_overall() -> Any:
    """Compute overall risk combining BP, diabetes, and mental-health.

    Expects JSON with keys:
      - bp_patient: fields for /api/bp
      - diab_patient: fields for /api/diabetes
      - mental: {sleep_record, activity_record, messages}
    """

    payload = request.get_json(force=True) or {}
    bp_patient = payload.get("bp_patient") or {}
    diab_patient = payload.get("diab_patient") or {}
    mental = payload.get("mental") or {}

    # --- BP ---
    bp_height_cm = float(bp_patient.get("Height(cm)", 0) or 0)
    bp_weight_kg = float(bp_patient.get("Weight(kg)", 0) or 0)
    if bp_height_cm <= 0 or bp_weight_kg <= 0:
        return jsonify({"error": "Invalid or missing BP height/weight"}), 400

    height_m = bp_height_cm / 100.0
    bmi = bp_weight_kg / (height_m ** 2)

    bp_struct = {
        "Sex(M/F)": int(bp_patient.get("Sex(M/F)", 0)),
        "Age(year)": int(bp_patient.get("Age(year)", 0)),
        "Height(cm)": bp_height_cm,
        "Weight(kg)": bp_weight_kg,
        "Heart Rate(b/m)": float(bp_patient.get("Heart Rate(b/m)", 0)),
        "BMI(kg/m^2)": float(bmi),
    }

    X_bp = pd.DataFrame([bp_struct])[MODELS["bp_features"]]
    X_bp_scaled = MODELS["bp_scaler"].transform(X_bp)
    bp_prob = float(MODELS["bp_model"].predict_proba(X_bp_scaled)[:, 1][0])
    bp_level = bp_risk_level(bp_prob)

    # --- Diabetes ---
    diab_struct = {
        "Pregnancies": int(diab_patient.get("Pregnancies", 0)),
        "Glucose": float(diab_patient.get("Glucose", 0)),
        "BloodPressure": float(diab_patient.get("BloodPressure", 0)),
        "SkinThickness": float(diab_patient.get("SkinThickness", 0)),
        "Insulin": float(diab_patient.get("Insulin", 0)),
        "BMI": float(diab_patient.get("BMI", 0)),
        "DiabetesPedigreeFunction": float(
            diab_patient.get("DiabetesPedigreeFunction", 0)
        ),
        "Age": int(diab_patient.get("Age", 0)),
    }

    X_diab = pd.DataFrame([diab_struct])[MODELS["diab_features"]]
    X_diab_scaled = MODELS["diab_scaler"].transform(X_diab)
    diab_prob = float(MODELS["diab_model"].predict_proba(X_diab_scaled)[:, 1][0])
    diab_level = diabetes_risk_level(diab_prob)

    # --- Mental ---
    sleep_record = mental.get("sleep_record") or {}
    activity_record = mental.get("activity_record") or {}
    messages: List[str] = mental.get("messages") or []

    mh_result = predict_mental_health_risk_for_day(
        user_id="web_user_overall",
        day_date=date.today(),
        sleep_record=sleep_record,
        activity_record=activity_record,
        text_messages=messages,
        activity_history_before_today=[],
        fusion_model_path=MODELS["fusion_model_path"],
    )

    mh_prob = float(mh_result["fusion_probability"])
    mh_level = str(mh_result["fusion_risk_level"])

    # Combined overall risks
    bp_mh_overall = overall_bp_and_mental(bp_level, mh_level)
    bp_diab_overall = overall_bp_and_diabetes(bp_level, diab_level)
    mh_diab_overall = overall_mental_and_diabetes(mh_level, diab_level)
    all_three_overall = overall_bp_diabetes_mental(bp_level, diab_level, mh_level)

    return jsonify(
        {
            "bp": {"probability": bp_prob, "risk_level": bp_level},
            "diabetes": {"probability": diab_prob, "risk_level": diab_level},
            "mental": {"probability": mh_prob, "risk_level": mh_level},
            "overall": {
                "bp_and_mental": bp_mh_overall,
                "bp_and_diabetes": bp_diab_overall,
                "mental_and_diabetes": mh_diab_overall,
                "all_three": all_three_overall,
            },
        }
    )


if __name__ == "__main__":
    # Default Flask dev server on port 5001 to avoid clashes
    app.run(host="0.0.0.0", port=5001, debug=True)
