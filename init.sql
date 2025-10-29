-- database/init.sql
-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Transactions table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_hash VARCHAR(255) UNIQUE NOT NULL,
    chain VARCHAR(50) NOT NULL,
    block_number BIGINT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    wallet_address VARCHAR(255) NOT NULL,
    from_address VARCHAR(255),
    to_address VARCHAR(255),
    value DECIMAL(36, 18),
    token_address VARCHAR(255),
    gas_used DECIMAL(18, 8),
    gas_price DECIMAL(18, 8),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Convert to hypertable for time-series data
SELECT create_hypertable('transactions', 'timestamp');

-- Wallet behavior table
CREATE TABLE wallet_behavior (
    id SERIAL PRIMARY KEY,
    wallet_address VARCHAR(255) UNIQUE NOT NULL,
    total_transactions INTEGER DEFAULT 0,
    total_volume DECIMAL(36, 18) DEFAULT 0,
    avg_transaction_size DECIMAL(36, 18),
    first_transaction TIMESTAMP,
    last_transaction TIMESTAMP,
    wallet_age_days INTEGER,
    behavior_cluster INTEGER,
    risk_score DECIMAL(5, 4),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model predictions table
CREATE TABLE model_predictions (
    id SERIAL PRIMARY KEY,
    model_type VARCHAR(100) NOT NULL,
    prediction_type VARCHAR(100) NOT NULL,
    input_features JSONB,
    prediction_output JSONB,
    confidence DECIMAL(5, 4),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actual_outcome JSONB NULL
);

-- Feature store for ML
CREATE TABLE feature_store (
    id SERIAL PRIMARY KEY,
    feature_set_name VARCHAR(255) NOT NULL,
    wallet_address VARCHAR(255),
    timestamp TIMESTAMP NOT NULL,
    features JSONB NOT NULL,
    label JSONB NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contract deployments table
CREATE TABLE contract_deployments (
    id VARCHAR(36) PRIMARY KEY,
    chain VARCHAR(50) NOT NULL,
    contract_address VARCHAR(255) UNIQUE NOT NULL,
    code_hash VARCHAR(255) NOT NULL,
    contract_name VARCHAR(255) NOT NULL,
    deployer_address VARCHAR(255) NOT NULL,
    artifact_metadata JSONB,
    deployment_tx_hash VARCHAR(255) NOT NULL,
    block_number INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_transactions_wallet ON transactions(wallet_address);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX idx_transactions_hash ON transactions(transaction_hash);
CREATE INDEX idx_wallet_behavior_address ON wallet_behavior(wallet_address);
CREATE INDEX idx_feature_store_timestamp ON feature_store(timestamp);
CREATE INDEX idx_contract_deployments_chain ON contract_deployments(chain);

-- Create admin user
CREATE USER tbcoin_admin WITH PASSWORD 'admin_password';
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tbcoin_admin;