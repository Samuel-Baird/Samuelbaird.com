"""Static page bodies for /connect and /donate (kept apart from build.py)."""
import html

E = html.escape
MCP_URL = "https://urim.samuelbaird.com/api/mcp"
NAME = "Urim"
EMAIL = "ithinksamofficial@gmail.com"


def copy(value, label="", wrap=False):
    lab = f'<span class="small-caps lbl">{E(label)}</span>' if label else ""
    return (f'<div class="copyfield">{lab}<code class="{"wrap" if wrap else ""}">{E(value)}</code>'
            f'<button type="button" data-copy="{E(value, quote=True)}" aria-label="Copy {E(label or "text")}">Copy</button>'
            f'<span class="sr" role="status"></span></div>')


def step(n, title, *body):
    return (f'<li><span class="n serif">{n}</span><div><h3>{title}</h3><div class="stepbody">'
            + "".join(body) + "</div></div></li>")


B = lambda s: f"<strong>{s}</strong>"

CLAUDE = "".join([
    step(1, "Open Customize", f"<p>In the sidebar on the left, click {B('Customize')}.</p>"),
    step(2, "Choose &ldquo;Add custom connector&rdquo;",
         f"<p>Click the {B('Connectors')} tab, then the {B('+ Add')} button, then {B('Add custom connector')}.</p>"),
    step(3, "Name it and paste the address",
         f"<p>Type {B(NAME)} in the first box. Copy the address below and paste it into the second box. "
         f"Then click {B('Continue')}.</p>", copy(MCP_URL)),
    step(4, "Leave &ldquo;No sign-in&rdquo; and click Add",
         f"<p>Claude checks the address and picks {B('No sign-in')} for you. That is correct: the data is free and needs no "
         f"account. Don&rsquo;t change anything else, then click {B('Add')}.</p>",
         "<p>A yellow warning appears for every connector that has no sign-in. It doesn&rsquo;t mean anything is wrong.</p>"),
    step(5, "Check it&rsquo;s switched on",
         f"<p>Start a new chat. Click the {B('+')} below the message box, then {B('Connectors')}. The switch next to "
         f"{NAME} should be on. It usually already is, and it stays that way for new chats.</p>"),
])

CHATGPT = "".join([
    step(1, "Open Plugins", f"<p>In the sidebar on the left, click {B('Plugins')}.</p>"),
    step(2, "Choose &ldquo;Add custom MCP server&rdquo;",
         f"<p>Click {B('Add')} in the top-right corner, then {B('Add custom MCP server')}. MCP is just the technical name "
         "for this kind of connection.</p>"),
    step(3, "Fill in the form", "<p>Work down the form from top to bottom:</p><ol class=\"plain\">"
         f"<li>{B('Name:')} type {NAME}. Leave Description empty.</li>"
         f"<li>{B('Connection:')} paste the address below.</li>"
         f"<li>{B('Authentication:')} change OAuth to {B('No authentication')}.</li>"
         f"<li>Tick {B('I understand and want to continue')}.</li>"
         f"<li>Click {B('Create as a plugin')}.</li></ol>", copy(MCP_URL),
         "<p>The step people miss is Authentication. It starts on OAuth. If you leave it there, ChatGPT will ask you to sign "
         "in somewhere and fail. Pick No authentication.</p>"),
    step(4, f"Click &ldquo;Connect {NAME}&rdquo;",
         f"<p>ChatGPT checks the address for a few seconds and then asks you to confirm. Click {B('Connect ' + NAME)}. "
         "A green message says it is now connected, and a new icon appears under Installed.</p>"),
    step(5, "Ask for it by name",
         f"<p>Say &ldquo;use {NAME}&rdquo; in your message. To be sure it&rsquo;s used, type {B('@')} and the first letters "
         "of the name and pick it from the list.</p>"),
])

PROMPTS = [
    'Use Urim: how does the Church translate "endowment" into Portuguese and Spanish, and how often is each rendering used?',
    "Use Urim: which Church terms are in this sentence, and how should I render them in Spanish? "
    "\"The priesthood keys were restored so that we can receive our endowment.\"",
    "Use Urim: which English terms have more than one Church rendering in Spanish, and what are they?",
]

