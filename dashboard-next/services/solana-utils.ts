import { Connection, PublicKey, clusterApiUrl } from '@solana/web3.js'

import { getTokenMetadata } from '../lib/solana-client'

export const DEFAULT_SOLANA_RPC = clusterApiUrl('mainnet-beta')

export function getSolanaRpcUrl(): string {
  return process.env.SOLANA_RPC_URL || DEFAULT_SOLANA_RPC
}

export function createSolanaConnection(commitment: 'finalized' | 'confirmed' | 'processed' = 'confirmed'): Connection {
  return new Connection(getSolanaRpcUrl(), commitment)
}

export function toPublicKey(address: string): PublicKey {
  try {
    return new PublicKey(address)
  } catch (error) {
    throw new Error(`Invalid Solana address: ${address}`)
  }
}

export interface TokenDisplayInfo {
  name: string
  symbol: string
  logo: string | null
}

const SOL_MINT_ADDRESSES = new Set([
  'So11111111111111111111111111111111111111112',
  '11111111111111111111111111111111'
])

const SOL_FALLBACK_INFO: TokenDisplayInfo = {
  name: 'Solana',
  symbol: 'SOL',
  logo: 'https://assets.coingecko.com/coins/images/4128/large/solana.png?1640133422'
}

/**
 * Retrieve display metadata for a Solana token.
 *
 * @param identifier Mint address or ticker symbol for the token.
 * @returns Normalised display information (name, symbol, logo URL when available).
 *
 * @throws Error when the identifier is missing or only whitespace.
 *
 * Notes:
 * - Uses Solscan public API under the hood; if unavailable, returns a best-effort fallback.
 * - Respects the `SOLANA_RPC_URL` env var for connection defaults, though metadata lookups rely on Solscan.
 */
export async function fetchTokenDisplayInfo(identifier: string): Promise<TokenDisplayInfo> {
  if (!identifier) {
    throw new Error('Token identifier (mint or symbol) is required')
  }

  const normalised = identifier.trim()
  if (!normalised) {
    throw new Error('Token identifier (mint or symbol) cannot be empty')
  }

  if (SOL_MINT_ADDRESSES.has(normalised) || normalised.toUpperCase() === 'SOL') {
    return SOL_FALLBACK_INFO
  }

  const metadata = await getTokenMetadata(normalised).catch((error) => {
    console.warn('[solana-utils] token metadata fetch failed', normalised, error)
    return null
  })

  if (metadata) {
    return {
      name: metadata.name ?? normalised,
      symbol: metadata.symbol ?? normalised.slice(0, 8).toUpperCase(),
      logo: metadata.image ?? null
    }
  }

  // Fallback minimal display info when metadata is unavailable
  return {
    name: normalised,
    symbol: normalised.slice(0, 8).toUpperCase(),
    logo: null
  }
}
