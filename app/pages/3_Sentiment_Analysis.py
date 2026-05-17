from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"


st.set_page_config(
    page_title="Sentiment Analysis",
    page_icon="💬",
    layout="wide",
)


def load_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


st.title("💬 新闻情感分析")

df = load_csv(PROCESSED_DIR / "sentiment_news.csv")
summary_df = load_csv(RESULTS_DIR / "sentiment_summary.csv")

if df.empty:
    st.warning("未找到 data/processed/sentiment_news.csv")
    st.stop()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("新闻数量", len(df))

with col2:
    if "sentiment_score" in df.columns:
        st.metric("平均情感分数", f"{df['sentiment_score'].mean():.3f}")
    else:
        st.metric("平均情感分数", "暂无")

with col3:
    if "sentiment_label" in df.columns:
        positive_count = (df["sentiment_label"] == "positive").sum()
        st.metric("积极新闻数", positive_count)
    else:
        st.metric("积极新闻数", "暂无")

with col4:
    if "sentiment_label" in df.columns:
        negative_count = (df["sentiment_label"] == "negative").sum()
        st.metric("消极新闻数", negative_count)
    else:
        st.metric("消极新闻数", "暂无")

st.divider()

if not summary_df.empty:
    col_left, col_right = st.columns([2, 1])

    with col_left:
        fig = px.bar(
            summary_df,
            x="sentiment_label",
            y="count",
            title="情感极性数量分布",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        fig = px.pie(
            summary_df,
            names="sentiment_label",
            values="count",
            title="情感极性占比",
        )
        st.plotly_chart(fig, use_container_width=True)

if "sentiment_score" in df.columns:
    fig = px.histogram(
        df,
        x="sentiment_score",
        nbins=20,
        title="情感分数分布",
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("情感分析明细")

display_columns = [
    column
    for column in [
        "analysis_date",
        "title",
        "topic",
        "sentiment_label",
        "sentiment_score",
        "positive_hits",
        "negative_hits",
        "bullish_hits",
        "bearish_hits",
    ]
    if column in df.columns
]

st.dataframe(df[display_columns], use_container_width=True)