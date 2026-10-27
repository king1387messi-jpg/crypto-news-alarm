"""Technical indicators: RSI, SMA, ATR."""


def sma(values, period):
    if len(values) < period or period <= 0:
        return None
    return sum(values[-period:]) / period


def rsi(closes, period=14):
    if len(closes) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0.0))
        losses.append(max(-d, 0.0))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def _true_ranges(highs, lows, closes):
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        trs.append(tr)
    return trs


def atr(highs, lows, closes, period=14):
    trs = _true_ranges(highs, lows, closes)
    if len(trs) < period:
        return None
    return sum(trs[-period:]) / period


def atr_ratio(highs, lows, closes, period=14, lookback=20):
    """Current ATR divided by average ATR over `lookback` periods."""
    trs = _true_ranges(highs, lows, closes)
    if len(trs) < period:
        return None
    cur = sum(trs[-period:]) / period
    # rolling ATR series
    atrs = []
    for i in range(period, len(trs) + 1):
        atrs.append(sum(trs[i - period:i]) / period)
    if not atrs:
        return None
    if len(atrs) >= lookback:
        avg = sum(atrs[-lookback:]) / lookback
    else:
        avg = sum(atrs) / len(atrs)
    if avg == 0:
        return None
    return cur / avg


def sma_status(closes):
    """Return trend label based on 20/50/200 SMA stack."""
    p = closes[-1]
    s20 = sma(closes, 20)
    s50 = sma(closes, 50)
    s200 = sma(closes, 200)
    if s20 is None or s50 is None:
        return "insufficient data"
    if s200 is None:
        # fallback: use available
        s200 = s50
    if p > s20 > s50 > s200:
        return "above 20/50/200 SMA ^"
    if p < s20 < s50 < s200:
        return "below 20/50/200 SMA v"
    return "SMAs tangled !"
