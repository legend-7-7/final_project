"""
Text preprocessing module.

This module reads raw EIA energy news data and generates cleaned text data.

Input:
- data/raw/eia_energy_news.csv

Output:
- data/processed/processed_news.csv
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "while", "with", "without",
    "of", "to", "in", "on", "for", "from", "by", "as", "at", "is", "are",
    "was", "were", "be", "been", "being", "this", "that", "these", "those",
    "it", "its", "into", "about", "over", "under", "after", "before",
    "than", "then", "so", "such", "their", "there", "we", "our", "you",
    "your", "they", "them", "he", "she", "his", "her", "will", "would",
    "can", "could", "may", "might", "also", "more", "most", "less",
    "least", "not", "no", "yes", "do", "does", "did", "have", "has",
    "had", "according", "latest", "new", "u", "s"
}


def ensure_processed_data_dir() -> None:
    """Create processed data directory if it does not exist."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def normalize_text(text: str) -> str:
    """
    Normalize raw text.

    Steps:
    - Lowercase
    - Remove URLs
    - Remove numbers
    - Remove punctuation
    - Normalize spaces
    """
    if pd.isna(text):
        return ""

    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def tokenize_text(text: str) -> List[str]:
    """
    Tokenize text and remove stopwords.
    """
    words = text.split()

    tokens = [
        word
        for word in words
        if word not in STOPWORDS and len(word) > 2
    ]

    return tokens


def preprocess_news(
    input_file: Path | None = None,
    output_file: Path | None = None,
) -> pd.DataFrame:
    """
    Preprocess raw news data.

    Parameters
    ----------
    input_file:
        Raw news CSV file.
    output_file:
        Processed news CSV file.

    Returns
    -------
    pd.DataFrame
        Processed news data.
    """
    ensure_processed_data_dir()

    if input_file is None:
        input_file = RAW_DATA_DIR / "eia_energy_news.csv"

    if output_file is None:
        output_file = PROCESSED_DATA_DIR / "processed_news.csv"

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    news_df = pd.read_csv(input_file)

    required_columns = {"title", "summary", "url"}
    missing_columns = required_columns - set(news_df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    news_df["title"] = news_df["title"].fillna("")
    news_df["summary"] = news_df["summary"].fillna("")

    if "text" not in news_df.columns:
        news_df["text"] = (
            news_df["title"].astype(str)
            + " "
            + news_df["summary"].astype(str)
        )

    news_df["raw_text"] = news_df["text"].fillna("")
    news_df["clean_text"] = news_df["raw_text"].apply(normalize_text)
    news_df["tokens"] = news_df["clean_text"].apply(tokenize_text)
    news_df["processed_text"] = news_df["tokens"].apply(lambda tokens: " ".join(tokens))
    news_df["token_count"] = news_df["tokens"].apply(len)

    if "analysis_date" in news_df.columns:
        news_df["analysis_date"] = pd.to_datetime(
            news_df["analysis_date"],
            errors="coerce",
            utc=True,
        )
    elif "published" in news_df.columns:
        news_df["analysis_date"] = pd.to_datetime(
            news_df["published"],
            errors="coerce",
            utc=True,
        )
    else:
        news_df["analysis_date"] = pd.NaT

    output_columns = [
        "source",
        "title",
        "summary",
        "url",
        "analysis_date",
        "raw_text",
        "clean_text",
        "processed_text",
        "token_count",
    ]

    available_columns = [
        column for column in output_columns if column in news_df.columns
    ]

    processed_df = news_df[available_columns].copy()

    processed_df = processed_df[
        processed_df["processed_text"].str.len() > 0
    ].copy()

    processed_df = processed_df.drop_duplicates(subset=["url"])
    processed_df = processed_df.sort_values("analysis_date", ascending=False)

    processed_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"Saved processed news data to: {output_file}")
    print(f"Processed news rows: {len(processed_df)}")
    print("Columns:")
    print(list(processed_df.columns))

    return processed_df


def main() -> None:
    """Run text preprocessing."""
    preprocess_news()


if __name__ == "__main__":
    main()