from __future__ import annotations

import json
import time
import requests
import yfinance as yf
from dataclasses import dataclass
from decimal import Decimal, getcontext, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, Optional, List

# Precision settings
getcontext().prec = 28

CACHE_FILE = Path(__file__).resolve().parent.parent / "rates_cache.json"
CACHE_TTL_SECONDS = 60 * 60  # 1 hour
DECIMAL_PLACES = 4

# Yahoo Finance base URL for currency conversion
YAHOO_FINANCE_BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"

# Major currency pairs for Yahoo Finance API
MAJOR_CURRENCIES = [
    "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "SEK", "NOK", 
    "DKK", "PLN", "CZK", "HUF", "RON", "BGN", "HRK", "ISK", "RUB", "TRY",
    "KRW", "INR", "SGD", "HKD", "TWD", "THB", "MYR", "IDR", "PHP", "VND",
    "NZD", "PKR", "BDT", "LKR", "MMK", "KHR", "LAK", "NPR", "BTN", "MVR",
    "SAR", "AED", "QAR", "OMR", "KWD", "BHD", "JOD", "ILS", "EGP", "LBP",
    "ZAR", "NGN", "GHS", "KES", "UGX", "TZS", "ETB", "MAD", "TND", "DZD",
    "XOF", "XAF", "MXN", "BRL", "ARS", "CLP", "COP", "PEN", "UYU", "BOB",
    "PYG", "VEF", "GYD", "SRD", "AWG", "BBD", "BZD", "BMD", "KYD", "XCD"
]

@dataclass 
class Rates:
    base: str
    rates: Dict[str, Decimal]
    timestamp: int

    def convert(self, amount: Decimal, src: str, dst: str) -> Decimal:
        if src == dst:
            return amount
        # Convert via base (USD for Yahoo Finance)
        if src == self.base:
            usd_amount = amount
        else:
            src_rate = self.rates.get(src)
            if src_rate is None or src_rate == 0:
                raise ValueError(f"Unknown or invalid source currency: {src}")
            usd_amount = amount / src_rate
        if dst == self.base:
            return usd_amount
        dst_rate = self.rates.get(dst)
        if dst_rate is None or dst_rate == 0:
            raise ValueError(f"Unknown or invalid destination currency: {dst}")
        return usd_amount * dst_rate


