import { NextResponse } from 'next/server'

// Demo endpoint disabled.
export async function GET() {
  return NextResponse.json(
    { status: 'gone', message: 'This demo endpoint has been removed.' },
    { status: 410 }
  )
}
