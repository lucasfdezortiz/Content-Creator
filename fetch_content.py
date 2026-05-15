import sys
import json
import argparse
import os
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from config import (
    RSS_SOURCES, RESEARCH_SOURCES, RESEARCH_BOOST,
    REDDIT_SUBREDDITS, REDDIT_MIN_SCORE,
    KEYWORDS_HIGH, KEYWORDS_MED, FOCUS_KEYWORDS,
    HEADERS, REDDIT_HEADERS,
    DATA_DIR, CACHE_FILE, CACHE_TTL_HOURS, TOP_ITEMS,
)


def _fetch_rss(source_name: str, url: str) -> list:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "xml")
        out = []
        for item in soup.find_all("item"):
            title   = item.find("title")
            link    = item.find("link")
            desc    = item.find("description") or item.find("summary")
            pubdate = item.find("pubDate") or item.find("dc:date")
            if not title:
                continue
            summary_text = ""
            if desc:
                raw = desc.get_text()
                summary_text = BeautifulSoup(raw, "lxml").get_text(strip=True)[:400]
            out.append({
                "title":    title.get_text(strip=True),
                "url":      link.get_text(strip=True) if link else "",
                "summary":  summary_text,
                "source":   source_name,
                "pub_date": pubdate.get_text(strip=True) if pubdate else "",
                "reddit_score": 0,
            })
        return out
    except Exception:
        return []


