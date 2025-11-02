import {
  calculateAverageBalance,
  calculateGiniCoefficient,
  calculateTopNPercentage,
  getAccountInfo,
  getTokenLargestAccounts,
  getTokenMetadata,
  getTokenSupply
} from '../lib/solana-client'
import { getRealMarketData, type MarketData } from './real-market-data'
import { performRealAnalysis, type AnalysisResult } from './real-analysis-engine'

const TOKEN_2022_PROGRAM_ID = 'TokenzQdBJF4jipnsnVFo4x1tFSCs9DJG7kzbjGBPmCz'
const TOKEN_PROGRAM_ID = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'

export type TokenProfile = {
  basicInfo: {
    mintAddress: string
    name: string | null
    symbol: string | null
    decimals: number | null
    totalSupplyRaw: string | null
    totalSupplyUi: number | null
    creator: string | null
    created: string | null
  }
  metadata: {
    uri: string | null
    image: string | null
    description: string | null
    externalUrl: string | null
    updateAuthority: string | null
  }
}

export type HolderAccount = {
  rank: number
  address: string
  rawAmount: number
  uiAmount: number
  percentage: number
  isProgram: boolean
  owner?: string | null
}

export type HolderAnalysis = {
  totalHolders: number
  topHolders: HolderAccount[]
  distribution: {
    giniCoefficient: number
    top10Percentage: number
    averageBalance: number
  }
  whaleAnalysis: {
    whales: HolderAccount[]
    recentLargeTransfers: Array<{
      signature: string
      amount: number
      source?: string | null
      destination?: string | null
      timestamp?: string | null
    }>
    recentLargeTransfersFetchFailed?: boolean
  }
}

export type LiquidityPoolSnapshot = {
  name: string
  exchange: string
  liquidityUsd: number
  volume24h: number
  txns24h: number
  price?: number
  url?: string
  lockedUsd?: number
}

export type LiquidityAnalysis = {
  marketData: MarketData
  pools: LiquidityPoolSnapshot[]
  trading: {
    volume24h: number
    priceChange24h: number
    trades24h: number
    price?: number
  }
  concentration: {
    topPoolPercentage: number | null
    lpLockedPercentage: number | null
    lpConcentration: string | null
  }
  notes: string[]
}

export type ContractAudit = {
  authorities: {
    mintAuthority: string | null
    freezeAuthority: string | null
    updateAuthority: string | null
  }
  permissions: {
    canMint: boolean
    canFreeze: boolean
    canUpdate: boolean
  }
  programAnalysis: {
    programId: string | null
    isToken2022: boolean
    customLogic: string | null
  }
  securityFlags: {
    revokedAuthorities: boolean
    suspiciousPermissions: boolean
    blacklisted: boolean
  }
}

export type RiskCategories = {
  tokenomics: number
  liquidity: number
  security: number
  social: number
}

export type RiskReport = {
  overall: number
  categories: RiskCategories
  flags: {
    critical: string[]
    warnings: string[]
  }
  recommendations: string[]
  profile: TokenProfile
  holders: HolderAnalysis
  liquidity: LiquidityAnalysis
  audit: ContractAudit
  market?: {
    data: MarketData
    analysis: AnalysisResult
  }
}

function safeNumber(value: unknown, fallback = 0): number {
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value === 'string') {
    const parsed = Number(value)
    return Number.isFinite(parsed) ? parsed : fallback
  }
  return fallback
}

export async function fetchTokenProfile(mint: string): Promise<TokenProfile> {
  const [supply, metadata, accountInfo] = await Promise.all([
    getTokenSupply(mint).catch(() => null),
    getTokenMetadata(mint).catch(() => null),
    getAccountInfo(mint).catch(() => null)
  ])

  const decimals = supply?.decimals ?? accountInfo?.data?.parsed?.info?.decimals ?? null
  const totalSupplyRaw = supply?.amount ?? accountInfo?.data?.parsed?.info?.supply ?? null
  let totalSupplyUi: number | null = null
  if (typeof supply?.uiAmountString === 'string') {
    const parsed = Number(supply.uiAmountString)
    totalSupplyUi = Number.isFinite(parsed) ? parsed : null
  } else if (decimals != null && totalSupplyRaw) {
    const parsedRaw = Number(totalSupplyRaw)
    if (Number.isFinite(parsedRaw)) {
      totalSupplyUi = parsedRaw / Math.pow(10, decimals)
    }
  }

  return {
    basicInfo: {
      mintAddress: mint,
      name: metadata?.name ?? null,
      symbol: metadata?.symbol ?? null,
      decimals,
      totalSupplyRaw: totalSupplyRaw ?? null,
      totalSupplyUi: typeof totalSupplyUi === 'number' ? totalSupplyUi : null,
      creator: metadata?.updateAuthority ?? accountInfo?.data?.parsed?.info?.mintAuthority ?? null,
      created: metadata?.createdAt
        ? new Date(
            metadata.createdAt < 1e12
              ? metadata.createdAt * 1000
              : metadata.createdAt
          ).toISOString()
        : null
    },
    metadata: {
      uri: metadata?.uri ?? null,
      image: metadata?.image ?? null,
      description: metadata?.description ?? null,
      externalUrl: metadata?.externalUrl ?? null,
      updateAuthority: metadata?.updateAuthority ?? null
    }
  }
}

