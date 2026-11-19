// Writes site/index.html, site/connect.html and site/about.html (committed; Vercel serves site/ as is).
// Run: npm run build:site   after changing the data, so titles and figures come from the engine itself.
//   DESERET_MCP_URL  public origin, default https://mcp.deseret.wiki
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { load } from '../src/load.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ORIGIN = (process.env.DESERET_MCP_URL || 'https://mcp.deseret.wiki').replace(/\/$/, '');
const ENDPOINT = `${ORIGIN}/api/mcp`;
const REPO = 'https://github.com/Samuel-Baird/deseret-mcp';
const MAIL = 'mailto:ithinksamofficial@gmail.com?subject=Deseret%20MCP';
const { engine, corpus } = load();
const D = (s) => engine.text(s).deseret;
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const n = (x) => x.toLocaleString('en');

// figures
const article = corpus.records.filter((r) => r.kind === 'article').map((r) => r.text).join('\n');
const cov = engine.text(article).stats;
const pct = (a) => ((a / cov.words) * 100).toFixed(1);
const C = corpus.counts;

const icon = (d) => `<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`;
const I = {
  home: '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h5v-6h4v6h5V10"/>',
  ai: '<path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
  about: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6"/><path d="M12 7.5v.01"/>',
  book: '<path d="M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2z"/><path d="M4 19V5"/><path d="M9 7h6"/>',
  globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a14 14 0 010 18a14 14 0 010-18"/>',
  mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
  code: '<path d="M8 8l-5 4 5 4"/><path d="M16 8l5 4-5 4"/><path d="M14 5l-4 14"/>',
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
};
const FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='4' fill='%23243A50'/%3E%3Crect x='5' y='5' width='90' height='90' rx='2' fill='none' stroke='%23A98442' stroke-width='3'/%3E%3Ctext x='50' y='68' font-size='54' text-anchor='middle' fill='%23F3E9D2' font-family='Georgia,serif'%3ED%3C/text%3E%3C/svg%3E";
const copy = (text, { wrap = false, label } = {}) =>
  `<div class="copyfield">${label ? `<span class="small-caps lbl">${esc(label)}</span>` : ''}<code class="${wrap ? 'wrap' : ''}">${esc(text)}</code><button type="button" data-copy="${esc(text)}" aria-label="Copy ${esc(label || 'text')}">Copy</button><span class="sr" role="status"></span></div>`;
const step = (i, title, body) => `<li><span class="n">${i}</span><div><h3>${title}</h3><div class="stepbody">${body}</div></div></li>`;

// The sidebar, top bar and colophon are the shared Samuel Baird family chrome, stamped into the
// <!--family:*--> markers by `node scripts/family-sync.mjs` at the monorepo root. Run it after this.
function page({ file, title, description, current, body, scripts = [] }) {
  const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description)}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#F3E9D2" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#16161A" media="(prefers-color-scheme: dark)">
<link rel="icon" href="${FAVICON}">
<link rel="stylesheet" href="/tokens.css">
<link rel="stylesheet" href="/site.css">
<link rel="stylesheet" href="/pages.css">
<link rel="stylesheet" href="/bg/bg.css">
<!--family:head--><!--/family:head-->
<script src="/bg/glyphwind.js" charset="utf-8" defer></script><script src="/bg/bg.js" defer></script>
<script src="/deseret.js" charset="utf-8" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<!--family:top--><!--/family:top-->
<main id="main" class="rail">
${body.trim()}
</main>
<p class="rail disclaimer">Deseret MCP is a companion to <a href="https://deseret.wiki">deseret.wiki</a> and is not affiliated with The Church of Jesus Christ of Latter-day Saints. Pronunciations from the CMU Pronouncing Dictionary.</p>
<!--family:foot--><!--/family:foot-->
${scripts.map((s) => `<script src="${s}" charset="utf-8" defer></script>`).join('\n')}
</body>
</html>
`;
  fs.writeFileSync(path.join(ROOT, 'site', file), html);
}

// ---- front page
const SAMPLE = 'In 1854 the Regents of the University of Deseret approved a new alphabet: one letter for every sound of English. Brigham Young hoped the Saints would read and write it.';
const hello = 'Holiness to the Lord';
page({
  file: 'index.html',
  current: 'home',
  title: 'Deseret MCP: the Deseret Alphabet for your AI assistant',
  description: 'Connect Claude or ChatGPT to the Deseret Alphabet: write any English in Deseret letters, read Deseret back, and ask questions answered from deseret.wiki with links. Free, no account.',
  scripts: ['/connect.js', '/try.js'],
  body: `
