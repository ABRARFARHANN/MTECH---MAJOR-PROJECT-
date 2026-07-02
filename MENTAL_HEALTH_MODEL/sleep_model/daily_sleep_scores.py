import pandas as pd
from sleep_agent import SleepAgent  # make sure filename matches


def build_daily_sleep_scores(
    input_csv: str = "sleep_data.csv",
    output_csv: str = "daily_sleep_scores.csv",
):
    print(f"[INFO] Reading sleep data from: {input_csv}")
    df = pd.read_csv(input_csv)

    # Required input columns
    required_cols = {
        "user_id",
        "date",
        "total_sleep_hours",
        "awakenings",
        "sleep_efficiency",
    }
    if not required_cols.issubset(df.columns):
        raise ValueError(
            f"Input CSV must contain columns at least: {required_cols}, "
            f"found: {df.columns.tolist()}"
        )

    # Normalize date
    df["date"] = df["date"].astype(str)

    # Group by user and date (safety for multi-row nights)
    groups = df.groupby(["user_id", "date"])

    agent = SleepAgent()
    results = []

    for (user_id, date), group in groups:
        # ---- Aggregate nightly metrics ----
        total_sleep_hours = float(group["total_sleep_hours"].sum())
        total_sleep_minutes = total_sleep_hours * 60.0

        sleep_efficiency = float(group["sleep_efficiency"].mean())

        # Derive time in bed
        if sleep_efficiency > 0:
            time_in_bed_minutes = total_sleep_minutes / sleep_efficiency
        else:
            time_in_bed_minutes = total_sleep_minutes

        # Awakenings → WASO approximation (10 min per awakening)
        num_awakenings = int(group["awakenings"].sum())
        waso_minutes = num_awakenings * 10.0

        record = {
            "time_in_bed_minutes": time_in_bed_minutes,
            "total_sleep_minutes": total_sleep_minutes,
            "waso_minutes": waso_minutes,
            "num_awakenings": num_awakenings,
        }

        print(f"[INFO] Analyzing sleep for user_id={user_id}, date={date}")
        analysis = agent.analyze_night(record)

        results.append(
            {
                "user_id": user_id,
                "date": date,
                "total_sleep_hours": round(total_sleep_hours, 2),
                "sleep_efficiency": round(analysis["sleep_efficiency"], 3),
                "sleep_score": round(analysis["sleep_score"], 3),
                "sleep_risk_level": analysis["sleep_risk_level"],
                "waso_minutes": round(analysis["waso_minutes"], 1),
                "num_awakenings": analysis["num_awakenings"],
                "rem_ratio_estimated": round(analysis["rem_ratio_estimated"], 3),
                "deep_ratio_estimated": round(analysis["deep_ratio_estimated"], 3),
                "sleep_reasons": "; ".join(analysis["reasons"]),
            }
        )

    out_df = pd.DataFrame(results)

    preferred_order = [
        "user_id",
        "date",
        "total_sleep_hours",
        "sleep_efficiency",
        "sleep_score",
        "sleep_risk_level",
        "waso_minutes",
        "num_awakenings",
        "rem_ratio_estimated",
        "deep_ratio_estimated",
        "sleep_reasons",
    ]

    out_df = out_df[preferred_order]

    print(f"[INFO] Saving daily sleep scores to: {output_csv}")
    out_df.to_csv(output_csv, index=False)
    print("[INFO] Done.")


if __name__ == "__main__":
    build_daily_sleep_scores()
