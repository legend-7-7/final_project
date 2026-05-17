from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"


st.set_page_config(
    page_title="News Summary",
    page_icon="📝",
    layout="wide",
)


def load_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


st.title("📝 新闻摘要展示")

df = load_csv(PROCESSED_DIR / "summarized_news.csv")
summary_df = load_csv(RESULTS_DIR / "summarization_summary.csv")

if df.empty:
    st.warning("未找到 data/processed/summarized_news.csv")
    st.stop()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("新闻数量", len(df))

with col2:
    if "compression_ratio" in df.columns:
        st.metric("平均压缩率", f"{df['compression_ratio'].mean():.2f}")
    else:
        st.metric("平均压缩率", "暂无")

with col3:
    if "summary_length" in df.columns:
        st.metric("平均摘要长度", f"{df['summary_length'].mean():.0f}")
    else:
        st.metric("平均摘要长度", "暂无")

st.divider()

if "compression_ratio" in df.columns:
    fig = px.histogram(
        df,
        x="compression_ratio",
        nbins=20,
        title="摘要压缩率分布",
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("摘要结果")

topic_options = ["全部"]

if "topic" in df.columns:
    topic_options += sorted(df["topic"].dropna().unique().tolist())

selected_topic = st.selectbox("选择主题", topic_options)

display_df = df.copy()

if selected_topic != "全部" and "topic" in display_df.columns:
    display_df = display_df[display_df["topic"] == selected_topic]

for _, row in display_df.iterrows():
    with st.expander(str(row.get("title", "Untitled"))):
        st.markdown("**主题：** " + str(row.get("topic", "未知")))
        st.markdown("**情感：** " + str(row.get("sentiment_label", "未知")))
        st.markdown("**生成摘要：**")
        st.write(row.get("summary_generated", ""))

        if "raw_text" in row:
            st.markdown("**原始文本：**")
            st.write(row.get("raw_text", ""))