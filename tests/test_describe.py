# Test the describe function without flags
exec(open('currency_converter/currencies.py').read())

print("Testing currency descriptions without flags:")
print("USD:", describe('USD'))
print("EUR:", describe('EUR'))
print("GBP:", describe('GBP'))
print("JPY:", describe('JPY'))

print("\nTesting that flags are still stored but not shown:")
print("USD flag still exists:", get_flag('USD'))
print("But describe function doesn't show it:", describe('USD'))
