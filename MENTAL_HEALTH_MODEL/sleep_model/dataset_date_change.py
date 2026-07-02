import pandas as pd

# Load sleep agent CSV
df = pd.read_csv("sleep_data.csv")

# Convert date column to datetime
df["date"] = pd.to_datetime(df["date"])

# Define new start date
NEW_START_DATE = pd.to_datetime("2025-11-05")

# Apply date shift PER USER
df["date"] = df.groupby("user_id").cumcount().apply(
    lambda x: NEW_START_DATE + pd.Timedelta(days=x)
)

# Save corrected file
df.to_csv("sleep_agent_1.csv", index=False)

print("✅ Sleep agent dates corrected")