async function identifyProgramAccounts(addresses: string[]): Promise<Record<string, string | null>> {
  const lookups = await Promise.all(
    addresses.map((address) =>
      getAccountInfo(address)
        .then((info) => info?.owner ?? info?.data?.owner ?? null)
        .catch(() => null)
    )
  )

  const owners: Record<string, string | null> = {}
  addresses.forEach((address, idx) => {
    owners[address] = lookups[idx] ?? null
  })
  return owners
}

async function fetchRecentTransfers(mint: string): Promise<HolderAnalysis['whaleAnalysis']['recentLargeTransfers'] | null> {
  try {
    const res = await fetch(`https://public-api.solscan.io/account/splTransfers?address=${mint}&limit=5`)
    if (!res.ok) return null
    const payload = await res.json()
    const transfers = Array.isArray(payload?.data) ? payload.data : Array.isArray(payload) ? payload : []
    return transfers.map((transfer: any) => ({
      signature: transfer.txHash ?? transfer.signature ?? '',
      amount: safeNumber(transfer.changeAmount ?? transfer.amount ?? 0, 0),
      source: transfer.source ?? transfer.from ?? null,
      destination: transfer.destination ?? transfer.to ?? null,
      timestamp: transfer.blockTime ? new Date(transfer.blockTime * 1000).toISOString() : null
    }))
  } catch (error) {
    console.warn('[token-analysis] recent transfer lookup failed', error)
    return null
  }
}

export async function fetchHolderAnalysis(mint: string, profile?: TokenProfile): Promise<HolderAnalysis> {
  let supplyUi = profile?.basicInfo.totalSupplyUi ?? null
  if (supplyUi == null) {
    const supply = await getTokenSupply(mint).catch(() => null)
    supplyUi = safeNumber(supply?.uiAmountString ?? 0)
  }

  const supplyInfo = supplyUi || 0
  const largestAccounts = await getTokenLargestAccounts(mint).catch(() => [])

  const holders = (largestAccounts || []).map((account: any, idx: number) => {
    const uiAmount = safeNumber(account.uiAmount ?? account.uiAmountString ?? account.amount)
    const percentage = supplyInfo > 0 ? (uiAmount / supplyInfo) * 100 : 0
    return {
      rank: idx + 1,
      address: account.address,
      rawAmount: safeNumber(account.amount),
      uiAmount,
      percentage
    }
  })
  const topAddresses = holders.slice(0, 10).map((h) => h.address)
  const ownerMap = await identifyProgramAccounts(topAddresses)
  const enrichedHolders = holders.map((holder) => ({
    ...holder,
    owner: ownerMap[holder.address] ?? null,
    isProgram: Boolean(
      ownerMap[holder.address] &&
      ownerMap[holder.address] !== TOKEN_PROGRAM_ID &&
      ownerMap[holder.address] !== TOKEN_2022_PROGRAM_ID
    )
  }))
  const topTen = enrichedHolders.slice(0, 10)
  const topAmounts = topTen.map((holder) => ({ amount: holder.uiAmount }))

  const distribution = {
    giniCoefficient: calculateGiniCoefficient(enrichedHolders.map((holder) => ({ amount: holder.uiAmount }))),
    top10Percentage: calculateTopNPercentage(topAmounts, supplyInfo, 10),
    averageBalance: calculateAverageBalance(enrichedHolders.map((holder) => ({ amount: holder.uiAmount })))
  }

  const recentLargeTransfersRaw = await fetchRecentTransfers(mint)
  const recentLargeTransfers = Array.isArray(recentLargeTransfersRaw) ? recentLargeTransfersRaw : []

  return {
    totalHolders: largestAccounts?.length ?? 0,
    topHolders: topTen,
    distribution,
    whaleAnalysis: {
      whales: topTen.filter((holder) => holder.percentage > 5),
      recentLargeTransfers,
      recentLargeTransfersFetchFailed: recentLargeTransfersRaw === null
    }
  }
}

