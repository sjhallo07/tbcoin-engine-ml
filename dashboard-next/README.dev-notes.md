Developer notes:
- To install Tailwind run: npx tailwindcss -i ./styles/globals.css -o ./public/output.css --watch (not required; Next + Tailwind via PostCSS works with the above config)
- If you hit rate limits, add GITHUB_TOKEN environment variable
- Token metadata helpers live in `services/solana-utils.ts`; use `fetchTokenDisplayInfo(mintOrSymbol)` to access display name/symbol/logo. It queries Solscan first and falls back to derived values when metadata is missing.
- Ensure `SOLANA_RPC_URL` is set if you rely on a private RPC, and expect Solscan public API availability for logo/name lookups (UI should handle null logos gracefully).
