import { NextResponse } from "next/server";

// RFC 8058 one-click unsubscribe target advertised (List-Unsubscribe) by the
// monthly newsletter, which has ended. Mail clients may still POST here from
// old emails; there is nothing left to unsubscribe from, so answer 200.
export function POST() {
  return NextResponse.json({ ok: true });
}
