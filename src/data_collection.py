"""
Data collection module.

This module collects:
1. Energy-related news from EIA RSS feeds
2. WTI crude oil futures price data from Yahoo Finance through yfinance

Output:
- data/raw/eia_energy_news.csv
- data/raw/wti_price.csv
"""

from __future__ import annotations

import html
import time
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from io import StringIO


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


EIA_RSS_FEEDS = {
    "today_in_energy": "https://www.eia.gov/rss/todayinenergy.xml",
    "press_releases": "https://www.eia.gov/rss/press_rss.xml",
    "gasoline_diesel": "https://www.eia.gov/petroleum/gasdiesel/includes/gas_diesel_rss.xml",
}


ENERGY_KEYWORDS = [
    "oil",
    "crude",
    "wti",
    "petroleum",
    "gasoline",
    "diesel",
    "opec",
    "energy",
    "fuel",
    "refinery",
    "inventory",
    "natural gas",
]


def ensure_raw_data_dir() -> None:
    """Create raw data directory if it does not exist."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def clean_html_text(text: Optional[str]) -> str:
    """Remove HTML tags and normalize whitespace."""
    if text is None:
        return ""

    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def save_dataframe(df: pd.DataFrame, output_path: Path) -> None:
    """Save DataFrame to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Saved file: {output_path}")
    print(f"Rows: {len(df)}")


def fetch_rss_xml(feed_url: str) -> str:
    """Fetch RSS XML content."""
    headers = {
        "User-Agent": "Mozilla/5.0 FinalProjectDataCollector/1.0"
    }

    response = requests.get(feed_url, headers=headers, timeout=30)
    response.raise_for_status()

    return response.text


def parse_rss_feed(feed_name: str, feed_url: str) -> pd.DataFrame:
    """
    Parse one RSS feed into a DataFrame.

    Fields:
    - source
    - title
    - summary
    - url
    - published
    """
    print(f"Collecting RSS feed: {feed_name}")

    xml_text = fetch_rss_xml(feed_url)
    root = ET.fromstring(xml_text)

    records = []

    for item in root.findall(".//item"):
        title = clean_html_text(item.findtext("title"))
        summary = clean_html_text(item.findtext("description"))
        url = clean_html_text(item.findtext("link"))
        published = clean_html_text(item.findtext("pubDate"))

        records.append(
            {
                "source": feed_name,
                "title": title,
                "summary": summary,
                "url": url,
                "published": published,
                "collected_at": pd.Timestamp.now(tz="UTC"),
            }
        )

    return pd.DataFrame(records)


