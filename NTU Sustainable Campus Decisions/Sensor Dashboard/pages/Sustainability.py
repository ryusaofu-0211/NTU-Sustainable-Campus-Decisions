import streamlit as st
import plotly.express as px
from utils.database import get_board

st.title("Sustainability")
st.subheader("Are electricity and energy wasted in the room?")
st.write("This is determined based on my own opinions :)")
st.markdown("""
## Alert scale

Sustainability is evaluated into the following 4 categories:

- 🔴Danger
- 🟠Warning
- 🟡Caution
- 🟢Safe
""")

boards = {
    "Board 1": get_board("WioLink"),
    "Board 2": get_board("WioLink_2"),
    "Board 3": get_board("WioLink_3"),
    "Board 4": get_board("WioLink_4"),
}

latest = {
    name: df.iloc[-1]
    for name, df in boards.items()
    if not df.empty
}

st.subheader("👥 Occupancy")

occupied_boards = 0

for name, row in latest.items():

    motion = row["motion"]
    touchup = row["touchup"]
    touchdown =row["touchdown"]
if motion == 1 or touchup == 1 or touchdown == 1:
    if motion or touchup or touchdown:
        occupied_boards += 1
st.metric(
    "Active Areas",
    f"{occupied_boards} / {len(latest)}"
)

if occupied_boards == 0:
    st.warning("⚠️ No monitored areas currently show signs of occupancy.")
elif occupied_boards < len(latest):
    st.info("🟡 Some monitored areas show signs of occupancy.")
else:
    st.success("🟢 All monitored areas currently show signs of occupancy.")