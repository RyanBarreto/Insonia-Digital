# 🌙 Digital Insomnia: How Screen Habits Shape Your Sleep

> **8,500+ records linking bedtime app usage, blue light exposure, caffeine intake, and next-day fatigue.**

---

## 📋 Overview

Modern sleep architecture is severely disrupted by late-night digital consumption. Dopaminergic hyper-arousal from short-form video (TikTok, Reels) and melatonin suppression from unmitigated blue light exposure directly compound into chronic sleep debt and elevated next-day fatigue.

This dataset provides **cross-sectional lifestyle telemetry** for **8,500 individuals**, mapping their evening tech habits, caffeine intake, and demographic chronotypes against physiological sleep metrics and resulting fatigue scores.

---

## 📊 Dataset Schema

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | `user_id` | int | Unique participant identifier |
| 2 | `age` | int | Age (16–65) |
| 3 | `gender` | str | Male / Female / Non-Binary |
| 4 | `chronotype` | str | Early Bird / Night Owl / Intermediate |
| 5 | `occupation` | str | Student / Professional / Freelancer / Retired / Unemployed |
| 6 | `bedtime_hour` | float | Bedtime in 24h format (e.g. 23.5 = 11:30 PM, 1.25 = 1:15 AM) |
| 7 | `screen_time_before_bed_min` | int | Minutes of screen usage before sleep (5–240) |
| 8 | `primary_app_category` | str | Dominant app type used before bed |
| 9 | `screen_brightness_pct` | int | Screen brightness level (5–100%) |
| 10 | `blue_light_filter_on` | bool | Whether blue-light filter / night mode was active |
| 11 | `caffeine_intake_mg` | int | Total daily caffeine intake in mg |
| 12 | `caffeine_last_hour` | float | Hour of last caffeine intake (24h format) |
| 13 | `physical_activity_min` | int | Daily exercise minutes |
| 14 | `room_temperature_f` | float | Bedroom temperature (°F) |
| 15 | `ambient_noise_db` | float | Bedroom ambient noise level (dB) |
| 16 | `sleep_onset_latency_min` | float | Time to fall asleep (minutes) |
| 17 | `total_sleep_hours` | float | Total hours of sleep obtained |
| 18 | `rem_sleep_pct` | float | % of total sleep that was REM |
| 19 | `deep_sleep_pct` | float | % of total sleep that was deep / slow-wave |
| 20 | `awakenings_count` | int | Number of mid-sleep awakenings |
| 21 | `sleep_efficiency_pct` | float | Time asleep ÷ time in bed × 100 |
| 22 | `next_day_fatigue_score` | float | **Regression target** — fatigue score (1–10) |
| 23 | `sleep_debt_category` | str | **Classification target** — None / Mild / Moderate / Severe |

---

## 🧬 Data Engineering & Biophysical Logic

This dataset is generated via a simulation grounded in established biophysical models:

- **Melatonin Suppression:** Scales with screen brightness × exposure duration, mitigated non-linearly by blue-light filter activation (~45% reduction).
- **Cognitive Arousal Weights:** Each app genre carries a distinct arousal coefficient (e.g., short-form algorithmic video = 0.95 vs. e-reading = 0.20).
- **Caffeine Pharmacokinetics:** Residual caffeine at bedtime follows a 5-hour half-life model.
- **Sleep Architecture:** REM and deep sleep percentages are suppressed by arousal, caffeine, and melatonin disruption signals.
- **Demographic Chronotypes:** Night owls naturally skew to later bedtimes, reducing total available sleep through wake-time pressure.

### App Category Arousal Weights

| App Category | Arousal Weight |
|---|---|
| Short-Form Video | 0.95 |
| Gaming | 0.85 |
| Social Media | 0.80 |
| Messaging | 0.65 |
| Streaming | 0.60 |
| News | 0.55 |
| E-Reading | 0.20 |

---

## 🎯 Target Variables

| Target | Type | Use Case |
|--------|------|----------|
| `next_day_fatigue_score` | Continuous (1–10) | Regression |
| `sleep_debt_category` | Categorical (4 classes) | Classification |

### Sleep Debt Category Distribution

| Category | Count | % |
|----------|-------|---|
| Mild | ~4,400 | ~52% |
| Moderate | ~2,360 | ~28% |
| No Debt | ~1,720 | ~20% |
| Severe | ~25 | <1% |

---

## 🔬 Starter Research Questions

1. **The Doomscroll Penalty:** Can you quantify the exact reduction in REM sleep per 30 minutes of bedtime scrolling on short-form video?
2. **Blue-Light Filter Efficacy:** Does activating a blue-light filter mathematically offset the fatigue penalty of 100% screen brightness?
3. **Caffeine Half-Life Window:** At what hour must caffeine consumption stop to avoid measurable impact on sleep onset latency?
4. **Chronotype × Screen Time Interaction:** Do Night Owls suffer disproportionately from late-night screen exposure compared to Early Birds?
5. **Predictive Modeling:** Train an XGBoost or Random Forest regressor to predict `next_day_fatigue_score` using only behavioral features (caffeine, app choice, screen time) — excluding physiological outputs.

---

## 📁 Files

| File | Description |
|------|-------------|
| `sleep_debt_screen_time.csv` | Main dataset (8,500 rows × 23 columns) |
| `generate_dataset.py` | Reproducible generation script |
| `README.md` | This file |

---

## 📜 License

CC BY-SA 4.0 — Creative Commons Attribution-ShareAlike 4.0 International

---

## 🏷️ Tags

`classification` · `regression` · `health` · `sleep` · `screen-time` · `blue-light` · `fatigue` · `lifestyle` · `public-health`
