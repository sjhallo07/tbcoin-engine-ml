'use client';

import { useMemo, useState } from 'react';

type RiskReport = {
  overall: number;
  categories: {
    tokenomics: number;
    liquidity: number;
    security: number;
    social: number;
  };
  flags: {
    critical: string[];
    warnings: string[];
  };
  recommendations: string[];
  holders?: {
    totalHolders: number;
    distribution: {
      top10Percentage: number;
      giniCoefficient: number;
      averageBalance: number;
    };
  };
  liquidity?: {
    pools: any;
    trading: {
      volume24h: number;
    };
  };
  audit?: {
    permissions?: {
      canMint?: boolean;
      canFreeze?: boolean;
    };
  };
  profile?: any;
};

type Props = {
  defaultMint?: string;
};

type TokenIntelResponse = {
  tokens: Array<{
    address: string;
    network: 'solana' | 'ethereum' | 'polygon';
    name: string;
    symbol: string;
    creator: string | null;
    createdAt: number;
    totalSupply: number;
    proofMechanism: 'pow' | 'pos';
    risk: {
      score: number;
      level: string;
      breakdown?: Record<string, number>;
    };
    liquidity: {
      liquidUSD: number;
      frozenUSD: number;
      flag: 'green' | 'orange' | 'red';
    };
    summary: string;
    rankingScore: number;
  }>;
  ranking: string[];
};

type IntelToken = {
  address: string;
  network: 'solana' | 'ethereum' | 'polygon';
};

const DEMO_TOKENS: IntelToken[] = [
  { address: 'So11111111111111111111111111111111111111112', network: 'solana' },
  { address: '0xC02aaA39b223FE8D0A0E5C4F27eAD9083C756Cc2', network: 'ethereum' },
  { address: '0x0000000000000000000000000000000000001010', network: 'polygon' },
];

const FLAG_CLASSES: Record<'green' | 'orange' | 'red', string> = {
  green: 'bg-emerald-500/10 text-emerald-400 border-emerald-400/40',
  orange: 'bg-amber-500/10 text-amber-300 border-amber-400/40',
  red: 'bg-rose-500/10 text-rose-300 border-rose-400/40',
};

