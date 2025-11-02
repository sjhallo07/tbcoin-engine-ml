import { NextResponse } from 'next/server'
import { getMint } from '@solana/spl-token'

import { createSolanaConnection, toPublicKey } from '../../../../services/solana-utils'

export async function POST(request: Request) {
  try {
    const { mintAddress } = await request.json().catch(() => ({})) as { mintAddress?: string }

    if (!mintAddress) {
      return NextResponse.json({
        status: 'error',
        error: 'Mint address required'
      }, { status: 400 })
    }

    const connection = createSolanaConnection('confirmed')
    const mintKey = toPublicKey(mintAddress)

    const [mintInfo, largestAccounts] = await Promise.all([
      getMint(connection, mintKey),
      connection.getTokenLargestAccounts(mintKey)
    ])

    const decimals = mintInfo.decimals
    const supply = mintInfo.supply

  const totalSupplyUi = Number(mintInfo.supply) / Math.pow(10, decimals)

    const holders = largestAccounts.value.slice(0, 5).map((account) => {
      const uiAmount = Number(account.uiAmountString ?? account.uiAmount ?? 0)
      const percentage = totalSupplyUi > 0 ? Number(((uiAmount / totalSupplyUi) * 100).toFixed(4)) : 0

      return {
        address: account.address.toBase58(),
        amountRaw: account.amount,
        uiAmount,
        percentage
      }
    })

    return NextResponse.json({
      status: 'success',
      data: {
        mint: mintAddress,
        decimals,
        supply: supply.toString(),
        mintAuthority: mintInfo.mintAuthority?.toBase58?.() || null,
        freezeAuthority: mintInfo.freezeAuthority?.toBase58?.() || null,
        largestHolders: holders,
        isInitialized: mintInfo.isInitialized
      },
      message: 'Real token information fetched successfully'
    })
  } catch (error: any) {
    console.error('[real-token-info] error', error)
    return NextResponse.json({
      status: 'error',
      error: 'Failed to fetch token info',
      message: error?.message || 'Unknown error'
    }, { status: 500 })
  }
}
