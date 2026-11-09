const url = process.argv[2] ?? "http://localhost:3000/api/mcp";
const rpc = async (id, method, params) =>
  (
    await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json", accept: "application/json, text/event-stream" },
      body: JSON.stringify({ jsonrpc: "2.0", id, method, params }),
    })
  ).json();

console.log((await rpc(1, "initialize", { protocolVersion: "2025-03-26" })).result.serverInfo);
const tools = (await rpc(2, "tools/list")).result.tools;
const by = {};
for (const t of tools) {
  const p = t.name.split("_")[0];
  by[p] = (by[p] ?? 0) + 1;
}
console.log(tools.length, "tools", by);
if (process.argv[3]) {
  const r = await rpc(3, "tools/call", { name: process.argv[3], arguments: JSON.parse(process.argv[4] ?? "{}") });
  console.log(JSON.stringify(r).slice(0, 600));
}
