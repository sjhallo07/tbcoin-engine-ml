curl -X POST "https://api.tbcoin.com/api/v1/blockchain/honeycomb/instantiate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "suri": "//Alice",
    "constructor": "new",
    "args": ["1000000", "TB Coin", "TB", "8"],
    "code_hash": "0xbc1b42256696c8a4187ec3ed79fc602789fc11287c4c30926f5e31ed8169574e",
    "execute": true
  }'