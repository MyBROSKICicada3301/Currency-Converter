from __future__ import annotations

import json
import time
from dataclasses import dataclass
from decimal import Decimal, getcontext, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, Optional

import urllib.request
import urllib.error

# Precision settings
getcontext().prec = 28

CACHE_FILE = Path(__file__).resolve().parent.parent / "rates_cache.json"
CACHE_TTL_SECONDS = 60 * 60  # 1 hour
DECIMAL_PLACES = 4

ECB_RATES_URL = "https://api.exchangerate.host/latest?base=EUR"
# Fallback provider (same API family)
FALLBACK_URL = "https://open.er-api.com/v6/latest/EUR"

@dataclass
class Rates:
    base: str
    rates: Dict[str, Decimal]
    timestamp: int

    def convert(self, amount: Decimal, src: str, dst: str) -> Decimal:
        if src == dst:
            return amount
        # Convert via base (EUR)
        if src == self.base:
            eur_amount = amount
        else:
            src_rate = self.rates.get(src)
            if src_rate is None or src_rate == 0:
                raise ValueError(f"Unknown or invalid source currency: {src}")
            eur_amount = amount / src_rate
        if dst == self.base:
            return eur_amount
        dst_rate = self.rates.get(dst)
        if dst_rate is None or dst_rate == 0:
            raise ValueError(f"Unknown or invalid destination currency: {dst}")
        return eur_amount * dst_rate


def _fetch_json(url: str) -> Optional[dict]:
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            if resp.status != 200:
                return None
            data = resp.read()
            return json.loads(data.decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None


def fetch_latest_rates() -> Rates:
    # Try primary provider
    data = _fetch_json(ECB_RATES_URL)
    if data and "rates" in data and data.get("base") == "EUR":
        rates = {k: Decimal(str(v)) for k, v in data["rates"].items()}
        ts = int(time.time())
        return Rates(base="EUR", rates=rates, timestamp=ts)

    # Try fallback provider format
    data2 = _fetch_json(FALLBACK_URL)
    if data2 and data2.get("result") == "success" and data2.get("base_code") == "EUR":
        rates = {k: Decimal(str(v)) for k, v in data2.get("rates", {}).items()}
        ts = int(time.time())
        return Rates(base="EUR", rates=rates, timestamp=ts)

    raise RuntimeError("Failed to fetch latest rates from all providers")


def load_cached_rates() -> Optional[Rates]:
    if not CACHE_FILE.exists():
        return None
    try:
        raw = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        rates = {k: Decimal(str(v)) for k, v in raw.get("rates", {}).items()}
        return Rates(base=raw.get("base", "EUR"), rates=rates, timestamp=raw.get("timestamp", 0))
    except Exception:
        return None


def save_cached_rates(r: Rates) -> None:
    payload = {
        "base": r.base,
        "rates": {k: float(v) for k, v in r.rates.items()},
        "timestamp": r.timestamp,
    }
    try:
        CACHE_FILE.write_text(json.dumps(payload), encoding="utf-8")
    except Exception:
        pass


def get_rates(use_cache: bool = True) -> Rates:
    # Use fresh cache if valid
    if use_cache:
        cached = load_cached_rates()
        if cached and (int(time.time()) - cached.timestamp) < CACHE_TTL_SECONDS:
            return cached
    # Fetch; on success, cache; on failure, fallback to any cache
    try:
        latest = fetch_latest_rates()
        save_cached_rates(latest)
        return latest
    except Exception:
        cached = load_cached_rates()
        if cached:
            return cached
        raise


def format_decimal(value: Decimal, places: int = DECIMAL_PLACES) -> str:
    q = Decimal(10) ** -places
    return str(value.quantize(q, rounding=ROUND_HALF_UP))
