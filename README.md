# Currency Converter (GUI)

A simple, universal currency converter desktop app with an interactive Tkinter GUI.

- Live exchange rates from European Central Bank (ECB) with fallback providers.
- Offline-friendly: caches the last successful rates locally.
- Searchable dropdowns with keyboard navigation.
- Precise decimal math; auto-updates when amount or currencies change.

## Requirements

- Python 3.9+

Optional (only for development):
- pytest (for tests)

## Quick start (Windows PowerShell)

```powershell
# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Run the app
python -m currency_converter
```

The GUI should open. Type an amount, pick From/To currencies, and see the converted value instantly.

## Project structure

```
currency_converter/
  __init__.py
  __main__.py         # python -m currency_converter launches the app
  app.py              # Tkinter GUI
  rates.py            # Rate fetching + caching
  currencies.py       # ISO currency list + helpers
  version.py

tests/
  test_rates.py       # Minimal sanity tests for rate math

rates_cache.json      # Stored after first successful fetch
```

## Notes

- Rates are base EUR from ECB; we convert between any two currencies via EUR.
- If online fetching fails, we use the cached rates if available.
- Precision uses Decimal with quantization to 4 fractional digits (configurable in `rates.py`).

## Troubleshooting

- If SSL errors occur, ensure your Python has up-to-date certificates.
- If the app can't fetch rates, you can still convert using the last cached rates.

## License

MIT
