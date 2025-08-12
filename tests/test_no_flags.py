from currency_converter.currencies import describe, get_flag

print("Testing currency descriptions without flags:")
print("USD:", describe('USD'))
print("EUR:", describe('EUR'))
print("GBP:", describe('GBP'))

print("\nFlag function still works (but not used in describe):")
print("USD flag:", get_flag('USD'))