def _fetch_yahoo_rate(from_currency: str, to_currency: str) -> Optional[Decimal]:
    """Fetch exchange rate from Yahoo Finance API"""
    if from_currency == to_currency:
        return Decimal("1.0")
    
    try:
        # Create the currency pair symbol for Yahoo Finance
        symbol = f"{from_currency}{to_currency}=X"
        
        # Use yfinance to get the latest rate
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="1d")
        
        if not data.empty:
            # Get the latest close price
            latest_rate = data['Close'].iloc[-1]
            return Decimal(str(latest_rate))
            
        # Fallback: try direct API call to Yahoo Finance
        url = f"{YAHOO_FINANCE_BASE_URL}{symbol}"
        params = {
            "range": "1d",
            "interval": "1d",
            "indicators": "quote",
            "includeTimestamps": "false"
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            chart = data.get("chart", {})
            result = chart.get("result", [])
            if result:
                quotes = result[0].get("indicators", {}).get("quote", [])
                if quotes and quotes[0].get("close"):
                    close_prices = quotes[0]["close"]
                    # Get the last non-null price
                    for price in reversed(close_prices):
                        if price is not None:
                            return Decimal(str(price))
                            
    except Exception as e:
        print(f"Error fetching rate for {from_currency}/{to_currency}: {e}")
        return None
    
    return None


def fetch_yahoo_rates() -> Rates:
    """Fetch exchange rates from Yahoo Finance with USD as base currency"""
    rates = {"USD": Decimal("1.0")}  # USD is our base
    
    # Batch fetch major currencies to reduce API calls
    priority_currencies = ["EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "INR", "KRW", "SGD"]
    
    # Fetch priority currencies first
    for currency in priority_currencies:
        if currency == "USD":
            continue
            
        rate = _fetch_yahoo_rate("USD", currency)
        if rate is not None and rate > 0:
            rates[currency] = rate
        else:
            # Try reverse conversion (currency to USD) and invert
            reverse_rate = _fetch_yahoo_rate(currency, "USD")
            if reverse_rate is not None and reverse_rate > 0:
                rates[currency] = Decimal("1.0") / reverse_rate
    
    # Then fetch remaining currencies
    remaining_currencies = [c for c in MAJOR_CURRENCIES if c not in priority_currencies and c != "USD"]
    for currency in remaining_currencies:
        rate = _fetch_yahoo_rate("USD", currency)
        if rate is not None and rate > 0:
            rates[currency] = rate
        else:
            # Try reverse conversion (currency to USD) and invert
            reverse_rate = _fetch_yahoo_rate(currency, "USD")
            if reverse_rate is not None and reverse_rate > 0:
                rates[currency] = Decimal("1.0") / reverse_rate
    
    if len(rates) < 5:  # Ensure we have at least basic coverage
        raise RuntimeError(f"Failed to fetch sufficient currency rates from Yahoo Finance. Got {len(rates)} currencies.")
    
    print(f"Successfully fetched {len(rates)} currency rates from Yahoo Finance")
    return Rates(base="USD", rates=rates, timestamp=int(time.time()))


def _fetch_json_fallback(url: str) -> Optional[dict]:
    """Fallback to the original API providers"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def fetch_latest_rates() -> Rates:
    """Fetch latest rates with Yahoo Finance as primary, original APIs as fallback"""
    try:
        # Primary: Yahoo Finance API
        return fetch_yahoo_rates()
    except Exception as yahoo_error:
        print(f"Yahoo Finance API failed: {yahoo_error}")
        
        # Fallback 1: Original ECB API
        try:
            ECB_RATES_URL = "https://api.exchangerate.host/latest?base=EUR"
            data = _fetch_json_fallback(ECB_RATES_URL)
            if data and "rates" in data and data.get("base") == "EUR":
                rates = {k: Decimal(str(v)) for k, v in data["rates"].items()}
                ts = int(time.time())
                return Rates(base="EUR", rates=rates, timestamp=ts)
        except Exception as ecb_error:
            print(f"ECB API fallback failed: {ecb_error}")
        
        # Fallback 2: Open Exchange Rates API
        try:
            FALLBACK_URL = "https://open.er-api.com/v6/latest/EUR"
            data2 = _fetch_json_fallback(FALLBACK_URL)
            if data2 and data2.get("result") == "success" and data2.get("base_code") == "EUR":
                rates = {k: Decimal(str(v)) for k, v in data2.get("rates", {}).items()}
                ts = int(time.time())
                return Rates(base="EUR", rates=rates, timestamp=ts)
        except Exception as fallback_error:
            print(f"Open Exchange Rates fallback failed: {fallback_error}")

    raise RuntimeError("Failed to fetch latest rates from all providers (Yahoo Finance, ECB, Open Exchange Rates)")


def load_cached_rates() -> Optional[Rates]:
    """Load cached exchange rates from file"""
    if not CACHE_FILE.exists():
        return None
    try:
        raw = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        rates = {k: Decimal(str(v)) for k, v in raw.get("rates", {}).items()}
        return Rates(base=raw.get("base", "USD"), rates=rates, timestamp=raw.get("timestamp", 0))
    except Exception:
        return None


def save_cached_rates(r: Rates) -> None:
    """Save exchange rates to cache file"""
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
    """Get exchange rates with caching support"""
    # Use fresh cache if valid
    if use_cache:
        cached = load_cached_rates()
        if cached and (int(time.time()) - cached.timestamp) < CACHE_TTL_SECONDS:
            return cached
    
    # Fetch fresh rates; on success, cache; on failure, fallback to any cache
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
    """Format decimal with specified precision"""
    q = Decimal(10) ** -places
    return str(value.quantize(q, rounding=ROUND_HALF_UP))


def get_historical_data(from_currency: str, to_currency: str, period: str = "1mo") -> List[Dict]:
    """Get historical exchange rate data for charting"""
    try:
        if from_currency == to_currency:
            # Return flat line at 1.0 for same currency
            return [{"date": int(time.time()) * 1000, "rate": 1.0}]
        
        symbol = f"{from_currency}{to_currency}=X"
        ticker = yf.Ticker(symbol)
        
        # Get historical data
        data = ticker.history(period=period, interval="1d")
        
        if data.empty:
            return []
        
        # Convert to list of dictionaries for JSON response
        historical_data = []
        for index, row in data.iterrows():
            historical_data.append({
                "date": int(index.timestamp()) * 1000,  # Convert to milliseconds for JavaScript
                "rate": float(row['Close'])
            })
        
        return historical_data
        
    except Exception as e:
        print(f"Error fetching historical data for {from_currency}/{to_currency}: {e}")
        return []