<div class="hero">
  <div class="hero-grid">
    <div>
      <p class="eyebrow small-caps">A connector for Claude and ChatGPT</p>
      <h1 data-dsrt="${esc(D('Deseret MCP'))}">Deseret MCP</h1>
      <p class="lede">Your AI assistant can write any English in the Deseret Alphabet, read Deseret back into Latin letters, and answer questions about the alphabet from every source on <a href="https://deseret.wiki">deseret.wiki</a>, with a link to the page each answer came from. It is free and needs no account.</p>
      ${copy(ENDPOINT, { label: 'Address' })}
      <p class="btns" style="margin-top:20px"><a class="primary" href="/connect">Add it to your AI</a><a class="secondary" href="/about">How it works</a></p>
    </div>
    <figure class="specimen"><span class="dsrt" lang="en-Dsrt">${esc(D(hello))}</span><figcaption>&ldquo;${hello},&rdquo; as struck on the 1860 five-dollar gold piece, spelled here by the server itself.</figcaption></figure>
  </div>
</div>

<section id="try" aria-labelledby="try-h">
  <h2 id="try-h">Try it</h2>
  <p class="muted">This box uses the same server your assistant would. Words it cannot spell stay in Latin letters and are listed, never guessed.</p>
  <div class="try">
    <div class="tabs" role="tablist" aria-label="Direction">
      <button role="tab" type="button" id="mode-to" aria-selected="true">English to Deseret</button>
      <button role="tab" type="button" id="mode-from" aria-selected="false">Deseret to English</button>
    </div>
    <textarea id="try-in" aria-label="English text" spellcheck="false">${esc(SAMPLE)}</textarea>
    <div class="row"><button type="button" class="primary" id="try-go">Transliterate</button><span class="status" id="try-status" role="status"></span></div>
    <div class="out dsrt" id="try-out" lang="en-Dsrt" aria-live="polite"></div>
    <div class="report" id="try-report"></div>
  </div>
</section>

<section aria-labelledby="can-h">
  <h2 id="can-h">What your assistant can do with it</h2>
  <div class="cards">
    <div class="card"><h3>Write in Deseret <span class="dsrt" aria-hidden="true">${esc(D('write'))}</span></h3>
      <p>Single words, passages or whole files. Every word of the ${n(engine.size)}-word CMU Pronouncing Dictionary, spelled sound by sound the way deseret.wiki spells its own pages.</p>
      <ul><li>Explains a word letter by letter: name, sound, key word.</li><li>Lists the words it could not spell, and the ones it built from their parts.</li><li>Keeps Markdown and HTML intact: links, code, footnotes.</li><li>Reads Deseret back, naming the homophones.</li></ul></div>
    <div class="card"><h3>Ask about the alphabet <span class="dsrt" aria-hidden="true">${esc(D('ask'))}</span></h3>
      <p>Answers come from what deseret.wiki holds, with the page to cite.</p>
      <ul><li>The encyclopedia article, section by section (${C.article} sections).</li><li>The library: ${C.library} PDFs, sermons and readings.</li><li>${C.font} fonts, ${C.book} books &amp; prints, ${C.video} videos, ${C.resource} resources${C.quote ? `, ${C.quote} quote${C.quote > 1 ? 's' : ''}` : ''}.</li><li>The ${C.letter}-letter chart with sounds and key words.</li></ul></div>
  </div>
