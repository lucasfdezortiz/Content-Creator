"""
Orchestrates chart generation for the daily Substack content pipeline.
Reads today's cached news, picks the most relevant charts, generates HTML files,
and prints file:// URLs for browser capture.
"""
import json
import sys
import os
from pathlib import Path

from config import CACHE_FILE
from chart_generator import generate_chart_for_text, generate_daily_charts


def pick_topics_from_cache() -> list[str]:
    if not os.path.exists(CACHE_FILE):
        return []
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items", [])
    # Use top 9 items: titles + first 100 chars of summary
    topics = []
    for item in items[:9]:
        topics.append(item.get("title", "") + " " + item.get("summary", "")[:100])
    return topics


def main():
    topics = pick_topics_from_cache()
    if not topics:
        print("No cache found — run fetch_content.py first.", file=sys.stderr)
        sys.exit(1)

    # Deduplicate chart functions (multiple topics may map to same chart)
    seen_urls = set()
    charts = []
    for topic in topics:
        url, label = generate_chart_for_text(topic)
        if url and url not in seen_urls:
            seen_urls.add(url)
            charts.append((label, url))

    print("=" * 65)
    print("  GRÁFICAS GENERADAS (TradingView Lightweight Charts)")
    print("=" * 65)
    for i, (label, url) in enumerate(charts, 1):
        print(f"\n  [{i}] {label}")
        print(f"      {url}")
    print()
    print(f"  Total: {len(charts)} gráficas — abrir en navegador para capturar")
    print("=" * 65)


if __name__ == "__main__":
    main()
