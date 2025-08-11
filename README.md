# Currency Converter (Web UI)

A simple, modern currency converter with a sleek browser-based UI (no Tkinter).

- Live exchange rates from European Central Bank (ECB) with fallback providers.
- Offline-friendly: caches the last successful rates locally.
- Fast, responsive UI with instant updates as you type.
- Precise decimal math; configurable precision.

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

# Or visit manually if it didn't open: http://127.0.0.1:5000
```

The web UI should open in your default browser. Type an amount, pick From/To currencies, and see the converted value instantly.

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
