import { UPSTREAMS, type Upstream } from "./upstreams";
import { upstreamRequest } from "./upstream-client";

type Json = Record<string, any>;
type Tool = Json & { name: string };

const CACHE_MS = 5 * 60_000;
let cache: { at: number; tools: Tool[] } | null = null;

async function listUpstreamTools(up: Upstream): Promise<Tool[]> {
  const tools: Tool[] = [];
  let cursor: string | undefined;
  do {
    const r = await upstreamRequest(up, "tools/list", cursor ? { cursor } : {});
    for (const t of r.tools ?? []) {
      tools.push({
        ...t,
        name: `${up.id}_${t.name}`,
        title: t.title ? `${up.name}: ${t.title}` : undefined,
        description: `[${up.name}] ${t.description ?? ""}`.trim(),
      });
    }
    cursor = r.nextCursor;
  } while (cursor);
  return tools;
}

export async function listTools(): Promise<Tool[]> {
  if (cache && Date.now() - cache.at < CACHE_MS) return cache.tools;
  const results = await Promise.allSettled(UPSTREAMS.map(listUpstreamTools));
  const tools = results.flatMap((r) => (r.status === "fulfilled" ? r.value : []));
  results.forEach((r, i) => {
    if (r.status === "rejected") console.error(`omni: ${UPSTREAMS[i].id} tools/list failed:`, r.reason);
  });
  // Only cache complete results so a flaky upstream is retried on the next request.
  if (tools.length && results.every((r) => r.status === "fulfilled")) cache = { at: Date.now(), tools };
  else if (!tools.length && cache) return cache.tools; // everything down: serve stale
  return tools;
}

export async function callTool(name: string, args: Json) {
  const up = UPSTREAMS.find((u) => typeof name === "string" && name.startsWith(`${u.id}_`));
  if (!up) return { isError: true, content: [{ type: "text", text: `Unknown tool: ${name}` }] };
  try {
    return await upstreamRequest(up, "tools/call", { name: name.slice(up.id.length + 1), arguments: args ?? {} });
  } catch (e) {
    return { isError: true, content: [{ type: "text", text: `Upstream error: ${(e as Error).message}` }] };
  }
}

export const INSTRUCTIONS =
  "Omni is a single entry point to several Latter-day Saint research MCP servers. Every tool is prefixed with its source: " +
  UPSTREAMS.map((u) => `${u.id}_ = ${u.name} (${u.description})`).join("; ") +
  ". Cite sources using the URLs the tools return.";
