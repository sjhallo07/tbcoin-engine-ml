import { NextRequest, NextResponse } from 'next/server';
import { spawnSync } from 'node:child_process';
import path from 'node:path';

const PYTHON = process.env.PYTHON_BIN || 'python';
const SCRIPT_PATH = path.resolve(process.cwd(), '..', 'agents', 'orders.py');

type Mode = 'autonomous' | 'guided' | 'manual';

type FetchResponse = {
  orders: Array<Record<string, unknown>>;
};

type ProcessResponse = {
  report: Record<string, unknown>;
};

function runPython(args: string[], input?: string) {
  const result = spawnSync(PYTHON, [SCRIPT_PATH, ...args], {
    input,
    encoding: 'utf-8',
    maxBuffer: 5 * 1024 * 1024,
  });

  if (result.error) {
    throw result.error;
  }

  if (result.status !== 0) {
    throw new Error(result.stderr || `Python exited with code ${result.status}`);
  }

  return result.stdout;
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const mode = searchParams.get('mode') as Mode | null;

  const args = ['fetch'];
  if (mode) {
    args.push('--mode', mode);
  }

  try {
    const stdout = runPython(args);
    const payload = JSON.parse(stdout) as FetchResponse;
    return NextResponse.json({ status: 'success', data: payload.orders });
  } catch (error) {
    console.error('[llearners] fetch failed', error);
    return NextResponse.json(
      { status: 'error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 },
    );
  }
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const orders = body?.orders;
  if (!Array.isArray(orders)) {
    return NextResponse.json(
      { status: 'error', message: 'orders array is required' },
      { status: 400 },
    );
  }

  try {
    const stdout = runPython(['process', '--orders', JSON.stringify(orders)]);
    const report = JSON.parse(stdout) as ProcessResponse;
    return NextResponse.json({ status: 'success', data: report.report });
  } catch (error) {
    console.error('[llearners] process failed', error);
    return NextResponse.json(
      { status: 'error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 },
    );
  }
}
