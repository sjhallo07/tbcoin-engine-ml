class TradingConfig:
    """Minimal trading-related settings for the autonomous agent."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.DEFAULT_POSITION_SIZE = kwargs.get("DEFAULT_POSITION_SIZE", 0.01)
        self.MAX_LEVERAGE = kwargs.get("MAX_LEVERAGE", 1)
        self.RISK_LIMIT = kwargs.get("RISK_LIMIT", 0.02)
