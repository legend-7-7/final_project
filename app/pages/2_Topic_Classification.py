from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


st.set_page_config(
    page_title="Topic Classification",
    page_icon="🏷️",
    layout="wide",
)


def load_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


st.title("🏷️ 新闻主题分类分析")

df = load_csv(PROCESSED_DIR / "classified_news.csv")

if df.empty:
    st.warning("未找到 data/processed/classified_news.csv")
    st.stop()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("新闻数量", len(df))

with col2:
    st.metric("主题数量", df["topic"].nunique() if "topic" in df.columns else 0)

with col3:
    if "topic_confidence" in df.columns:
        st.metric("平均分类置信度", f"{df['topic_confidence'].mean():.2f}")
    else:
        st.metric("平均分类置信度", "暂无")

st.divider()

if "topic" in df.columns:
    topic_count = df["topic"].value_counts().reset_index()
    topic_count.columns = ["topic", "count"]

    col_left, col_right = st.columns([2, 1])

    with col_left:
        fig = px.bar(
            topic_count,
            x="topic",
            y="count",
            title="新闻主题分布",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        fig = px.pie(
            topic_count,
            names="topic",
            values="count",
            title="主题占比",
        )
        st.plotly_chart(fig, use_container_width=True)

st.subheader("分类结果明细")

display_columns = [
    column
    for column in [
        "analysis_date",
        "title",
        "topic",
        "topic_score",
        "topic_confidence",
        "url",
    ]
    if column in df.columns
]

st.dataframe(df[display_columns], use_container_width=True)