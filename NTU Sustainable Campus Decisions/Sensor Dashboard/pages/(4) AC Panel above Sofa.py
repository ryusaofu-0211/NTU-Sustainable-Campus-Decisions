import streamlit as st
import plotly.express as px
from utils.database import get_board


st.title("(4) AC Panel above Sofa")

df = get_board("WioLink_5")

latest = df.iloc[-1]
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🌡 event_source",
    f"{latest['event_source']} °C"
)

col2.metric(
    "💧 touchdown",
    f"{latest['touchdown']} %"
)

col3.metric(
    "☀ touchup",
    latest["touchup"]
)


fig = px.line(
    df,
    x="created_at",
    y="touchdown",
    title="touchdown"
)

st.plotly_chart(fig, use_container_width=True)

fig = px.line(
    df,
    x="created_at",
    y="touchup",
    title="touchup"
)

st.plotly_chart(fig, use_container_width=True)

