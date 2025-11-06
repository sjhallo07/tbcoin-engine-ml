AUTONOMOUS_AGENT_CONFIG = {
    'trading': {
        'initial_capital': 10000,
        'max_position_size': 0.05,  # 5% of portfolio
        'daily_loss_limit': 0.02,   # 2% daily loss limit
        'max_drawdown': 0.15,       # 15% max drawdown
    },
    'ai_models': {
        'llm_model': 'microsoft/DialoGPT-medium',
        'rl_training_episodes': 10000,
        'confidence_threshold': 0.7,
    },
    'blockchain': {
        'rpc_url': 'https://api.mainnet-beta.solana.com',
        'confirm_timeout': 30,
        'max_slippage_bps': 200,  # 2% max slippage
    },
    'learning': {
        'retraining_interval_hours': 24,
        'performance_review_interval': 100,  # trades
        'strategy_evolution_interval': 7,    # days
    }
}
