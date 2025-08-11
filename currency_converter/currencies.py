# ISO 4217 currency list (common + ECB supported). Extend as needed.
CURRENCIES = {
    "EUR": "Euro",
    "USD": "US Dollar",
    "GBP": "British Pound",
    "JPY": "Japanese Yen",
    "AUD": "Australian Dollar",
    "CAD": "Canadian Dollar",
    "CHF": "Swiss Franc",
    "CNY": "Chinese Yuan",
    "SEK": "Swedish Krona",
    "NZD": "New Zealand Dollar",
    "MXN": "Mexican Peso",
    "SGD": "Singapore Dollar",
    "HKD": "Hong Kong Dollar",
    "NOK": "Norwegian Krone",
    "KRW": "South Korean Won",
    "TRY": "Turkish Lira",
    "INR": "Indian Rupee",
    "RUB": "Russian Ruble",
    "ZAR": "South African Rand",
    "BRL": "Brazilian Real",
    "DKK": "Danish Krone",
    "PLN": "Polish Zloty",
    "TWD": "New Taiwan Dollar",
    "THB": "Thai Baht",
    "MYR": "Malaysian Ringgit",
    "IDR": "Indonesian Rupiah",
    "CZK": "Czech Koruna",
    "HUF": "Hungarian Forint",
    "ILS": "Israeli New Shekel",
    "PHP": "Philippine Peso",
    "AED": "United Arab Emirates Dirham",
    "SAR": "Saudi Riyal",
    "RON": "Romanian Leu",
    "BGN": "Bulgarian Lev",
    "HRK": "Croatian Kuna",
    "ISK": "Icelandic Krona",
}

def sorted_currency_codes():
    return sorted(CURRENCIES.keys())

def describe(code: str) -> str:
    name = CURRENCIES.get(code, "Unknown")
    return f"{code} - {name}"
