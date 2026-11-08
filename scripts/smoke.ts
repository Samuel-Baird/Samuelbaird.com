/**
 * Live smoke test: exercises every tool against www.josephsmithpapers.org.
 *   npm run smoke            # all
 *   npm run smoke -- search  # only tools whose name contains "search"
 */
import { McpServer } from "@modelcontextprotocol/server";
import { INSTRUCTIONS, SERVER_INFO, registerTools } from "../src/server";

const calls: Array<[string, Record<string, unknown>]> = [
  ["search", { query: "Kirtland Temple", types: ["journals"], per_page: 5 }],
  ["search", { query: "temple", people: ["Hyrum Smith"], places: ["Nauvoo, Illinois"], start_date: "1840-01-01", end_date: "1842-12-31", per_page: 3 }],
  ["get_document", { document: "journal-1835-1836", page: 11 }],
  ["get_document", { document: "https://www.josephsmithpapers.org/paper-summary/revelation-february-1829-dc-4/1", include: ["transcript", "footnotes", "historicalIntro", "sourceNote", "versions"] }],
  ["get_document_pages", { document: "journal-1835-1836" }],
  ["get_person", { query: "Emma Hale Smith", related_limit: 5 }],
  ["get_place", { query: "nauvoo-illinois", related_limit: 3 }],
  ["get_glossary_term", { query: "Nauvoo Legion", related_limit: 3 }],
  ["get_event", { query: "reorganization-of-nauvoo-house-association" }],
  ["get_calendar", { start_date: "1831-01-01", end_date: "1831-01-31" }],
  ["browse_papers", { path: "" }],
  ["browse_papers", { path: "journals/jsppj1" }],
  ["get_article", { article: "/articles/introduction-to-calendar-of-documents" }],
  ["cite_page", { url: "https://www.josephsmithpapers.org/paper-summary/journal-1835-1836/11" }],
  ["get_page_image", { document: "journal-1835-1836", page: 11 }],
  ["fetch_jsp_url", { url: "/topic/nauvoo-legion" }],
  ["fetch_jsp_url", { url: "/reference/people?filter=b" }],
  ["fetch_jsp_url", { url: "/media/videos" }],
  ["fetch_jsp_url", { url: "https://www.josephsmithpapers.org/site/note-on-seer-stone-images?p=1" }],
  ["fetch_jsp_url", { url: "/intro/series-introduction-for-the-journals-series" }],
  ["fetch_jsp_url", { url: "/back/nauvoo-city-officers-1841-1844" }],
];
/** Calls that should return a clean, explanatory error. */
const expectErrors: Array<[string, Record<string, unknown>]> = [
  ["get_person", { query: "no-such-person-xyz" }],
  ["fetch_jsp_url", { url: "https://example.com/" }],
];

// Capture tool handlers by registering against a recording shim.
const handlers = new Map<string, (args: any) => Promise<any>>();
const server = new McpServer(SERVER_INFO, { instructions: INSTRUCTIONS });
const orig = server.registerTool.bind(server);
(server as any).registerTool = (name: string, config: any, cb: any) => {
  handlers.set(name, cb);
  return orig(name, config, cb);
};
registerTools(server);

const filter = process.argv[2];
const preview = Number(process.env.PREVIEW ?? 900);
let failures = 0;
for (const [name, args] of calls) {
  if (filter && !name.includes(filter)) continue;
  const t0 = Date.now();
  const res = await handlers.get(name)!(args);
  const text: string = res.content?.[0]?.text ?? "";
  const status = res.isError ? "FAIL" : "ok";
  if (res.isError) failures++;
  console.log(`\n===== ${status} ${name} ${JSON.stringify(args)} (${Date.now() - t0} ms, ${text.length} chars)`);
  console.log(text.slice(0, preview));
}
for (const [name, args] of expectErrors) {
  if (filter && !name.includes(filter)) continue;
  const res = await handlers.get(name)!(args);
  const text: string = res.content?.[0]?.text ?? "";
  if (!res.isError) failures++;
  console.log(`\n===== ${res.isError ? "ok (expected error)" : "FAIL (expected an error)"} ${name} ${JSON.stringify(args)}\n${text}`);
}
console.log(`\n${failures ? `${failures} failure(s)` : "all tools ok"}`);
process.exit(failures ? 1 : 0);