export function TokenAnalysisDashboard({ defaultMint = '' }: Props) {
  const [mint, setMint] = useState(defaultMint);
  const [report, setReport] = useState<RiskReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [intel, setIntel] = useState<TokenIntelResponse | null>(null);
  const [intelTokens, setIntelTokens] = useState<IntelToken[]>(DEMO_TOKENS);
  const [intelLoading, setIntelLoading] = useState(false);
  const [intelError, setIntelError] = useState<string | null>(null);
  const [intelFetchedAt, setIntelFetchedAt] = useState<string | null>(null);

  const sentimentColor = useMemo(() => {
    if (!report) return 'text-slate-500';
    if (report.overall < 3) return 'text-emerald-600';
    if (report.overall < 7) return 'text-amber-500';
    return 'text-rose-600';
  }, [report]);

  const origin = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000';

  const buildQuery = (tokens: IntelToken[]) =>
    tokens
      .map((token) => `token=${encodeURIComponent(`${token.network}:${token.address}`)}`)
      .join('&');

  const curlGetSnippet = useMemo(() => {
    const query = buildQuery(intelTokens);
    return `curl "${origin}/api/token/analysis${query ? `?${query}` : ''}"`;
  }, [intelTokens, origin]);

  const curlPostSnippet = useMemo(() => {
    const payload = JSON.stringify({ tokens: intelTokens }, null, 2).replace(/"/g, '\"');
    return [
      `curl -X POST "${origin}/api/token/analysis"`,
      '  -H "Content-Type: application/json"',
      `  -d "${payload}"`,
    ].join('\n');
  }, [intelTokens, origin]);

  const analyzeToken = async () => {
    const trimmed = mint.trim();
    if (!trimmed) {
      setError('Enter a token mint address.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/token/risk/${trimmed}`);
      if (!res.ok) throw new Error(`Request failed (${res.status})`);
      const json = await res.json();
      setReport(json);
    } catch (err) {
      setError((err as Error).message);
      setReport(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchIntel = async () => {
    setIntelLoading(true);
    setIntelError(null);
    try {
      const query = buildQuery(intelTokens.length ? intelTokens : DEMO_TOKENS);
      const res = await fetch(`/api/token/analysis${query ? `?${query}` : ''}`);
      if (!res.ok) throw new Error(`Request failed (${res.status})`);
      const json = await res.json();
      if (Array.isArray(json?.tokens) && json.tokens.length) {
        const parsedTokens = json.tokens
          .map((token: any) => ({
            address: String(token.address ?? token.mint ?? ''),
            network: String(token.network ?? 'solana').toLowerCase(),
          }))
          .filter(
            (token: any): token is IntelToken =>
              token.address.length >= 8 && ['solana', 'ethereum', 'polygon'].includes(token.network),
          );
        if (parsedTokens.length) {
          setIntelTokens(parsedTokens);
        }
      }
      setIntel(json?.data ?? null);
      setIntelFetchedAt(new Date().toISOString());
    } catch (err) {
      setIntelError((err as Error).message);
      setIntel(null);
    } finally {
      setIntelLoading(false);
    }
  };

  return (
    <section className="mt-8 space-y-6">
      <div className="flex flex-col md:flex-row gap-4">
        <input
          value={mint}
          onChange={(e) => setMint(e.target.value)}
          placeholder="Enter token mint address"
          className="flex-1 min-w-0 border border-slate-300 rounded px-3 py-2 text-sm"
        />
        <button
          onClick={analyzeToken}
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white px-4 py-2 rounded text-sm"
        >
          {loading ? 'Analyzing…' : 'Analyze Token'}
        </button>
      </div>

      {error && <div className="p-3 border border-rose-400 bg-rose-50 text-rose-700 text-sm rounded">{error}</div>}

      {report && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="lg:col-span-3 p-5 bg-white border rounded shadow-sm">
            <h3 className="font-semibold text-lg mb-3">⚠️ Overall Risk Score</h3>
            <p className={`text-3xl font-bold ${sentimentColor}`}>{report.overall ?? '—'} / 10</p>
            <p className="text-xs text-slate-500 mt-2">Lower scores indicate lower risk. Scores are heuristics only.</p>
          </div>

          <div className="p-5 bg-white border rounded shadow-sm space-y-2">
            <h4 className="font-semibold text-base">📊 Tokenomics Risk</h4>
            <p className="text-2xl font-bold">{report.categories.tokenomics ?? '—'} / 10</p>
            <div className="text-sm text-slate-600 space-y-1">
              <p>Total holders: {report.holders?.totalHolders ?? '—'}</p>
              <p>Top 10 concentration: {report.holders?.distribution.top10Percentage?.toFixed(2) ?? '—'}%</p>
              <p>Gini coefficient: {report.holders?.distribution.giniCoefficient?.toFixed(3) ?? '—'}</p>
            </div>
          </div>

          <div className="p-5 bg-white border rounded shadow-sm space-y-2">
            <h4 className="font-semibold text-base">💧 Liquidity Risk</h4>
            <p className="text-2xl font-bold">{report.categories.liquidity ?? '—'} / 10</p>
            <div className="text-sm text-slate-600 space-y-1">
              <p>24h Volume: ${report.liquidity?.trading.volume24h?.toLocaleString() ?? '—'}</p>
              <p>Pools reported: {Array.isArray(report.liquidity?.pools) ? report.liquidity?.pools.length : '—'}</p>
            </div>
          </div>

          <div className="p-5 bg-white border rounded shadow-sm space-y-2">
            <h4 className="font-semibold text-base">🔒 Security Risk</h4>
            <p className="text-2xl font-bold">{report.categories.security ?? '—'} / 10</p>
            <div className="text-sm text-slate-600 space-y-1">
              <p>Mint authority: {report.audit?.permissions?.canMint ? 'Present' : 'Revoked'}</p>
              <p>Freeze authority: {report.audit?.permissions?.canFreeze ? 'Present' : 'Revoked'}</p>
            </div>
          </div>

          <div className="p-5 bg-white border rounded shadow-sm lg:col-span-3">
            <h4 className="font-semibold text-base mb-2">🚨 Critical Flags</h4>
            {report.flags.critical.length ? (
              <ul className="list-disc list-inside text-sm text-rose-600 space-y-1">
                {report.flags.critical.map((flag, idx) => (
                  <li key={idx}>{flag}</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500">No critical flags detected.</p>
            )}
          </div>

          {report.flags.warnings.length > 0 && (
            <div className="p-5 bg-amber-50 border border-amber-200 rounded shadow-sm lg:col-span-3">
              <h4 className="font-semibold text-base mb-2 text-amber-700">⚠️ Warnings</h4>
              <ul className="list-disc list-inside text-sm text-amber-700 space-y-1">
                {report.flags.warnings.map((flag, idx) => (
                  <li key={idx}>{flag}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="p-5 bg-white border rounded shadow-sm lg:col-span-3">
            <h4 className="font-semibold text-base mb-2">💡 Recommendations</h4>
            <ul className="list-disc list-inside text-sm text-slate-600 space-y-1">
              {report.recommendations.map((rec, idx) => (
                <li key={idx}>{rec}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">Token Intelligence Snapshot</h3>
            <p className="text-sm text-slate-600">
              Fetch aggregated risk, liquidity, and ranking insights through the `/api/token/analysis` endpoint.
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={fetchIntel}
              disabled={intelLoading}
              className="rounded border border-indigo-200 bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {intelLoading ? 'Fetching…' : 'Fetch Demo Tokens'}
            </button>
          </div>
        </div>

        {intelError && (
          <div className="mt-4 rounded border border-rose-300 bg-rose-50 p-3 text-sm text-rose-700">
            {intelError}
          </div>
        )}

        {intel && (
          <div className="mt-6 grid grid-cols-1 gap-4 xl:grid-cols-3">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <h4 className="text-sm font-semibold text-slate-700">Ranking Order</h4>
              <ol className="mt-3 space-y-2 text-sm text-slate-600">
                {intel.ranking.map((address, idx) => {
                  const token = intel.tokens.find((item) => item.address === address);
                  return (
                    <li key={address} className="flex items-center justify-between gap-3">
                      <span className="font-medium text-slate-700">#{idx + 1}</span>
                      <div className="flex-1">
                        <p className="font-medium text-slate-800">{token?.name ?? address.slice(0, 6)}</p>
                        <p className="text-xs uppercase text-slate-500">{token?.network ?? 'unknown'}</p>
                      </div>
                      <span className="font-mono text-xs text-slate-500">{token?.risk?.level?.toUpperCase() ?? '—'}</span>
                    </li>
                  );
                })}
              </ol>
              <p className="mt-4 text-xs text-slate-500">
                Last fetched: {intelFetchedAt ? new Date(intelFetchedAt).toLocaleTimeString() : '—'}
              </p>
            </div>

            <div className="xl:col-span-2 space-y-4">
              {intel.tokens.map((token) => (
                <div
                  key={`${token.network}:${token.address}`}
                  className="rounded-2xl border border-slate-200 p-4 shadow-sm"
                >
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <h4 className="text-base font-semibold text-slate-900">
                        {token.name ?? token.address.slice(0, 6)}{' '}
                        <span className="text-sm text-slate-500">({token.symbol ?? '—'})</span>
                      </h4>
                      <p className="text-xs text-slate-500">{token.network.toUpperCase()} · Risk {token.risk.level.toUpperCase()}</p>
                    </div>
                    <span
                      className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium ${FLAG_CLASSES[token.liquidity.flag]}`}
                    >
                      Liquidity flag: {token.liquidity.flag}
                    </span>
                  </div>
                  <div className="mt-4 grid gap-3 text-sm text-slate-600 md:grid-cols-2">
                    <div className="space-y-1">
                      <p>
                        Risk score:{' '}
                        <span className="font-semibold text-slate-900">
                          {Number(token.risk.score ?? 0).toFixed(2)}
                        </span>
                      </p>
                      <p>
                        Ranking score:{' '}
                        <span className="font-semibold text-slate-900">
                          {Number(token.rankingScore ?? 0).toFixed(2)}
                        </span>
                      </p>
                      <p>
                        Proof: <span className="font-semibold uppercase text-slate-900">{token.proofMechanism}</span>
                      </p>
                    </div>
                    <div className="space-y-1">
                      <p>
                        Liquid USD: <span className="font-mono">${token.liquidity.liquidUSD.toLocaleString()}</span>
                      </p>
                      <p>
                        Frozen USD: <span className="font-mono">${token.liquidity.frozenUSD.toLocaleString()}</span>
                      </p>
                      <p className="text-xs text-slate-500">{token.summary}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <h4 className="text-sm font-semibold text-slate-700">GET via curl</h4>
            <pre className="mt-2 overflow-x-auto rounded bg-slate-900/90 p-3 text-xs text-slate-100">{curlGetSnippet}</pre>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <h4 className="text-sm font-semibold text-slate-700">POST via curl</h4>
            <pre className="mt-2 whitespace-pre-wrap overflow-x-auto rounded bg-slate-900/90 p-3 text-xs text-slate-100">{curlPostSnippet}</pre>
          </div>
        </div>
      </div>
    </section>
  );
}
