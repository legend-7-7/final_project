"""
Streamlit home page.

Run:
streamlit run app/Home.py
"""

from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"


st.set_page_config(
    page_title="WTI Oil Price Forecasting System",
    page_icon="🛢️",
    layout="wide",
)


def load_csv(path: Path) -> pd.DataFrame:
    """Load CSV file safely."""
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def main() -> None:
    st.title("🛢️ 基于能源新闻情绪分析的 WTI 原油价格预测系统")

    st.markdown(
        """
        本系统围绕能源新闻文本信息是否能够辅助 WTI 原油价格预测展开分析，
        构建了从新闻数据采集、文本预处理、主题分类、情感分析、新闻摘要、
        周度特征工程到油价预测与结果展示的完整流程。
        """
    )

    st.divider()

    news_df = load_csv(PROCESSED_DIR / "summarized_news.csv")
    weekly_df = load_csv(PROCESSED_DIR / "weekly_features.csv")
    metrics_df = load_csv(RESULTS_DIR / "price_prediction_metrics.csv")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("新闻数量", len(news_df) if not news_df.empty else 0)

    with col2:
        st.metric("周度样本数", len(weekly_df) if not weekly_df.empty else 0)

    with col3:
        if not metrics_df.empty:
            best_row = metrics_df.sort_values("mape").iloc[0]
            st.metric("最佳模型", best_row["model"])
        else:
            st.metric("最佳模型", "暂无")

    with col4:
        if not metrics_df.empty:
            best_mape = metrics_df["mape"].min()
            st.metric("最低 MAPE", f"{best_mape:.2f}%")
        else:
            st.metric("最低 MAPE", "暂无")

    st.divider()

    st.subheader("📌 项目流程")

    st.markdown(
        """
        ```text
        EIA 能源新闻采集
        → 文本预处理
        → 新闻主题分类
        → 情感分析
        → 新闻摘要提取
        → 周度特征构建
        → WTI 油价预测
        → Streamlit 可视化展示
        ```
        """
    )

    st.subheader("📁 系统页面说明")

    st.markdown(
        """
        - **Data Overview**：查看原始新闻和油价数据  
        - **Topic Classification**：展示新闻主题分类结果  
        - **Sentiment Analysis**：展示情感分布和情感得分  
        - **News Summary**：查看新闻摘要和压缩率  
        - **Price Prediction**：展示预测结果和模型指标  
        - **Result Review**：综合复核各阶段输出结果  
        """
    )


if __name__ == "__main__":
    main()