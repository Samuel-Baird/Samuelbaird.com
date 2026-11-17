import { UPSTREAMS } from "@/lib/upstreams";

export default function Home() {
  return (
    <main>
      <h1>Omni</h1>
      <p>One MCP endpoint that fronts several others. Add this URL as a custom connector:</p>
      <pre><code>https://omni.samuelbaird.com/api/mcp</code></pre>
      <ul>
        {UPSTREAMS.map((u) => (
          <li key={u.id}>
            <b>{u.name}</b> (<code>{u.id}_*</code>): {u.description}
          </li>
        ))}
      </ul>
    </main>
  );
}
