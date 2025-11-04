import { NextRequest, NextResponse } from 'next/server';
import { spawnSync } from 'node:child_process';
import path from 'node:path';

const PYTHON = process.env.PYTHON_BIN || 'python';
const SCRIPT_PATH = path.resolve(process.cwd(), '..', 'agents', 'orders.py');

type Action = 'execute' | 'audit';

type ExecutePayload = {
  decision: string;
  confidence: number;
  summary?: string;
  metrics?: Record<string, unknown>;
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

export async function POST(request: NextRequest) {
  const body = await request.json();
  const action = body?.action as Action | undefined;
  const orders = body?.orders;

  if (!action) {
    return NextResponse.json(
      { status: 'error', message: 'action is required' },
      { status: 400 },
    );
  }

  if (action === 'execute' && !Array.isArray(orders)) {
    return NextResponse.json(
      { status: 'error', message: 'orders array required for execute action' },
      { status: 400 },
    );
  }

  try {
    const args = action === 'execute' ? ['execute', '--orders', JSON.stringify(orders)] : ['audit'];
    const stdout = runPython(args);
    const payload = JSON.parse(stdout) as ExecutePayload;
    return NextResponse.json({ status: 'success', data: payload });
  } catch (error) {
    console.error('[executor] action failed', error);
    return NextResponse.json(
      { status: 'error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 },
    );
  }
}
