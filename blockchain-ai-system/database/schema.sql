CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS blockchain_predictions (
    prediction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    blockchain_name VARCHAR(50) NOT NULL,
    prediction_type VARCHAR(100) NOT NULL,
    confidence_score NUMERIC(5, 4) CHECK (confidence_score BETWEEN 0 AND 1),
    input_features JSONB NOT NULL,
    predicted_output JSONB NOT NULL,
    actual_result JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    accuracy_measured BOOLEAN NOT NULL DEFAULT FALSE,
    metadata JSONB,
    CONSTRAINT chk_prediction_payload CHECK (jsonb_typeof(input_features) = 'object')
) PARTITION BY RANGE (created_at);

CREATE TABLE IF NOT EXISTS blockchain_predictions_default
    PARTITION OF blockchain_predictions
    DEFAULT;

-- Partition template for rolling time-series partitions
CREATE TABLE IF NOT EXISTS blockchain_predictions_2025_q4
    PARTITION OF blockchain_predictions
    FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');

CREATE INDEX IF NOT EXISTS idx_predictions_blockchain_created
    ON blockchain_predictions (blockchain_name, created_at);

CREATE INDEX IF NOT EXISTS idx_predictions_confidence
    ON blockchain_predictions (confidence_score DESC);

CREATE INDEX IF NOT EXISTS idx_predictions_pred_type
    ON blockchain_predictions (prediction_type);

CREATE INDEX IF NOT EXISTS idx_predictions_accuracy_measured
    ON blockchain_predictions (accuracy_measured) WHERE accuracy_measured = FALSE;

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_prediction_accuracy_daily AS
SELECT
    date_trunc('day', created_at) AS day,
    blockchain_name,
    prediction_type,
    COUNT(*) AS total_predictions,
    AVG((predicted_output ->> 'price')::NUMERIC) FILTER (WHERE predicted_output ? 'price') AS avg_predicted_price,
    AVG((actual_result ->> 'price')::NUMERIC) FILTER (WHERE actual_result ? 'price') AS avg_actual_price,
    AVG(CASE WHEN accuracy_measured THEN 1 ELSE 0 END)::NUMERIC AS accuracy_reporting_ratio
FROM blockchain_predictions
GROUP BY 1, 2, 3
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW mv_prediction_accuracy_daily IS 'Daily aggregation of model accuracy by blockchain and prediction type.';

CREATE OR REPLACE FUNCTION refresh_mv_prediction_accuracy_daily()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_prediction_accuracy_daily;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE IF NOT EXISTS prediction_feature_store (
    feature_store_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    blockchain_name VARCHAR(50) NOT NULL,
    feature_namespace VARCHAR(100) NOT NULL,
    feature_data JSONB NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    UNIQUE (blockchain_name, feature_namespace, generated_at)
);

CREATE INDEX IF NOT EXISTS idx_feature_store_expiry
    ON prediction_feature_store (expires_at)
    WHERE expires_at IS NOT NULL;