</section>

<section aria-labelledby="ask-h">
  <h2 id="ask-h">Things to ask</h2>
  <p class="muted">Name it in your question so the assistant knows to use it.</p>
  <div class="stack">
    ${copy('Use Deseret MCP: write "I will go and do the things which the Lord hath commanded" in the Deseret Alphabet, and tell me any words you could not spell.', { wrap: true })}
    ${copy('Use Deseret MCP: who designed the Deseret Alphabet, and why was it abandoned? Cite the Deseret Wiki pages.', { wrap: true })}
    ${copy('Use Deseret MCP: spell "Zarahemla" in Deseret and explain each letter.', { wrap: true })}
    ${copy('Use Deseret MCP: which fonts can I install to type Deseret in Word, and what licence is each under?', { wrap: true })}
  </div>
</section>

<section aria-labelledby="tools-h">
  <h2 id="tools-h">The tools</h2>
  <div class="tablewrap"><table>
    <thead><tr><th>Tool</th><th>What it does</th></tr></thead>
    <tbody>
      <tr><td><code>to_deseret</code></td><td>English text, up to 100,000 characters, to Deseret, with a report of unknown, built-up and two-sense words.</td></tr>
      <tr><td><code>deseret_word</code></td><td>One word explained: phones, each letter's name and sound, every pronunciation.</td></tr>
      <tr><td><code>from_deseret</code></td><td>Deseret back to Latin letters, naming homophones and respelled words.</td></tr>
      <tr><td><code>search_wiki</code></td><td>Search every source on deseret.wiki; each hit links to its page and original source.</td></tr>
      <tr><td><code>read_wiki</code></td><td>The full text of a hit with a ready-made citation.</td></tr>
      <tr><td><code>wiki_contents</code></td><td>What the wiki holds, by kind.</td></tr>
      <tr><td><code>deseret_file</code></td><td>Local server only: transliterates a text, Markdown or HTML file on your computer.</td></tr>
    </tbody>
  </table></div>
  <p class="ornament" aria-hidden="true">${esc(D('the end'))}</p>
</section>`,
});

// ---- connect
const steps = (list) => `<ol class="steps">${list.map((s, i) => step(i + 1, s[0], s[1])).join('')}</ol>`;
page({
  file: 'connect.html',
  current: 'connect',
  title: 'Use with Claude or ChatGPT | Deseret MCP',
  description: 'Connect Deseret MCP to Claude or ChatGPT to write in the Deseret Alphabet and ask about it. Free, no account needed.',
  scripts: ['/connect.js'],
  body: `
<div class="pagehead">
  <p class="eyebrow small-caps">Connect</p>
  <h1 data-dsrt="${esc(D('Use with Claude or ChatGPT').replace('ChatGPT', '𐐕𐐰𐐻𐐾𐐨𐐹𐐨𐐻𐐨'))}">Use with Claude or ChatGPT</h1>
  <p class="lede">Add Deseret MCP to your AI assistant once, then ask in plain language. It is free and needs no account.</p>
  ${copy(ENDPOINT, { label: 'Deseret MCP' })}
