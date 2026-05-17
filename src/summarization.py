"""
News summarization module.

This module generates short extractive summaries for energy news.

Input:
- data/processed/sentiment_news.csv

Output:
- data/processed/summarized_news.csv
- results/summarization_summary.csv
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import List

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"


STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "while", "with", "without",
    "of", "to", "in", "on", "for", "from", "by", "as", "at", "is", "are",
    "was", "were", "be", "been", "being", "this", "that", "these", "those",
    "it", "its", "into", "about", "over", "under", "after", "before",
    "than", "then", "so", "such", "their", "there", "we", "our", "you",
    "your", "they", "them", "he", "she", "his", "her", "will", "would",
    "can", "could", "may", "might", "also", "more", "most", "less",
    "least", "not", "no", "do", "does", "did", "have", "has", "had",
}


def ensure_output_dirs() -> None:
    """Create output directories if they do not exist."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def split_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    if pd.isna(text):
        return []

    text = str(text).strip()

    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    return sentences


def tokenize(text: str) -> List[str]:
    """Tokenize text into meaningful lowercase words."""
    if pd.isna(text):
        return []

    text = str(text).lower()
    words = re.findall(r"[a-z]+", text)

    return [
        word
        for word in words
        if word not in STOPWORDS and len(word) > 2
    ]


def calculate_title_overlap(sentence: str, title: str) -> float:
    """Calculate overlap ratio between sentence words and title words."""
    sentence_words = set(tokenize(sentence))
    title_words = set(tokenize(title))

    if not sentence_words or not title_words:
        return 0.0

    return len(sentence_words & title_words) / len(title_words)


def score_sentences(sentences: List[str], title: str) -> List[tuple[int, float]]:
    """
    Score sentences using:
    - word frequency score
    - title overlap score
    - sentence position score
    """
    all_words = []

    for sentence in sentences:
        all_words.extend(tokenize(sentence))

    word_freq = Counter(all_words)

    if not word_freq:
        return [(index, 0.0) for index in range(len(sentences))]

    max_freq = max(word_freq.values())

    scored_sentences = []

    for index, sentence in enumerate(sentences):
        words = tokenize(sentence)

        if not words:
            scored_sentences.append((index, 0.0))
            continue

        frequency_score = sum(
            word_freq[word] / max_freq
            for word in words
        ) / len(words)

        title_overlap_score = calculate_title_overlap(sentence, title)

        # Earlier sentences are usually more informative in news.
        position_score = 1.0 / (index + 1)

        final_score = (
            0.6 * frequency_score
            + 0.25 * title_overlap_score
            + 0.15 * position_score
        )

        scored_sentences.append((index, final_score))

    return scored_sentences


def generate_summary(
    title: str,
    text: str,
    max_sentences: int = 2,
) -> str:
    """
    Generate an extractive summary.

    Top-scored sentences are selected and then restored to original order.
    """
    sentences = split_sentences(text)

    if not sentences:
        return ""

    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    scored_sentences = score_sentences(sentences, title)

    top_indices = sorted(
        [index for index, _ in sorted(
            scored_sentences,
            key=lambda item: item[1],
            reverse=True,
        )[:max_sentences]]
    )

    summary = " ".join(sentences[index] for index in top_indices)

    return summary.strip()


def summarize_news(
    input_file: Path | None = None,
    output_file: Path | None = None,
    summary_file: Path | None = None,
) -> pd.DataFrame:
    """
    Generate summaries for sentiment news data.
    """
    ensure_output_dirs()

    if input_file is None:
        input_file = PROCESSED_DATA_DIR / "sentiment_news.csv"

    if output_file is None:
        output_file = PROCESSED_DATA_DIR / "summarized_news.csv"

    if summary_file is None:
        summary_file = RESULTS_DIR / "summarization_summary.csv"

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    news_df = pd.read_csv(input_file)

    required_columns = {"title", "raw_text"}

    missing_columns = required_columns - set(news_df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    news_df["title"] = news_df["title"].fillna("")
    news_df["raw_text"] = news_df["raw_text"].fillna("")

    news_df["summary_generated"] = news_df.apply(
        lambda row: generate_summary(
            title=row["title"],
            text=row["raw_text"],
            max_sentences=2,
        ),
        axis=1,
    )

    news_df["raw_text_length"] = news_df["raw_text"].str.len()
    news_df["summary_length"] = news_df["summary_generated"].str.len()

    news_df["compression_ratio"] = news_df.apply(
        lambda row: round(row["summary_length"] / row["raw_text_length"], 4)
        if row["raw_text_length"] > 0
        else 0.0,
        axis=1,
    )

    if "analysis_date" in news_df.columns:
        news_df["analysis_date"] = pd.to_datetime(
            news_df["analysis_date"],
            errors="coerce",
            utc=True,
        )
        news_df = news_df.sort_values("analysis_date", ascending=False)

    news_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    summary_stats = {
        "news_count": len(news_df),
        "avg_raw_text_length": round(news_df["raw_text_length"].mean(), 2),
        "avg_summary_length": round(news_df["summary_length"].mean(), 2),
        "avg_compression_ratio": round(news_df["compression_ratio"].mean(), 4),
        "median_compression_ratio": round(news_df["compression_ratio"].median(), 4),
    }

    summary_df = pd.DataFrame([summary_stats])
    summary_df.to_csv(summary_file, index=False, encoding="utf-8-sig")

    print(f"Saved summarized news data to: {output_file}")
    print(f"Saved summarization summary to: {summary_file}")
    print()
    print("Summarization summary:")
    print(summary_df)

    return news_df


def main() -> None:
    """Run news summarization."""
    summarize_news()


if __name__ == "__main__":
    main()