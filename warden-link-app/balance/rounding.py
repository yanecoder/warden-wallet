from decimal import Decimal, ROUND_DOWN

def round_down_4(balance):
    balance_rd4 = Decimal(balance)
    balance = balance_rd4.quantize(Decimal('0.0001'), rounding=ROUND_DOWN)
    return balance