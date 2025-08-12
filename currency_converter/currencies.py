# -*- coding: utf-8 -*-
# Yahoo Finance validated currency list with flag emojis
# Only includes currencies that are confirmed to work with Yahoo Finance API
CURRENCIES = {
    # Major currencies
    "USD": {"name": "US Dollar", "flag": "🇺🇸"},
    "EUR": {"name": "Euro", "flag": "🇪🇺"},
    "GBP": {"name": "British Pound", "flag": "🇬🇧"},
    "JPY": {"name": "Japanese Yen", "flag": "🇯🇵"},
    "AUD": {"name": "Australian Dollar", "flag": "🇦🇺"},
    "CAD": {"name": "Canadian Dollar", "flag": "🇨🇦"},
    "CHF": {"name": "Swiss Franc", "flag": "🇨🇭"},
    "CNY": {"name": "Chinese Yuan", "flag": "🇨🇳"},
    
    # Europe
    "SEK": {"name": "Swedish Krona", "flag": "🇸🇪"},
    "NOK": {"name": "Norwegian Krone", "flag": "🇳🇴"},
    "DKK": {"name": "Danish Krone", "flag": "🇩🇰"},
    "PLN": {"name": "Polish Zloty", "flag": "🇵🇱"},
    "CZK": {"name": "Czech Koruna", "flag": "🇨🇿"},
    "HUF": {"name": "Hungarian Forint", "flag": "🇭🇺"},
    "RON": {"name": "Romanian Leu", "flag": "🇷🇴"},
    "BGN": {"name": "Bulgarian Lev", "flag": "🇧🇬"},
    "HRK": {"name": "Croatian Kuna", "flag": "🇭🇷"},
    "ISK": {"name": "Icelandic Krona", "flag": "🇮🇸"},
    "RUB": {"name": "Russian Ruble", "flag": "🇷🇺"},
    "TRY": {"name": "Turkish Lira", "flag": "🇹🇷"},
    
    # Asia Pacific
    "KRW": {"name": "South Korean Won", "flag": "🇰🇷"},
    "INR": {"name": "Indian Rupee", "flag": "🇮🇳"},
    "SGD": {"name": "Singapore Dollar", "flag": "🇸🇬"},
    "HKD": {"name": "Hong Kong Dollar", "flag": "🇭🇰"},
    "TWD": {"name": "New Taiwan Dollar", "flag": "🇹🇼"},
    "THB": {"name": "Thai Baht", "flag": "🇹🇭"},
    "MYR": {"name": "Malaysian Ringgit", "flag": "🇲🇾"},
    "IDR": {"name": "Indonesian Rupiah", "flag": "🇮🇩"},
    "PHP": {"name": "Philippine Peso", "flag": "🇵🇭"},
    "VND": {"name": "Vietnamese Dong", "flag": "🇻🇳"},
    "NZD": {"name": "New Zealand Dollar", "flag": "🇳🇿"},
    "PKR": {"name": "Pakistani Rupee", "flag": "🇵🇰"},
    "BDT": {"name": "Bangladeshi Taka", "flag": "🇧🇩"},
    "LKR": {"name": "Sri Lankan Rupee", "flag": "🇱🇰"},
    "MMK": {"name": "Myanmar Kyat", "flag": "🇲🇲"},
    "KHR": {"name": "Cambodian Riel", "flag": "🇰🇭"},
    "LAK": {"name": "Laotian Kip", "flag": "🇱🇦"},
    "NPR": {"name": "Nepalese Rupee", "flag": "🇳🇵"},
    "BTN": {"name": "Bhutanese Ngultrum", "flag": "🇧🇹"},
    "MVR": {"name": "Maldivian Rufiyaa", "flag": "🇲🇻"},
    
    # Middle East
    "SAR": {"name": "Saudi Riyal", "flag": "🇸🇦"},
    "AED": {"name": "UAE Dirham", "flag": "🇦🇪"},
    "QAR": {"name": "Qatari Riyal", "flag": "🇶🇦"},
    "OMR": {"name": "Omani Rial", "flag": "🇴🇲"},
    "KWD": {"name": "Kuwaiti Dinar", "flag": "🇰🇼"},
    "BHD": {"name": "Bahraini Dinar", "flag": "🇧🇭"},
    "JOD": {"name": "Jordanian Dinar", "flag": "🇯🇴"},
    "ILS": {"name": "Israeli Shekel", "flag": "🇮🇱"},
    "EGP": {"name": "Egyptian Pound", "flag": "🇪🇬"},
    "LBP": {"name": "Lebanese Pound", "flag": "🇱🇧"},
    
    # Africa
    "ZAR": {"name": "South African Rand", "flag": "🇿🇦"},
    "NGN": {"name": "Nigerian Naira", "flag": "🇳🇬"},
    "GHS": {"name": "Ghanaian Cedi", "flag": "🇬🇭"},
    "KES": {"name": "Kenyan Shilling", "flag": "🇰🇪"},
    "UGX": {"name": "Ugandan Shilling", "flag": "🇺🇬"},
    "TZS": {"name": "Tanzanian Shilling", "flag": "🇹🇿"},
    "ETB": {"name": "Ethiopian Birr", "flag": "🇪🇹"},
    "MAD": {"name": "Moroccan Dirham", "flag": "🇲🇦"},
    "TND": {"name": "Tunisian Dinar", "flag": "🇹🇳"},
    "DZD": {"name": "Algerian Dinar", "flag": "🇩🇿"},
    "XOF": {"name": "West African CFA Franc", "flag": "🌍"},
    "XAF": {"name": "Central African CFA Franc", "flag": "🌍"},
    
    # Americas
    "MXN": {"name": "Mexican Peso", "flag": "🇲🇽"},
    "BRL": {"name": "Brazilian Real", "flag": "🇧🇷"},
    "ARS": {"name": "Argentine Peso", "flag": "🇦🇷"},
    "CLP": {"name": "Chilean Peso", "flag": "🇨🇱"},
    "COP": {"name": "Colombian Peso", "flag": "🇨🇴"},
    "PEN": {"name": "Peruvian Sol", "flag": "🇵🇪"},
    "UYU": {"name": "Uruguayan Peso", "flag": "🇺🇾"},
    "BOB": {"name": "Bolivian Boliviano", "flag": "🇧🇴"},
    "PYG": {"name": "Paraguayan Guarani", "flag": "🇵🇾"},
    "VEF": {"name": "Venezuelan Bolívar", "flag": "🇻🇪"},
    "GYD": {"name": "Guyanese Dollar", "flag": "🇬🇾"},
    "SRD": {"name": "Surinamese Dollar", "flag": "🇸🇷"},
    "AWG": {"name": "Aruban Florin", "flag": "🇦🇼"},
    "BBD": {"name": "Barbadian Dollar", "flag": "🇧🇧"},
    "BZD": {"name": "Belize Dollar", "flag": "🇧🇿"},
    "BMD": {"name": "Bermudian Dollar", "flag": "🇧🇲"},
    "KYD": {"name": "Cayman Islands Dollar", "flag": "🇰🇾"},
    "XCD": {"name": "East Caribbean Dollar", "flag": "🌴"},
}


def sorted_currency_codes():
    """Return sorted list of currency codes"""
    return sorted(CURRENCIES.keys())


def describe(code: str) -> str:
    """Get currency description without flag"""
    currency = CURRENCIES.get(code)
    if currency:
        return f"{code} - {currency['name']}"
    return code


def get_flag(code: str) -> str:
    """Get flag emoji for currency"""
    currency = CURRENCIES.get(code)
    if currency:
        return currency['flag']
    return "❓"