def _fetch_expansion() -> list:
    try:
        r = requests.get("https://www.expansion.com", headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        seen = set()
        for tag in soup.find_all(["h2", "h3", "h4"]):
            text = tag.get_text(strip=True)
            if len(text) < 30 or text in seen:
                continue
            seen.add(text)
            a    = tag.find("a", href=True) or tag.find_parent("a", href=True)
            href = ""
            if a:
                href = a["href"]
                if href.startswith("/"):
                    href = "https://www.expansion.com" + href
            out.append({
                "title": text, "url": href, "source": "Expansión",
                "summary": "", "pub_date": "", "reddit_score": 0,
            })
            if len(out) >= 12:
                break
        return out
    except Exception:
        return []


def _fetch_el_economista() -> list:
    try:
        r = requests.get("https://www.eleconomista.es/mercados-cotizaciones/", headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        seen = set()
        for tag in soup.find_all(["h2", "h3", "h4"]):
            text = tag.get_text(strip=True)
            if len(text) < 30 or text in seen:
                continue
            seen.add(text)
            a    = tag.find("a", href=True) or tag.find_parent("a", href=True)
            href = ""
            if a:
                href = a["href"]
                if href.startswith("/"):
                    href = "https://www.eleconomista.es" + href
            out.append({
                "title": text, "url": href, "source": "El Economista",
                "summary": "", "pub_date": "", "reddit_score": 0,
            })
            if len(out) >= 10:
                break
        return out
    except Exception:
        return []


def _fetch_research(institution: str, url: str) -> list:
    """Scrape public insights/research pages from major financial institutions."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        seen = set()

        # Try article/card patterns first (modern CMS layouts)
        candidates = []
        for tag in soup.find_all(["article", "div"], class_=lambda c: c and any(
            kw in c.lower() for kw in ["card", "insight", "article", "post", "item", "teaser", "feature"]
        )):
            heading = tag.find(["h1", "h2", "h3", "h4"])
            if heading:
                candidates.append((heading, tag))

        # Fallback: bare headings
        if not candidates:
            for tag in soup.find_all(["h2", "h3", "h4"]):
                candidates.append((tag, tag))

        for heading, container in candidates:
            text = heading.get_text(strip=True)
            if len(text) < 25 or text in seen:
                continue
            # Skip navigation / boilerplate
            if any(skip in text.lower() for skip in ["cookie", "privacy", "log in", "sign in", "subscribe", "menu", "search"]):
                continue
            seen.add(text)

            # Try to find a link
            a = heading.find("a", href=True) or container.find("a", href=True)
            href = ""
            if a:
                href = a["href"]
                if href.startswith("/"):
                    href = url.split("/")[0] + "//" + url.split("/")[2] + href

            # Try to find a summary/description
            summary = ""
            for p in container.find_all("p"):
                p_text = p.get_text(strip=True)
                if len(p_text) > 40:
                    summary = p_text[:300]
                    break

            out.append({
                "title":        text,
                "url":          href,
                "summary":      summary,
                "source":       institution,
                "pub_date":     "",
                "reddit_score": 0,
                "is_research":  True,   # flag for scoring boost
            })
            if len(out) >= 8:
                break
        return out
    except Exception:
        return []


def _fetch_all_research() -> list:
    items = []
    for institution, url in RESEARCH_SOURCES.items():
        items += _fetch_research(institution, url)
    return items


def _fetch_reddit(subreddit: str) -> list:
    try:
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=15"
        r = requests.get(url, headers=REDDIT_HEADERS, timeout=10)
        r.raise_for_status()
        posts = r.json()["data"]["children"]
        out = []
        for post in posts:
            d = post["data"]
            if d.get("score", 0) < REDDIT_MIN_SCORE:
                continue
            if d.get("stickied") or d.get("is_video"):
                continue
            out.append({
                "title":        d.get("title", ""),
                "url":          d.get("url", ""),
                "summary":      d.get("selftext", "")[:300],
                "source":       f"Reddit r/{subreddit}",
                "pub_date":     "",
                "reddit_score": d.get("score", 0),
            })
        return out
    except Exception:
        return []


def _fetch_all_reddit() -> list:
    items = []
    for sub in REDDIT_SUBREDDITS:
        items += _fetch_reddit(sub)
    return items


def _deduplicate(items: list) -> list:
    seen, unique = [], []
    for item in items:
        words = set(item["title"].lower().split())
        if len(words) < 3:
            continue
        is_dup = any(
            len(words & s) / max(len(words | s), 1) > 0.55
            for s in seen
        )
        if not is_dup:
            seen.append(words)
            unique.append(item)
    return unique


def _score_and_sort(items: list, focus: str = None) -> list:
    focus_kws = FOCUS_KEYWORDS.get(focus, []) if focus else []
    for item in items:
        text  = (item["title"] + " " + item.get("summary", "")).lower()
        score = sum(2 for k in KEYWORDS_HIGH if k in text)
        score += sum(1 for k in KEYWORDS_MED if k in text)
        score += sum(3 for k in focus_kws if k in text)
        score += item.get("reddit_score", 0) // 500
        if item.get("is_research"):
            score += RESEARCH_BOOST
        item["relevance_score"] = score
    return sorted(items, key=lambda x: x.get("relevance_score", 0), reverse=True)


def _is_cache_valid() -> bool:
    if not os.path.exists(CACHE_FILE):
        return False
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        fetched_at = datetime.fromisoformat(data.get("fetched_at", "2000-01-01"))
        return datetime.now() - fetched_at < timedelta(hours=CACHE_TTL_HOURS)
    except Exception:
        return False


def fetch_all_content(force: bool = False, focus: str = None) -> dict:
    if not force and _is_cache_valid():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    print("  Fetching RSS feeds...", file=sys.stderr)
    items = []
    for name, url in RSS_SOURCES.items():
        items += _fetch_rss(name, url)

    print("  Fetching Expansión...", file=sys.stderr)
    items += _fetch_expansion()

    print("  Fetching El Economista...", file=sys.stderr)
    items += _fetch_el_economista()

    print("  Fetching Reddit...", file=sys.stderr)
    items += _fetch_all_reddit()

    print("  Fetching institutional research (GS, JPM, MS, BlackRock, PIMCO)...", file=sys.stderr)
    items += _fetch_all_research()

    items = _deduplicate(items)
    items = _score_and_sort(items, focus=focus)
    items = items[:TOP_ITEMS]

    result = {
        "fetched_at": datetime.now().isoformat(),
        "focus":      focus,
        "count":      len(items),
        "items":      items,
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--focus", default=None, choices=list(FOCUS_KEYWORDS.keys()))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    data = fetch_all_content(force=args.force, focus=args.focus)
    print(json.dumps(data, indent=2, ensure_ascii=False))
