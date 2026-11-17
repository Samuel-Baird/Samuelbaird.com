import { UPSTREAMS } from "@/lib/upstreams";

// Upstreams that are research tools only and never named on a public page.
const PRIVATE = new Set(["gsa"]);

export default function Home() {
  const shown = UPSTREAMS.filter((u) => !PRIVATE.has(u.id));
  return (
    <>
      <p className="kicker">AI tool · MCP server</p>
      <h1>Omni</h1>
      <p className="lede-text">One connector for every Latter-day Saint research server.</p>
      <p>
        Omni is one Model Context Protocol endpoint that fronts several others. Add it once as a custom connector in
        Claude (Settings, Connectors, Add custom connector) or any MCP client:
      </p>
      <pre className="dw-frame" style={{ overflowX: "auto" }}><code>https://samuelbaird.com/omni/api/mcp</code></pre>
      <h2>What it connects</h2>
      <ol className="register">
        {shown.map((u) => (
          <li key={u.id}>
            <span className="reg-title">{u.name}</span>
            <p className="reg-note">
              {u.description}. Tools are prefixed <code>{u.id}_</code>.
            </p>
          </li>
        ))}
      </ol>
      <p className="small">
        A server that is down is skipped without breaking the rest. More about Omni on{" "}
        <a href="https://samuelbaird.com/projects/omni">samuelbaird.com</a>.
      </p>
    </>
  );
}
