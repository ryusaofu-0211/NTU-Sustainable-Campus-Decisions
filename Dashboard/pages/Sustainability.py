import streamlit as st
import pandas as pd

from utils.database import get_board
from utils.weather import get_outdoor_conditions, get_outdoor_pm25
st.set_page_config(page_title="Sustainability", page_icon="🌍", layout="wide")

st.title("🌍 Sustainability Overview")
st.write("This page flags scenarios where the room's energy use, ventilation, or air handling may be wasteful or suboptimal.")

# ---- Load data ----
boards = {
    "Board 1": get_board("WioLink"),     # temp, humidity, light_intensity, motion
    "Board 2": get_board("WioLink_3"),   # temp, humidity, tvoc, eco2, motion
    "Board 3": get_board("WioLink_4"),   # temp, humidity, pm2_5, window_state
    "Board 4": get_board("WioLink_5"),   # touchup, touchdown (AC panel)
}

latest = {
    name: df.iloc[-1]
    for name, df in boards.items()
    if not df.empty
}

if len(latest) < 4:
    st.error("Not enough recent sensor data to evaluate sustainability scenarios.")
    st.stop()

b1, b2, b3, b4 = latest["Board 1"], latest["Board 2"], latest["Board 3"], latest["Board 4"]

indoor_temp = (b1["celsius_degree"] + b2["celsius_degree"] + b3["celsius_degree"]) / 3
indoor_humidity = (b1["humidity"] + b2["humidity"] + b3["humidity"]) / 3
motion_detected = (b1["motion"] == 1) or (b2["motion"] == 1)
window_open = b3["window_state"] == 1  # confirm: does 1 mean open?
light_on = b1["light_intensity"] > 100  # placeholder threshold — tune to your actual lux values

# ---- AC "active" proxy ----
# Since WioLink_5 only reports touch events (not true on/off), we treat the AC
# as "recently active" if there was a touch in the last N hours.
ac_df = boards["Board 4"].copy()
ac_df["created_at"] = pd.to_datetime(ac_df["created_at"])
recent_cutoff = pd.Timestamp.now(tz=ac_df["created_at"].dt.tz) - pd.Timedelta(hours=3)
recent_touches = ac_df[ac_df["created_at"] >= recent_cutoff]
ac_recently_active = len(recent_touches) > 0

# ---- AC setpoint inference ----
# Rough heuristic: start from an assumed baseline setpoint, then apply the
# net effect of touchup/touchdown events over time. This is an approximation,
# not a real reading — flag it as such in the UI.
BASELINE_SETPOINT = 25  # assumed starting point, °C — adjust to your unit's default
ac_df_sorted = ac_df.sort_values("created_at")
net_touches = ac_df_sorted["touchup"].sum() - ac_df_sorted["touchdown"].sum()
estimated_setpoint = BASELINE_SETPOINT + net_touches
estimated_setpoint = max(16, min(30, estimated_setpoint))  # clamp to realistic AC range

# ---- Outdoor data ----
outdoor = get_outdoor_conditions()

# =========================================================
# Overview metrics
# =========================================================
st.subheader("Current Conditions")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Indoor Temp", f"{indoor_temp:.1f} °C")
col2.metric("Indoor Humidity", f"{indoor_humidity:.1f} %")
col3.metric("Occupancy", "🟢 Present" if motion_detected else "⚪ Empty")
col4.metric("Est. AC Setpoint", f"{estimated_setpoint:.0f} °C" if ac_recently_active else "AC likely off")

if outdoor:
    st.caption(f"Outdoor reference: {outdoor['station_name']} · {outdoor['temperature']:.1f} °C, {outdoor['humidity']:.0f}% humidity (as of {outdoor['obs_time']})")
else:
    st.caption("⚠️ Outdoor weather data unavailable — some scenarios below are skipped.")

st.divider()

# =========================================================
# Scenario checks
# =========================================================
st.subheader("Scenario Flags")

flags = []  # collect (severity, message) tuples

# 1. AC on + window open (wasted conditioning)
if ac_recently_active and window_open:
    flags.append(("error", "❄️🪟 AC appears active while the window is open — conditioned air is escaping."))

# 2. AC on + no one in the room
if ac_recently_active and not motion_detected:
    flags.append(("error", "❄️👻 AC appears active but no motion has been detected recently — likely cooling an empty room."))

# 3. Light on + no motion
if light_on and not motion_detected:
    flags.append(("warning", "💡👻 Lights appear on but no motion has been detected recently."))

# 4. AC on while indoor ≈ outdoor conditions (natural ventilation could work instead)
if outdoor and ac_recently_active:
    temp_diff = abs(indoor_temp - outdoor["temperature"])
    humidity_diff = abs(indoor_humidity - outdoor["humidity"])
    if temp_diff < 2 and humidity_diff < 10:
        flags.append(("warning", f"🌤️ Outdoor conditions ({outdoor['temperature']:.1f}°C) are very close to indoor — natural ventilation might work instead of AC."))

