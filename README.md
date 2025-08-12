# Currency Converter (Web UI)

A modern, self-contained currency converter with automatic dependency installation featuring 77 Yahoo Finance validated currencies and real-time exchange rates.

- **🚀 Zero Setup**: Automatic dependency installation - just run and go!
- **🏦 77 Validated Currencies**: Only Yahoo Finance API supported currencies for reliable data
- **💰 Real-time Rates**: Yahoo Finance API with ECB and Open Exchange Rates fallbacks
- **📱 Modern UI**: Clean, responsive interface with animated currency symbols
- **⚡ Fast & Offline**: Smart caching with 1-hour refresh and offline capability
- **🎯 Professional**: Clean currency descriptions without emoji clutter

## Features

- **🔧 Automatic Setup**: Dependencies install automatically when you run the app
- **🌐 Yahoo Finance Primary**: Real-time exchange rates from Yahoo Finance API
- **🛡️ Reliable Fallbacks**: ECB and Open Exchange Rates APIs ensure availability  
- **💵 USD Base Currency**: USD-based rates for optimal global coverage
- **📊 77 Active Currencies**: Curated list of working Yahoo Finance currency pairs
- **💾 Smart Caching**: 1-hour cache with automatic refresh and offline fallback
- **🎨 Modern Interface**: Dark theme, responsive design, accessibility features
- **⚡ Real-time Updates**: Live conversion as you type with optimized debouncing

## Requirements

- Python 3.9+ (Python 3.13+ recommended)
- Internet connection (for initial dependency installation and rate fetching)

**No manual dependency installation required!** The app automatically installs:
- Flask (web framework)
- yfinance (Yahoo Finance API)  
- requests (HTTP client)

## Quick start (Windows PowerShell)

**🎯 Super Simple (Automatic Dependencies):**
```powershell
# Just run the app - it will install dependencies automatically!
python run.py
```

**📦 Traditional Method:**
```powershell
# Create and activate a virtual environment (optional)
python -m venv .venv
 .\.venv\Scripts\Activate.ps1

# Install dependencies manually
pip install -r requirements.txt

# Run the app
python -m currency_converter
```

**💻 Direct Execution:**
```powershell
# Run the app.py file directly (also auto-installs dependencies)
python currency_converter/app.py
```

The web UI opens automatically in your default browser with a searchable list of 77 Yahoo Finance validated currencies, each with clean, professional descriptions.

## Supported Currencies

The app includes **77 Yahoo Finance validated currencies** organized by region:

### 🌟 **Major Currencies (8)**
USD 🇺🇸, EUR 🇪🇺, GBP 🇬🇧, JPY 🇯🇵, AUD 🇦🇺, CAD 🇨🇦, CHF 🇨🇭, CNY 🇨🇳

### 🇪🇺 **European Currencies (13)**  
SEK, NOK, DKK, PLN, CZK, HUF, RON, BGN, HRK, ISK, RUB, TRY

### 🌏 **Asia-Pacific Currencies (18)**
KRW, INR, SGD, HKD, TWD, THB, MYR, IDR, PHP, VND, NZD, PKR, BDT, LKR, MMK, KHR, LAK, NPR, BTN, MVR

### 🕌 **Middle Eastern Currencies (10)**
SAR, AED, QAR, OMR, KWD, BHD, JOD, ILS, EGP, LBP

### 🌍 **African Currencies (12)**
ZAR, NGN, GHS, KES, UGX, TZS, ETB, MAD, TND, DZD, XOF, XAF

### 🌎 **American Currencies (16)**
MXN, BRL, ARS, CLP, COP, PEN, UYU, BOB, PYG, VEF, GYD, SRD, AWG, BBD, BZD, BMD, KYD, XCD

*All currencies are tested and validated to work reliably with the Yahoo Finance API.*

## Project Structure

```
Currency-Converter/
├── run.py                     # 🚀 Simple launcher with auto-install
├── requirements.txt           # 📦 Package dependencies  
├── rates_cache.json          # 💾 Cached exchange rates
├── README.md                  # 📖 This file
├── currency_converter/
│   ├── __init__.py
│   ├── __main__.py           # python -m currency_converter
│   ├── app.py                # 🌐 Flask web app + auto-install
│   ├── currencies.py         # 💱 77 validated currencies
│   ├── rates.py              # 📈 Yahoo Finance rate fetching
│   └── version.py            # 🏷️ App version
└── tests/
    ├── test_rates.py         # ✅ Rate conversion tests
    └── test_yahoo_rates.py   # ✅ Yahoo Finance API tests
```

## API Endpoints

The web application exposes a clean JSON API:

- **GET** `/api/currencies` → List all supported currencies
  ```json
  { "currencies": [{ "code": "USD", "name": "US Dollar" }, ...] }
  ```

- **GET** `/api/convert?amount=100&src=USD&dst=EUR` → Convert currency  
  ```json
  { 
    "amount": 100, "src": "USD", "dst": "EUR", 
    "converted": 85.23, 
    "formatted_amount": "100.0000", 
    "formatted_converted": "85.2300" 
  }
  ```

- **POST** `/api/refresh` → Refresh exchange rates
  ```json
  { "status": "refreshing" }
  ```

## Technical Details

- **🏦 Primary Source**: Yahoo Finance API for real-time rates
- **🛡️ Fallback Sources**: ECB API and Open Exchange Rates  
- **💰 Base Currency**: USD for optimal currency pair coverage
- **🎯 Precision**: Decimal arithmetic with 4 decimal places
- **⏰ Cache Duration**: 1 hour for optimal performance
- **🔄 Auto-refresh**: Background rate updates every hour
- **📱 Responsive**: Works on desktop, tablet, and mobile
- **🎨 Animations**: Floating currency symbols background

## Troubleshooting

### 🔧 **Common Issues**

**Dependencies won't install automatically:**
```powershell
# Manual installation fallback
pip install flask yfinance requests
```

**Can't access the web interface:**
- Check that the app shows "Running on http://127.0.0.1:5000"
- Try opening http://localhost:5000 instead
- Ensure no other service is using port 5000

**Exchange rates not updating:**
- Check your internet connection
- The app will use cached rates if APIs are unavailable
- Try the `/api/refresh` endpoint to force update

**SSL/Certificate errors:**
- Update your Python installation
- Try: `pip install --upgrade certifi`

### 💡 **Performance Tips**

- The app caches rates for 1 hour - this is optimal for most use cases
- Background rate updates won't interrupt your usage
- Offline mode works with previously cached rates
- Modern browsers cache the web UI for faster loading

## Development

### Running Tests
```powershell
# Install pytest for testing
pip install pytest

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_rates.py -v
```

### Project Philosophy

This Currency Converter prioritizes **reliability and user experience**:

- ✅ **Curated currency list**: Only Yahoo Finance validated currencies
- ✅ **Zero-friction setup**: Automatic dependency installation  
- ✅ **Professional UI**: Clean descriptions without emoji clutter
- ✅ **Robust error handling**: Graceful fallbacks and helpful messages
- ✅ **Modern architecture**: Clean separation of concerns
- ✅ **Comprehensive testing**: Reliable rate conversion logic

## License

MIT License - Feel free to use this project for personal or commercial purposes.

---

**🚀 Ready to get started?** Just run `python run.py` and your currency converter will be up and running in seconds!
