from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR = DATA_DIR / "raw"
RESULTS_DIR = PROJECT_ROOT / "results"


st.set_page_config(
    page_title="Result Review",
    page_icon="✅",
    layout="wide",
)


def load_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


st.title("✅ 结果复核")

files = {
    "原始新闻数据": RAW_DIR / "eia_energy_news.csv",
    "WTI 油价数据": RAW_DIR / "wti_price.csv",
    "文本预处理结果": PROCESSED_DIR / "processed_news.csv",
    "主题分类结果": PROCESSED_DIR / "classified_news.csv",
    "情感分析结果": PROCESSED_DIR / "sentiment_news.csv",
    "新闻摘要结果": PROCESSED_DIR / "summarized_news.csv",
    "周度特征数据": PROCESSED_DIR / "weekly_features.csv",
    "情感统计结果": RESULTS_DIR / "sentiment_summary.csv",
    "摘要统计结果": RESULTS_DIR / "summarization_summary.csv",
    "特征工程统计结果": RESULTS_DIR / "feature_engineering_summary.csv",
    "预测结果": RESULTS_DIR / "price_prediction_results.csv",
    "预测评价指标": RESULTS_DIR / "price_prediction_metrics.csv",
    "特征重要性": RESULTS_DIR / "price_prediction_feature_importance.csv",
}

review_rows = []

for name, path in files.items():
    df = load_csv(path)

    review_rows.append(
        {
            "模块": name,
            "文件路径": str(path.relative_to(PROJECT_ROOT)),
            "是否存在": path.exists(),
            "行数": len(df) if not df.empty else 0,
            "列数": len(df.columns) if not df.empty else 0,
        }
    )

review_df = pd.DataFrame(review_rows)

st.subheader("文件生成情况")

st.dataframe(review_df, use_container_width=True)

st.divider()

st.subheader("阶段性结果预览")

selected_name = st.selectbox("选择要查看的文件", list(files.keys()))

selected_path = files[selected_name]
selected_df = load_csv(selected_path)

if selected_df.empty:
    st.warning("该文件不存在或内容为空。")
else:
    st.dataframe(selected_df.head(20), use_container_width=True)

st.divider()

st.subheader("项目完成情况")

completed_count = review_df["是否存在"].sum()
total_count = len(review_df)

st.progress(completed_count / total_count)

st.write(f"已生成文件：{completed_count} / {total_count}")

if completed_count == total_count:
    st.success("所有核心结果文件均已生成。")
else:
    st.warning("仍有部分结果文件未生成。")