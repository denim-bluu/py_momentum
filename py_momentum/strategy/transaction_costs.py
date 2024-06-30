class TransactionCosts:
    def __init__(self, commission_rate=0.001, slippage_rate=0.0005):
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate

    def calculate_costs(self, price: float, shares: int) -> float:
        transaction_value = price * shares
        commission = transaction_value * self.commission_rate
        slippage = transaction_value * self.slippage_rate
        return commission + slippage
