from decimal import Decimal
from currency_converter.rates import Rates


def test_convert_roundtrip():
    r = Rates(base="EUR", rates={"USD": Decimal("1.2"), "EUR": Decimal("1")}, timestamp=0)
    amount = Decimal("10")
    usd = r.convert(amount, "EUR", "USD")
    eur = r.convert(usd, "USD", "EUR")
    assert abs(eur - amount) < Decimal("1e-12")


def test_same_currency():
    r = Rates(base="EUR", rates={"USD": Decimal("1.2")}, timestamp=0)
    amount = Decimal("10")
    assert r.convert(amount, "USD", "USD") == amount
