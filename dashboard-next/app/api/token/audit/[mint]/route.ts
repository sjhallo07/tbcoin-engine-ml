import { NextResponse } from 'next/server';
import sol from '../../../../../lib/solana-client';

export async function GET(request: Request, { params }: { params: { mint: string } }) {
  const { mint } = params;
  try {
    const metadata = await sol.getTokenMetadata(mint);
    // try RPC account info for mint (may need binary parsing for full details)
    const mintAccount = await sol.getAccountInfo(mint).catch(() => null);

    const authorities: any = {
      mintAuthority: null,
      freezeAuthority: null,
      updateAuthority: metadata?.updateAuthority ?? null
    };

    // try to extract parsed info when RPC provides it
    if (mintAccount?.data?.parsed?.info) {
      const info = mintAccount.data.parsed.info;
      authorities.mintAuthority = info.mintAuthority || null;
      authorities.freezeAuthority = info.freezeAuthority || null;
    }

    const permissions = {
      canMint: !!authorities.mintAuthority,
      canFreeze: !!authorities.freezeAuthority,
      canUpdate: !!authorities.updateAuthority
    };

    const programAnalysis = {
      programId: mintAccount?.owner || null,
      isToken2022: false,
      customLogic: null
    };

    // security flags (best-effort)
    const securityFlags = {
      revokedAuthorities: false,
      suspiciousPermissions: false,
      blacklisted: false
    };

    return NextResponse.json({ authorities, permissions, programAnalysis, securityFlags, metadata });
  } catch (err: any) {
    return NextResponse.json({ error: String(err.message || err) }, { status: 500 });
  }
}
