import streamlit as st
import pandas as pd
import plotly.express as px

from utils.database import get_board
from pythermalcomfort.models import pmv_ppd_ashrae

st.title("Thermal Comfort")
st.subheader("How comfortable do people feel in the room?")
st.write("The standards follows ASHRAE Standard 55 created by American Society of Heating, Refridgerating and Air-Conditioning Engineers (ASHRAE). This is also approved by American National Standards Institute (ANSI).")
st.markdown("""
## Alert scale

Thermal Sensation is evaluated into the following 5 categories:

- ⚫Frigid
- 🟣Cold
- 🔵Cool
- 🟢Neutral
- 🟠Warm
- 🔴Hot
- ⚪Torrid

Thermal Comfort is evaluated into the following 3 categories 

- 🟢 Comfortable 
- 🟡 Slightly Outside Comfort Range 
- 🔴 Uncomfortable 
""")

boards = { #get data from specific tables in supabase
    "Board 1": get_board("WioLink"),
    "Board 2": get_board("WioLink_3"),
    "Board 3": get_board("WioLink_4"),
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

col1, col2 = st.columns(2)

with col1:
    st.metric("Average Temperature", f"{average_temperature:.1f} °C")


with col2:
    st.metric("Humidity",f"{average_humidity:.1f} %")


tdb = average_temperature
tr = average_temperature

met = 1.1 #Person sitting and typing 
clo = 0.5 #Light indoor clothing
v = 0.1 #Relatively still indoor air

result = pmv_ppd_ashrae(
    tdb=tdb, #Air temperature
    tr=tr, #Mean Radiant temperature (Temperature of walls, etc)
    vr=v, #Relative air velocity
    rh=average_humidity,
    met=met, #How much heat is produced from a person doing a certain acitivity 
    clo=clo, #Clothing insulation
    model="55-2023"
)

pmv = result.pmv
ppd = result.ppd

col1, col2 = st.columns(2)

col1.metric(
    "PMV",
    f"{pmv:.2f}"
)

col2.metric(
    "PPD",
    f"{ppd:.1f}%"
)


if pmv <= -2.5:
    sensation = "⚫Frigid"
elif pmv <= -1.5:
    sensation = "🟣Cold"
elif pmv <= -0.5:
    sensation = "🔵Cool"
elif pmv < 0.5:
    sensation = "🟢Neutral"
elif pmv < 1.5:
    sensation = "🟠Warm"
elif pmv < 2.5:
    sensation = "🔴Hot"
else:
    sensation = "⚪Torrid"

st.subheader("Thermal Sensation")
st.write(f"## {sensation}")

if -0.5 <= pmv <= 0.5 and ppd <= 20:
    comfort_status = "🟢 Comfortable"
elif ppd <= 20:
    comfort_status = "🟡 Slightly Outside Comfort Range"
else:
    comfort_status = "🔴 Uncomfortable"

st.subheader("Thermal Comfort Status")
st.write(f"## {comfort_status}")

def calculate_pmv(row):
    result = pmv_ppd_ashrae(
        tdb=row["average_temperature"],
        tr=row["average_temperature"],
        vr=0.1,
        rh=row["average_humidity"],
        met=1.1,
        clo=0.5,
        model="55-2023"
    )

    return float(result.pmv)


# Create a DataFrame for the PMV trend
pmv_df = boards["Board 1"][["created_at"]].copy()

pmv_df["average_temperature"] = (
    boards["Board 1"]["celsius_degree"]
    + boards["Board 2"]["celsius_degree"]
    + boards["Board 3"]["celsius_degree"]
) / 3

pmv_df["average_humidity"] = (
    boards["Board 1"]["humidity"]
    + boards["Board 2"]["humidity"]
    + boards["Board 3"]["humidity"]
) / 3

# Calculate PMV for every timestamp
pmv_df["pmv"] = pmv_df.apply(calculate_pmv, axis=1)

# Create graph
fig = px.line(
    pmv_df,
    x="created_at",
    y="pmv",
    title="PMV Trend",
    labels={
        "created_at": "Time",
        "pmv": "PMV"
    }
)

fig.add_hline(
    y=0.5,
    line_color="red",
    line_dash="dash",
    annotation_text="Upper comfort limit (+0.5)"
)

fig.add_hline(
    y=-0.5,
    line_color="red",
    line_dash="dash",
    annotation_text="Lower comfort limit (-0.5)"
)
st.plotly_chart(fig, use_container_width=True)

fig = px.line(
    pmv_df,
    x="created_at",
    y="average_temperature",
    title="Temperature Trend",
    labels={
        "created_at": "Time",
        "average_temperature": "Average Temperature (°C)"
    }
)

st.plotly_chart(fig, use_container_width=True)

fig = px.line(
    pmv_df,
    x="created_at",
    y="average_humidity",
    title="Humidity Trend",
    labels={
        "created_at": "Time",
        "average_humidity": "Average Relative Humidity (%)"
    }
)

st.plotly_chart(fig, use_container_width=True)


st.subheader("Core Principles")
st.write("What is PMV?")
st.info("Prediced Mean Vote (PMV) is the predicted average thermal sensation vote of a group of people.")
st.write("Pressumed parameters for PMV/PPD")
st.info("""
**PMV/PPD Assumptions:**

- **Mean Radiant Temperature:** Assumed equal to air temperature.
- **Air Velocity:** Assumed to be 0.1 m/s, representing relatively still indoor air.
- **Metabolic Rate:** Assumed to be 1.1 met, representing a person sitting and typing.
- **Clothing:** Assumed to be 0.5 clo, representing light indoor clothing.
""")
st.write("What is the difference between mean radiant temperature and air temperature?")
st.info("Mean Radiant Temperature is the temeperature of the walls, the ceiling, and other physical surfaces, while air temperature is the temperature of the ambient air surrounding a person.")
st.write("What is PPD?")
st.info("Predicted Percentage Dissatified (PPD) is the predicted percetange of people who would be dissatified with the current thermal conditions.")
