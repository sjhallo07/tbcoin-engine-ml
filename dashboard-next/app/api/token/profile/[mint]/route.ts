import { NextResponse } from 'next/server';
import sol from '../../../../../lib/solana-client';

export async function GET(request: Request, { params }: { params: { mint: string } }) {
  const { mint } = params;
  try {
    const supply = await sol.getTokenSupply(mint);
    const largest = await sol.getTokenLargestAccounts(mint);
    const metadata = await sol.getTokenMetadata(mint);

    return NextResponse.json({
      basicInfo: {
        mintAddress: mint,
        decimals: supply?.decimals ?? null,
        totalSupply: supply?.amount ?? null,
        totalSupplyUi: supply?.uiAmountString ?? null,
        topAccounts: largest?.slice(0, 10) ?? []
      },
      metadata
    });
  } catch (err: any) {
    return NextResponse.json({ error: String(err.message || err) }, { status: 500 });
  }
}
