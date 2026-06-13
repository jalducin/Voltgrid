import { NextResponse } from 'next/server';

// Healthcheck a nivel de proceso (no llama al backend).
export const dynamic = 'force-dynamic';

export function GET() {
  return NextResponse.json({ status: 'ok' }, { status: 200 });
}
