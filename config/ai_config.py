class AIConfig:
    """Minimal AI config mixin for local runs/tests."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Which local model to use for lightweight tests (string name or path)
        self.AI_MODEL = kwargs.get("AI_MODEL", "local_dummy")
        self.AI_AGENT_NAME = kwargs.get("AI_AGENT_NAME", "tbcoin-autonomous-agent")
