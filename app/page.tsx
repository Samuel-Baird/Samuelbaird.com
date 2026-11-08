export default function Home() {
  return (
    <main>
      <h1>Peepstone</h1>
      <p>
        An <a href="https://modelcontextprotocol.io">MCP</a> server for searching and reading{" "}
        <a href="https://www.josephsmithpapers.org">The Joseph Smith Papers</a>.
      </p>
      <p>
        MCP endpoint: <code>/mcp</code>. Add it to Claude as a custom connector, using this site&apos;s URL followed by{" "}
        <code>/mcp</code>.
      </p>
      <p>
        <a href="https://github.com/Samuel-Baird/peepstone">Source on GitHub</a>. Not affiliated with The Church of Jesus Christ
        of Latter-day Saints or the Joseph Smith Papers Project.
      </p>
    </main>
  );
}
