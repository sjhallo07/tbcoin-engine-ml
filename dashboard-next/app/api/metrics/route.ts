export const runtime = 'nodejs'

import { NextResponse } from 'next/server'
import client from 'prom-client'

// Create or reuse a singleton registry to avoid duplicate metric registration during HMR.
const g = global as unknown as { __tbcoinPromRegistry?: client.Registry; __tbcoinMetricsInit?: boolean }
if (!g.__tbcoinPromRegistry) {
  g.__tbcoinPromRegistry = new client.Registry()
}
const registry = g.__tbcoinPromRegistry

if (!g.__tbcoinMetricsInit) {
  client.collectDefaultMetrics({ register: registry })
  g.__tbcoinMetricsInit = true
}

export async function GET() {
  try {
    const metrics = await registry.metrics()
    return new Response(metrics, {
      status: 200,
      headers: { 'Content-Type': registry.contentType },
    })
  } catch (error: any) {
    return NextResponse.json({ status: 'error', message: error?.message || 'metrics error' }, { status: 500 })
  }
}
