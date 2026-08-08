import streamlit as st
import plotly.express as px
from utils.database import get_board


st.title("(1) Above Long Sofa")

df = get_board("WioLink")

latest = df.iloc[-1]
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🌡 Temperature",
    f"{latest['celsius_degree']} °C"
)

col2.metric(
    "💧 Humidity",
    f"{latest['humidity']} %"
)

col3.metric(
    "☀ Light",
    latest["light_intensity"]
)

col4.metric(
    "🚶 Motion",
    latest["motion"]
)
fig = px.line(
    df,
    x="created_at",
    y="celsius_degree",
    title="Temperature"
)

st.plotly_chart(fig, use_container_width=True)

fig = px.line(
    df,
    x="created_at",
    y="humidity",
    title="humidity"
)

st.plotly_chart(fig, use_container_width=True)

fig = px.line(
    df,
    x="created_at",
    y="light_intensity",
    title="light_intensity"
)

st.plotly_chart(fig, use_container_width=True)

fig = px.line(
    df,
    x="created_at",
    y="motion",
    title="motion"
)

st.plotly_chart(fig, use_container_width=True)