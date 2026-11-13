// Render a JSON array of {tex, display} from stdin to a JSON array of HTML strings.
const katex = require("katex");
let buf = "";
process.stdin.on("data", (d) => (buf += d));
process.stdin.on("end", () => {
  const items = JSON.parse(buf);
  const out = items.map(({ tex, display }) => {
    try {
      return katex.renderToString(tex, { displayMode: !!display, throwOnError: true, strict: "ignore" });
    } catch (e) {
      process.stderr.write("KaTeX error: " + e.message + "\n  in: " + tex + "\n");
      process.exitCode = 2;
      return `<code class="katex-error">${tex}</code>`;
    }
  });
  process.stdout.write(JSON.stringify(out));
});
