import { NextResponse } from 'next/server'

import { fetchHolderAnalysis } from '../../../../../services/token-analysis'

export async function GET(request: Request, { params }: { params: { mint: string } }) {
  const { mint } = params

  try {
    const analysis = await fetchHolderAnalysis(mint)
    return NextResponse.json(analysis)
  } catch (error: any) {
    return NextResponse.json({ error: String(error?.message || error) }, { status: 500 })
  }
}
