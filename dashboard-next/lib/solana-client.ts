import { Connection, PublicKey, clusterApiUrl } from '@solana/web3.js'

export type AmountEntry = { amount: number }

export function getRpcUrl(): string
{
    return process.env.SOLANA_RPC_URL || clusterApiUrl('mainnet-beta')
}

export async function getTokenSupply(mint: string): Promise<{ amount: string; decimals: number; uiAmount: number | null; uiAmountString: string | null }>
{
    const connection = new Connection(getRpcUrl(), 'confirmed')
    const pk = new PublicKey(mint)
    const res = await connection.getTokenSupply(pk)
    return res.value as any
}

export async function getTokenLargestAccounts(mint: string)
{
    const connection = new Connection(getRpcUrl(), 'confirmed')
    const pk = new PublicKey(mint)
    const res = await connection.getTokenLargestAccounts(pk)
    // Normalize response to an array of accounts with address, amount and uiAmount
    return (res?.value || []).map((acc) => ({
        address: acc.address?.toBase58?.() ?? '',
        amount: Number(acc.amount),
        uiAmount: typeof acc.uiAmount === 'number' ? acc.uiAmount : Number(acc.uiAmountString || 0),
    }))
}

export async function getAccountInfo(address: string)
{
    const connection = new Connection(getRpcUrl(), 'confirmed')
    const pk = new PublicKey(address)
    const res = await connection.getParsedAccountInfo(pk)
    const value: any = res?.value ?? null
    if (!value) return null
    const owner = value.owner?.toBase58?.() ?? null
    return {
        owner,
        data: value.data ?? null,
    }
}

export type TokenMetadata = {
    name?: string
    symbol?: string
    image?: string
    uri?: string
    description?: string
    externalUrl?: string
    updateAuthority?: string
    createdAt?: number
}

export async function getTokenMetadata(mint: string): Promise<TokenMetadata>
{
    // Use Solscan public API as a simple metadata provider
    try {
        const url = `https://public-api.solscan.io/token/meta?tokenAddress=${encodeURIComponent(mint)}`
        const res = await fetch(url, { headers: { Accept: 'application/json' }, next: { revalidate: 60 } })
        if (!res.ok) throw new Error(`Solscan meta HTTP ${res.status}`)
        const data = await res.json()
        return {
            name: data?.name ?? data?.symbol ?? undefined,
            symbol: data?.symbol ?? undefined,
            image: data?.icon ?? data?.image ?? undefined,
            uri: data?.website ?? undefined,
            description: data?.description ?? undefined,
            externalUrl: data?.website ?? undefined,
            updateAuthority: data?.updateAuthority ?? undefined,
            createdAt: typeof data?.createdAt === 'number' ? data.createdAt : undefined,
        }
    } catch (err) {
        // Best-effort fallback: return minimal metadata
        return { name: mint.slice(0, 8), symbol: mint.slice(0, 8).toUpperCase() }
    }
}

export function calculateGiniCoefficient(entries: AmountEntry[]): number
{
    const amounts = entries.map((e) => (typeof e.amount === 'number' ? e.amount : 0)).filter((n) => Number.isFinite(n))
    if (amounts.length === 0) return 0
    const sorted = amounts.slice().sort((a, b) => a - b)
    const n = sorted.length
    const sum = sorted.reduce((a, b) => a + b, 0)
    if (sum === 0) return 0
    let cum = 0
    for (let i = 0; i < n; i++) cum += sorted[i] * (i + 1)
    // Gini = (2*sum_i(i*xi))/(n*sum) - (n+1)/n
    const gini = (2 * cum) / (n * sum) - (n + 1) / n
    return Math.max(0, Math.min(1, gini))
}

export function calculateTopNPercentage(entries: AmountEntry[], total: number, n: number): number
{
    if (!Array.isArray(entries) || entries.length === 0 || !Number.isFinite(total) || total <= 0) return 0
    const sorted = entries.map((e) => (typeof e.amount === 'number' ? e.amount : 0)).sort((a, b) => b - a)
    const top = sorted.slice(0, n).reduce((a, b) => a + b, 0)
    return (top / total) * 100
}

export function calculateAverageBalance(entries: AmountEntry[]): number
{
    const arr = entries.map((e) => (typeof e.amount === 'number' ? e.amount : 0))
    if (arr.length === 0) return 0
    const sum = arr.reduce((a, b) => a + b, 0)
    return sum / arr.length
}
