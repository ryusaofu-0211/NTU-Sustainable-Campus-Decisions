import streamlit as st
import plotly.express as px
from utils.database import get_board


st.title("Window next to Kitchen")

df = get_board("WioLink_4")

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
    "💨 PM2.5",
    latest["pm2_5"]
)

col4.metric(
    "🚶 window_state",
    latest["window_state"]
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
    y="pm2_5",
    title="pm2_5"
)

st.plotly_chart(fig, use_container_width=True)

fig = px.line(
    df,
    x="created_at",
    y="window_state",
    title="window_state"
)

st.plotly_chart(fig, use_container_width=True)