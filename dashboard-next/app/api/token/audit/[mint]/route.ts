import { NextResponse } from 'next/server'

import { fetchContractAudit } from '../../../../../services/token-analysis'

export async function GET(request: Request, { params }: { params: { mint: string } }) {
  const { mint } = params

  try {
    const audit = await fetchContractAudit(mint)
    return NextResponse.json(audit)
  } catch (error: any) {
    return NextResponse.json({ error: String(error?.message || error) }, { status: 500 })
  }
}
