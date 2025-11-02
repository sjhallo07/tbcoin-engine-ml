import { NextResponse } from 'next/server'

import { buildTokenRiskReport } from '../../../../../services/token-analysis'

export async function GET(request: Request, { params }: { params: { mint: string } }) {
  const { mint } = params

  try {
    const report = await buildTokenRiskReport(mint)
    return NextResponse.json(report)
  } catch (error: any) {
    return NextResponse.json({ error: String(error?.message || error) }, { status: 500 })
  }
}
