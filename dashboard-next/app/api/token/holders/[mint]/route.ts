import { NextResponse } from 'next/server';
import sol from '../../../../../lib/solana-client';

export async function GET(request: Request, { params }: { params: { mint: string } }) {
  const { mint } = params;
  try {
    const supply = await sol.getTokenSupply(mint);
    const totalSupply = Number(supply?.amount || 0);
    const largest = await sol.getTokenLargestAccounts(mint);

    // normalize holders
    const holders = (largest || []).map((h: any) => ({ address: h.address, amount: Number(h.amount) }));

    const top10Percentage = sol.calculateTopNPercentage(holders, totalSupply, 10);
    const gini = sol.calculateGiniCoefficient(holders);
    const avg = sol.calculateAverageBalance(holders);

    const topHolders = holders.slice(0, 10).map(h => ({ address: h.address, balance: h.amount, percentage: totalSupply ? (h.amount / totalSupply) * 100 : 0, isProgram: false }));

    // placeholder for recent large transfers (requires indexer) — return empty array for now
    const recentLargeTransfers: any[] = [];

    return NextResponse.json({
      totalHolders: holders.length,
      topHolders,
      distribution: {
        giniCoefficient: gini,
        top10Percentage,
        averageBalance: avg
      },
      whaleAnalysis: {
        whales: topHolders.filter(h => h.percentage > 5),
        recentLargeTransfers
      }
    });
  } catch (err: any) {
    return NextResponse.json({ error: String(err.message || err) }, { status: 500 });
  }
}
