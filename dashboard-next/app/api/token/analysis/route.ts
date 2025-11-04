import { NextRequest, NextResponse } from 'next/server';

import {
  getTokenAnalysis,
  postTokenAnalysis,
  type TokenAnalysisOptions,
  type SupportedNetwork,
} from '../../../../lib/token-analysis';

const FALLBACK_TOKENS: Array<{ address: string; network: SupportedNetwork }> = [
  { address: 'So11111111111111111111111111111111111111112', network: 'solana' },
  { address: '0xC02aaA39b223FE8D0A0E5C4F27eAD9083C756Cc2', network: 'ethereum' },
  { address: '0x0000000000000000000000000000000000001010', network: 'polygon' },
];

function parseTokens(searchParams: URLSearchParams) {
  const tokenParams = searchParams.getAll('token');
  if (tokenParams.length === 0) {
    const singleAddress = searchParams.get('address');
    const network = (searchParams.get('network') as SupportedNetwork | null) || null;
    if (singleAddress && network) {
      return [{ address: singleAddress, network }];
    }
    return FALLBACK_TOKENS;
  }

  const tokens: Array<{ address: string; network: SupportedNetwork }> = [];
  for (const token of tokenParams) {
    const [network, address] = token.split(':');
    if (address && isSupportedNetwork(network)) {
      tokens.push({ address, network });
    }
  }
  return tokens.length ? tokens : FALLBACK_TOKENS;
}

function parseOptions(searchParams: URLSearchParams): TokenAnalysisOptions {
  const options: TokenAnalysisOptions = {};
  const minLiquidity = searchParams.get('minLiquidityUSD');
  if (minLiquidity) {
    const parsed = Number(minLiquidity);
    if (Number.isFinite(parsed)) options.minLiquidityUSD = parsed;
  }
  const liquidityFloor = searchParams.get('liquidityFloorUSD');
  if (liquidityFloor) {
    const parsed = Number(liquidityFloor);
    if (Number.isFinite(parsed)) options.liquidityFloorUSD = parsed;
  }
  const concentration = searchParams.get('concentrationThreshold');
  if (concentration) {
    const parsed = Number(concentration);
    if (Number.isFinite(parsed)) options.concentrationThreshold = parsed;
  }
  return options;
}

function isSupportedNetwork(value: string | null): value is SupportedNetwork {
  return value === 'solana' || value === 'ethereum' || value === 'polygon';
}

export async function GET(request: NextRequest) {
  try {
    const tokens = parseTokens(request.nextUrl.searchParams);
    const options = parseOptions(request.nextUrl.searchParams);
    const payload = await getTokenAnalysis(tokens, options);
    return NextResponse.json({ status: 'success', data: payload, tokens });
  } catch (error) {
    console.error('[token/analysis] GET failed', error);
    return NextResponse.json(
      { status: 'error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 },
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const tokens = Array.isArray(body?.tokens) ? body.tokens : null;
    if (!tokens || !tokens.length) {
      return NextResponse.json(
        { status: 'error', message: 'tokens array is required' },
        { status: 400 },
      );
    }

    const parsedTokens = tokens
      .map((token: any) => ({
        address: String(token?.address ?? ''),
        network: token?.network as SupportedNetwork,
      }))
      .filter((token) => token.address.length >= 8 && isSupportedNetwork(token.network));

    if (!parsedTokens.length) {
      return NextResponse.json(
        { status: 'error', message: 'No valid tokens supplied' },
        { status: 400 },
      );
    }

    const options: TokenAnalysisOptions = body?.options ?? {};
    const payload = await postTokenAnalysis(parsedTokens, options);
    const { status: _ignoredStatus, ...responsePayload } = payload;
    return NextResponse.json({ status: 'success', ...responsePayload });
  } catch (error) {
    console.error('[token/analysis] POST failed', error);
    return NextResponse.json(
      { status: 'error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 },
    );
  }
}
