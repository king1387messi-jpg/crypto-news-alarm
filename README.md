# Daily Crypto Digest Bot

Sends a short daily Telegram digest at 16:00 (UTC+3:30), weekdays only:
BTC/ETH price + 24h change, RSI, 3-SMA trend status, BTC.D, USDT.D,
ATR risk flag, top 5 filtered news headlines.

## Setup

1. Create a Telegram bot via @BotFather and get the token.
2. Get your chat id via @userinfobot.
3. Sign up at cryptopanic.com for a free API key.
4. Copy `.env.example` to `.env` and fill in the values.
5. Install deps: `pip install -r requirements.txt`
6. Test locally: `python bot.py`
7. Push to a GitHub repo, add the three values as repository Secrets
   (Settings -> Secrets and variables -> Actions), and enable Actions.

## Notes

- CoinGecko / Binance public endpoints are used; no keys needed.
- If Telegram creds are missing, the digest is printed to stdout instead.
- ATR ratio > 1.5x flags reduced risk (0.25%) per your trading plan.
- SMAs tangled -> no trend trades today warning.