</div>
<div class="two">
  <div class="main">
    <p class="small-caps muted" id="which">Which AI do you use?</p>
    <div class="tabs" role="tablist" aria-labelledby="which">
      <button role="tab" type="button" id="tab-claude" aria-controls="panel-claude" aria-selected="true">Claude</button>
      <button role="tab" type="button" id="tab-chatgpt" aria-controls="panel-chatgpt" aria-selected="false">ChatGPT</button>
    </div>
    <section role="tabpanel" id="panel-claude" aria-labelledby="tab-claude" style="padding:0">
      <div class="before"><p><strong>Before you start</strong></p><ul>
        <li>Do this <strong>on a computer</strong>, in the Claude app or at claude.ai. It carries over to your phone.</li>
        <li>The free plan allows one custom connector.</li>
        <li>On a <strong>work or school</strong> account, only an admin can add connectors.</li></ul></div>
      ${steps([
        ['Open Customize', '<p>In the sidebar on the left, click <strong>Customize</strong>.</p>'],
        ['Choose &ldquo;Add custom connector&rdquo;', '<p>Click the <strong>Connectors</strong> tab, then the <strong>+ Add</strong> button, then <strong>Add custom connector</strong>.</p>'],
        ['Name it and paste the address', `<p>Type <strong>Deseret</strong> in the first box. Copy the address below and paste it into the second box. Then click <strong>Continue</strong>.</p>${copy(ENDPOINT)}`],
        ['Leave &ldquo;No sign-in&rdquo; and click Add', '<p>Claude checks the address and picks <strong>No sign-in</strong> for you. That is correct: the tools are free and need no account. Don&rsquo;t change anything else, then click <strong>Add</strong>.</p><p>A yellow warning appears for every connector that has no sign-in. It doesn&rsquo;t mean anything is wrong.</p>'],
        ['Check it&rsquo;s switched on', '<p>Start a new chat. Click the <strong>+</strong> below the message box, then <strong>Connectors</strong>. The switch next to Deseret should be on. It usually already is, and it stays that way for new chats.</p>'],
      ])}
    </section>
    <section role="tabpanel" id="panel-chatgpt" aria-labelledby="tab-chatgpt" hidden style="padding:0">
      <div class="before"><p><strong>Before you start</strong></p><ul>
        <li>Custom connections need a ChatGPT plan that allows them; if you don&rsquo;t see <strong>Plugins</strong>, your plan or workspace may not.</li>
        <li>Do this on a computer, at chatgpt.com.</li></ul></div>
      ${steps([
        ['Open Plugins', '<p>In the sidebar on the left, click <strong>Plugins</strong>.</p>'],
        ['Choose &ldquo;Add custom MCP server&rdquo;', '<p>Click <strong>Add</strong> in the top-right corner, then <strong>Add custom MCP server</strong>. MCP is just the technical name for this kind of connection.</p>'],
        ['Fill in the form', `<p>Work down the form from top to bottom:</p><ol class="plain"><li><strong>Name:</strong> type Deseret. Leave Description empty.</li><li><strong>Connection:</strong> paste the address below.</li><li><strong>Authentication:</strong> change OAuth to <strong>No authentication</strong>.</li><li>Tick <strong>I understand and want to continue</strong>.</li><li>Click <strong>Create as a plugin</strong>.</li></ol>${copy(ENDPOINT)}<p>The step people miss is Authentication. It starts on OAuth. If you leave it there, ChatGPT will ask you to sign in somewhere and fail. Pick No authentication.</p>`],
        ['Click &ldquo;Connect Deseret&rdquo;', '<p>ChatGPT checks the address for a few seconds and then asks you to confirm. Click <strong>Connect Deseret</strong>. A green message says it is now connected, and a new icon appears under Installed.</p>'],
        ['Ask for it by name', '<p>Say &ldquo;use Deseret MCP&rdquo; in your message. To be sure it&rsquo;s used, type <strong>@</strong> and the first letters of the name and pick it from the list.</p>'],
      ])}
    </section>
    <section class="block"><h2>Try it</h2>
      <p class="muted">Name it in your question so the AI knows where to look.</p>
      <div class="stack">
        ${copy('Use Deseret MCP: write "The glory of God is intelligence" in the Deseret Alphabet and explain the first word letter by letter.', { wrap: true })}
        ${copy('Use Deseret MCP: what did Brigham Young say about teaching the Deseret Alphabet? Give the sources from the Deseret Wiki.', { wrap: true })}
        ${copy('Use Deseret MCP: read this back into English: 𐐜 𐐔𐐯𐑆𐐲𐑉𐐯𐐻 𐐈𐑊𐑁𐐲𐐺𐐯𐐻', { wrap: true })}
      </div></section>
    <section class="block"><h2>If something goes wrong</h2><div class="trouble">
      <details><summary>&ldquo;Add custom connector&rdquo; is greyed out</summary><p>Custom connectors need a paid plan or an admin on work and school accounts. On a free Claude plan you get one custom connector, so remove another one first.</p></details>
      <details><summary>It says a connector with this address already exists</summary><p>It is already added. Open Connectors and make sure the switch next to Deseret is on.</p></details>
      <details><summary>ChatGPT asks me to sign in, or the plugin won&rsquo;t connect</summary><p>Set Authentication to <strong>No authentication</strong> before you create it. If you already created it with OAuth, delete it and add it again.</p></details>
      <details><summary>The Deseret letters show as boxes</summary><p>Your device has no Deseret font. Install one from the <a href="https://deseret.wiki/fonts/">Deseret Wiki&rsquo;s font page</a>; Noto Sans Deseret is a good start.</p></details>
      <details><summary>The AI answers without using the tools</summary><p>Name it in your question (&ldquo;use Deseret MCP&rdquo;) and check the connector is switched on for the chat. In ChatGPT, type @ and pick it from the list.</p></details>
      <details><summary>What can this connection see?</summary><p>Only the text you ask it to transliterate, and only while it does so; nothing is stored. The wiki answers come from the public pages of deseret.wiki. It never sees your account or your other chats.</p></details>
    </div></section>
    <section class="block"><h2>On your own computer</h2>
      <p class="muted">The same server runs locally with Node.js 20 or newer and nothing else to install. Locally it can also transliterate whole files (<code>deseret_file</code>), writing <code>name.dsrt.md</code> beside the original. Setup is in the <a href="${REPO}#install">README on GitHub</a>.</p>
      ${copy('claude mcp add deseret -- node <repo>/bin/deseret-mcp.mjs')}</section>
  </div>
  <aside>
    <section><h2 class="small-caps">Other tools</h2>
      <div class="asidebody">
        <p>Claude Code: run this once in a terminal.</p>
        ${copy(`claude mcp add --transport http deseret ${ENDPOINT}`, { wrap: true })}
        <p>Apps that only speak stdio can use <a href="https://www.npmjs.com/package/mcp-remote">mcp-remote</a>, or the local server:</p>
        <pre>${esc(JSON.stringify({ mcpServers: { deseret: { command: 'npx', args: ['-y', 'mcp-remote', ENDPOINT] } } }, null, 2))}</pre>
      </div></section>
    <section><h2 class="small-caps">What it can do</h2>
      <ul class="side"><li>Write any English in the Deseret Alphabet.</li><li>Explain a word letter by letter.</li><li>Read Deseret back into Latin letters.</li><li>Answer questions from every source on deseret.wiki, with links.</li><li>Say plainly which words it could not spell.</li></ul></section>
    <section><h2 class="small-caps">Questions</h2>
      <p class="side">Stuck? <a href="${MAIL}">Send a message</a>. The source for the connection is <a href="${REPO}">on GitHub</a>.</p></section>
  </aside>
