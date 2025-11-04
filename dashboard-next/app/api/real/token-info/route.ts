import { NextResponse } from 'next/server'
import type { ParsedAccountData } from '@solana/web3.js'

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

  const [mintAccountInfo, largestAccounts] = await Promise.all([
    connection.getParsedAccountInfo(mintKey),
    connection.getTokenLargestAccounts(mintKey)
  ])

  if (!mintAccountInfo.value) {
    throw new Error('Mint account not found')
  }

  const accountData = mintAccountInfo.value.data

  if (!accountData || typeof accountData !== 'object' || !('parsed' in accountData)) {
    throw new Error('Unable to parse mint account data')
  }

  const parsedInfo = (accountData as ParsedAccountData).parsed.info as {
    decimals: number
    supply: string
    mintAuthority: string | null
    freezeAuthority: string | null
    isInitialized: boolean
  }

  const { decimals, supply, mintAuthority, freezeAuthority, isInitialized } = parsedInfo

  const holders = (largestAccounts.value ?? []).map((account) => {
    const amount = Number(account.amount)
    const supplyNumber = Number(supply) || 0
    const uiAmount = amount / Math.pow(10, decimals)
    const percentage = supplyNumber > 0 ? amount / supplyNumber : 0

    return {
      address: account.address?.toBase58?.() ?? String(account.address),
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
      supply,
      mintAuthority,
      freezeAuthority,
      largestHolders: holders,
      isInitialized
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
