"""
Feature engineering module.

This module builds weekly features by combining:
1. News topic, sentiment and summarization indicators
2. WTI crude oil price data

Input:
- data/processed/summarized_news.csv
- data/raw/wti_price.csv

Output:
- data/processed/weekly_features.csv
- results/feature_engineering_summary.csv
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"


def ensure_output_dirs() -> None:
    """Create output directories if they do not exist."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def get_week_end(date_series: pd.Series) -> pd.Series:
    """
    Convert dates to weekly period ending on Sunday.
    """
    return (
        pd.to_datetime(date_series, errors="coerce", utc=True)
        .dt.tz_convert(None)
        .dt.to_period("W-SUN")
        .apply(lambda period: period.end_time)
        .dt.normalize()
    )


def load_news_data(input_file: Path) -> pd.DataFrame:
    """
    Load summarized news data.
    """
    if not input_file.exists():
        raise FileNotFoundError(f"News input file not found: {input_file}")

    news_df = pd.read_csv(input_file)

    required_columns = {
        "topic",
        "sentiment_score",
        "sentiment_label",
        "analysis_date",
    }

    missing_columns = required_columns - set(news_df.columns)

    if missing_columns:
        raise ValueError(f"Missing required news columns: {missing_columns}")

    news_df["analysis_date"] = pd.to_datetime(
        news_df["analysis_date"],
        errors="coerce",
        utc=True,
    )

    news_df["sentiment_score"] = pd.to_numeric(
        news_df["sentiment_score"],
        errors="coerce",
    ).fillna(0.0)

    if "topic_confidence" in news_df.columns:
        news_df["topic_confidence"] = pd.to_numeric(
            news_df["topic_confidence"],
            errors="coerce",
        ).fillna(0.0)
    else:
        news_df["topic_confidence"] = 0.0

    if "compression_ratio" in news_df.columns:
        news_df["compression_ratio"] = pd.to_numeric(
            news_df["compression_ratio"],
            errors="coerce",
        ).fillna(0.0)
    else:
        news_df["compression_ratio"] = 0.0

    if "token_count" in news_df.columns:
        news_df["token_count"] = pd.to_numeric(
            news_df["token_count"],
            errors="coerce",
        ).fillna(0.0)
    else:
        news_df["token_count"] = 0.0

    return news_df


def load_price_data(input_file: Path) -> pd.DataFrame:
    """
    Load WTI price data.

    Supported price formats:
    - date,wti_price
    - date,close_cl_f
    - date,close
    """
    if not input_file.exists():
        raise FileNotFoundError(f"Price input file not found: {input_file}")

    price_df = pd.read_csv(input_file)

    if "date" not in price_df.columns:
        raise ValueError("Price data must contain a 'date' column.")

    price_candidates = [
        "wti_price",
        "close_cl_f",
        "close",
        "adj_close_cl_f",
    ]

    price_column = None

    for candidate in price_candidates:
        if candidate in price_df.columns:
            price_column = candidate
            break

    if price_column is None:
        raise ValueError(
            f"No supported price column found. Expected one of: {price_candidates}"
        )

    price_df["date"] = pd.to_datetime(price_df["date"], errors="coerce")
    price_df["wti_price"] = pd.to_numeric(
        price_df[price_column],
        errors="coerce",
    )

    price_df = price_df.dropna(subset=["date", "wti_price"])
    price_df = price_df.sort_values("date")

    return price_df[["date", "wti_price"]].copy()


def prepare_news_dates(
    news_df: pd.DataFrame,
    price_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, str]:
    """
    Prepare news dates for weekly aggregation.

    If RSS news dates do not overlap with the available WTI price range,
    the function assigns demo dates across the WTI price period. This keeps
    the experimental pipeline runnable for a small course project dataset.
    """
    news_df = news_df.copy()

    price_min = price_df["date"].min()
    price_max = price_df["date"].max()

    valid_news = news_df.dropna(subset=["analysis_date"]).copy()

    if valid_news.empty:
        date_source = "demo_assigned_date_no_valid_news_date"
    else:
        news_min = valid_news["analysis_date"].dt.tz_convert(None).min()
        news_max = valid_news["analysis_date"].dt.tz_convert(None).max()

        has_overlap = (news_min <= price_max) and (news_max >= price_min)

        if has_overlap:
            news_df["feature_date"] = news_df["analysis_date"].dt.tz_convert(None)
            return news_df, "analysis_date"

        date_source = "demo_assigned_date_no_overlap"

    print(
        "Warning: News dates do not overlap with WTI price dates. "
        "Assigning demo dates across the price period for pipeline testing."
    )

    if len(news_df) == 1:
        assigned_dates = [price_min]
    else:
        assigned_dates = pd.date_range(
            start=price_min,
            end=price_max,
            periods=len(news_df),
        )

    news_df["feature_date"] = assigned_dates

    return news_df, date_source


