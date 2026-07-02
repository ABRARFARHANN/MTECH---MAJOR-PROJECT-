RISK_SCORE = {
    "LOW": 0,
    "MEDIUM": 1,
    "MODERATE": 1,
    "HIGH": 2,
}


def _score(level: str) -> int:
    """Convert a textual risk level to a numeric severity score."""
    if level is None:
        return 0
    return RISK_SCORE.get(str(level).upper(), 0)


def _score_to_level(score: float) -> str:
    """Map an average/max score back to LOW/MEDIUM/HIGH."""
    # Simple rule: 0 -> LOW, 0<score<1.5 -> MEDIUM, >=1.5 -> HIGH
    if score >= 1.5:
        return "HIGH"
    elif score >= 0.5:
        return "MEDIUM"
    else:
        return "LOW"


def combine_levels(*levels: str) -> str:
    """Generic combiner for any set of risk levels.

    Strategy:
    - Map each level to 0 (LOW), 1 (MEDIUM/MODERATE), 2 (HIGH).
    - Take the maximum severity across all provided levels.
    - Map back to LOW/MEDIUM/HIGH.

    This makes overall risk HIGH if any component is HIGH,
    MEDIUM if at least one component is MEDIUM/MODERATE (and none HIGH),
    otherwise LOW.
    """

    if not levels:
        return "LOW"

    scores = [_score(lvl) for lvl in levels]
    max_score = max(scores)
    return _score_to_level(float(max_score))


def overall_bp_and_mental(bp_level: str, mental_level: str) -> str:
    """Overall risk combining BP and mental-health risk levels."""
    return combine_levels(bp_level, mental_level)


def overall_bp_and_diabetes(bp_level: str, diabetes_level: str) -> str:
    """Overall risk combining BP and diabetes risk levels."""
    return combine_levels(bp_level, diabetes_level)


def overall_mental_and_diabetes(mental_level: str, diabetes_level: str) -> str:
    """Overall risk combining mental-health and diabetes risk levels."""
    return combine_levels(mental_level, diabetes_level)


def overall_bp_diabetes_mental(bp_level: str, diabetes_level: str, mental_level: str) -> str:
    """Overall risk combining BP, diabetes, and mental-health risk levels."""
    return combine_levels(bp_level, diabetes_level, mental_level)


if __name__ == "__main__":
    # Small demo using example levels
    examples = [
        ("LOW", "LOW", "LOW"),
        ("HIGH", "LOW", "LOW"),
        ("LOW", "MEDIUM", "LOW"),
        ("LOW", "LOW", "HIGH"),
    ]

    for bp, diab, mh in examples:
        print("\nExample:")
        print("  BP:", bp, "Diabetes:", diab, "Mental:", mh)
        print("  BP + Mental ->", overall_bp_and_mental(bp, mh))
        print("  BP + Diabetes ->", overall_bp_and_diabetes(bp, diab))
        print("  Mental + Diabetes ->", overall_mental_and_diabetes(mh, diab))
        print("  All three ->", overall_bp_diabetes_mental(bp, diab, mh))
