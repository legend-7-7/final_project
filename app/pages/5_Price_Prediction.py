from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PROJECT_ROOT / "results"


st.set_page_config(
    page_title="Price Prediction",
    page_icon="📈",
    layout="wide",
)


def load_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


st.title("📈 WTI 油价预测结果")

prediction_df = load_csv(RESULTS_DIR / "price_prediction_results.csv")
metrics_df = load_csv(RESULTS_DIR / "price_prediction_metrics.csv")
importance_df = load_csv(RESULTS_DIR / "price_prediction_feature_importance.csv")

if prediction_df.empty:
    st.warning("未找到 results/price_prediction_results.csv")
    st.stop()

if not metrics_df.empty:
    best_model = metrics_df.sort_values("mape").iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("最佳模型", best_model["model"])

    with col2:
        st.metric("MAE", f"{best_model['mae']:.3f}")

    with col3:
        st.metric("RMSE", f"{best_model['rmse']:.3f}")

    with col4:
        st.metric("MAPE", f"{best_model['mape']:.2f}%")

st.divider()

st.subheader("模型评价指标")

if not metrics_df.empty:
    st.dataframe(metrics_df, use_container_width=True)

    fig = px.bar(
        metrics_df,
        x="model",
        y="mape",
        title="不同模型 MAPE 对比",
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("预测值与实际值对比")

prediction_df["week"] = pd.to_datetime(prediction_df["week"], errors="coerce")

value_columns = [
    column
    for column in prediction_df.columns
    if column.endswith("_prediction") or column == "actual_next_week_close"
]

plot_df = prediction_df[["week"] + value_columns].melt(
    id_vars="week",
    var_name="series",
    value_name="price",
)

fig = px.line(
    plot_df,
    x="week",
    y="price",
    color="series",
    markers=True,
    title="预测结果对比",
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("预测结果数据")

st.dataframe(prediction_df, use_container_width=True)

if not importance_df.empty:
    st.subheader("特征重要性")

    top_importance = importance_df.head(15)

    fig = px.bar(
        top_importance,
        x="random_forest_importance",
        y="feature",
        orientation="h",
        title="随机森林特征重要性 Top 15",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(importance_df, use_container_width=True)