def build_weekly_price_features(price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate daily WTI prices into weekly price features.
    """
    price_df = price_df.copy()
    price_df["week"] = get_week_end(price_df["date"])

    weekly_price = (
        price_df.groupby("week")
        .agg(
            wti_open=("wti_price", "first"),
            wti_close=("wti_price", "last"),
            wti_mean=("wti_price", "mean"),
            wti_high=("wti_price", "max"),
            wti_low=("wti_price", "min"),
            price_observations=("wti_price", "count"),
        )
        .reset_index()
        .sort_values("week")
    )

    weekly_price["wti_return"] = weekly_price["wti_close"].pct_change()
    weekly_price["wti_close_lag1"] = weekly_price["wti_close"].shift(1)
    weekly_price["wti_close_lag2"] = weekly_price["wti_close"].shift(2)
    weekly_price["target_next_week_close"] = weekly_price["wti_close"].shift(-1)

    return weekly_price


def build_weekly_news_features(news_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate news indicators into weekly features.
    """
    news_df = news_df.copy()
    news_df["week"] = get_week_end(news_df["feature_date"])

    base_features = (
        news_df.groupby("week")
        .agg(
            news_count=("title", "count"),
            avg_sentiment_score=("sentiment_score", "mean"),
            avg_topic_confidence=("topic_confidence", "mean"),
            avg_compression_ratio=("compression_ratio", "mean"),
            avg_token_count=("token_count", "mean"),
        )
        .reset_index()
    )

    sentiment_counts = pd.crosstab(
        news_df["week"],
        news_df["sentiment_label"],
    ).reset_index()

    topic_counts = pd.crosstab(
        news_df["week"],
        news_df["topic"],
    ).reset_index()

    sentiment_counts.columns = [
        "week" if column == "week" else f"sentiment_count_{column}"
        for column in sentiment_counts.columns
    ]

    topic_counts.columns = [
        "week" if column == "week" else f"topic_count_{column}"
        for column in topic_counts.columns
    ]

    weekly_news = base_features.merge(
        sentiment_counts,
        on="week",
        how="left",
    ).merge(
        topic_counts,
        on="week",
        how="left",
    )

    for label in ["positive", "negative", "neutral"]:
        column = f"sentiment_count_{label}"

        if column not in weekly_news.columns:
            weekly_news[column] = 0

        ratio_column = f"{label}_ratio"
        weekly_news[ratio_column] = (
            weekly_news[column] / weekly_news["news_count"]
        ).fillna(0.0)

    return weekly_news


def build_weekly_features(
    news_file: Path | None = None,
    price_file: Path | None = None,
    output_file: Path | None = None,
    summary_file: Path | None = None,
) -> pd.DataFrame:
    """
    Build final weekly modeling dataset.
    """
    ensure_output_dirs()

    if news_file is None:
        news_file = PROCESSED_DATA_DIR / "summarized_news.csv"

    if price_file is None:
        price_file = RAW_DATA_DIR / "wti_price.csv"

    if output_file is None:
        output_file = PROCESSED_DATA_DIR / "weekly_features.csv"

    if summary_file is None:
        summary_file = RESULTS_DIR / "feature_engineering_summary.csv"

    news_df = load_news_data(news_file)
    price_df = load_price_data(price_file)

    news_df, date_source = prepare_news_dates(news_df, price_df)

    weekly_price = build_weekly_price_features(price_df)
    weekly_news = build_weekly_news_features(news_df)

    weekly_features = weekly_price.merge(
        weekly_news,
        on="week",
        how="left",
    )

    news_feature_columns = [
        column
        for column in weekly_features.columns
        if column.startswith("news_")
        or column.startswith("avg_")
        or column.startswith("sentiment_")
        or column.startswith("topic_")
        or column.endswith("_ratio")
    ]

    weekly_features[news_feature_columns] = weekly_features[
        news_feature_columns
    ].fillna(0)

    weekly_features = weekly_features.sort_values("week")

    weekly_features.to_csv(output_file, index=False, encoding="utf-8-sig")

    summary_stats = {
        "news_rows": len(news_df),
        "price_rows": len(price_df),
        "weekly_rows": len(weekly_features),
        "news_date_source": date_source,
        "start_week": weekly_features["week"].min(),
        "end_week": weekly_features["week"].max(),
        "weeks_with_news": int((weekly_features["news_count"] > 0).sum())
        if "news_count" in weekly_features.columns
        else 0,
    }

    summary_df = pd.DataFrame([summary_stats])
    summary_df.to_csv(summary_file, index=False, encoding="utf-8-sig")

    print(f"Saved weekly features to: {output_file}")
    print(f"Saved feature engineering summary to: {summary_file}")
    print()
    print("Feature engineering summary:")
    print(summary_df)

    return weekly_features


def main() -> None:
    """Run feature engineering."""
    build_weekly_features()


if __name__ == "__main__":
    main()