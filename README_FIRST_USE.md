# TB Coin Engine ML - First Use Guide

## Mint TB Tokens to a Wallet

To mint TB tokens to a wallet using the API, use the following `curl` command:

```
curl -X POST "https://whole-clowns-press.loca.lt/api/token/mint" \
  -H "Content-Type: application/json" \
  -d '{
    "wallet": "4Ci4xVxKDdB4bLB2CASFtV2qxCpMg9BRBfFus5wv2ThD",
    "amount": "100",
    "memo": "POST prueba mint test"
  }'
```

- Replace the `wallet` address with your own if needed.
- Adjust the `amount` and `memo` as desired.
- The endpoint `/api/token/mint` must be available and running on the backend (see project documentation for backend setup).

## Troubleshooting
- If you receive a connection error, ensure the backend is running and accessible at the specified URL.
- For local development, replace the URL with your local server address (e.g., `http://localhost:8000`).

## Additional Endpoints
- See the main README or API documentation for more endpoints (transfer, balance, etc).
