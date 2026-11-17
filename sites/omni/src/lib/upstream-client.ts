import type { Upstream } from "./upstreams";

type Json = Record<string, any>;
const PROTOCOL = "2025-03-26";
const TIMEOUT_MS = 25_000;

async function parseBody(res: Response): Promise<Json | null> {
  const text = await res.text();
  if (!text.trim()) return null;
  if ((res.headers.get("content-type") ?? "").includes("text/event-stream")) {
    // Take the last JSON-RPC message that carries a result or error.
    let found: Json | null = null;
    for (const block of text.split(/\r?\n\r?\n/)) {
      const data = block
        .split(/\r?\n/)
        .filter((l) => l.startsWith("data:"))
        .map((l) => l.slice(5).trim())
        .join("\n");
      if (!data) continue;
      try {
        const msg = JSON.parse(data);
        if (msg && ("result" in msg || "error" in msg)) found = msg;
      } catch {}
    }
    return found;
  }
  return JSON.parse(text);
}

async function post(up: Upstream, body: Json, sessionId?: string | null) {
  const headers: Record<string, string> = {
    "content-type": "application/json",
    accept: "application/json, text/event-stream",
    "mcp-protocol-version": PROTOCOL,
  };
  if (sessionId) headers["mcp-session-id"] = sessionId;
  const res = await fetch(up.url, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(TIMEOUT_MS),
    cache: "no-store",
  });
  return { res, msg: res.ok ? await parseBody(res) : null };
}

/** Run one request against an upstream using a fresh short-lived session. */
export async function upstreamRequest(up: Upstream, method: string, params: Json = {}): Promise<Json> {
  const init = await post(up, {
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: { protocolVersion: PROTOCOL, capabilities: {}, clientInfo: { name: "omni", version: "0.1.0" } },
  });
  if (!init.res.ok || !init.msg || init.msg.error) {
    throw new Error(`${up.name}: initialize failed (${init.res.status}) ${init.msg?.error?.message ?? ""}`.trim());
  }
  const sid = init.res.headers.get("mcp-session-id");
  await post(up, { jsonrpc: "2.0", method: "notifications/initialized" }, sid).catch(() => {});
  const out = await post(up, { jsonrpc: "2.0", id: 2, method, params }, sid);
  if (sid) fetch(up.url, { method: "DELETE", headers: { "mcp-session-id": sid } }).catch(() => {});
  if (!out.res.ok || !out.msg) throw new Error(`${up.name}: ${method} failed (${out.res.status})`);
  if (out.msg.error) throw new Error(`${up.name}: ${out.msg.error.message ?? "error"}`);
  return out.msg.result ?? {};
}
