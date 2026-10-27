"""News fetching: CryptoPanic API + RSS feeds, filtered & deduped."""


import requests
import feedparser

from config import KEYWORDS, RSS_FEEDS, HEADERS, CRYPTOPANIC_KEY


def fetch_cryptopanic(api_key, currencies="BTC,ETH"):
    if not api_key:
        return []
    url = "https://cryptopanic.com/api/v1/posts/"
    params = {
        "auth_token": api_key,
        "currencies": currencies,
        "kind": "news",
        "filter": "important",
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        out = []
        for p in data.get("results", [])[:25]:
            out.append({"title": p.get("title", ""), "url": p.get("url", ""), "source": "CryptoPanic"})
        return out
    except Exception as e:
        print(f"CryptoPanic fetch failed: {e}")
        return []


def fetch_rss(feeds=None):
    feeds = feeds or RSS_FEEDS
    out = []
    for feed_url in feeds:
        try:
            d = feedparser.parse(feed_url)
            for e in d.entries[:12]:
                out.append({"title": e.get("title", ""), "url": e.get("link", ""), "source": feed_url})
        except Exception as e:
            print(f"RSS fetch failed ({feed_url}): {e}")
    return out


def filter_news(items, keywords=None):
    keywords = [k.lower() for k in (keywords or KEYWORDS)]
    seen = set()
    out = []
    for it in items:
        title = it.get("title", "")
        if not title:
            continue
        low = title.lower()
        if not any(k in low for k in keywords):
            continue
        key = low[:70]
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
        if len(out) >= 5:
            break
    return out
