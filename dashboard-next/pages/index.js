import Head from 'next/head'
import { useCallback, useEffect, useMemo, useState } from 'react'

import { AIDashboard } from '../components/AIDashboard'
import { TokenAnalysisDashboard } from '../components/TokenAnalysisDashboard'

function formatCurrency(value) {
  if (value === null || value === undefined) return '—'
  const abs = Math.abs(value)
  const fractionDigits = abs >= 1 ? 2 : 4
  return `$${Number(value).toLocaleString(undefined, {
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  })}`
}

function formatPercent(value) {
  if (value === null || value === undefined) return '—'
  const formatted = Number(value).toFixed(2)
  return `${Number(value) > 0 ? '+' : ''}${formatted}%`
}

function formatCompact(value) {
  if (value === null || value === undefined) return '—'
  return Number(value).toLocaleString(undefined, {
    notation: 'compact',
    maximumFractionDigits: 2,
  })
}

function formatRelativeTime(timestamp) {
  if (!timestamp) return '—'
  const parsed = new Date(timestamp)
  if (Number.isNaN(parsed.getTime())) return '—'
  const diffMs = Date.now() - parsed.getTime()
  if (diffMs < 0) return 'just now'
  const minutes = Math.floor(diffMs / 60000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

const toneClassMap = {
  neutral: 'text-slate-200 border-slate-700/70 bg-slate-900/60',
  positive: 'text-emerald-300 border-emerald-500/50 bg-emerald-500/5',
  negative: 'text-rose-300 border-rose-500/50 bg-rose-500/5',
  warning: 'text-amber-300 border-amber-400/50 bg-amber-400/10',
}

const statusToneMap = {
  healthy: 'text-emerald-300 border-emerald-500/40 bg-emerald-500/10',
  warning: 'text-amber-300 border-amber-400/40 bg-amber-400/10',
  error: 'text-rose-300 border-rose-400/40 bg-rose-400/10',
  pending: 'text-sky-300 border-sky-400/40 bg-sky-400/10',
  idle: 'text-slate-300 border-slate-500/40 bg-slate-500/10',
}

function DashboardSection({ title, description, actions, children }) {
  return (
    <section className="rounded-3xl border border-slate-800/80 bg-slate-900/70 p-7 shadow-xl shadow-slate-900/40">
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">{title}</h2>
          {description && <p className="mt-1 text-sm text-slate-400">{description}</p>}
        </div>
        {actions}
      </div>
      {children}
    </section>
  )
}

function StatCard({ id, title, subtitle, value, tone = 'neutral', footnote }) {
  return (
    <div
      key={id}
      className={`flex flex-col justify-between rounded-2xl border px-5 py-4 shadow-inner shadow-slate-900/20 ${
        toneClassMap[tone] || toneClassMap.neutral
      }`}
    >
      <div>
        <p className="text-xs uppercase tracking-wide text-slate-400">{subtitle}</p>
        <h3 className="mt-1 text-lg font-semibold text-white">{title}</h3>
      </div>
      <div className="mt-4 text-3xl font-bold">{value}</div>
      {footnote && <p className="mt-3 text-xs text-slate-400">{footnote}</p>}
    </div>
  )
}

function StatusPill({ tone, children }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium ${
        statusToneMap[tone] || statusToneMap.idle
      }`}
    >
      {children}
    </span>
  )
}

function PostTestPanel({ loading, error, result }) {
  const statusTone = loading ? 'pending' : error ? 'error' : result ? 'healthy' : 'idle'
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-5">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-white">POST Analysis Result</h3>
          <p className="text-xs text-slate-400">/api/solana/test</p>
        </div>
        <StatusPill tone={statusTone}>
          {loading ? 'running' : error ? 'error' : result ? 'ready' : 'idle'}
        </StatusPill>
      </div>

      <div className="mt-4 text-sm text-slate-200">
        {loading && <p className="text-slate-400">Running POST workflow…</p>}
        {!loading && error && <p className="text-rose-300">Error: {error}</p>}
        {!loading && !error && !result && <p className="text-slate-400">Run the POST test to capture AI market insights.</p>}
        {!loading && !error && result && (
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-slate-400">
              <span>Status</span>
              <span className="font-mono text-slate-200">{result.status}</span>
            </div>
            <div className="flex justify-between text-xs text-slate-400">
              <span>Processed</span>
              <span className="font-mono text-slate-200">{String(result.data?.processed)}</span>
            </div>
            <div className="flex justify-between text-xs text-slate-400">
              <span>Action</span>
              <span className="font-mono text-slate-200">{result.data?.action || '—'}</span>
            </div>
            <div className="rounded-xl border border-slate-800/80 bg-slate-900/70 p-3">
              <p className="text-xs text-slate-500">AI Sentiment</p>
              <h4 className="text-lg font-semibold text-white">{result.data?.analysis?.sentiment || '—'}</h4>
              <div className="mt-2 grid grid-cols-2 gap-3 text-xs text-slate-300">
                <div>
                  <p className="text-slate-500">Confidence</p>
                  <p className="font-mono">
                    {result.data?.analysis?.confidence !== undefined
                      ? `${(Number(result.data.analysis.confidence) * 100).toFixed(1)}%`
                      : '—'}
                  </p>
                </div>
                <div>
                  <p className="text-slate-500">Risk Level</p>
                  <p className="font-mono capitalize">{result.data?.analysis?.riskLevel || '—'}</p>
                </div>
              </div>
              <p className="mt-3 text-xs text-slate-400">Recommendation: {result.data?.analysis?.recommendation || '—'}</p>
            </div>
            <p className="text-xs text-slate-500">
              Updated {result.data?.timestamp ? formatRelativeTime(result.data.timestamp) : 'just now'} · {result.message}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default function Home() {
  const [solana, setSolana] = useState(null)
  const [tbcoin, setTbcoin] = useState(null)
  const [postResult, setPostResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [postLoading, setPostLoading] = useState(false)
  const [error, setError] = useState(null)
  const [postError, setPostError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [solRes, tbRes] = await Promise.all([
        fetch('/api/solana/price'),
        fetch('/api/tbcoin/data'),
      ])

      if (!solRes.ok) throw new Error('Failed to retrieve Solana data')
      if (!tbRes.ok) throw new Error('Failed to retrieve TB Coin data')

      const solJson = await solRes.json()
      const tbJson = await tbRes.json()

      setSolana(solJson?.data || null)
      setTbcoin(tbJson?.data || null)
      setLastUpdated(new Date().toISOString())
    } catch (err) {
      setError(err?.message || String(err))
    } finally {
      setLoading(false)
    }
  }, [])

  const runPostTest = useCallback(async () => {
    setPostLoading(true)
    setPostError(null)
    try {
      const response = await fetch('/api/solana/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'test_market_analysis', symbol: 'SOL', demo: true }),
      })

      if (!response.ok) throw new Error(`POST failed (${response.status})`)
      const json = await response.json()
      setPostResult(json)
    } catch (err) {
      setPostError(err?.message || String(err))
      setPostResult(null)
    } finally {
      setPostLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const overviewCards = useMemo(() => {
    return [
      {
        id: 'sol-price',
        title: solana?.display?.name || 'Solana',
        subtitle: 'Spot price',
        value: solana ? formatCurrency(solana.price) : '—',
        tone: 'neutral',
        footnote: solana?.timestamp ? `Updated ${formatRelativeTime(solana.timestamp)}` : 'Awaiting update',
      },
      {
        id: 'sol-change',
        title: '24h Change',
        subtitle: 'Solana momentum',
        value: solana ? formatPercent(solana.change24h) : '—',
        tone: solana ? (solana.change24h >= 0 ? 'positive' : 'negative') : 'neutral',
        footnote: solana ? `${formatCurrency(solana.volume24h)} volume (24h)` : '—',
      },
      {
        id: 'sol-cap',
        title: 'Market Cap',
        subtitle: 'Solana valuation',
        value: solana ? `$${formatCompact(solana.marketCap)}` : '—',
        tone: 'neutral',
        footnote: solana?.display?.symbol ? `${solana.display.symbol} network overview` : 'Layer 1 insight',
      },
      {
        id: 'tb-price',
        title: 'TB Coin',
        subtitle: 'Synthetic price feed',
        value: tbcoin ? formatCurrency(tbcoin.price) : '—',
        tone: 'neutral',
        footnote: tbcoin?.timestamp ? `Updated ${formatRelativeTime(tbcoin.timestamp)}` : 'Awaiting update',
      },
      {
        id: 'tb-holders',
        title: 'TB Holders',
        subtitle: 'Community size',
        value: tbcoin ? tbcoin.holders.toLocaleString() : '—',
        tone: tbcoin && tbcoin.holders > 0 ? 'positive' : 'neutral',
        footnote: tbcoin ? `${tbcoin.transactions.toLocaleString()} lifetime transactions` : '—',
      },
    ]
  }, [solana, tbcoin])

  const statusRows = useMemo(() => {
    return [
      {
        id: 'sol-endpoint',
        label: 'Solana price endpoint',
        endpoint: '/api/solana/price',
        tone: loading ? 'pending' : solana ? 'healthy' : error ? 'error' : 'idle',
        detail: solana
          ? `Last refreshed ${formatRelativeTime(solana.timestamp)}`
          : error || 'Awaiting data refresh',
      },
      {
        id: 'tb-endpoint',
        label: 'TB Coin endpoint',
        endpoint: '/api/tbcoin/data',
        tone: loading ? 'pending' : tbcoin ? 'healthy' : error ? 'error' : 'idle',
        detail: tbcoin
          ? `Market cap ${tbcoin.marketCap ? formatCurrency(tbcoin.marketCap) : '—'}`
          : error || 'Awaiting data refresh',
      },
      {
        id: 'post-endpoint',
        label: 'AI POST analysis',
        endpoint: '/api/solana/test',
        tone: postLoading ? 'pending' : postResult ? 'healthy' : postError ? 'error' : 'idle',
        detail: postResult
          ? `Sentiment ${postResult.data?.analysis?.sentiment || '—'} · ${(postResult.data?.analysis?.confidence ?? 0) * 100}% confidence`
          : postError || 'No test executed yet',
      },
    ]
  }, [solana, tbcoin, postResult, loading, error, postLoading, postError])

  const activityLog = useMemo(() => {
    const events = []
    if (solana) {
      events.push({
        id: `sol-${solana.timestamp}`,
        label: 'Solana price refreshed',
        detail: `${formatCurrency(solana.price)} · ${formatPercent(solana.change24h)}`,
        timestamp: solana.timestamp,
      })
    }
    if (tbcoin) {
      events.push({
        id: `tb-${tbcoin.timestamp}`,
        label: 'TB Coin telemetry updated',
        detail: `${tbcoin.transactions.toLocaleString()} transactions`,
        timestamp: tbcoin.timestamp,
      })
    }
    if (postResult) {
      events.push({
        id: `post-${postResult.data?.timestamp || postResult.status}`,
        label: 'POST analysis completed',
        detail: `${postResult.data?.analysis?.recommendation || '—'} recommendation`,
        timestamp: postResult.data?.timestamp || new Date().toISOString(),
      })
    }
    return events
      .filter(Boolean)
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
  }, [solana, tbcoin, postResult])

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 pb-16">
      <Head>
        <title>TBcoin Operations Console</title>
      </Head>
      <main className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-10">
        <header className="rounded-3xl border border-slate-800/60 bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 p-8 shadow-2xl shadow-black/50">
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs uppercase tracking-widest text-sky-400/80">Operations Console</p>
              <h1 className="mt-2 text-3xl font-semibold text-white sm:text-4xl">TBcoin Command Dashboard</h1>
              <p className="mt-2 max-w-2xl text-sm text-slate-300">
                Monitor live Solana telemetry, TBcoin fundamentals, and AI-driven workflows in a single control surface.
                Use the quick actions to refresh endpoints or trigger autonomous analysis checks.
              </p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              <button
                onClick={fetchData}
                disabled={loading}
                className="inline-flex items-center justify-center rounded-full border border-sky-500/40 bg-sky-500/10 px-5 py-2 text-sm font-medium text-sky-200 transition hover:bg-sky-500/20 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? 'Refreshing…' : 'Refresh Endpoints'}
              </button>
              <button
                onClick={runPostTest}
                disabled={postLoading}
                className="inline-flex items-center justify-center rounded-full border border-emerald-500/40 bg-emerald-500/10 px-5 py-2 text-sm font-medium text-emerald-200 transition hover:bg-emerald-500/20 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {postLoading ? 'Running POST…' : 'Run POST Analysis'}
              </button>
            </div>
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-3 text-xs text-slate-400">
            <span className="rounded-full border border-slate-700/60 bg-slate-900/70 px-3 py-1">
              Last refresh: {lastUpdated ? formatRelativeTime(lastUpdated) : 'pending'}
            </span>
            <span className="rounded-full border border-slate-700/60 bg-slate-900/70 px-3 py-1">
              API calls: Solana, TBcoin, POST test
            </span>
          </div>
        </header>

        {error && (
          <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-200">
            Unable to refresh endpoints: {error}
          </div>
        )}
        {postError && !postLoading && (
          <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-200">
            POST analysis error: {postError}
          </div>
        )}

        <DashboardSection
          title="Key network metrics"
          description="Real-time Solana and TBcoin telemetry pulled from local API routes. Values update when you refresh the console."
        >
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            {overviewCards.map((card) => (
              <StatCard key={card.id} {...card} />
            ))}
          </div>
        </DashboardSection>

        <DashboardSection
          title="API health & activity"
          description="Track endpoint availability and review the latest automation events streaming through the console."
        >
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2 rounded-2xl border border-slate-800/70 bg-slate-950/40">
              <table className="min-w-full divide-y divide-slate-800/80 text-sm">
                <thead className="text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th className="px-5 py-3 text-left">Service</th>
                    <th className="px-5 py-3 text-left">Endpoint</th>
                    <th className="px-5 py-3 text-left">Status</th>
                    <th className="px-5 py-3 text-left">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/80 text-slate-200">
                  {statusRows.map((row) => (
                    <tr key={row.id}>
                      <td className="px-5 py-3 font-medium text-white">{row.label}</td>
                      <td className="px-5 py-3 font-mono text-xs text-slate-400">{row.endpoint}</td>
                      <td className="px-5 py-3">
                        <StatusPill tone={row.tone}>
                          {row.tone === 'healthy'
                            ? 'healthy'
                            : row.tone === 'pending'
                            ? 'refreshing'
                            : row.tone === 'error'
                            ? 'error'
                            : row.tone === 'warning'
                            ? 'warning'
                            : 'idle'}
                        </StatusPill>
                      </td>
                      <td className="px-5 py-3 text-xs text-slate-400">{row.detail}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <PostTestPanel loading={postLoading} error={postError} result={postResult} />
          </div>

          <div className="mt-6">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Recent automation events</h3>
            {activityLog.length === 0 ? (
              <p className="mt-3 text-xs text-slate-500">Interact with the console to populate the activity log.</p>
            ) : (
              <ul className="mt-3 space-y-3 text-sm text-slate-200">
                {activityLog.map((event) => (
                  <li
                    key={event.id}
                    className="flex items-center justify-between rounded-2xl border border-slate-800/70 bg-slate-950/50 px-4 py-3"
                  >
                    <div>
                      <p className="font-medium text-white">{event.label}</p>
                      <p className="text-xs text-slate-400">{event.detail}</p>
                    </div>
                    <span className="text-xs text-slate-500">{formatRelativeTime(event.timestamp)}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </DashboardSection>

        <DashboardSection
          title="AI command center"
          description="Trigger predictive analysis, inspect model health, and surface AI recommendations without leaving the dashboard."
        >
          <AIDashboard />
        </DashboardSection>

        <DashboardSection
          title="Token risk workbench"
          description="Run the autonomous risk profiler against any Solana mint to capture tokenomics, liquidity, and governance heuristics."
        >
          <TokenAnalysisDashboard defaultMint="FyR7KcKwC2V1o1TDi1Vz1a64pE1Rx5SrwwnJocNbhgFE" />
        </DashboardSection>
      </main>
    </div>
  )
}
