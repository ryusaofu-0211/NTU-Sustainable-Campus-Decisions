import streamlit as st
import plotly.express as px
from utils.database import get_board


st.title("Right of Kitchen")

df = get_board("WioLink_3")

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
    "☁️ tvoc",
    f"{latest["tvoc"]} ppb"
)

col3.metric(
    "😮‍💨 eco2",
    f"{latest["eco2"]} ppm"
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
    y="tvoc",
    title="tvoc"
)

st.plotly_chart(fig, use_container_width=True)

fig = px.line(
    df,
    x="created_at",
    y="eco2",
    title="eco2"
)

st.plotly_chart(fig, use_container_width=True)

fig = px.line(
    df,
    x="created_at",
    y="motion",
    title="motion"
)

st.plotly_chart(fig, use_container_width=True)