import { NextResponse } from 'next/server'

import { fetchTokenProfile } from '../../../../../services/token-analysis'

export async function GET(request: Request, { params }: { params: { mint: string } }) {
  const { mint } = params

  try {
    const profile = await fetchTokenProfile(mint)
    return NextResponse.json(profile)
  } catch (error: any) {
    return NextResponse.json({ error: String(error?.message || error) }, { status: 500 })
  }
}
