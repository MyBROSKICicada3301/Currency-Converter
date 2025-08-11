# Currency Converter (Web UI)

A comprehensive currency converter with a modern browser-based UI featuring 150+ currencies with flag emojis.

- **150+ currencies**: Complete ISO 4217 support with flag emojis for easy identification
- Live exchange rates from European Central Bank (ECB) with fallback providers
- Offline-friendly: caches the last successful rates locally
- Fast, responsive UI with instant updates and animated currency symbols
- Precise decimal math with configurable precision

## Requirements

- Python 3.9+

Optional (only for development):
- pytest (for tests)

## Quick start (Windows PowerShell)

```powershell
# Create and activate a virtual environment
python -m venv .venv
 .\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the app (opens your browser)
python -m currency_converter
```

The web UI opens in your default browser with a searchable list of 150+ currencies, each with its flag emoji for easy identification.

## Features

- **Comprehensive currency support**: 150+ currencies including major world currencies, regional currencies, and precious metals
- **Visual identification**: Flag emojis for each currency make selection intuitive
- **Animated background**: Floating currency symbols ($, €, £, ¥, etc.) with smooth animations
- **Real-time conversion**: Updates as you type with debounced API calls
- **Modern UI**: Dark theme, responsive design, and accessibility features
- **Offline capability**: Caches exchange rates for continued use without internet

## Supported Currencies

The app includes all major ISO 4217 currencies organized by region:
- **Major**: USD 🇺🇸, EUR 🇪🇺, GBP 🇬🇧, JPY 🇯🇵, AUD 🇦🇺, CAD 🇨🇦, CHF 🇨🇭, CNY 🇨🇳
- **Europe**: All EU currencies plus regional ones (SEK, NOK, RUB, TRY, etc.)
- **Asia Pacific**: Complete coverage including emerging markets
- **Middle East & Africa**: Regional currencies with proper flag representation
- **Americas**: North, Central, and South American currencies
- **Precious Metals**: XAU (Gold), XAG (Silver), XPT (Platinum), XPD (Palladium)

## Project structure

```
currency_converter/
  __init__.py
  __main__.py         # python -m currency_converter launches the web server
  app.py              # Flask app serving the web UI + JSON API
  rates.py            # Rate fetching + caching
  currencies.py       # ISO currency list + helpers
  version.py

tests/
  test_rates.py       # Minimal sanity tests for rate math

rates_cache.json      # Stored after first successful fetch
```

## API

The server exposes a small JSON API:

- GET `/api/currencies` → `{ currencies: [{ code, name }] }`
- GET `/api/convert?amount=1.23&src=USD&dst=EUR` → `{ amount, src, dst, converted, formatted_amount, formatted_converted }`
- POST `/api/refresh` → `{ status: "refreshing" }` (reloads rates in background)

## Notes

- Rates are base EUR from ECB; we convert between any two currencies via EUR.
- If online fetching fails, we use the cached rates if available.
- Precision uses Decimal with quantization to 4 fractional digits (configurable in `rates.py`).

## Troubleshooting

- If SSL errors occur, ensure your Python has up-to-date certificates.
- If the app can't fetch rates, you can still convert using the last cached rates.

## License

MIT
