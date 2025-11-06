class BaseConfig:
    """Minimal base configuration fallback used for local runs and tests.

    This class uses cooperative multiple inheritance (calls super()) so that
    the composed `TBCoinConfig` in `config.__init__` can be instantiated
    reliably even when other config mixins are present.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Feature flags
        self.AI_AGENT_ENABLED = kwargs.get("AI_AGENT_ENABLED", False)
        self.AI_TRADING_ENABLED = kwargs.get("AI_TRADING_ENABLED", False)
        # Environment
        self.ENV = kwargs.get("ENV", "development")
