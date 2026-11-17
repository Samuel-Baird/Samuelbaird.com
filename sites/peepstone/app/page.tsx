export default function Home() {
  return (
    <>
      <p className="kicker">AI tool · MCP server</p>
      <h1>Peepstone</h1>
      <p className="lede-text">Search and read the Joseph Smith Papers from any AI assistant.</p>
      <p>
        Peepstone is a <a href="https://modelcontextprotocol.io">Model Context Protocol</a> server for{" "}
        <a href="https://www.josephsmithpapers.org">The Joseph Smith Papers</a>. It gives Claude and other assistants live
        search and reading access to the journals, letters, revelations, histories, minutes and legal records, with the
        project&apos;s transcriptions, footnotes and source notes. Every result carries the canonical josephsmithpapers.org
        URL and a citation. It stores no copy of the site.
      </p>
      <h2>Connect</h2>
      <p>Add it as a custom connector (in Claude: Settings, Connectors, Add custom connector) with this address:</p>
      <pre className="dw-frame" style={{ overflowX: "auto" }}><code>https://samuelbaird.com/peepstone/mcp</code></pre>
      <p className="small">
        Not affiliated with The Church of Jesus Christ of Latter-day Saints or the Joseph Smith Papers Project. More about
        Peepstone on <a href="https://samuelbaird.com/projects/peepstone">samuelbaird.com</a>.
      </p>
    </>
  );
}
