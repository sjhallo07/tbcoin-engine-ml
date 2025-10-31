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

export function TokenAnalysisDashboard({ defaultMint = '' }: Props) {
  const [mint, setMint] = useState(defaultMint);
  const [report, setReport] = useState<RiskReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sentimentColor = useMemo(() => {
    if (!report) return 'text-slate-500';
    if (report.overall < 3) return 'text-emerald-600';
    if (report.overall < 7) return 'text-amber-500';
    return 'text-rose-600';
  }, [report]);

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
    </section>
  );
}
