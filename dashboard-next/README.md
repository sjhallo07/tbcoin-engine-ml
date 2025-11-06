# TBcoin Build Dashboard (Next.js + Tailwind)

A small Next.js dashboard that queries the GitHub Actions API and shows build metrics (success rate, average duration, failed builds, and an approximate test pass rate) for a repository.

## Quickstart

1. Install dependencies

```bash
cd dashboard-next
npm install
```

2. (Optional) Create a GitHub personal access token with `repo` and `workflow` (or at least `public_repo` / `workflow` for public repos) to increase rate limits. Save it in `.env.local` or your environment as `GITHUB_TOKEN`.

```bash
# Windows PowerShell example
setx GITHUB_TOKEN "ghp_..."
# or create .env.local in dashboard-next with:
# GITHUB_TOKEN=ghp_...
```

3. Run the dev server

```bash
npm run dev
```

4. Open your browser at http://localhost:3001

The dashboard defaults to repository `sjhallo07/tbcoin-engine-ml`. Change owner/repo in the UI and click Fetch.

## Notes

- The API route `pages/api/builds` proxies requests to the GitHub Actions API and uses `GITHUB_TOKEN` from the environment when present.
- For production builds, set `GITHUB_TOKEN` in the environment where you run `next start`.
- This is a starter scaffold — you can extend the API to paginate, aggregate across multiple workflows, or display timeline charts.