TROUBLE = [
    ("&ldquo;Add custom connector&rdquo; is greyed out",
     "Custom connectors need a paid plan or an admin on work and school accounts. On a free Claude plan you get one custom "
     "connector, so remove another one first."),
    ("It says a connector with this address already exists",
     f"It is already added. Open Connectors and make sure the switch next to {NAME} is on."),
    ("ChatGPT asks me to sign in, or the plugin won&rsquo;t connect",
     "Set Authentication to <strong>No authentication</strong> before you create it. If you already created it with OAuth, "
     "delete it and add it again."),
    ("The AI answers without searching the data",
     f"Name it in your question (&ldquo;use {NAME}&rdquo;) and check the connector is switched on for the chat. In ChatGPT, "
     "type @ and pick it from the list."),
    ("What can this connection see?",
     "Only the public, read-only atlas you can already browse on this site: Church renderings, usage counts and links. It "
     "never sees your account or anything you type into the site, and it does not translate or store your text."),
]


def connect_page():
    trouble = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in TROUBLE)
    prompts = "".join(copy(p, wrap=True) for p in PROMPTS)
    mcp_remote = ('{\n  "mcpServers": {\n    "urim": {\n      "command": "npx",\n'
                  f'      "args": ["-y", "mcp-remote", "{MCP_URL}"]\n    }}\n  }}\n}}')
    body = f"""<div class="pagehead">
  <p class="eyebrow small-caps" style="color:var(--honey)">Connect</p>
  <h1>Use with Claude or ChatGPT</h1>
  <p class="lede">Add Urim to your AI assistant once, then ask how the Church translates its terms in plain language. It is free and needs no account.</p>
  {copy(MCP_URL, NAME)}
</div>
<div class="two">
  <div class="main">
    <p class="small-caps muted" id="which">Which AI do you use?</p>
    <div class="tabs" role="tablist" aria-labelledby="which">
      <button role="tab" type="button" id="tab-claude" aria-controls="panel-claude" aria-selected="true">Claude</button>
      <button role="tab" type="button" id="tab-chatgpt" aria-controls="panel-chatgpt" aria-selected="false">ChatGPT</button>
    </div>
    <section role="tabpanel" id="panel-claude" aria-labelledby="tab-claude">
      <div class="before"><p><strong>Before you start</strong></p><ul>
        <li>Do this <strong>on a computer</strong>, in the Claude app or at claude.ai. It carries over to your phone.</li>
        <li>The free plan allows one custom connector.</li>
        <li>On a <strong>work or school</strong> account, only an admin can add connectors.</li></ul></div>
      <ol class="steps">{CLAUDE}</ol>
    </section>
    <section role="tabpanel" id="panel-chatgpt" aria-labelledby="tab-chatgpt" hidden>
      <div class="before"><p><strong>Before you start</strong></p><ul>
        <li>Custom connections need a ChatGPT plan that allows them; if you don&rsquo;t see <strong>Plugins</strong>, your plan or workspace may not.</li>
        <li>Do this on a computer, at chatgpt.com.</li></ul></div>
      <ol class="steps">{CHATGPT}</ol>
    </section>
    <section class="block"><h2>Try it</h2>
      <p class="muted">Name the site in your question so the AI knows where to look.</p>
      <div class="stack">{prompts}</div></section>
    <section class="block"><h2>If something goes wrong</h2><div class="trouble">{trouble}</div></section>
    <section class="block"><h2>Free local translator</h2>
      <p class="muted">Separately from this connection, Urim ships a translation server that runs entirely on your own computer: it caches translations, enforces the Church terminology above, and uses local models, so there are no paid APIs. It is for developers and researchers; setup is in the <a href="https://github.com/Samuel-Baird/urim/blob/main/mcp/README.md">README on GitHub</a>.</p></section>
  </div>
  <aside>
    <section><h2 class="small-caps">Other tools</h2>
      <div class="asidebody">
        <p>Claude Code: run this once in a terminal.</p>
        {copy(f"claude mcp add --transport http urim {MCP_URL}", wrap=True)}
        <p>Apps that only speak stdio can use <a href="https://www.npmjs.com/package/mcp-remote">mcp-remote</a>:</p>
        <pre>{E(mcp_remote)}</pre>
      </div></section>
    <section><h2 class="small-caps">What it can do</h2>
      <ul class="side"><li>Look up a term in English, Portuguese or Spanish, including reverse lookup.</li>
      <li>Show every Church rendering with usage counts, years and source links.</li>
      <li>Pick out the Church terminology in a passage you are translating.</li>
      <li>List terms the Church renders inconsistently.</li></ul></section>
    <section><h2 class="small-caps">Questions</h2>
      <p class="side">Stuck? <a href="mailto:{EMAIL}?subject=Urim">Send a message</a>. The source for the connection is
      <a href="https://github.com/Samuel-Baird/urim/blob/main/api/mcp.js">on GitHub</a>.</p></section>
  </aside>
</div>
<script src="/connect.js" defer></script>"""
    return ("Use with Claude or ChatGPT | Urim", body,
            "Connect Urim to Claude or ChatGPT to look up how the Church translates Latter-day Saint terms. Free, no account needed.")


