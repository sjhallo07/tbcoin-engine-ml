import { NextResponse } from 'next/server';
import sol from '../../../../../lib/solana-client';

async function generateRecommendations(score: number) {
  const recs: string[] = [];
  if (score >= 7) {
    recs.push('High risk: avoid large exposure and monitor on-chain flows.');
  } else if (score >= 4) {
    recs.push('Medium risk: perform additional diligence and watch liquidity.');
  } else {
    recs.push('Low risk: standard monitoring recommended.');
  }
  recs.push('Check LP locking and verify update Authorities on metadata.');
  return recs;
}

export async function GET(request: Request, { params }: { params: { mint: string } }) {
  const { mint } = params;
  try {
    // Gather data in parallel
    const [supply, largest, metadata, pools] = await Promise.all([
      sol.getTokenSupply(mint).catch(() => null),
      sol.getTokenLargestAccounts(mint).catch(() => []),
      sol.getTokenMetadata(mint).catch(() => null),
      sol.getLiquidityPoolsFromJupiter(mint).catch(() => null)
    ]);

    const totalSupply = Number(supply?.amount || 0);
    const holders = (largest || []).map((h: any) => ({ address: h.address, amount: Number(h.amount) }));

    const holdersAnalysis = {
      totalHolders: holders.length,
      distribution: {
        top10Percentage: sol.calculateTopNPercentage(holders, totalSupply, 10),
        giniCoefficient: sol.calculateGiniCoefficient(holders),
        averageBalance: sol.calculateAverageBalance(holders)
      }
    };

    const liquidityAnalysis = {
      pools,
      trading: {
        volume24h: pools?.volume24h || 0
      }
    };

    const audit = {
      permissions: {
        canMint: !!metadata?.updateAuthority, // best-effort proxy
        canFreeze: false
      },
      securityFlags: {}
    };

    const overall = sol.calculateOverallRisk({ metadata, supply }, holdersAnalysis, liquidityAnalysis, audit);

    const categories = {
      tokenomics: Math.round(holdersAnalysis.distribution.top10Percentage / 10),
      liquidity: 10 - Math.min(10, Math.round((liquidityAnalysis.trading.volume24h || 0) / 10000)),
      security: audit.permissions.canMint ? 6 : 2,
      social: 4
    };

    const flags: { critical: string[]; warnings: string[] } = {
      critical: [],
      warnings: []
    };
    if (categories.tokenomics >= 8) flags.critical.push('High holder concentration');
    if ((liquidityAnalysis.trading.volume24h || 0) < 1000) flags.critical.push('Low liquidity');
    if (audit.permissions.canMint) flags.warnings.push('Mint authority present');

    const recommendations = await generateRecommendations(overall);

    return NextResponse.json({ overall, categories, flags, recommendations, holders: holdersAnalysis, liquidity: liquidityAnalysis, audit, profile: { metadata, totalSupply } });
  } catch (err: any) {
    return NextResponse.json({ error: String(err.message || err) }, { status: 500 });
  }
}
