# Using the API
curl -X POST "https://api.tbcoin.com/api/v1/blockchain/honeycomb/upload" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "suri": "//Alice",
    "manifest_path": "./tbcoin-contract/Cargo.toml",
    "execute": true
  }'