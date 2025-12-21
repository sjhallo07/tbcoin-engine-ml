import type { NextRequest } from 'next/server'
import { buildTokenRiskReport, type RiskReport } from '../services/token-analysis'

export type SupportedNetwork = 'solana' | 'ethereum' | 'polygon'

export type TokenRef = { address: string; network: SupportedNetwork }

export type TokenAnalysisOptions = {
    minLiquidityUSD?: number
    liquidityFloorUSD?: number
    concentrationThreshold?: number
}

export async function getTokenAnalysis(tokens: TokenRef[], _options: TokenAnalysisOptions = {})
{
    const results: Array<{ token: TokenRef; report: RiskReport | null; error?: string }> = []

    for (const token of tokens) {
        if (token.network === 'solana') {
            try {
                const report = await buildTokenRiskReport(token.address)
                results.push({ token, report })
            } catch (err: any) {
                results.push({ token, report: null, error: err?.message || 'analysis failed' })
            }
        } else {
            // Placeholder for EVM networks – not implemented yet
            results.push({ token, report: null, error: 'network not supported yet' })
        }
    }

    return {
        status: 'ok',
        count: results.length,
        results,
    }
}

export async function postTokenAnalysis(tokens: TokenRef[], options: TokenAnalysisOptions = {})
{
    return getTokenAnalysis(tokens, options)
}
