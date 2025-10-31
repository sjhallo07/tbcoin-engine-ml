import { useEffect, useState } from 'react'
import { TokenAnalysisDashboard } from '../components/TokenAnalysisDashboard'

export default function Home() {
  const [solana, setSolana] = useState(null)
  const [tbcoin, setTbcoin] = useState(null)
  const [postResult, setPostResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [postLoading, setPostLoading] = useState(false)
  const [postError, setPostError] = useState(null)

  async function fetchData() {
    setLoading(true)
    setError(null)
    try {
      const [sRes, tRes] = await Promise.all([
        fetch('/api/solana/price'),
        fetch('/api/tbcoin/data'),
      ])
      if (!sRes.ok) throw new Error('Failed to fetch solana')
      if (!tRes.ok) throw new Error('Failed to fetch tbcoin')
      const sJson = await sRes.json()
      const tJson = await tRes.json()
      setSolana(sJson.data || null)
      setTbcoin(tJson.data || null)
    } catch (err) {
      setError(err.message || String(err))
    } finally {
      setLoading(false)
    }
  }

  async function runPostTest() {
    setPostLoading(true)
    setPostError(null)
    setPostResult(null)
    try {
      const res = await fetch('/api/solana/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'test_market_analysis', symbol: 'SOL', test: true }),
      })
      if (!res.ok) throw new Error(`POST failed (${res.status})`)
      const json = await res.json()
      setPostResult(json)
    } catch (err) {
      setPostError(err.message || String(err))
    } finally {
      setPostLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-4xl mx-auto">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold mb-1">TBcoin Live Dashboard</h1>
          <p className="text-sm text-slate-600">Live data from local API routes for Solana and TB Coin.</p>
        </header>

        <main>
          <div className="mb-4">
            <div className="flex flex-wrap gap-2">
              <button className="bg-sky-600 text-white px-4 py-2 rounded" onClick={fetchData} disabled={loading}>
                {loading ? 'Refreshing…' : 'Refresh'}
              </button>
              <button className="bg-emerald-600 text-white px-4 py-2 rounded" onClick={runPostTest} disabled={postLoading}>
                {postLoading ? 'Running POST…' : 'Run POST Test'}
              </button>
            </div>
          </div>

          {loading && <div className="p-6 bg-white rounded shadow">Loading…</div>}
          {error && <div className="p-4 bg-rose-50 text-rose-700 rounded">Error: {error}</div>}

          {postError && <div className="p-4 bg-rose-50 text-rose-700 rounded">POST Error: {postError}</div>}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-white rounded shadow">
              <h2 className="text-lg font-medium">Solana</h2>
              {solana ? (
                <dl className="mt-3 space-y-2">
                  <div className="flex justify-between"><dt className="text-sm text-slate-600">Price</dt><dd className="font-mono">${solana.price}</dd></div>
                  <div className="flex justify-between"><dt className="text-sm text-slate-600">24h Change</dt><dd className="font-mono">{solana.change24h}%</dd></div>
                  <div className="flex justify-between"><dt className="text-sm text-slate-600">Market Cap</dt><dd className="font-mono">{solana.marketCap.toLocaleString()}</dd></div>
                  <div className="flex justify-between"><dt className="text-sm text-slate-600">Updated</dt><dd className="font-mono">{new Date(solana.timestamp).toLocaleString()}</dd></div>
                </dl>
              ) : <div className="text-sm text-slate-500">No data.</div>}
            </div>

            <div className="p-4 bg-white rounded shadow">
              <h2 className="text-lg font-medium">TB Coin</h2>
              {tbcoin ? (
                <dl className="mt-3 space-y-2">
                  <div className="flex justify-between"><dt className="text-sm text-slate-600">Price</dt><dd className="font-mono">${tbcoin.price}</dd></div>
                  <div className="flex justify-between"><dt className="text-sm text-slate-600">Holders</dt><dd className="font-mono">{tbcoin.holders}</dd></div>
                  <div className="flex justify-between"><dt className="text-sm text-slate-600">Transactions</dt><dd className="font-mono">{tbcoin.transactions}</dd></div>
                  <div className="flex justify-between"><dt className="text-sm text-slate-600">Updated</dt><dd className="font-mono">{new Date(tbcoin.timestamp).toLocaleString()}</dd></div>
                </dl>
              ) : <div className="text-sm text-slate-500">No data.</div>}
            </div>
          </div>

          <div className="mt-4 p-4 bg-white rounded shadow">
            <h2 className="text-lg font-medium">POST Test Result</h2>
            {postResult ? (
              <div className="mt-3 space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-slate-600">Status</span><span className="font-mono">{postResult.status}</span></div>
                <div className="flex justify-between"><span className="text-slate-600">Processed</span><span className="font-mono">{String(postResult.data?.processed)}</span></div>
                <div className="flex justify-between"><span className="text-slate-600">Action</span><span className="font-mono">{postResult.data?.action}</span></div>
                <div className="flex justify-between"><span className="text-slate-600">Sentiment</span><span className="font-mono">{postResult.data?.analysis?.sentiment}</span></div>
                <div className="flex justify-between"><span className="text-slate-600">Confidence</span><span className="font-mono">{postResult.data?.analysis?.confidence}</span></div>
                <div className="flex justify-between"><span className="text-slate-600">Recommendation</span><span className="font-mono">{postResult.data?.analysis?.recommendation}</span></div>
                <div className="flex justify-between"><span className="text-slate-600">Risk Level</span><span className="font-mono">{postResult.data?.analysis?.riskLevel}</span></div>
                <div className="text-xs text-slate-500">Last updated: {new Date(postResult.data?.timestamp || Date.now()).toLocaleString()}</div>
                <div className="text-xs text-slate-500">Message: {postResult.message}</div>
              </div>
            ) : (
              <div className="text-sm text-slate-500">No POST request run yet.</div>
            )}
          </div>

          <div className="mt-6 text-xs text-slate-500">
            These endpoints are served from the Next.js app's `app/api` routes. Use the Refresh button to re-query.
          </div>

          <div className="mt-10">
            <h2 className="text-xl font-semibold mb-3">Advanced Token Analysis</h2>
            <p className="text-sm text-slate-600 mb-4">Run the autonomous token risk profiler against any Solana mint.</p>
            <TokenAnalysisDashboard defaultMint="FyR7KcKwC2V1o1TDi1Vz1a64pE1Rx5SrwwnJocNbhgFE" />
          </div>
        </main>
      </div>
    </div>
  )
}