# 5. Frequent AC touches — possible thermostat "fighting" / discomfort
if len(recent_touches) >= 6:
    flags.append(("warning", f"🔁 {len(recent_touches)} AC panel touches in the last 3 hours — may indicate occupants are uncomfortable with the current setting."))

# 6 & 7. Poor indoor air + window response check
poor_air = (b2["eco2"] > 1000) or (b2["tvoc"] > 560) or (b3["pm2_5"] > 35)
if poor_air and not window_open:
    if outdoor:
        # We don't have outdoor PM2.5 in this version — flag conservatively
        flags.append(("warning", "🫁🪟 Indoor air quality is poor and the window is closed. Consider opening it if outdoor air quality is acceptable."))
    else:
        flags.append(("warning", "🫁 Indoor air quality is poor and the window is closed — outdoor comparison unavailable."))

# 8. AC on AND window open specifically for "fresh air" reasoning
# (distinct from #1: here we call out that AC does not ventilate — opening
# the window while the AC runs wastes energy without meaningfully improving air exchange)
if ac_recently_active and window_open:
    flags.append(("warning", "💡 Note: running the AC does not ventilate the room. If fresh air is the goal, opening the window alone (AC off) is more efficient."))

# 9. Late-night / early-morning activity with no motion
current_hour = pd.Timestamp.now().hour
is_off_hours = current_hour >= 23 or current_hour < 6
if is_off_hours and (ac_recently_active or light_on) and not motion_detected:
    flags.append(("error", "🌙 AC or lights appear active during off-hours (11PM–6AM) with no one present — likely forgotten."))

# 10. AC setpoint appropriateness
if ac_recently_active:
    if estimated_setpoint <= 20:
        flags.append(("warning", f"🥶 Estimated AC setpoint (~{estimated_setpoint:.0f}°C) is quite low — likely overcooling relative to comfort needs."))
    elif estimated_setpoint >= 28:
        flags.append(("warning", f"🥵 Estimated AC setpoint (~{estimated_setpoint:.0f}°C) is quite high for effective cooling — may indicate a unit struggling to keep up."))
# 11. Lights on despite adequate daylight
current_hour = pd.Timestamp.now().hour
is_daytime = 7 <= current_hour < 18  # rough daylight window for Taipei — adjust seasonally if needed
CLEAR_KEYWORDS = ["晴", "少雲"]  # "clear" / "mostly clear" substrings in CWA's Weather field

if outdoor and light_on and is_daytime:
    is_clear_weather = any(kw in outdoor["weather_desc"] for kw in CLEAR_KEYWORDS)
    if is_clear_weather:
        flags.append(("warning", f"☀️💡 Lights are on during daylight hours with clear skies outside ({outdoor['weather_desc']}) — natural light may be sufficient."))

outdoor_pm25 = get_outdoor_pm25()

# 10. Window open while outdoor air is worse than indoor
indoor_pm25 = b3["pm2_5"]

if outdoor_pm25 and window_open:
    if outdoor_pm25["pm2_5"] > indoor_pm25:
        flags.append(("error", f"🌫️🪟 Window is open, but outdoor PM2.5 ({outdoor_pm25['pm2_5']:.1f} µg/m³) is higher than indoor ({indoor_pm25:.1f} µg/m³) — actively letting in pollution."))
elif outdoor_pm25 and not window_open and indoor_pm25 > 35:
    if outdoor_pm25["pm2_5"] < indoor_pm25:
        flags.append(("warning", f"🫁🪟 Indoor PM2.5 ({indoor_pm25:.1f} µg/m³) is high, and outdoor air is cleaner ({outdoor_pm25['pm2_5']:.1f} µg/m³) — opening the window could help."))

# ---- Render flags ----
if not flags:
    st.success("🟢 No sustainability concerns detected right now.")
else:
    for severity, message in flags:
        if severity == "error":
            st.error(message)
        else:
            st.warning(message)

st.divider()
st.caption("Note: AC on/off state and setpoint are estimated from touch-panel activity, not a direct power reading — treat these as approximations.")

st.divider()
st.subheader("📋 All Scenarios This Page Monitors")
st.markdown("""
1. **AC on + window open** — conditioned air escaping through an open window
2. **AC on + no motion detected** — cooling an empty room
3. **Lights on + no motion detected** — lights left on in an empty room
4. **AC on while indoor ≈ outdoor conditions** — natural ventilation could replace AC
5. **Frequent AC touches in a short window** — possible thermostat "fighting" or discomfort
6. **Poor indoor air quality + window closed** — window could improve air if outdoor air is cleaner
7. **AC on + window open for "fresh air"** — AC doesn't ventilate; opening window with AC off is more efficient for air exchange
8. **Off-hours activity with no motion** — AC/lights active late night–early morning while room is empty
9. **AC setpoint estimated too low/high** — based on touch panel history, may indicate over/undercooling
10. **Window open while outdoor air is worse** *(planned — needs outdoor PM2.5 data)*
11. **Lights on despite daylight + clear skies** — natural light may be sufficient, based on nearby weather station data

*Outdoor comparisons use live data from the CWA weather station nearest NTU. AC on/off state and setpoint are estimated from touch-panel activity, not a direct power reading.*
""")
