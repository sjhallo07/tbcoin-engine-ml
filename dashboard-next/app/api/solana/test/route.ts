import { NextResponse } from 'next/server'

// Demo endpoint disabled. Use /api/real/* endpoints instead.
export async function POST() {
  return NextResponse.json(
    { status: 'gone', message: 'This demo endpoint has been removed. Use /api/real/*.' },
    { status: 410 }
  )
}
