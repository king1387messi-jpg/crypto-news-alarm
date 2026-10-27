"""Daily crypto digest bot: fetch prices/indicators/news, send to Telegram."""


import os
import sys
import time
import requests
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import indicators
import news

COINGECKO = "https://api.coingecko.com/api/v3"
BINANCE = "https://api.binance.com/api/v3"


def cg_get(path, params=None, retries=3):
    headers = dict(config.HEADERS)
    if getattr(config, "COINGECKO_KEY", None):
        headers["x-cg-demo-api-key"] = config.COINGECKO_KEY
    for attempt in range(retries):
        try:
            r = requests.get(f"{COINGECKO}{path}", params=params or {}, headers=headers, timeout=15)
            if r.status_code == 429:
                wait = 6 * (attempt + 1)
                print(f"CoinGecko 429, waiting {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError:
            if attempt == retries - 1:
                raise
            time.sleep(6 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {path}")


def fetch_global():
    try:
        return cg_get("/global").get("data", {})
    except Exception as e:
        print(f"Global fetch failed: {e}")
        return {}


def fetch_usdt_dominance(total_mcap_usd):
    try:
        time.sleep(2)
        coin = cg_get("/coins/tether", {
            "localization": "false", "tickers": "false",
            "market_data": "true", "community_data": "false",
            "developer_data": "false",
        })
        usdt_mcap = coin["market_data"]["market_cap"]["usd"]
        return usdt_mcap / total_mcap_usd * 100.0
    except Exception as e:
        print(f"USDT.D fetch failed: {e}")
        return None


def fetch_klines(symbol, interval="1d", limit=None):
    limit = limit or config.KLINES_LIMIT
    r = requests.get(f"{BINANCE}/klines", params={
        "symbol": symbol, "interval": interval, "limit": limit,
    }, headers=config.HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()
    highs = [float(x[2]) for x in data]
    lows = [float(x[3]) for x in data]
    closes = [float(x[4]) for x in data]
    return highs, lows, closes


def sma_status(closes):
    return indicators.sma_status(closes)


def build_message():
    # Prices from Binance (avoid CoinGecko rate limits)
    def binance_24h(symbol):
        r = requests.get(f"{BINANCE}/ticker/24hr", params={"symbol": symbol}, headers=config.HEADERS, timeout=15)
        r.raise_for_status()
        d = r.json()
        return float(d["lastPrice"]), float(d["priceChangePercent"])

    g = fetch_global()
    time.sleep(2)
    btc_d = g.get("market_cap_percentage", {}).get("btc") if g else None
    total_mcap = g.get("total_market_cap", {}).get("usd", 0) if g else 0
    usdt_d = fetch_usdt_dominance(total_mcap) if total_mcap else None

    # local time UTC+3:30
    now = datetime.now(timezone(timedelta(hours=3, minutes=30)))
    lines = [f"Crypto Digest - {now.strftime('%d %b %H:%M')} (UTC+3:30)", ""]

    asset_map = [("BTC", "BTCUSDT"), ("ETH", "ETHUSDT")]
    statuses = {}
    atr_ratio_val = None

    for sym, b_sym in asset_map:
        p, ch = binance_24h(b_sym)
        arrow = "+" if ch >= 0 else ""
        highs, lows, closes = fetch_klines(b_sym)
        r = indicators.rsi(closes)
        status = sma_status(closes)
        statuses[sym] = status
        atr_r = indicators.atr_ratio(highs, lows, closes)
        if sym == "BTC":
            atr_ratio_val = atr_r
        rsi_str = f"{r:.0f}" if r is not None else "n/a"
        lines.append(f"{sym}  ${p:,.0f}  ({ch:+.1f}%)  RSI {rsi_str}  | {status}")

    parts = []
    parts.append(f"BTC.D {btc_d:.1f}%" if btc_d is not None else "BTC.D n/a")
    if usdt_d is not None:
        parts.append(f"USDT.D {usdt_d:.1f}%")
    else:
        parts.append("USDT.D n/a")
    lines.append("  |  ".join(parts))

    if atr_ratio_val is not None:
        if atr_ratio_val > config.ATR_RISK_THRESHOLD:
            lines.append(f"ATR ratio {atr_ratio_val:.1f}x -> reduce risk to 0.25% !")
        else:
            lines.append(f"ATR ratio {atr_ratio_val:.1f}x -> normal risk (0.5%)")

    lines.append("")

    # News
    items = []
    if config.CRYPTOPANIC_KEY:
        items += news.fetch_cryptopanic(config.CRYPTOPANIC_KEY, config.CRYPTO_CURRENCIES)
    items += news.fetch_rss(config.RSS_FEEDS)
    filtered = news.filter_news(items, config.KEYWORDS)
    if filtered:
        lines.append("News:")
        for it in filtered:
            lines.append(f"- {it['title']}")
        lines.append("")

    # Warnings
    if "tangled" in statuses.get("ETH", ""):
        lines.append("WARN: ETH SMAs tangled -> skip alt longs today")
    if "tangled" in statuses.get("BTC", ""):
        lines.append("WARN: BTC SMAs tangled -> no trend trades today")

    return "\n".join(lines).strip()


def send_telegram(text):
    token = config.TELEGRAM_TOKEN
    chat = config.TELEGRAM_CHAT_ID
    if not token or not chat:
        print("Missing Telegram creds; printing digest instead:")
        print(text)
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    r = requests.post(url, json={"chat_id": chat, "text": text}, timeout=15)
    r.raise_for_status()


if __name__ == "__main__":
    msg = build_message()
    print(msg)
    send_telegram(msg)
