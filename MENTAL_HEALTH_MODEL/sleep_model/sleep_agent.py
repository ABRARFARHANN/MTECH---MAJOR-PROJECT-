from typing import Dict, Any, List


class SleepAgent:
    """
    Thesis-level Sleep Agent.

    Core inputs:
    - time_in_bed_minutes
    - total_sleep_minutes
    - waso_minutes
    - num_awakenings

    REM and Deep sleep ratios are ESTIMATED
    when not directly available.
    """

    def __init__(self):
        print("[INIT] SleepAgent initialized with thesis-level rules.")

    # ---------- Core feature computations ----------

    def _compute_sleep_efficiency(self, total_sleep_min: float, time_in_bed_min: float) -> float:
        if time_in_bed_min <= 0:
            return 0.0
        return float(max(0.0, min(1.0, total_sleep_min / time_in_bed_min)))

    # ---------- ESTIMATION of REM & Deep ratios ----------

    def _estimate_rem_ratio(
        self,
        total_sleep_min: float,
        sleep_efficiency: float,
        num_awakenings: int,
    ) -> float:
        """
        Estimate REM ratio using sleep quality proxies.
        """
        rem = 0.22  # baseline

        if sleep_efficiency < 0.85:
            rem -= 0.04
        if sleep_efficiency < 0.75:
            rem -= 0.03

        if num_awakenings >= 3:
            rem -= 0.03
        if num_awakenings >= 6:
            rem -= 0.04

        if total_sleep_min < 300:  # <5 hours
            rem -= 0.04

        return float(max(0.05, min(0.30, rem)))

    def _estimate_deep_ratio(
        self,
        total_sleep_min: float,
        sleep_efficiency: float,
        num_awakenings: int,
    ) -> float:
        """
        Estimate Deep sleep ratio using sleep quality proxies.
        """
        deep = 0.22  # baseline

        if sleep_efficiency < 0.85:
            deep -= 0.05
        if sleep_efficiency < 0.75:
            deep -= 0.05

        if num_awakenings >= 3:
            deep -= 0.03
        if num_awakenings >= 6:
            deep -= 0.05

        if total_sleep_min < 300:
            deep -= 0.04

        return float(max(0.05, min(0.35, deep)))

    # ---------- Risk scoring logic ----------

    def _sleep_score_from_features(
        self,
        sleep_efficiency: float,
        waso_min: float,
    ) -> float:
        """
        Combine Sleep Efficiency and WASO into a risk score.
        """
        se_component = 1.0 - sleep_efficiency
        waso_component = min(max(waso_min, 0.0) / 120.0, 1.0)

        score = 0.5 * se_component + 0.5 * waso_component
        return float(max(0.0, min(1.0, score)))

    def _risk_level_from_score(self, sleep_score: float) -> str:
        if sleep_score >= 0.7:
            return "high"
        elif sleep_score >= 0.4:
            return "medium"
        else:
            return "low"

    # ---------- Explainability ----------

    def _build_reasons(
        self,
        sleep_efficiency: float,
        waso_min: float,
        rem_ratio: float,
        deep_ratio: float,
        sleep_score: float,
    ) -> List[str]:
        reasons = []

        if sleep_efficiency < 0.85:
            reasons.append("Low sleep efficiency (<85%) suggests fragmented or poor-quality sleep.")
        else:
            reasons.append("Sleep efficiency is within a healthy range (≥85%).")

        if waso_min > 60:
            reasons.append("High wake after sleep onset (>60 minutes) indicates difficulty maintaining sleep.")
        elif waso_min > 30:
            reasons.append("Moderate wake after sleep onset (30–60 minutes) suggests some sleep disruption.")
        else:
            reasons.append("Wake after sleep onset is low (≤30 minutes), indicating stable sleep continuity.")

        if rem_ratio < 0.15:
            reasons.append("Estimated REM sleep proportion is low (<15%), which may affect emotional regulation.")
        elif rem_ratio > 0.25:
            reasons.append("Estimated REM sleep proportion is relatively high (>25%).")
        else:
            reasons.append("Estimated REM sleep proportion is within a typical range (15–25%).")

        if deep_ratio < 0.20:
            reasons.append("Estimated deep sleep proportion is low (<20%), which may impact physical recovery.")
        elif deep_ratio > 0.35:
            reasons.append("Estimated deep sleep proportion is relatively high (>35%).")
        else:
            reasons.append("Estimated deep sleep proportion is within a moderate range (20–35%).")

        level = self._risk_level_from_score(sleep_score)
        if level == "high":
            reasons.append("Overall sleep pattern suggests high risk for mood deterioration.")
        elif level == "medium":
            reasons.append("Overall sleep pattern suggests moderate risk; monitoring is recommended.")
        else:
            reasons.append("Overall sleep pattern suggests low risk.")

        return reasons

    # ---------- Public API ----------

    def analyze_night(self, record: Dict[str, Any]) -> Dict[str, Any]:
        time_in_bed = float(record.get("time_in_bed_minutes", 0.0))
        total_sleep = float(record.get("total_sleep_minutes", 0.0))
        waso = float(record.get("waso_minutes", 0.0))
        num_awakenings = int(record.get("num_awakenings", 0))

        sleep_efficiency = self._compute_sleep_efficiency(total_sleep, time_in_bed)

        rem_ratio = self._estimate_rem_ratio(
            total_sleep_min=total_sleep,
            sleep_efficiency=sleep_efficiency,
            num_awakenings=num_awakenings,
        )

        deep_ratio = self._estimate_deep_ratio(
            total_sleep_min=total_sleep,
            sleep_efficiency=sleep_efficiency,
            num_awakenings=num_awakenings,
        )

        sleep_score = self._sleep_score_from_features(
            sleep_efficiency=sleep_efficiency,
            waso_min=waso,
        )

        risk_level = self._risk_level_from_score(sleep_score)

        reasons = self._build_reasons(
            sleep_efficiency=sleep_efficiency,
            waso_min=waso,
            rem_ratio=rem_ratio,
            deep_ratio=deep_ratio,
            sleep_score=sleep_score,
        )

        return {
            "sleep_efficiency": sleep_efficiency,
            "sleep_score": sleep_score,
            "sleep_risk_level": risk_level,
            "waso_minutes": waso,
            "rem_ratio_estimated": rem_ratio,
            "deep_ratio_estimated": deep_ratio,
            "num_awakenings": num_awakenings,
            "reasons": reasons,
        }
