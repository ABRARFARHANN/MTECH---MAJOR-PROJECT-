import random
import pandas as pd
from datetime import datetime, timedelta

# -----------------------------
# CONFIG
# -----------------------------
NUM_PARTICIPANTS = 5
DAYS = 30
START_DATE = datetime(2025, 11, 5)

random.seed(42)

# -----------------------------
# MESSAGE BANKS
# -----------------------------
POSITIVE = [
    "Today felt calm.",
    "I slept well.",
    "I watched television.",
    "I spoke with my neighbor.",
    "I felt peaceful.",
    "The day went smoothly.",
]

NEUTRAL = [
    "Nothing much happened today.",
    "I stayed inside.",
    "The day was okay.",
    "I rested most of the time.",
    "I watched TV.",
]

NEGATIVE = [
    "I felt lonely today.",
    "I missed my family.",
    "I felt tired and weak.",
    "I felt sad.",
    "The day felt heavy.",
]

SEVERE_NEGATIVE = [
    "I feel very lonely.",
    "No one visited me.",
    "I feel abandoned.",
    "I feel hopeless.",
    "I do not feel like talking.",
    "Everything feels meaningless.",
]

# -----------------------------
# MOOD STATES
# -----------------------------
MOODS = ["stable", "vulnerable", "distressed"]

MOOD_TRANSITION = {
    "stable":      {"stable": 0.75, "vulnerable": 0.20, "distressed": 0.05},
    "vulnerable":  {"stable": 0.20, "vulnerable": 0.55, "distressed": 0.25},
    "distressed":  {"stable": 0.10, "vulnerable": 0.25, "distressed": 0.65},
}

# -----------------------------
# MESSAGE SAMPLER
# -----------------------------
def generate_messages(mood):
    n = random.randint(2, 4)

    if mood == "stable":
        pool = POSITIVE + NEUTRAL
    elif mood == "vulnerable":
        pool = NEUTRAL + NEGATIVE
    else:  # distressed
        pool = NEGATIVE + SEVERE_NEGATIVE

    return random.sample(pool, k=n)

# -----------------------------
# MOOD TRANSITION
# -----------------------------
def next_mood(current_mood):
    probs = MOOD_TRANSITION[current_mood]
    moods = list(probs.keys())
    weights = list(probs.values())
    return random.choices(moods, weights=weights)[0]

# -----------------------------
# MAIN GENERATION
# -----------------------------
rows = []

for pid in range(1, NUM_PARTICIPANTS + 1):
    person_id = f"G{pid}"
    mood = random.choices(
        MOODS,
        weights=[0.55, 0.30, 0.15],  # population distribution
    )[0]

    date = START_DATE

    for _ in range(DAYS):
        messages = generate_messages(mood)

        rows.append({
            "person_id": person_id,
            "date": date.strftime("%Y-%m-%d"),
            "messages": messages,
        })

        mood = next_mood(mood)
        date += timedelta(days=1)

# -----------------------------
# SAVE CSV
# -----------------------------
df = pd.DataFrame(rows)

# Store messages as string (CSV-safe)
df["messages"] = df["messages"].apply(lambda x: str(x))

df.to_csv("text_agent_input.csv", index=False)

print("✅ text_agent_input.csv created")
