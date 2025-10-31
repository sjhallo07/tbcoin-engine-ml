import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const { modelType, trainingData, epochs } = await request.json();

  await new Promise((resolve) => setTimeout(resolve, 2000));

  const trainingResult = {
    modelType,
    trainingData,
    accuracy: Math.random() * 0.2 + 0.8,
    loss: Math.random() * 0.1,
    epochsCompleted: epochs ?? 100,
    trainingTime: `${(Math.random() * 3 + 1).toFixed(1)}s`,
    timestamp: new Date().toISOString(),
  };

  return NextResponse.json({ status: 'success', trainingResult });
}
