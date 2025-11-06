# Blockchain AI System API Overview

## Endpoints

### POST /api/v1/predictions/gas-optimization
- **Description**: Produces gas optimization guidance and telemetry for a given blockchain network.
- **Request Body**:
  ```json
  {
    "network": "ethereum.mainnet",
    "transaction": { "to": "0x..." }
  }
  ```
- **Response Body**:
  ```json
  {
    "network": "ethereum.mainnet",
    "gas": { "gas": 21000, "maxFeePerGas": 42000000000 },
    "telemetry": { "gas_metrics": { "base_fee_mean": 23.4 } },
    "timestamp": 1700000000.0
  }
  ```

### POST /api/v1/execute/smart-contract
- **Description**: Executes a smart contract transaction after validation and simulation.
- **Request Body**:
  ```json
  {
    "network": "ethereum.mainnet",
    "private_key": "0x...",
    "account_address": "0x...",
    "prediction_data": {
      "contract_address": "0x...",
      "abi": [],
      "function_name": "trade",
      "function_args": []
    }
  }
  ```
- **Response Body**:
  ```json
  {
    "transaction_hash": "0xabc123..."
  }
  ```
