#converting all the datas so that it matches taiwan timezone (UTC+8)
#Used for real-time graphs

from supabase import create_client
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone


url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)


def get_board(table_name):
    # Current UTC time
    now = datetime.now(timezone.utc)

    # 48 hours ago
    start_time = now - timedelta(hours=48)


    response = (
        supabase
        .table(table_name)
        .select("*")
        .gte("created_at", start_time.isoformat())
        .order("created_at", desc=False)
        .execute()
    )

    # Convert response to DataFrame
    df = pd.DataFrame(response.data)

    # Convert UTC to Taiwan time (UTC+8)
    if not df.empty:
        df["created_at"] = (
            pd.to_datetime(df["created_at"], utc=True)
            .dt.tz_convert("Asia/Taipei")   # Convert to UTC+8
            .dt.tz_localize(None)           # Remove the +08:00 suffix
        )

    return df