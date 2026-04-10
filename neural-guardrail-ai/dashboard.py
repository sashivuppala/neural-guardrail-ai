"""Streamlit dashboard for monitoring API decisions."""

from __future__ import annotations

import sqlite3

import pandas as pd
import streamlit as st

from utils.config import settings


def load_logs() -> pd.DataFrame:
    try:
        with sqlite3.connect(settings.database_url.replace("sqlite:///", "")) as connection:
            return pd.read_sql_query("SELECT * FROM request_logs ORDER BY created_at ASC", connection)
    except Exception:
        return pd.DataFrame()


st.set_page_config(page_title="NeuralGuardrail-AI Dashboard", layout="wide")
st.title("NeuralGuardrail-AI Dashboard")

logs_df = load_logs()

if logs_df.empty:
    st.info("No request logs found yet. Start the API and send traffic to populate the dashboard.")
else:
    logs_df["created_at"] = pd.to_datetime(logs_df["created_at"])
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Requests", int(len(logs_df)))
    col2.metric("Blocked", int((logs_df["decision"] == "BLOCK").sum()))
    col3.metric("Throttled", int((logs_df["decision"] == "THROTTLE").sum()))

    st.subheader("Decision Distribution")
    st.bar_chart(logs_df["decision"].value_counts())

    st.subheader("Anomaly Score Trend")
    trend_df = logs_df[["created_at", "anomaly_score"]].set_index("created_at")
    st.line_chart(trend_df)

    st.subheader("Recent Decisions")
    st.dataframe(logs_df.sort_values("created_at", ascending=False).head(25), use_container_width=True)
