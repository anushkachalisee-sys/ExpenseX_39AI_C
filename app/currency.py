CURRENCIES = {
    "NPR": {"symbol": "Rs.", "name": "Nepali Rupee", "flag": "\U0001f1f3\U0001f1f5", "rate": 1.0},
    "INR": {"symbol": "\u20b9", "name": "Indian Rupee", "flag": "\U0001f1ee\U0001f1f3", "rate": 0.628},
    "USD": {"symbol": "$", "name": "US Dollar", "flag": "\U0001f1fa\U0001f1f8", "rate": 0.00752},
    "GBP": {"symbol": "\u00a3", "name": "British Pound", "flag": "\U0001f1ec\U0001f1e7", "rate": 0.00593},
}


def format_currency(amount_npr, currency_code, currencies=None):
    currencies = currencies or CURRENCIES
    try:
        c = currencies.get(currency_code, currencies["NPR"])
        v = float(amount_npr or 0) * float(c["rate"])
        if v >= 10_000_000:
            return f"{c['symbol']}{v / 10_000_000:.2f}Cr"
        if v >= 100_000:
            return f"{c['symbol']}{v / 100_000:.2f}L"
        if v >= 1_000:
            return f"{c['symbol']}{v:,.0f}"
        return f"{c['symbol']}{v:.2f}"
    except Exception:
        return "Rs.0.00"


def display_amount(amount_npr, currency_code, currencies=None):
    currencies = currencies or CURRENCIES
    code = currency_code if currency_code in currencies else "NPR"
    rate = float(currencies[code]["rate"])
    return round(float(amount_npr or 0) * rate, 2)


def to_npr(amount_display, currency_code, currencies=None):
    currencies = currencies or CURRENCIES
    code = currency_code if currency_code in currencies else "NPR"
    rate = currencies[code]["rate"]
    if rate <= 0:
        return float(amount_display)
    return float(amount_display) / rate
#working