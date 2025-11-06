# Building with AI Using CoinGecko

Use CoinGecko’s AI-native tooling to connect autonomous agents and LLM-powered apps to real-time, historical, and onchain market data.

## llms.txt Guidance

- Reference `https://www.coingecko.com/llms-full.txt` (or the mirrored asset in this repository if provided) so AI agents understand preferred API usage patterns.
- Surface this file inside MCP or other agent contexts to improve prompt grounding when requesting CoinGecko data.

## MCP Server Integration

- The CoinGecko MCP (Model-Context-Protocol) server links LLMs such as Claude or Gemini with live data streams.
- Follow the official quick start at `/docs/mcp-server` to register your agent, configure authentication, and subscribe to market feeds for conversational crypto analysis.

## Documentation Tooling

- **Copy page** buttons deliver endpoint-specific Markdown snippets tailored for LLM prompting. Paste these into your chat interface to bootstrap code generation or explore sample queries.
- **AI Support** buttons open an assistant trained on CoinGecko docs to help debug integration issues or clarify endpoint capabilities in real time.

## Onchain Coverage Highlights

- Solana and Polygon demo endpoints support token metadata, multi-token batching, and new pool discovery—ideal for AI-driven DeFi analysis.
- Metadata payloads include images, socials, descriptions, GT scores, and holder distributions (beta) refreshed roughly every 60 seconds.

## Recommended Workflow

1. Load the `llms-full.txt` guidance into your agent context.
2. Establish an MCP connection for live data retrieval.
3. Use Copy-page prompts to seed SDK-based templates (Python: `coingecko_sdk`, TypeScript: `@coingecko/coingecko-typescript`).
4. Iterate with the AI Support assistant when refining queries or debugging responses.

Leverage these tools to accelerate AI-powered trading bots, analytics dashboards, and portfolio copilots while respecting API usage policies.
