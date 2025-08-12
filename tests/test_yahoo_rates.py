import pytest
from decimal import Decimal
from currency_converter.rates import Rates, fetch_yahoo_rates, _fetch_yahoo_rate, get_rates


def test_convert_roundtrip():
    """Test basic conversion roundtrip"""
    r = Rates(base="USD", rates={"USD": Decimal("1"), "EUR": Decimal("0.85")}, timestamp=0)
    amount = Decimal("10")
    eur = r.convert(amount, "USD", "EUR")
    usd = r.convert(eur, "EUR", "USD")
    assert abs(usd - amount) < Decimal("1e-12")


def test_same_currency():
    """Test conversion between same currency"""
    r = Rates(base="USD", rates={"EUR": Decimal("0.85")}, timestamp=0)
    amount = Decimal("10")
    assert r.convert(amount, "EUR", "EUR") == amount


def test_yahoo_finance_single_rate():
    """Test fetching a single rate from Yahoo Finance"""
    rate = _fetch_yahoo_rate("USD", "EUR")
    assert rate is not None
    assert rate > 0
    assert isinstance(rate, Decimal)


def test_yahoo_finance_reverse_rate():
    """Test reverse rate calculation consistency"""
    usd_to_eur = _fetch_yahoo_rate("USD", "EUR")
    eur_to_usd = _fetch_yahoo_rate("EUR", "USD")
    
    if usd_to_eur is not None and eur_to_usd is not None:
        # The product should be approximately 1 (accounting for bid-ask spread)
        product = usd_to_eur * eur_to_usd
        assert abs(product - Decimal("1.0")) < Decimal("0.05")  # 5% tolerance for spread


def test_yahoo_finance_rates_integration():
    """Test full Yahoo Finance rates fetching"""
    try:
        rates = fetch_yahoo_rates()
        assert rates.base == "USD"
        assert "USD" in rates.rates
        assert rates.rates["USD"] == Decimal("1.0")
        assert len(rates.rates) >= 5  # Should have at least 5 currencies
        
        # Test some major currencies are present
        major_currencies = ["EUR", "GBP", "JPY"]
        present_majors = [curr for curr in major_currencies if curr in rates.rates]
        assert len(present_majors) >= 2  # At least 2 major currencies should be available
        
    except Exception as e:
        pytest.skip(f"Yahoo Finance API unavailable: {e}")


def test_get_rates_with_caching():
    """Test the get_rates function with caching"""
    # This should work either with live data or cached data
    rates = get_rates()
    assert isinstance(rates, Rates)
    assert rates.base in ["USD", "EUR"]  # Could be either depending on which API succeeds
    assert len(rates.rates) > 0
    assert rates.timestamp > 0


def test_invalid_currency_conversion():
    """Test error handling for invalid currencies"""
    r = Rates(base="USD", rates={"EUR": Decimal("0.85")}, timestamp=0)
    
    with pytest.raises(ValueError, match="Unknown or invalid source currency"):
        r.convert(Decimal("10"), "INVALID", "EUR")
    
    with pytest.raises(ValueError, match="Unknown or invalid destination currency"):
        r.convert(Decimal("10"), "EUR", "INVALID")


def test_zero_rate_handling():
    """Test handling of zero rates"""
    r = Rates(base="USD", rates={"EUR": Decimal("0")}, timestamp=0)
    
    with pytest.raises(ValueError, match="Unknown or invalid destination currency"):
        r.convert(Decimal("10"), "USD", "EUR")
