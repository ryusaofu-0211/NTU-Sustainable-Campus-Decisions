import streamlit as st 
import os
from utils.database import get_board
from pythermalcomfort.models import pmv_ppd_ashrae

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


boards = { #get data from specific tables in supabase
    "Board 1": get_board("WioLink"),
    "Board 2": get_board("WioLink_3"),
    "Board 3": get_board("WioLink_4"),
    "Board 4": get_board("WioLink_5"),
}
latest = {
    name: df.iloc[-1]
    for name, df in boards.items()
    if not df.empty
}

average_temperature = (
    latest["Board 1"]["celsius_degree"] +
    latest["Board 2"]["celsius_degree"] + 
    latest["Board 3"]["celsius_degree"]
) / 3

average_humidity = (
    latest["Board 1"]["humidity"] +
    latest["Board 2"]["humidity"] + 
    latest["Board 3"]["humidity"]
) / 3

motion = (
    latest["Board 1"]["motion"] == 1
    or
    latest["Board 2"]["motion"] == 1
)
if motion:
    motion_text = "🟢 Motion Detected"
else:
    motion_text = "⚪ No Motion"

st.set_page_config(
    page_title="Indoor Environmental Dashboard",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 Indoor Environmental Dashboard: NTU CERB 6th floor CLab")
st.write("Created by: Sao-Fu Liu (liusaofu@gmail.com)")
st.write("Contributiors: Dr. Yuntsui (Tracey) Chang, Dr. Tzong-Hann (Richard) Wu, Dr. Shang-Hsien (Patrick) Hsieh")
st.subheader("Real-Time Data on Current Room Conditions")
st.write(
    """
This dashboard monitors four WioLink sensor nodes located throughout the
room. Data are uploaded to Supabase and refreshed automatically every 10 minutes. All the data are recorded UTC+8. To prevent overflow of data, the graphs only show the lastest 48 hours.
"""
)
st.markdown("""
## Sustainability Summary

This dashboard evaluates:

- Indoor Air Quality
- Thermal Comfort
- Occupancy
- Energy Waste

Choose the pages on the sideboard for more specific data. 
""")
st.subheader("Overview")
col1, col2, col3= st.columns(3)

col1.metric(
    "Average Temperature",
    f"{average_temperature:.1f} °C"
)

col2.metric(
    "Average Humidity",
    f"{average_humidity:.1f} %"
)

col3.metric(
    "Occupancy",
    motion_text
)

st.image(
    os.path.join(BASE_DIR, "assets", "CLab_drawing.png"),
    caption="Room Layout",
    width='stretch'
)
st.write("Choose a board from the sidebar for more specific data")

st.subheader("Alerts")
st.write("Air Purity")
air_any_exceeded = (
    latest["Board 2"]["eco2"] > 1000
    or latest["Board 3"]["pm2_5"] > 35
    or latest["Board 2"]["tvoc"] > 560
)
if air_any_exceeded:
    st.error("⚠️ One or more IAQ parameters exceed the Taiwan standard. Check the 'Air Purity page' for more information")
else:
    st.success("🟢 All monitored IAQ parameters are within the Taiwan standards.")

st.write("Thermal Comfort")

result = pmv_ppd_ashrae(
    tdb=average_temperature,
    tr=average_temperature,
    vr=0.1,
    rh=average_humidity,
    met=1.1,
    clo=0.5,
    model="55-2023"
)

pmv = float(result.pmv)
ppd = float(result.ppd)

thermal_any_exceeded = (
    pmv < -0.5
    or pmv > 0.5
    or ppd > 20
)

if thermal_any_exceeded:
    st.error(
        "⚠️ The current average classroom conditions are outside the thermal comfort range. "
        "Check the 'Thermal Comfort' page for more information."
    )
else:
    st.success(
        "🟢 The current average classroom conditions are within the thermal comfort range."
    )


