"""
News topic classification module.

This module classifies processed energy news into oil-price-related topics.

Input:
- data/processed/processed_news.csv

Output:
- data/processed/classified_news.csv
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


TOPIC_KEYWORDS: Dict[str, list[str]] = {
    "supply": [
        "production", "produce", "output", "supply", "reserve", "drilling",
        "refinery", "barrel", "crude", "export", "import", "opec",
        "strategic petroleum reserve", "spr"
    ],
    "demand": [
        "demand", "consumption", "consume", "industrial", "manufacturing",
        "transportation", "gasoline", "diesel", "fuel", "travel"
    ],
    "inventory": [
        "inventory", "stock", "stocks", "storage", "weekly petroleum",
        "reserve", "stored"
    ],
    "geopolitics": [
        "war", "conflict", "sanction", "geopolitical", "hormuz",
        "middle east", "russia", "ukraine", "iran", "red sea"
    ],
    "financial_market": [
        "price", "prices", "futures", "spot", "benchmark", "market",
        "trader", "financial", "dollar", "interest", "inflation"
    ],
    "weather_event": [
        "weather", "hurricane", "storm", "freeze", "winter", "heat",
        "temperature", "wildfire"
    ],
    "natural_gas": [
        "natural gas", "lng", "gas", "bcf", "pipeline", "henry hub"
    ],
    "energy_transition": [
        "renewable", "solar", "wind", "biofuel", "sustainable",
        "aviation fuel", "saf", "electricity", "coal", "emission"
    ],
}


def ensure_processed_data_dir() -> None:
    """Create processed data directory if it does not exist."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def count_keyword_hits(text: str, keywords: list[str]) -> int:
    """
    Count keyword hits in a text.

    Both single words and phrases are supported.
    """
    if pd.isna(text):
        return 0

    text = str(text).lower()
    total_hits = 0

    for keyword in keywords:
        keyword = keyword.lower().strip()

        if not keyword:
            continue

        pattern = r"\b" + re.escape(keyword) + r"\b"
        total_hits += len(re.findall(pattern, text))

    return total_hits


def classify_one_news(text: str) -> Tuple[str, int, float, Dict[str, int]]:
    """
    Classify one news item into a topic.

    Returns:
    - best topic
    - best topic score
    - confidence
    - all topic scores
    """
    topic_scores = {
        topic: count_keyword_hits(text, keywords)
        for topic, keywords in TOPIC_KEYWORDS.items()
    }

    total_score = sum(topic_scores.values())

    if total_score == 0:
        return "other", 0, 0.0, topic_scores

    best_topic = max(topic_scores, key=topic_scores.get)
    best_score = topic_scores[best_topic]
    confidence = best_score / total_score

    return best_topic, best_score, confidence, topic_scores


def classify_news(
    input_file: Path | None = None,
    output_file: Path | None = None,
) -> pd.DataFrame:
    """
    Classify processed news into oil-price-related topics.
    """
    ensure_processed_data_dir()

    if input_file is None:
        input_file = PROCESSED_DATA_DIR / "processed_news.csv"

    if output_file is None:
        output_file = PROCESSED_DATA_DIR / "classified_news.csv"

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    news_df = pd.read_csv(input_file)

    if "processed_text" not in news_df.columns:
        raise ValueError("Column 'processed_text' is required for classification.")

    results = news_df["processed_text"].fillna("").apply(classify_one_news)

    news_df["topic"] = results.apply(lambda item: item[0])
    news_df["topic_score"] = results.apply(lambda item: item[1])
    news_df["topic_confidence"] = results.apply(lambda item: round(item[2], 4))
    news_df["topic_scores"] = results.apply(
        lambda item: json.dumps(item[3], ensure_ascii=False)
    )

    if "analysis_date" in news_df.columns:
        news_df["analysis_date"] = pd.to_datetime(
            news_df["analysis_date"],
            errors="coerce",
            utc=True,
        )
        news_df = news_df.sort_values("analysis_date", ascending=False)

    news_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"Saved classified news data to: {output_file}")
    print(f"Classified news rows: {len(news_df)}")
    print()
    print("Topic distribution:")
    print(news_df["topic"].value_counts())

    return news_df


def main() -> None:
    """Run news topic classification."""
    classify_news()


if __name__ == "__main__":
    main()