async function fetchDexscreenerPairs(mint: string) {
  try {
    const res = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${mint}`)
    if (!res.ok) return []
    const payload = await res.json()
    const pairs = Array.isArray(payload?.pairs) ? payload.pairs : []
    return pairs
  } catch (error) {
    console.warn('[token-analysis] dex screener lookup failed', error)
    return []
  }
}

function summarisePools(pairs: any[]): LiquidityPoolSnapshot[] {
  return pairs.map((pair) => ({
    name: `${pair.baseToken?.symbol ?? 'Token'}/${pair.quoteToken?.symbol ?? 'SOL'}`,
    exchange: pair.dexId ?? 'unknown',
    liquidityUsd: safeNumber(pair.liquidity?.usd ?? pair.liquidityUsd, 0),
    volume24h: safeNumber(pair.volume?.h24 ?? pair.volume24h, 0),
    txns24h: safeNumber(pair.txns?.h24 ?? pair.txns24h, 0),
    price: (() => {
      const raw = pair.priceUsd ?? pair.priceNative
      const parsed = Number(raw)
      return Number.isFinite(parsed) ? parsed : undefined
    })(),
    url: pair.url ?? null,
    lockedUsd: (() => {
      const raw = pair.liquidityLockedUsd ?? pair.liquidity?.lockedUsd
      const parsed = Number(raw)
      return Number.isFinite(parsed) ? parsed : 0
    })()
  }))
}

function computeConcentration(pools: LiquidityPoolSnapshot[]) {
  if (!pools.length) {
    return {
      topPoolPercentage: null,
      lpLockedPercentage: null,
      lpConcentration: null
    }
  }

  const sorted = [...pools].sort((a, b) => b.liquidityUsd - a.liquidityUsd)
  const totalLiquidity = sorted.reduce((sum, pool) => sum + pool.liquidityUsd, 0)
  const topPoolPercentage = totalLiquidity > 0 ? (sorted[0].liquidityUsd / totalLiquidity) * 100 : null

  const concentrationLabel = topPoolPercentage != null
    ? topPoolPercentage > 60
      ? 'high'
      : topPoolPercentage > 30
      ? 'moderate'
      : 'diversified'
    : null

  const lockedTotal = pools.reduce((sum, pool) => sum + (pool.lockedUsd ?? 0), 0)
  const lpLockedPercentage = totalLiquidity > 0 ? (lockedTotal / totalLiquidity) * 100 : null

  return {
    topPoolPercentage,
    lpLockedPercentage,
    lpConcentration: concentrationLabel
  }
}

export async function fetchLiquidityAnalysis(mint: string, profile?: TokenProfile): Promise<LiquidityAnalysis> {
  const [pairs, marketDataRaw] = await Promise.all([
    fetchDexscreenerPairs(mint),
    getRealMarketData(profile?.basicInfo.symbol ?? 'UNKNOWN', mint)
  ])

  const pools = summarisePools(pairs)
  const tradingVolume = pools.reduce((sum, pool) => sum + pool.volume24h, 0)
  const priceChanges = pairs
    .map((pair) => safeNumber(pair.priceChange?.h24 ?? pair.priceChange24h, 0))
    .filter((value) => Number.isFinite(value))

  const priceChange24h = priceChanges.length
    ? priceChanges.reduce((sum, change) => sum + change, 0) / priceChanges.length
    : marketDataRaw.priceChange24h

  const trades24h = pools.reduce((sum, pool) => sum + pool.txns24h, 0)
  const concentration = computeConcentration(pools)

  const notes: string[] = []
  if (!pools.length) notes.push('No DEX liquidity pairs found; token may be illiquid or new.')
  if (concentration.topPoolPercentage && concentration.topPoolPercentage > 60) {
    notes.push('Liquidity heavily concentrated in a single pool.')
  }
  if (tradingVolume === 0 && marketDataRaw.volume24h > 0) {
    notes.push('Volume sourced from aggregated market data; DEX pair data unavailable.')
  }

  const marketData: MarketData = {
    ...marketDataRaw,
    volume24h: marketDataRaw.volume24h || tradingVolume
  }

  return {
    marketData,
    pools,
    trading: {
      volume24h: tradingVolume || marketData.volume24h,
      priceChange24h,
      trades24h,
      price: marketData.price
    },
    concentration,
    notes
  }
}

export async function fetchContractAudit(mint: string, profile?: TokenProfile): Promise<ContractAudit> {
  const accountInfo = await getAccountInfo(mint).catch(() => null)
  const metadata = profile?.metadata ?? (await getTokenMetadata(mint).catch(() => null))
  const parsedInfo = accountInfo?.data?.parsed?.info ?? {}

  const mintAuthority = parsedInfo.mintAuthority ?? null
  const freezeAuthority = parsedInfo.freezeAuthority ?? null
  const updateAuthority = metadata?.updateAuthority ?? null
  const programId = accountInfo?.owner ?? null

  const permissions = {
    canMint: Boolean(mintAuthority),
    canFreeze: Boolean(freezeAuthority),
    canUpdate: Boolean(updateAuthority)
  }

  const securityFlags = {
    revokedAuthorities: !mintAuthority && !freezeAuthority,
    suspiciousPermissions: Boolean(mintAuthority && mintAuthority === freezeAuthority),
    blacklisted: false
  }

  const programAnalysis = {
    programId,
    isToken2022: programId === TOKEN_2022_PROGRAM_ID,
    customLogic: programId && programId !== TOKEN_PROGRAM_ID && programId !== TOKEN_2022_PROGRAM_ID ? 'Custom program detected' : null
  }

  return {
    authorities: {
      mintAuthority,
      freezeAuthority,
      updateAuthority
    },
    permissions,
    programAnalysis,
    securityFlags
  }
}

function scaleScore(value: number, min: number, max: number): number {
  if (Number.isNaN(value)) return 0
  const clamped = Math.min(Math.max(value, min), max)
  const range = max - min || 1
  return ((clamped - min) / range) * 10
}

function calculateTokenomicsRisk(holders: HolderAnalysis): number {
  const top10 = holders.distribution.top10Percentage
  const gini = holders.distribution.giniCoefficient
  const whales = holders.whaleAnalysis.whales.length

  const concentrationScore = scaleScore(top10, 10, 95)
  const giniScore = Math.min(10, Math.round(gini * 10))
  const whalePenalty = Math.min(3, whales)

  return Math.min(10, Math.round((concentrationScore * 0.5) + (giniScore * 0.35) + whalePenalty))
}
const DEFAULT_CONCENTRATION_PENALTY = 4

function calculateLiquidityRisk(liquidity: LiquidityAnalysis): number {
  const volumeScore = scaleScore(Math.log10(liquidity.trading.volume24h + 1), 2, 8)
  const poolPenalty = liquidity.pools.length === 0 ? 10 : liquidity.pools.length === 1 ? 6 : 2
  const concentrationPenalty = liquidity.concentration.topPoolPercentage ? scaleScore(liquidity.concentration.topPoolPercentage, 20, 95) : DEFAULT_CONCENTRATION_PENALTY

  return Math.min(10, Math.round(volumeScore * 0.5 + poolPenalty * 0.3 + concentrationPenalty * 0.2))
}

function calculateSecurityRisk(audit: ContractAudit): number {
  let score = 0
  if (audit.permissions.canMint) score += 4
  if (audit.permissions.canFreeze) score += 2
  if (!audit.securityFlags.revokedAuthorities) score += 2
  if (audit.securityFlags.suspiciousPermissions) score += 2
  if (audit.programAnalysis.customLogic) score += 1
  return Math.min(10, score)
}

function calculateSocialRisk(profile: TokenProfile): number {
  const hasWebsite = Boolean(profile.metadata.externalUrl)
  const hasImage = Boolean(profile.metadata.image)
  const hasDescription = Boolean(profile.metadata.description)

  let score = 5
  if (!hasWebsite) score += 2
  if (!hasImage) score += 1
  if (!hasDescription) score += 1

  if (hasWebsite && hasDescription) score -= 2
  return Math.min(10, Math.max(0, score))
}

function aggregateOverallRisk(categories: RiskCategories): number {
  const weighted = categories.tokenomics * 0.35 + categories.liquidity * 0.3 + categories.security * 0.25 + categories.social * 0.1
  return Math.min(10, Math.round(weighted))
}

function extractHolderFlags(holders: HolderAnalysis) {
  const critical: string[] = []
  const warnings: string[] = []

  if (holders.distribution.top10Percentage > 80) critical.push('High holder concentration (>80% in top 10 wallets)')
  else if (holders.distribution.top10Percentage > 60) warnings.push('Top 10 wallets control majority of supply')

  if (holders.whaleAnalysis.whales.length > 3) warnings.push('Multiple whale wallets detected (>5% supply each)')
  if (
    Array.isArray(holders.whaleAnalysis.recentLargeTransfers) &&
    holders.whaleAnalysis.recentLargeTransfers.length === 0 &&
    !holders.whaleAnalysis.recentLargeTransfersFetchFailed
  ) {
    warnings.push('No transfer history found; verify activity via explorers')
  } else if (holders.whaleAnalysis.recentLargeTransfersFetchFailed) {
    warnings.push('Transfer history unavailable due to API error')
  }

  return { critical, warnings }
}

function extractLiquidityFlags(liquidity: LiquidityAnalysis) {
  const critical: string[] = []
  const warnings: string[] = []

  if (liquidity.trading.volume24h < 1000) critical.push('Extremely low 24h trading volume (<$1k)')
  else if (liquidity.trading.volume24h < 10000) warnings.push('Low 24h trading volume (<$10k)')

  if (liquidity.pools.length === 0) critical.push('No active liquidity pools identified')
  else if (liquidity.concentration.topPoolPercentage && liquidity.concentration.topPoolPercentage > 70) {
    warnings.push('Liquidity heavily concentrated in a single pool')
  }

  return { critical, warnings }
}

function extractSecurityFlags(audit: ContractAudit) {
  const critical: string[] = []
  const warnings: string[] = []

  if (audit.permissions.canMint) critical.push('Mint authority still active; token can be inflated')
  if (audit.permissions.canFreeze) warnings.push('Freeze authority active; accounts could be frozen')
  if (!audit.securityFlags.revokedAuthorities) warnings.push('Authorities not revoked; verify team trust')
  if (audit.securityFlags.suspiciousPermissions) critical.push('Mint and freeze authority controlled by same address')
  if (audit.programAnalysis.customLogic) warnings.push('Custom program detected; review contract source')

  return { critical, warnings }
}

function buildRecommendations(categories: RiskCategories, flags: { critical: string[]; warnings: string[] }): string[] {
  const suggestions = new Set<string>()

  if (categories.liquidity > 6) suggestions.add('Verify liquidity locks and depth before entering positions.')
  if (categories.security > 6) suggestions.add('Request authority revocation or multisig controls from the team.')
  if (categories.tokenomics > 6) suggestions.add('Track whale wallets and set on-chain alerts for large moves.')
  if (categories.social > 6) suggestions.add('Review project documentation and community channels for legitimacy.')

  flags.critical.forEach((flag) => {
    if (flag.includes('Mint authority')) suggestions.add('Avoid large exposure until mint authority is revoked.')
    if (flag.includes('liquidity')) suggestions.add('Use limit orders to mitigate slippage due to low liquidity.')
  })

  if (!suggestions.size) {
    suggestions.add('Maintain standard monitoring and risk management practices.')
  }

  return Array.from(suggestions)
}

export async function buildTokenRiskReport(mint: string): Promise<RiskReport> {
  const profile = await fetchTokenProfile(mint)
  const [holders, liquidity, audit] = await Promise.all([
    fetchHolderAnalysis(mint, profile),
    fetchLiquidityAnalysis(mint, profile),
    fetchContractAudit(mint, profile)
  ])

  const categories: RiskCategories = {
    tokenomics: calculateTokenomicsRisk(holders),
    liquidity: calculateLiquidityRisk(liquidity),
    security: calculateSecurityRisk(audit),
    social: calculateSocialRisk(profile)
  }

  const overall = aggregateOverallRisk(categories)

  const holderFlags = extractHolderFlags(holders)
  const liquidityFlags = extractLiquidityFlags(liquidity)
  const securityFlags = extractSecurityFlags(audit)

  const flags = {
    critical: [...holderFlags.critical, ...liquidityFlags.critical, ...securityFlags.critical],
    warnings: [...holderFlags.warnings, ...liquidityFlags.warnings, ...securityFlags.warnings]
  }

  const recommendations = buildRecommendations(categories, flags)

  let marketAnalysis: AnalysisResult | null = null
  try {
    marketAnalysis = await performRealAnalysis(liquidity.marketData, null)
  } catch (error) {
    console.warn('[token-analysis] market analysis generation failed', error)
  }

  return {
    overall,
    categories,
    flags,
    recommendations,
    profile,
    holders,
    liquidity,
    audit,
    market: marketAnalysis
      ? {
          data: liquidity.marketData,
          analysis: marketAnalysis
        }
      : undefined
  }
}