def filter_energy_news(news_df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep news related to oil, WTI, petroleum, gasoline, diesel, and energy markets.
    """
    if news_df.empty:
        return news_df

    keyword_pattern = "|".join([re.escape(keyword) for keyword in ENERGY_KEYWORDS])

    text_series = (
        news_df["title"].fillna("")
        + " "
        + news_df["summary"].fillna("")
    ).str.lower()

    filtered_df = news_df[
        text_series.str.contains(keyword_pattern, case=False, regex=True, na=False)
    ].copy()

    return filtered_df


def collect_eia_news(
    output_file: Optional[Path] = None,
    filter_keywords: bool = True,
) -> pd.DataFrame:
    """
    Collect energy-related news from EIA RSS feeds.

    The RSS source is more stable than GDELT for a first working version.
    """
    ensure_raw_data_dir()

    if output_file is None:
        output_file = RAW_DATA_DIR / "eia_energy_news.csv"

    all_news = []

    for feed_name, feed_url in EIA_RSS_FEEDS.items():
        try:
            feed_df = parse_rss_feed(feed_name, feed_url)
            all_news.append(feed_df)
        except Exception as error:
            print(f"Failed to collect {feed_name}: {error}")

    if not all_news:
        raise RuntimeError("No RSS data was collected from EIA feeds.")

    news_df = pd.concat(all_news, ignore_index=True)

    if not news_df.empty:
        news_df = news_df.drop_duplicates(subset=["url"])
        news_df["published"] = pd.to_datetime(
            news_df["published"],
            errors="coerce",
            utc=True,
        )
        news_df["analysis_date"] = news_df["published"].fillna(news_df["collected_at"])
        news_df["text"] = (
            news_df["title"].fillna("")
            + " "
            + news_df["summary"].fillna("")
        ).str.strip()

    if filter_keywords:
        news_df = filter_energy_news(news_df)

    news_df = news_df.sort_values("analysis_date", ascending=False)

    save_dataframe(news_df, output_file)

    return news_df


def clean_yfinance_columns(price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean column names returned by yfinance.

    Some yfinance versions return MultiIndex columns.
    This function handles both normal columns and MultiIndex columns.
    """
    if isinstance(price_df.columns, pd.MultiIndex):
        price_df.columns = [
            "_".join([str(part) for part in col if str(part) != ""])
            for col in price_df.columns
        ]

    price_df = price_df.reset_index()

    price_df.columns = [
        str(col).lower().replace(" ", "_").replace("=", "_")
        for col in price_df.columns
    ]

    return price_df


def collect_wti_price(
    start_date: str = "2024-01-01",
    end_date: str = "2024-04-01",
    output_file: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Download WTI crude oil spot price data from FRED.

    If the online request fails because of timeout or network issues,
    the function will use the existing local CSV file as a fallback.
    """
    ensure_raw_data_dir()

    if output_file is None:
        output_file = RAW_DATA_DIR / "wti_price.csv"

    fred_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILWTICO"

    headers = {
        "User-Agent": "Mozilla/5.0 FinalProjectDataCollector/1.0"
    }

    last_error = None

    for attempt in range(1, 4):
        try:
            print(f"Downloading WTI price data from FRED... attempt {attempt}/3")

            response = requests.get(
                fred_url,
                headers=headers,
                timeout=90,
            )
            response.raise_for_status()

            price_df = pd.read_csv(StringIO(response.text))

            if price_df.empty:
                raise ValueError("No WTI price data was downloaded from FRED.")

            date_column = price_df.columns[0]
            value_column = price_df.columns[1]

            price_df = price_df.rename(
                columns={
                    date_column: "date",
                    value_column: "wti_price",
                }
            )

            price_df["date"] = pd.to_datetime(price_df["date"], errors="coerce")
            price_df["wti_price"] = pd.to_numeric(price_df["wti_price"], errors="coerce")

            price_df = price_df.dropna(subset=["date", "wti_price"])

            start_date_dt = pd.to_datetime(start_date)
            end_date_dt = pd.to_datetime(end_date)

            price_df = price_df[
                (price_df["date"] >= start_date_dt)
                & (price_df["date"] < end_date_dt)
            ].copy()

            if price_df.empty:
                raise ValueError(
                    "No WTI price data remained after filtering by date range."
                )

            price_df = price_df.sort_values("date")

            save_dataframe(price_df, output_file)

            return price_df

        except Exception as error:
            last_error = error
            wait_seconds = 10 * attempt
            print(f"Failed to download WTI price data: {error}")
            print(f"Waiting {wait_seconds} seconds before retry...")
            time.sleep(wait_seconds)

    if output_file.exists():
        print("Online WTI price download failed.")
        print(f"Using existing local file instead: {output_file}")

        local_df = pd.read_csv(output_file)
        print(f"Loaded local WTI price data. Rows: {len(local_df)}")

        return local_df

    raise RuntimeError(
        f"Failed to download WTI price data and no local fallback file exists. "
        f"Last error: {last_error}"
    )


def main() -> None:
    """
    Run data collection tasks.

    In the current version:
    - EIA RSS news is collected online.
    - WTI price data is loaded from the local CSV file.
    """
    print("Starting data collection...")

    collect_eia_news()

    local_wti_file = RAW_DATA_DIR / "wti_price.csv"

    if local_wti_file.exists():
        wti_df = pd.read_csv(local_wti_file)
        print(f"Using local WTI price data: {local_wti_file}")
        print(f"WTI price rows: {len(wti_df)}")
    else:
        raise FileNotFoundError(
            "Local WTI price file not found. Please create data/raw/wti_price.csv first."
        )

    print("Data collection finished.")


if __name__ == "__main__":
    main()