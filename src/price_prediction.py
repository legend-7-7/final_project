"""
Price prediction module.

This module builds simple WTI price prediction models based on weekly features.

Input:
- data/processed/weekly_features.csv

Output:
- results/price_prediction_results.csv
- results/price_prediction_metrics.csv
- results/price_prediction_feature_importance.csv
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"


def ensure_results_dir() -> None:
    """Create results directory if it does not exist."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Mean Absolute Percentage Error.

    Zero values are ignored to avoid division errors.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    mask = y_true != 0

    if mask.sum() == 0:
        return np.nan

    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def evaluate_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str,
) -> Dict[str, float | str]:
    """
    Calculate MAE, RMSE and MAPE.
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = calculate_mape(y_true, y_pred)

    return {
        "model": model_name,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "mape": round(mape, 4),
    }


def load_weekly_features(input_file: Path) -> pd.DataFrame:
    """
    Load weekly feature dataset.
    """
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    df = pd.read_csv(input_file)

    required_columns = {
        "week",
        "wti_close",
        "target_next_week_close",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    df["week"] = pd.to_datetime(df["week"], errors="coerce")
    df["wti_close"] = pd.to_numeric(df["wti_close"], errors="coerce")
    df["target_next_week_close"] = pd.to_numeric(
        df["target_next_week_close"],
        errors="coerce",
    )

    df = df.sort_values("week")
    df = df.dropna(subset=["week", "wti_close", "target_next_week_close"])

    return df


def select_feature_columns(df: pd.DataFrame) -> List[str]:
    """
    Select numeric feature columns for prediction.

    The target is next week's WTI close price.
    Current-week price and news features are used as predictors.
    """
    excluded_columns = {
        "week",
        "target_next_week_close",
    }

    candidate_columns = []

    for column in df.columns:
        if column in excluded_columns:
            continue

        if pd.api.types.is_numeric_dtype(df[column]):
            candidate_columns.append(column)

    # Remove the target-like future column if it appears by accident.
    candidate_columns = [
        column
        for column in candidate_columns
        if not column.startswith("target_")
    ]

    return candidate_columns


def time_based_train_test_split(
    df: pd.DataFrame,
    test_ratio: float = 0.3,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split data by time order.

    The earlier part is used for training, and the later part is used for testing.
    """
    if len(df) < 5:
        raise ValueError(
            "Not enough weekly rows for train-test split. "
            "Please provide more WTI price data."
        )

    test_size = max(2, int(round(len(df) * test_ratio)))
    train_size = len(df) - test_size

    if train_size < 3:
        train_size = max(3, len(df) - 2)
        test_size = len(df) - train_size

    train_df = df.iloc[:train_size].copy()
    test_df = df.iloc[train_size:].copy()

    return train_df, test_df


def train_and_predict_models(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_columns: List[str],
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Train baseline and machine learning models.

    Models:
    - Baseline: current week close price as next week prediction
    - Linear Regression
    - Ridge Regression
    - Random Forest
    """
    x_train = train_df[feature_columns].fillna(0)
    y_train = train_df["target_next_week_close"]

    x_test = test_df[feature_columns].fillna(0)
    y_test = test_df["target_next_week_close"]

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    prediction_df = test_df[["week", "wti_close", "target_next_week_close"]].copy()
    prediction_df = prediction_df.rename(
        columns={
            "target_next_week_close": "actual_next_week_close",
        }
    )

    metrics = []

    # Baseline model
    prediction_df["baseline_prediction"] = test_df["wti_close"].values
    metrics.append(
        evaluate_predictions(
            y_true=y_test.values,
            y_pred=prediction_df["baseline_prediction"].values,
            model_name="baseline_current_week_close",
        )
    )

    # Linear regression
    linear_model = LinearRegression()
    linear_model.fit(x_train_scaled, y_train)
    prediction_df["linear_regression_prediction"] = linear_model.predict(x_test_scaled)
    metrics.append(
        evaluate_predictions(
            y_true=y_test.values,
            y_pred=prediction_df["linear_regression_prediction"].values,
            model_name="linear_regression",
        )
    )

    # Ridge regression
    ridge_model = Ridge(alpha=1.0)
    ridge_model.fit(x_train_scaled, y_train)
    prediction_df["ridge_regression_prediction"] = ridge_model.predict(x_test_scaled)
    metrics.append(
        evaluate_predictions(
            y_true=y_test.values,
            y_pred=prediction_df["ridge_regression_prediction"].values,
            model_name="ridge_regression",
        )
    )

    # Random forest
    forest_model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        max_depth=3,
    )
    forest_model.fit(x_train, y_train)
    prediction_df["random_forest_prediction"] = forest_model.predict(x_test)
    metrics.append(
        evaluate_predictions(
            y_true=y_test.values,
            y_pred=prediction_df["random_forest_prediction"].values,
            model_name="random_forest",
        )
    )

    metrics_df = pd.DataFrame(metrics)

    feature_importance_df = pd.DataFrame(
        {
            "feature": feature_columns,
            "random_forest_importance": forest_model.feature_importances_,
            "ridge_coefficient": ridge_model.coef_,
            "linear_coefficient": linear_model.coef_,
        }
    ).sort_values("random_forest_importance", ascending=False)

    return prediction_df, metrics_df, feature_importance_df


def run_price_prediction(
    input_file: Path | None = None,
    prediction_file: Path | None = None,
    metrics_file: Path | None = None,
    feature_importance_file: Path | None = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Run the full price prediction workflow.
    """
    ensure_results_dir()

    if input_file is None:
        input_file = PROCESSED_DATA_DIR / "weekly_features.csv"

    if prediction_file is None:
        prediction_file = RESULTS_DIR / "price_prediction_results.csv"

    if metrics_file is None:
        metrics_file = RESULTS_DIR / "price_prediction_metrics.csv"

    if feature_importance_file is None:
        feature_importance_file = RESULTS_DIR / "price_prediction_feature_importance.csv"

    df = load_weekly_features(input_file)

    feature_columns = select_feature_columns(df)

    if not feature_columns:
        raise ValueError("No numeric feature columns found for prediction.")

    train_df, test_df = time_based_train_test_split(df, test_ratio=0.3)

    prediction_df, metrics_df, feature_importance_df = train_and_predict_models(
        train_df=train_df,
        test_df=test_df,
        feature_columns=feature_columns,
    )

    prediction_df.to_csv(prediction_file, index=False, encoding="utf-8-sig")
    metrics_df.to_csv(metrics_file, index=False, encoding="utf-8-sig")
    feature_importance_df.to_csv(
        feature_importance_file,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"Saved prediction results to: {prediction_file}")
    print(f"Saved prediction metrics to: {metrics_file}")
    print(f"Saved feature importance to: {feature_importance_file}")
    print()
    print("Feature columns:")
    print(feature_columns)
    print()
    print("Prediction metrics:")
    print(metrics_df)

    return prediction_df, metrics_df, feature_importance_df


def main() -> None:
    """Run price prediction."""
    run_price_prediction()


if __name__ == "__main__":
    main()