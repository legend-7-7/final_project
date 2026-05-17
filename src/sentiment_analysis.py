"""
Sentiment analysis module.

This module calculates sentiment indicators for classified energy news.

Input:
- data/processed/classified_news.csv

Output:
- data/processed/sentiment_news.csv
- results/sentiment_summary.csv
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"


GENERAL_POSITIVE_WORDS = {
    "increase", "increased", "increases", "increasing",
    "growth", "grow", "grew", "higher", "high", "strong", "stronger",
    "rise", "rising", "rose", "surge", "surged", "surging",
    "gain", "gains", "recovery", "recover", "improve", "improved",
    "record", "boost", "expand", "expanded", "expansion",
}

GENERAL_NEGATIVE_WORDS = {
    "decrease", "decreased", "decreases", "decreasing",
    "decline", "declined", "declines", "declining",
    "drop", "dropped", "fall", "falling", "fell",
    "lower", "low", "weak", "weaker", "slow", "slower",
    "loss", "losses", "cut", "cuts", "reduce", "reduced",
    "risk", "risks", "uncertain", "uncertainty", "shortage",
    "disruption", "disruptions",
}

DOMAIN_BULLISH_WORDS = {
    "supply cut", "production cut", "inventory draw", "stock draw",
    "tight supply", "supply disruption", "geopolitical risk",
    "hormuz", "sanction", "war", "conflict",
    "strong demand", "higher demand", "price surge", "prices rise",
    "crude oil prices rise", "brent crude oil spot prices surge",
}

DOMAIN_BEARISH_WORDS = {
    "demand weakness", "weak demand", "lower demand",
    "inventory build", "stock build", "higher inventory",
    "oversupply", "surplus", "production increase",
    "supply increase", "prices fall", "price decline",
    "lower prices", "coal", "renewable", "solar",
}


def ensure_output_dirs() -> None:
    """Create output directories if they do not exist."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def normalize_text(text: str) -> str:
    """Normalize text for sentiment matching."""
    if pd.isna(text):
        return ""

    text = str(text).lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def count_matches(text: str, lexicon: set[str]) -> int:
    """Count word or phrase matches in text."""
    if not text:
        return 0

    total = 0

    for item in lexicon:
        item = item.lower().strip()

        if not item:
            continue

        pattern = r"\b" + re.escape(item) + r"\b"
        total += len(re.findall(pattern, text))

    return total


def calculate_sentiment_for_text(text: str) -> Dict[str, float | int | str]:
    """
    Calculate sentiment score for one piece of text.

    The final score combines:
    - general positive / negative sentiment
    - domain-specific bullish / bearish oil-market signals
    """
    normalized_text = normalize_text(text)

    positive_hits = count_matches(normalized_text, GENERAL_POSITIVE_WORDS)
    negative_hits = count_matches(normalized_text, GENERAL_NEGATIVE_WORDS)

    bullish_hits = count_matches(normalized_text, DOMAIN_BULLISH_WORDS)
    bearish_hits = count_matches(normalized_text, DOMAIN_BEARISH_WORDS)

    general_score = positive_hits - negative_hits
    domain_score = bullish_hits - bearish_hits

    raw_score = general_score + 1.5 * domain_score

    total_hits = positive_hits + negative_hits + bullish_hits + bearish_hits

    if total_hits == 0:
        sentiment_score = 0.0
    else:
        sentiment_score = raw_score / total_hits

    if sentiment_score > 0.05:
        sentiment_label = "positive"
    elif sentiment_score < -0.05:
        sentiment_label = "negative"
    else:
        sentiment_label = "neutral"

    return {
        "positive_hits": positive_hits,
        "negative_hits": negative_hits,
        "bullish_hits": bullish_hits,
        "bearish_hits": bearish_hits,
        "sentiment_hits": total_hits,
        "sentiment_score": round(sentiment_score, 4),
        "sentiment_label": sentiment_label,
    }


def analyze_sentiment(
    input_file: Path | None = None,
    output_file: Path | None = None,
    summary_file: Path | None = None,
) -> pd.DataFrame:
    """
    Run sentiment analysis for classified news.
    """
    ensure_output_dirs()

    if input_file is None:
        input_file = PROCESSED_DATA_DIR / "classified_news.csv"

    if output_file is None:
        output_file = PROCESSED_DATA_DIR / "sentiment_news.csv"

    if summary_file is None:
        summary_file = RESULTS_DIR / "sentiment_summary.csv"

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    news_df = pd.read_csv(input_file)

    if "raw_text" in news_df.columns:
        text_column = "raw_text"
    elif "processed_text" in news_df.columns:
        text_column = "processed_text"
    else:
        raise ValueError("Input data must contain 'raw_text' or 'processed_text'.")

    sentiment_results = news_df[text_column].fillna("").apply(
        calculate_sentiment_for_text
    )

    sentiment_df = pd.DataFrame(list(sentiment_results))
    news_df = pd.concat([news_df, sentiment_df], axis=1)

    if "analysis_date" in news_df.columns:
        news_df["analysis_date"] = pd.to_datetime(
            news_df["analysis_date"],
            errors="coerce",
            utc=True,
        )
        news_df = news_df.sort_values("analysis_date", ascending=False)

    news_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    summary_df = (
        news_df["sentiment_label"]
        .value_counts()
        .rename_axis("sentiment_label")
        .reset_index(name="count")
    )

    summary_df["ratio"] = summary_df["count"] / summary_df["count"].sum()
    summary_df["ratio"] = summary_df["ratio"].round(4)

    summary_df.to_csv(summary_file, index=False, encoding="utf-8-sig")

    print(f"Saved sentiment news data to: {output_file}")
    print(f"Saved sentiment summary to: {summary_file}")
    print()
    print("Sentiment distribution:")
    print(summary_df)

    return news_df


def main() -> None:
    """Run sentiment analysis."""
    analyze_sentiment()


if __name__ == "__main__":
    main()