def donate_page():
    body = f"""<div class="pagehead">
  <p class="back"><a href="/">&larr; Urim</a></p>
  <p class="eyebrow small-caps" style="color:var(--honey)">Donate</p>
  <h1>Help keep Urim going.</h1>
</div>
<div class="two">
  <div class="main">
    <p>Urim is free, independent and ad-free. Donations go toward hosting and the time it takes to keep the atlas accurate and growing. Anything helps and is appreciated.</p>
    <section class="block" id="give"><h2 class="small-caps muted">Give money</h2>
      <div class="btns">
        <a class="primary" href="https://paypal.me/Baird90" target="_blank" rel="noopener noreferrer" data-thanks>Donate via PayPal &rarr;</a>
        <a class="secondary" href="https://venmo.com/Samuel-J-Baird" target="_blank" rel="noopener noreferrer" data-thanks>Donate via Venmo &rarr;</a>
      </div>
      <p class="note">You&rsquo;ll be taken to paypal.me/Baird90 or venmo.com/Samuel-J-Baird to complete the donation.</p></section>
    <section class="block" id="wishlist"><h2 class="small-caps muted">Or send a book</h2>
      <p>Prefer to give something tangible? My Amazon wishlist is mostly books and research materials.</p>
      <div class="btns"><a class="secondary" href="https://www.amazon.com/hz/wishlist/ls/3ECBMMP7G2LZ4" target="_blank" rel="noopener noreferrer">View Amazon wishlist &rarr;</a></div>
      <p class="note">Opens my wishlist on amazon.com. Amazon handles the purchase and shipping.</p></section>
  </div>
  <aside>
    <section><h2 class="small-caps">Where it goes</h2>
      <ul class="side"><li>Hosting and infrastructure costs.</li>
      <li>Time spent curating terms, checking sources and building tools.</li>
      <li>Books and research materials from the wishlist.</li>
      <li>Keeping the site free, public, and without ads.</li></ul></section>
    <section><h2 class="small-caps">Questions</h2>
      <p class="side">Email <a href="mailto:{EMAIL}?subject=Urim">{EMAIL}</a>.</p></section>
  </aside>
</div>
<div id="thanks" class="modal" role="dialog" aria-modal="true" aria-labelledby="thanks-title" hidden>
  <div class="backdrop" data-close></div>
  <div class="panel">
    <button type="button" class="x" data-close aria-label="Close">&times;</button>
    <h2 id="thanks-title">Thank you!</h2>
    <p>Your contribution helps make this work possible.</p>
    <button type="button" class="secondary" data-close>Close</button>
  </div>
</div>
<script src="/donate.js" defer></script>"""
    return ("Donate | Urim", body, "Support Urim, a free and independent atlas of how the Church translates its vocabulary.")
