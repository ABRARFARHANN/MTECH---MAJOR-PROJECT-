import joblib
from datetime import date
from pathlib import Path
import sys
import pandas as pd

# Ensure we can import helper modules regardless of CWD
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "OVERALL_RISK_MODEL"))
sys.path.append(str(ROOT / "MENTAL_HEALTH_MODEL"))

from overall_risk_levels import (  # type: ignore
    overall_bp_and_mental,
    overall_bp_and_diabetes,
    overall_mental_and_diabetes,
    overall_bp_diabetes_mental,
)
from mental_health_service import predict_mental_health_risk_for_day  # type: ignore


def bp_risk_level(prob: float) -> str:
    """BP risk mapping (same logic as in bp_model notebook)."""
    if prob >= 0.8:
        return "HIGH"
    elif prob >= 0.5:
        return "MEDIUM"
    else:
        return "LOW"


def diabetes_risk_level(prob: float) -> str:
    """Diabetes risk mapping (same as updated notebook thresholds)."""
    # LOW: prob < 0.008
    # MEDIUM: 0.008 <= prob < 0.012
    # HIGH: prob >= 0.012
    if prob >= 0.012:
        return "HIGH"
    elif prob >= 0.008:
        return "MEDIUM"
    else:
        return "LOW"


def run_demo_for_one_person():
    """Run two realistic synthetic examples: one low risk and one high risk.

    NOTE: These are synthetic, clinically plausible profiles for demo only,
    not real patients and not for medical use.
    """

    # Load models once
    bp_model = joblib.load("BP_MODEL/bp_model.pkl")
    bp_scaler = joblib.load("BP_MODEL/diabetes_encoder.pkl")
    bp_features = joblib.load("BP_MODEL/bp_features.pkl")

    diab_model = joblib.load("DIABETES_MODEL/diabetes_model.pkl")
    diab_scaler = joblib.load("DIABETES_MODEL/diabetes_scaler.pkl")
    diab_features = joblib.load("DIABETES_MODEL/diabetes_features.pkl")

    def evaluate_scenario(label: str, bp_patient: dict, diab_patient: dict, sleep_record: dict, activity_record: dict, text_messages: list[str]) -> None:
        # ---- BP prediction ----
        X_bp = pd.DataFrame([bp_patient])[bp_features]
        X_bp_scaled = bp_scaler.transform(X_bp)
        prob_bp = float(bp_model.predict_proba(X_bp_scaled)[:, 1][0])
        bp_level = bp_risk_level(prob_bp)

        # ---- Diabetes prediction ----
        X_diab = pd.DataFrame([diab_patient])[diab_features]
        X_diab_scaled = diab_scaler.transform(X_diab)
        prob_diab = float(diab_model.predict_proba(X_diab_scaled)[:, 1][0])
        diab_level = diabetes_risk_level(prob_diab)

        # ---- Mental-health prediction ----
        mh_result = predict_mental_health_risk_for_day(
            user_id=label,
            day_date=date.today(),
            sleep_record=sleep_record,
            activity_record=activity_record,
            text_messages=text_messages,
            activity_history_before_today=[],
            fusion_model_path=str(ROOT / "MENTAL_HEALTH_MODEL" / "final_model" / "fusion_rf_model.pkl"),
        )

        mh_level = mh_result["fusion_risk_level"]

        # ---- Combined overall risks ----
        bp_mh_overall = overall_bp_and_mental(bp_level, mh_level)
        bp_diab_overall = overall_bp_and_diabetes(bp_level, diab_level)
        mh_diab_overall = overall_mental_and_diabetes(mh_level, diab_level)
        all_three_overall = overall_bp_diabetes_mental(bp_level, diab_level, mh_level)

        print(f"\n===== {label} =====")
        print("=== Per-condition risks ===")
        print(f"BP: prob={prob_bp:.4f}, level={bp_level}")
        print(f"Diabetes: prob={prob_diab:.4f}, level={diab_level}")
        print(
            "Mental health: prob=%.4f, level=%s"
            % (mh_result["fusion_probability"], mh_level)
        )

        print("\n=== Combined overall risks ===")
        print("BP + Mental ->", bp_mh_overall)
        print("BP + Diabetes ->", bp_diab_overall)
        print("Mental + Diabetes ->", mh_diab_overall)
        print("All three ->", all_three_overall)

    # -------- LOW-RISK synthetic person --------
    low_bp_patient = {
        "Sex(M/F)": 0,          # female
        "Age(year)": 30,
        "Height(cm)": 165,
        "Weight(kg)": 60,
        "Heart Rate(b/m)": 70,
        "BMI(kg/m^2)": 22.0,
    }

    low_diab_patient = {
        "Pregnancies": 0,
        "Glucose": 92,
        "BloodPressure": 70,
        "SkinThickness": 24,
        "Insulin": 80,
        "BMI": 23.0,
        "DiabetesPedigreeFunction": 0.20,
        "Age": 30,
    }

    low_sleep = {
        "time_in_bed_minutes": 8 * 60,
        "total_sleep_minutes": 7 * 60,
        "waso_minutes": 20,
        "num_awakenings": 2,
    }

    low_activity = {
        "approx_steps": 8000,
        "walking_minutes": 40.0,
        "sitting_hours": 8.0,
        "went_outside_home": True,
        "num_outings": 2,
        "visited_by_someone": True,
        "felt_unsteady_while_walking": False,
        "any_fall_or_near_fall": False,
        "needed_support_while_walking": "none",
        "self_rated_energy": 4,
        "pain_while_walking": 1,
        "shortness_of_breath": "none",
    }

    low_text = [
        "I felt good today and had a productive day at work.",
        "Went for a walk with friends and enjoyed it.",
    ]

    evaluate_scenario(
        label="LOW-RISK synthetic person",
        bp_patient=low_bp_patient,
        diab_patient=low_diab_patient,
        sleep_record=low_sleep,
        activity_record=low_activity,
        text_messages=low_text,
    )

    # -------- MEDIUM-RISK synthetic person --------
    medium_bp_patient = {
        "Sex(M/F)": 1,
        "Age(year)": 55,
        "Height(cm)": 168,
        "Weight(kg)": 82,
        "Heart Rate(b/m)": 88,
        "BMI(kg/m^2)": 29.1,
    }

    # Diabetes profile chosen from a real medium-probability pattern in the dataset
    medium_diab_patient = {
        "Pregnancies": 8,
        "Glucose": 183,
        "BloodPressure": 64,
        "SkinThickness": 29,
        "Insulin": 125,
        "BMI": 23.3,
        "DiabetesPedigreeFunction": 0.672,
        "Age": 32,
    }

    medium_sleep = {
        "time_in_bed_minutes": 8 * 60,
        "total_sleep_minutes": 4.5 * 60,
        "waso_minutes": 90,
        "num_awakenings": 6,
    }

    medium_activity = {
        "approx_steps": 2000,
        "walking_minutes": 10.0,
        "sitting_hours": 12.0,
        "went_outside_home": False,
        "num_outings": 0,
        "visited_by_someone": False,
        "felt_unsteady_while_walking": True,
        "any_fall_or_near_fall": False,
        "needed_support_while_walking": "stick",
        "self_rated_energy": 3,
        "pain_while_walking": 5,
        "shortness_of_breath": "mild",
    }

    medium_text = [
        "I felt quite sad and stressed for part of today.",
        "But I also enjoyed a nice chat with a friend, which made me feel a bit better.",
    ]

    evaluate_scenario(
        label="MEDIUM-RISK synthetic person",
        bp_patient=medium_bp_patient,
        diab_patient=medium_diab_patient,
        sleep_record=medium_sleep,
        activity_record=medium_activity,
        text_messages=medium_text,
    )

    # -------- HIGH-RISK synthetic person --------
    high_bp_patient = {
        "Sex(M/F)": 1,
        "Age(year)": 68,
        "Height(cm)": 165,
        "Weight(kg)": 95,
        "Heart Rate(b/m)": 96,
        "BMI(kg/m^2)": 34.9,
    }

    high_diab_patient = {
        "Pregnancies": 0,
        "Glucose": 210,
        "BloodPressure": 88,
        "SkinThickness": 35,
        "Insulin": 220,
        "BMI": 36.0,
        "DiabetesPedigreeFunction": 1.50,
        "Age": 60,
    }

    high_sleep = {
        "time_in_bed_minutes": 7 * 60,
        "total_sleep_minutes": 4 * 60,
        "waso_minutes": 120,
        "num_awakenings": 7,
    }

    high_activity = {
        "approx_steps": 1500,
        "walking_minutes": 10.0,
        "sitting_hours": 13.0,
        "went_outside_home": False,
        "num_outings": 0,
        "visited_by_someone": False,
        "felt_unsteady_while_walking": True,
        "any_fall_or_near_fall": True,
        "needed_support_while_walking": "walker",
        "self_rated_energy": 1,
        "pain_while_walking": 7,
        "shortness_of_breath": "severe",
    }

    high_text = [
        "I feel very tired and worried about my health.",
        "Did not sleep well and stayed home all day.",
        "Feeling lonely and stressed most of the time.",
    ]

    evaluate_scenario(
        label="HIGH-RISK synthetic person",
        bp_patient=high_bp_patient,
        diab_patient=high_diab_patient,
        sleep_record=high_sleep,
        activity_record=high_activity,
        text_messages=high_text,
    )


if __name__ == "__main__":
    run_demo_for_one_person()
