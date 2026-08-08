import streamlit as st
import plotly.express as px
from utils.database import get_board

st.title("Air Purity")
st.subheader("Is the room air healthy and safe for us to breath?")
st.write("The standards follows Taiwan Indoor Air Quality Management Act (IAQ) 室內空氣品質管理法")
st.markdown("""
## Alert scale

Air Purity is evaluated into the following 4 categories:

- 🔴Danger
- 🟠Warning - Above Standard
- 🟡Caution
- 🟢Safe
""")
st.subheader("Overall Current Air Status")

boards = {
    "Board 2": get_board("WioLink_3"),
    "Board 3": get_board("WioLink_4"),
}
latest = {
    name: df.iloc[-1]
    for name, df in boards.items()
    if not df.empty
}
co2 = latest["Board 2"]["eco2"]

if co2 < 800:
    co2_status = "🟢 Safe"
elif co2 <= 1000:
    co2_status = "🟡 Caution"
elif co2 <= 1500:
    co2_status = "🟠 Warning - Above Standard"
else:
    co2_status = "🔴 Danger"

tvoc = latest["Board 2"]["tvoc"]

if tvoc < 300:
    tvoc_status = "🟢 Safe"
elif tvoc <= 560:
    tvoc_status = "🟡 Caution"
elif tvoc <= 1000:
    tvoc_status = "🟠 Warning - Above Standard"
else:
    tvoc_status = "🔴 Danger"


pm25 = latest["Board 3"]["pm2_5"]

if pm25 < 15:
    pm25_status = "🟢 Safe"
elif pm25 <= 35:
    pm25_status = "🟡 Caution"
elif pm25 <= 55:
    pm25_status = "🟠 Warning - Above Standard"
else:
    pm25_status = "🔴 Danger"

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("eCO2", f'{latest["Board 2"]["eco2"]} ppm')
    st.markdown(co2_status)

with col2:
    st.metric("TVOC", f'{latest["Board 2"]["tvoc"]} ppb')
    st.markdown(tvoc_status)

with col3:
    st.metric("PM2.5", f'{latest["Board 3"]["pm2_5"]} μg/m³')
    st.markdown(pm25_status)


fig = px.line(
    boards["Board 2"],
    x="created_at",
    y="eco2",
    title="eCO2 Trend",
    labels={
        "created_at": "Time",
        "eco2": "eCO2 (ppm)"
    }
)
fig.add_hline(
    y=1000,
    line_color="red",
    line_dash="dash",
    annotation_text="Taiwan Standard Safe Limit: 1000 ppm"
)
st.plotly_chart(fig, use_container_width=True)

fig = px.line(
    boards["Board 2"],
    x="created_at",
    y="tvoc",
    title="TVOC Trend",
    labels={
        "created_at": "Time",
        "tvoc": "TVOC (ppb)"
    }
)
fig.add_hline(
    y=560,
    line_color="red",
    line_dash="dash",
    annotation_text="Taiwan Standard Safe Limit: 560 ppb"
)
st.plotly_chart(fig, use_container_width=True)

fig = px.line(
    boards["Board 3"],
    x="created_at",
    y="pm2_5",
    title="PM2.5 Trend",
    labels={
        "created_at": "Time",
        "pm2_5": "PM2.5 (μg/m³)"
    }
)
fig.add_hline(
    y=35,
    line_color="red",
    line_dash="dash",
    annotation_text="Taiwan Standard Safe Limit: 35 μg/m³"
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Taiwan Indoor Air Quality Standards")

standards_data = {
    "Parameter": ["CO₂", "PM2.5", "PM10", "TVOC", "CO", "HCHO", "O₃"],
    "Standard": [
        "1000 ppm",
        "35 μg/m³",
        "75 μg/m³",
        "560 ppb",
        "9 ppm",
        "0.08 ppm",
        "0.06 ppm"
    ],
    "Averaging Time": [
        "8 hours",
        "24 hours",
        "24 hours",
        "1 hour",
        "8 hours",
        "1 hour",
        "8 hours"
    ]
}

st.table(standards_data)

st.subheader("Core Principles")
st.write("What is TVOC?")
st.info("Total Volatile Organic Compound (TVOC) represents the combined level of detected volatile organic compounds. VOCs can come from things such as cleaning products, paints, solvents, fragrances, and other materials.")
st.write("What is eCO2?")
st.info("Equivalent CO2 Concentration (eCO2) estimates the CO2 level that would correspond to the sensor's detected VOC conditions. This is usually affected by occupants breathing, ventilation of the room, etc.")
st.write("What is PM2.5?")
st.info("Particulate matter with a diameter of 2.5μm or smaller (PM2.5) are tiny airborne molecules. Sources can include dust, smoke, combustion, outdoor pollution entering the building, etc.")













