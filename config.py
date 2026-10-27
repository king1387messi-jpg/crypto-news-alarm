import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CRYPTOPANIC_KEY = os.getenv("CRYPTOPANIC_KEY")
COINGECKO_KEY = os.getenv("COINGECKO_KEY")  # optional, free demo key

# CryptoPanic currencies filter
CRYPTO_CURRENCIES = "BTC,ETH"

# News keyword filter (English only)
KEYWORDS = [
    "bitcoin", "ethereum", "btc", "eth", "crypto",
    "dominance", "btc.d", "usdt.d", "etf", "sec",
    "opec", "oil", "energy", "gas", "fed", "inflation",
    "halving", "whale", "liquidation",
]

RSS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://theblock.co/rss.xml",
]

ATR_RISK_THRESHOLD = 1.5
SMA_PERIODS = (20, 50, 200)
KLINES_LIMIT = 250
USER_AGENT = "crypto-digest-bot/1.0"
HEADERS = {"User-Agent": USER_AGENT}
