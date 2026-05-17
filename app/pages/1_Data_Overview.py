from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"


st.set_page_config(
    page_title="Data Overview",
    page_icon="📊",
    layout="wide",
)


def load_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


st.title("📊 数据总览")

news_df = load_csv(RAW_DIR / "eia_energy_news.csv")
price_df = load_csv(RAW_DIR / "wti_price.csv")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("原始新闻数量", len(news_df))

with col2:
    st.metric("油价记录数量", len(price_df))

with col3:
    st.metric("数据源", "EIA + WTI")

st.divider()

tab1, tab2 = st.tabs(["能源新闻数据", "WTI 油价数据"])

with tab1:
    st.subheader("能源新闻原始数据")

    if news_df.empty:
        st.warning("未找到 data/raw/eia_energy_news.csv")
    else:
        st.dataframe(news_df, use_container_width=True)

        if "source" in news_df.columns:
            source_count = news_df["source"].value_counts().reset_index()
            source_count.columns = ["source", "count"]

            fig = px.bar(
                source_count,
                x="source",
                y="count",
                title="新闻来源分布",
            )
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("WTI 油价数据")

    if price_df.empty:
        st.warning("未找到 data/raw/wti_price.csv")
    else:
        st.dataframe(price_df, use_container_width=True)

        if "date" in price_df.columns:
            price_df["date"] = pd.to_datetime(price_df["date"], errors="coerce")

        price_column = None

        for column in ["wti_price", "close_cl_f", "close", "adj_close_cl_f"]:
            if column in price_df.columns:
                price_column = column
                break

        if price_column:
            fig = px.line(
                price_df,
                x="date",
                y=price_column,
                title="WTI 原油价格走势",
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("未找到可用于绘图的油价列。")