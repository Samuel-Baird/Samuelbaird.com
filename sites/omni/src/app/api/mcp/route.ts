import { INSTRUCTIONS, callTool, listTools } from "@/lib/omni";

export const maxDuration = 60;
export const dynamic = "force-dynamic";

type Json = Record<string, any>;
const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "POST, GET, DELETE, OPTIONS",
  "access-control-allow-headers": "content-type, accept, mcp-session-id, mcp-protocol-version, authorization",
  "access-control-expose-headers": "mcp-session-id",
};

async function handle(msg: Json): Promise<Json | null> {
  const { id, method, params } = msg;
  if (id === undefined) return null; // notification
  const ok = (result: Json) => ({ jsonrpc: "2.0", id, result });
  switch (method) {
    case "initialize":
      return ok({
        protocolVersion: params?.protocolVersion ?? "2025-03-26",
        capabilities: { tools: { listChanged: false } },
        serverInfo: { name: "omni", version: "0.1.0" },
        instructions: INSTRUCTIONS,
      });
    case "ping":
      return ok({});
    case "tools/list":
      return ok({ tools: await listTools() });
    case "tools/call":
      return ok(await callTool(params?.name, params?.arguments));
    case "resources/list":
      return ok({ resources: [] });
    case "prompts/list":
      return ok({ prompts: [] });
    default:
      return { jsonrpc: "2.0", id, error: { code: -32601, message: `Method not found: ${method}` } };
  }
}

export async function POST(req: Request) {
  let body: Json | Json[];
  try {
    body = await req.json();
  } catch {
    return Response.json({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } }, { status: 400, headers: CORS });
  }
  const batch = Array.isArray(body);
  const out = (await Promise.all((batch ? body : [body]).map(handle))).filter(Boolean);
  if (!out.length) return new Response(null, { status: 202, headers: CORS });
  return Response.json(batch ? out : out[0], { headers: CORS });
}

export const GET = () =>
  new Response("Omni MCP: use POST (Streamable HTTP, stateless).", { status: 405, headers: { ...CORS, allow: "POST" } });
export const DELETE = () => new Response(null, { status: 204, headers: CORS });
export const OPTIONS = () => new Response(null, { status: 204, headers: CORS });
