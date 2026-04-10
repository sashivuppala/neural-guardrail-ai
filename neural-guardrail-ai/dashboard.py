"""Streamlit dashboard for monitoring API decisions."""

from __future__ import annotations

import json
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


def load_evaluation() -> dict:
    if not settings.evaluation_path.exists():
        return {}
    try:
        return json.loads(settings.evaluation_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


st.set_page_config(page_title="NeuralGuardrail-AI Dashboard", layout="wide")
st.title("NeuralGuardrail-AI Dashboard")

logs_df = load_logs()
evaluation = load_evaluation()

if evaluation:
    st.subheader("Model Evaluation")
    eval_col1, eval_col2, eval_col3, eval_col4 = st.columns(4)
    eval_col1.metric("Test AUC", evaluation.get("test_auc", 0))
    eval_col2.metric("Precision", evaluation.get("precision", 0))
    eval_col3.metric("Recall", evaluation.get("recall", 0))
    eval_col4.metric("F1 Score", evaluation.get("f1_score", 0))

if logs_df.empty:
    st.info("No request logs found yet. Start the API and send traffic to populate the dashboard.")
else:
    logs_df["created_at"] = pd.to_datetime(logs_df["created_at"])
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Requests", int(len(logs_df)))
    col2.metric("Blocked", int((logs_df["decision"] == "BLOCK").sum()))
    col3.metric("Throttled", int((logs_df["decision"] == "THROTTLE").sum()))

    score_col1, score_col2 = st.columns(2)
    score_col1.metric("Average Score", round(float(logs_df["anomaly_score"].mean()), 4))
    score_col2.metric("Max Score", round(float(logs_df["anomaly_score"].max()), 4))

    st.subheader("Decision Distribution")
    st.bar_chart(logs_df["decision"].value_counts())

    st.subheader("Top Guardrail Reasons")
    st.bar_chart(logs_df["reason"].value_counts().head(5))

    st.subheader("Anomaly Score Trend")
    trend_df = logs_df[["created_at", "anomaly_score"]].set_index("created_at")
    st.line_chart(trend_df)

    st.subheader("Recent Decisions")
    st.dataframe(logs_df.sort_values("created_at", ascending=False).head(25), use_container_width=True)
