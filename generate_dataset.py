"""
Generate a fresh synthetic dataset: Sleep Debt & Screen Time – Late Night Phone Habits
8,500 records with biophysically-grounded simulation logic.

Columns produced:
  - user_id
  - age
  - gender
  - chronotype                (Early Bird / Night Owl / Intermediate)
  - occupation                (Student / Professional / Freelancer / Retired / Unemployed)
  - bedtime_hour              (24h float, e.g. 23.5 = 11:30 PM)
  - screen_time_before_bed_min
  - primary_app_category      (Short-Form Video / Social Media / Streaming / Gaming / E-Reading / News / Messaging)
  - screen_brightness_pct     (0–100)
  - blue_light_filter_on      (True / False)
  - caffeine_intake_mg        (0–500)
  - caffeine_last_hour        (last caffeine intake hour, 24h)
  - physical_activity_min     (daily exercise minutes)
  - room_temperature_f        (bedroom temp)
  - ambient_noise_db          (bedroom noise level)
  - sleep_onset_latency_min   (time to fall asleep)
  - total_sleep_hours
  - rem_sleep_pct             (% of total sleep that is REM)
  - deep_sleep_pct            (% of total sleep that is deep/slow-wave)
  - awakenings_count          (number of mid-sleep awakenings)
  - sleep_efficiency_pct      (time asleep / time in bed * 100)
  - next_day_fatigue_score    (1–10 continuous, regression target)
  - sleep_debt_category       (None / Mild / Moderate / Severe – classification target)
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)
N = 8500

# === Demographics ===
user_ids = np.arange(1, N + 1)
ages = np.clip(np.random.normal(28, 10, N), 16, 65).astype(int)
genders = np.random.choice(["Male", "Female", "Non-Binary"], N, p=[0.48, 0.48, 0.04])

chronotypes = np.random.choice(
    ["Early Bird", "Night Owl", "Intermediate"], N, p=[0.25, 0.35, 0.40]
)
occupations = np.random.choice(
    ["Student", "Professional", "Freelancer", "Retired", "Unemployed"],
    N, p=[0.30, 0.35, 0.15, 0.10, 0.10]
)

# === Behavioral Features ===
# Bedtime hour (Night Owls skew later)
# We work in a continuous space where 24+ means past midnight
bedtime_base = np.where(
    chronotypes == "Night Owl",
    np.random.normal(25.0, 0.8, N),       # ~1 AM (25 = 1 AM next day)
    np.where(
        chronotypes == "Early Bird",
        np.random.normal(22.5, 0.6, N),   # ~10:30 PM
        np.random.normal(23.5, 0.7, N)    # ~11:30 PM
    )
)
bedtime_base = np.clip(bedtime_base, 20.0, 27.5)  # 8 PM to 3:30 AM
# Convert to 24h clock (wrap values > 24)
bedtime_hour = np.where(bedtime_base >= 24, bedtime_base - 24, bedtime_base)

# Screen time before bed
screen_time_min = np.clip(
    np.random.lognormal(np.log(45), 0.6, N), 5, 240
).astype(int)

# Primary app category with arousal weights
app_categories = [
    "Short-Form Video", "Social Media", "Streaming",
    "Gaming", "E-Reading", "News", "Messaging"
]
app_arousal = {
    "Short-Form Video": 0.95, "Social Media": 0.80, "Streaming": 0.60,
    "Gaming": 0.85, "E-Reading": 0.20, "News": 0.55, "Messaging": 0.65
}
# Younger people skew towards short-form video
app_probs_young = [0.35, 0.25, 0.12, 0.12, 0.03, 0.05, 0.08]
app_probs_old   = [0.10, 0.15, 0.20, 0.05, 0.25, 0.15, 0.10]

primary_app = []
for a in ages:
    weight = np.clip((a - 16) / (65 - 16), 0, 1)
    probs = np.array(app_probs_young) * (1 - weight) + np.array(app_probs_old) * weight
    probs /= probs.sum()
    primary_app.append(np.random.choice(app_categories, p=probs))
primary_app = np.array(primary_app)

screen_brightness = np.clip(np.random.normal(70, 20, N), 5, 100).astype(int)
blue_light_filter = np.random.choice([True, False], N, p=[0.35, 0.65])

# Caffeine
caffeine_mg = np.clip(np.random.exponential(80, N), 0, 500).astype(int)
caffeine_last_hour = np.clip(
    np.random.normal(16, 4, N), 6, 23
).round(1)

# Physical activity
physical_activity_min = np.clip(np.random.exponential(30, N), 0, 180).astype(int)

# Room conditions
room_temp_f = np.clip(np.random.normal(70, 4, N), 58, 82).round(1)
ambient_noise_db = np.clip(np.random.normal(35, 10, N), 10, 70).round(1)

# === Biophysical Simulation ===

# 1. Melatonin suppression factor (0 = no suppression, 1 = max)
brightness_norm = screen_brightness / 100.0
blue_filter_mitigation = np.where(blue_light_filter, 0.55, 1.0)
time_factor = np.clip(screen_time_min / 120.0, 0, 1)  # saturates at 2h
melatonin_suppression = brightness_norm * blue_filter_mitigation * time_factor

# 2. Cognitive arousal from app type
arousal_scores = np.array([app_arousal[a] for a in primary_app])

# 3. Caffeine half-life impact (caffeine half-life ~5h)
hours_since_caffeine = np.clip(
    np.where(bedtime_hour >= 12, bedtime_hour, bedtime_hour + 24) - caffeine_last_hour,
    0, 18
)
caffeine_at_bed = caffeine_mg * (0.5 ** (hours_since_caffeine / 5.0))
caffeine_effect = np.clip(caffeine_at_bed / 200.0, 0, 1)  # normalized

# 4. Sleep onset latency
sol_base = 10
sol = sol_base + (
    melatonin_suppression * 20 +
    arousal_scores * 15 +
    caffeine_effect * 25 +
    np.where(room_temp_f > 74, (room_temp_f - 74) * 1.5, 0) +
    np.where(ambient_noise_db > 40, (ambient_noise_db - 40) * 0.5, 0) +
    np.random.normal(0, 5, N)
)
sleep_onset_latency = np.clip(sol, 3, 90).round(1)

# 5. Total sleep hours (ideal ~7.5h, reduced by disruptions)
ideal_sleep = np.where(ages < 25, 8.5, np.where(ages < 45, 7.5, 7.0))
# late bedtimes reduce available sleep (wake time constrained)
# Use bedtime_base (continuous) for wake pressure calculation
wake_pressure = np.clip(
    (bedtime_base - 22) * 0.25, 0, 2.0
)
total_sleep = ideal_sleep - wake_pressure - (sleep_onset_latency / 60) - (
    melatonin_suppression * 0.3 + caffeine_effect * 0.25
) + np.random.normal(0, 0.6, N)
total_sleep = np.clip(total_sleep, 2.5, 10.5).round(2)

# 6. REM sleep % (normal ~20-25%, suppressed by arousal + caffeine)
rem_pct = np.clip(
    22 - arousal_scores * 5 - caffeine_effect * 4 - melatonin_suppression * 3
    + np.random.normal(0, 2, N),
    5, 35
).round(1)

# 7. Deep sleep % (normal ~15-20%)
deep_pct = np.clip(
    18 - melatonin_suppression * 4 - caffeine_effect * 3
    + (physical_activity_min / 60) * 2
    + np.random.normal(0, 2, N),
    3, 30
).round(1)

# 8. Awakenings
awakenings = np.clip(
    np.random.poisson(
        1.5 + caffeine_effect * 2 + melatonin_suppression * 1.5 +
        np.where(ambient_noise_db > 45, 1.0, 0),
        N
    ), 0, 12
)

# 9. Sleep efficiency
sleep_efficiency = np.clip(
    92 - (sleep_onset_latency / 60 * 10) - awakenings * 1.5
    - melatonin_suppression * 5 + np.random.normal(0, 3, N),
    50, 99
).round(1)

# === Target Variables ===

# Next-day fatigue score (1-10)
fatigue = (
    1.5 +
    (8.0 - total_sleep) * 0.7 +
    melatonin_suppression * 1.2 +
    arousal_scores * 0.8 +
    caffeine_effect * 0.6 +
    (100 - sleep_efficiency) * 0.03 +
    awakenings * 0.15 +
    (25 - rem_pct) * 0.04 +
    np.random.normal(0, 0.4, N)
)
next_day_fatigue_score = np.clip(fatigue, 1.0, 10.0).round(2)

# Sleep debt category
sleep_debt_hours = ideal_sleep - total_sleep
sleep_debt_category = np.where(
    sleep_debt_hours < 0.5, "No Debt",
    np.where(
        sleep_debt_hours < 1.5, "Mild",
        np.where(
            sleep_debt_hours < 3.0, "Moderate",
            "Severe"
        )
    )
)

# === Build DataFrame ===
df = pd.DataFrame({
    "user_id": user_ids,
    "age": ages,
    "gender": genders,
    "chronotype": chronotypes,
    "occupation": occupations,
    "bedtime_hour": bedtime_hour.round(2),
    "screen_time_before_bed_min": screen_time_min,
    "primary_app_category": primary_app,
    "screen_brightness_pct": screen_brightness,
    "blue_light_filter_on": blue_light_filter,
    "caffeine_intake_mg": caffeine_mg,
    "caffeine_last_hour": caffeine_last_hour,
    "physical_activity_min": physical_activity_min,
    "room_temperature_f": room_temp_f,
    "ambient_noise_db": ambient_noise_db,
    "sleep_onset_latency_min": sleep_onset_latency,
    "total_sleep_hours": total_sleep,
    "rem_sleep_pct": rem_pct,
    "deep_sleep_pct": deep_pct,
    "awakenings_count": awakenings,
    "sleep_efficiency_pct": sleep_efficiency,
    "next_day_fatigue_score": next_day_fatigue_score,
    "sleep_debt_category": sleep_debt_category,
})

# === Save ===
out_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(out_dir, "sleep_debt_screen_time.csv")
df.to_csv(csv_path, index=False)

print(f"[OK] Dataset generated: {csv_path}")
print(f"   Shape: {df.shape}")
print(f"\n--- Sleep Debt Category Distribution ---")
print(df["sleep_debt_category"].value_counts().to_string())
print(f"\n--- Fatigue Score Stats ---")
print(df["next_day_fatigue_score"].describe().to_string())
print(f"\n--- Sample rows ---")
print(df.head(10).to_string(index=False))
