class BlockchainConfig:
    """Minimal blockchain configuration mixin.

    Provides a sensible RPC endpoint default for local/dev runs. Projects
    should replace these values via environment variables or a proper
    settings system in production.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.BLOCKCHAIN_RPC = kwargs.get("BLOCKCHAIN_RPC", "https://api.devnet.solana.com")
        self.BLOCKCHAIN_TIMEOUT = kwargs.get("BLOCKCHAIN_TIMEOUT", 10)
