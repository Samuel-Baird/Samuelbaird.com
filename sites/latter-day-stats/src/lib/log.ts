// Single-line JSON logs so log search (Vercel logs, Cloudflare Workers Logs) can filter on evt/level.
export function logEvent(
  evt: string,
  data: Record<string, unknown> = {},
  level: "info" | "error" = "info",
) {
  const line = JSON.stringify({
    evt,
    level,
    ts: new Date().toISOString(),
    ...data,
  });
  if (level === "error") console.error(line);
  else console.log(line);
}
