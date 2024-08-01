class PortfolioStateNotFoundError(Exception):
    def __init__(self, date):
        self.date = date
        super().__init__(f"Portfolio state not found for date: {date}")
