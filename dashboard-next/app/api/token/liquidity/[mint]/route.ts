import { NextResponse } from 'next/server';
import sol from '../../../../../lib/solana-client';

export async function GET(request: Request, { params }: { params: { mint: string } }) {
  const { mint } = params;
  try {
    const pools = await sol.getLiquidityPoolsFromJupiter(mint);

    // try Dexscreener for trading data (chain prefix 'solana:')
    let trading = null;
    try {
      const r = await fetch(`https://api.dexscreener.com/latest/dex/tokens/solana:${mint}`);
      if (r.ok) trading = await r.json();
    } catch (e) {
      trading = null;
    }

    // basic concentration metrics (best-effort)
    const concentration = {
      topPoolPercentage: null,
      lpLocked: null,
      lpConcentration: null
    };

    return NextResponse.json({ pools, trading, concentration });
  } catch (err: any) {
    return NextResponse.json({ error: String(err.message || err) }, { status: 500 });
  }
}
