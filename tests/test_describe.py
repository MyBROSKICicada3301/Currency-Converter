# Test the describe function without flags
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from currency_converter.currencies import describe, get_flag

def test_describe_function():
    """Test the describe function without flags"""
    print("Testing currency descriptions without flags:")
    print("USD:", describe('USD'))
    print("EUR:", describe('EUR'))
    print("GBP:", describe('GBP'))
    print("JPY:", describe('JPY'))

    print("\nTesting that flags are still stored but not shown:")
    print("USD flag still exists:", get_flag('USD'))
    print("But describe function doesn't show it:", describe('USD'))

if __name__ == "__main__":
    test_describe_function()