</div>`,
});

// ---- about
page({
  file: 'about.html',
  current: 'about',
  title: 'Method & data | Deseret MCP',
  description: 'How Deseret MCP spells English in the Deseret Alphabet, what it does with words it does not know, and which deseret.wiki sources it answers from.',
  body: `
<div class="hero"><p class="eyebrow small-caps">Method &amp; data</p><h1 data-dsrt="${esc(D('How it works'))}">How it works</h1>
<p class="lede">Deseret writes sounds, not spellings: one letter for each sound of English. So every word is first turned into its sounds, then each sound into its letter.</p></div>
<section class="prose"><h2>Spelling English in Deseret</h2>
<ul>
<li><b>Pronunciations:</b> the <a href="https://github.com/cmusphinx/cmudict">CMU Pronouncing Dictionary</a>, ${n(engine.size)} words with their sounds in ARPAbet, pinned to one published version.</li>
<li><b>Sounds to letters:</b> the same one-to-one table the Deseret Wiki uses for its own pages, so a word is spelled the same way here and there. <i>Y</i> + <i>oo</i> is the single letter ${esc(D('few').slice(-2))} and <i>oi</i> is ${esc(D('boy').slice(-2))}, the two letters added in 1859.</li>
<li><b>Hand corrections:</b> the wiki&rsquo;s own (<i>and</i>, <i>not</i>, <i>Deseret</i>&hellip;) and Book of Mormon names after the Church&rsquo;s pronunciation guide.</li>
<li><b>Words the dictionary lacks</b> are built from a known word and a regular ending or prefix (<i>unfaithfulness</i> = <i>unfaithful</i> + <i>-ness</i>). These are listed as built from parts, so you can check them, and can be left in Latin letters instead.</li>
<li><b>Anything else stays in Latin letters</b> and is listed by name with how often it occurs. Nothing is guessed letter by letter.</li>
<li><b>Words with two senses</b> such as <i>read</i> and <i>live</i> are decided by the word before (<i>have read</i>, <i>will read</i>) and reported.</li>
</ul>
<h2>How well it covers English</h2>
<p>On the Deseret Wiki&rsquo;s encyclopedia article, ${n(cov.words)} words dense with names and technical terms, ${pct(cov.from_dictionary)}% are spelled from the dictionary, ${pct(cov.derived)}% are built from their parts and ${pct(cov.unknown)}% are reported as unknown. Ordinary prose does better. Against the wiki&rsquo;s own word table the spellings agree on every word except four with two senses (<i>lead</i>, <i>read</i>, <i>use</i>, <i>wind</i>), where this server picks the common reading.</p>
<h2>Reading Deseret back</h2>
<p>The dictionary is reversed. Deseret records sound, so words that sound alike are spelled alike (${esc(D('by'))} is <i>by</i>, <i>buy</i> or <i>bye</i>); the server picks the likelier one and names the others. Spellings that match no dictionary word, such as the older conventions of the 1860s books, are respelled letter by letter and flagged.</p>
<h2>Answering questions</h2>
<p>Answers come from a snapshot of every source on <a href="https://deseret.wiki">deseret.wiki</a>, and every result links back to the page it is on, and to the original where the wiki links out:</p>
<ul>
<li>the encyclopedia article on the Deseret Alphabet, in ${C.article} sections (text from Wikipedia, CC BY-SA 4.0, credited with every answer);</li>
<li>the library: ${C.library} hosted PDFs, sermons and conference addresses, and further reading;</li>
<li>${C.resource} resources, ${C.video} videos, ${C.font} fonts, ${C.book} books &amp; prints${C.quote ? ` and ${C.quote} quote${C.quote > 1 ? 's' : ''}` : ''};</li>
<li>the ${C.letter}-letter chart with each letter&rsquo;s name, sound and key word.</li>
</ul>
<p>Snapshot of ${esc(corpus.built)}${corpus.commit ? `, wiki commit <code>${esc(corpus.commit.slice(0, 10))}</code>` : ''}.</p>
<h2>Limits</h2>
<ul>
<li>Spellings follow one modern American pronunciation, not a regional accent or the conventions of the 1860s printings.</li>
<li>Only a short list of two-sense words is decided from context; the rest use the dictionary&rsquo;s first reading.</li>
<li>The wiki snapshot is rebuilt when the wiki changes, so a page added today may not be searchable yet.</li>
</ul>
<h2>Privacy</h2>
<p>The connection keeps nothing: text you send is transliterated and returned, not stored or logged by the server. No account, no sign-in.</p>
<h2>Source and credits</h2>
<p>Source code, tests and the data files: <a href="${REPO}">github.com/Samuel-Baird/deseret-mcp</a>. Pronunciations &copy; Carnegie Mellon University (BSD licence). Method, letter table and corrections from the <a href="https://deseret.wiki/">Deseret Wiki</a>. Sister project of <a href="https://samuelbaird.com/urim">Urim</a>, whose layout this site shares.</p>
</section>`,
});
console.log(`site written for ${ORIGIN}`);
