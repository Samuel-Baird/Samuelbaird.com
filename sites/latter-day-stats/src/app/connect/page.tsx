import type { Metadata } from "next";
import Link from "next/link";
import { ConnectGuide } from "@/components/connect-guide";
import { CopyField } from "@/components/copy-field";
import { DeseretTitle } from "@/components/deseret-title";
import { MCP_URL } from "@/lib/mcp";

export const metadata: Metadata = {
  title: "Use with Claude or ChatGPT",
  description:
    "Connect Latter-day Stats to Claude or ChatGPT so you can ask questions about LDS YouTube channels, studies, and survey data in plain language. Free, no account needed.",
  alternates: { canonical: "/connect" },
};

const PROMPTS = [
  "Use Latter-day Stats: which five channels have the most subscribers, and what do they cover? Link each channel.",
  "Use Latter-day Stats: list the studies in the research library about missions and summarize what each one found.",
  "Use Latter-day Stats: what datasets are in the Data Explorer, and which one would show how belief varies by age?",
];

const TROUBLE: { q: string; a: React.ReactNode }[] = [
  {
    q: "“Add custom connector” is greyed out",
    a: (
      <>
        Custom connectors need a paid plan or an admin on work and school
        accounts. On a free Claude plan you get one custom connector, so remove
        another one first.
      </>
    ),
  },
  {
    q: "It says a connector with this address already exists",
    a: (
      <>
        It is already added. Open Connectors and make sure the switch next to
        Latter-day Stats is on.
      </>
    ),
  },
  {
    q: "ChatGPT asks me to sign in, or the plugin won’t connect",
    a: (
      <>
        Set Authentication to <strong>No authentication</strong> before you
        create it. If you already created it with OAuth, delete it and add it
        again.
      </>
    ),
  },
  {
    q: "The AI answers without searching the data",
    a: (
      <>
        Name it in your question (“use Latter-day Stats”) and check the
        connector is switched on for the chat. In ChatGPT, type @ and pick it
        from the list.
      </>
    ),
  },
  {
    q: "What can this connection see?",
    a: (
      <>
        Only the public, read-only data you can already browse on this site:
        tracked channels and their stats, the research library, and the Data
        Explorer datasets. It never sees your account, bookmarks, or anything
        you type into the site.
      </>
    ),
  },
];

export default function ConnectPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <p className="small-caps text-xs font-medium text-[color:var(--honey)]">
        Connect
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
        <DeseretTitle text="Use with Claude or ChatGPT" />
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)] sm:text-lg">
        Add Latter-day Stats to your AI assistant once, then ask about channels,
        studies, and survey data in plain language. It is free and needs no
        account.
      </p>

      <div className="mt-8 max-w-3xl">
        <CopyField label="Latter-day Stats" value={MCP_URL} />
      </div>

      <div className="mt-10 lg:grid lg:grid-cols-[minmax(0,1fr)_20rem] lg:gap-14">
        <div className="max-w-3xl">
          <ConnectGuide />

          <section className="mt-12">
            <h2 className="serif text-2xl font-semibold tracking-tight">
              Try it
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-[color:var(--muted)]">
              Name the site in your question so the AI knows where to look.
            </p>
            <div className="mt-4 space-y-3">
              {PROMPTS.map((p) => (
                <CopyField key={p} value={p} wrap />
              ))}
            </div>
          </section>

          <section className="mt-12">
            <h2 className="serif text-2xl font-semibold tracking-tight">
              If something goes wrong
            </h2>
            <div className="mt-4 divide-y divide-[color:var(--border)] rounded-[var(--radius)] border border-[color:var(--border)] bg-white">
              {TROUBLE.map((t) => (
                <details key={t.q} className="group px-5 py-4">
                  <summary className="cursor-pointer text-sm font-medium">
                    {t.q}
                  </summary>
                  <p className="mt-3 text-sm leading-relaxed text-[color:var(--muted)]">
                    {t.a}
                  </p>
                </details>
              ))}
            </div>
          </section>
        </div>

        <aside className="mt-14 space-y-8 lg:mt-0 lg:border-l lg:border-[color:var(--border)] lg:pl-10">
          <section>
            <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              Other tools
            </h2>
            <div className="mt-3 space-y-4 border-t border-[color:var(--border)] pt-3 text-sm leading-relaxed text-[color:var(--muted)]">
              <p>
                Claude Code: run this once in a terminal.
              </p>
              <CopyField
                wrap
                value={`claude mcp add --transport http latter-day-stats ${MCP_URL}`}
              />
              <p>
                Apps that only speak stdio can use{" "}
                <a
                  href="https://www.npmjs.com/package/mcp-remote"
                  className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
                >
                  mcp-remote
                </a>
                :
              </p>
              <pre className="overflow-x-auto rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-3 text-xs leading-relaxed text-[color:var(--foreground)]">
{`{
  "mcpServers": {
    "latter-day-stats": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "${MCP_URL}"]
    }
  }
}`}
              </pre>
            </div>
          </section>

          <section>
            <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              What it can do
            </h2>
            <ul className="mt-3 space-y-2 border-t border-[color:var(--border)] pt-3 text-sm leading-relaxed text-[color:var(--muted)]">
              <li>List and look up tracked channels and their stats.</li>
              <li>Search the research library and read study details.</li>
              <li>Browse the Data Explorer datasets and their groups.</li>
            </ul>
          </section>

          <section>
            <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              Questions
            </h2>
            <p className="mt-3 border-t border-[color:var(--border)] pt-3 text-sm leading-relaxed text-[color:var(--muted)]">
              Stuck?{" "}
              <Link
                href="/contact"
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                Send a message
              </Link>
              . The source for the connection is{" "}
              <a
                href="https://github.com/Samuel-Baird/latter-day-stats/blob/main/src/app/api/mcp/route.ts"
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                on GitHub
              </a>
              .
            </p>
          </section>
        </aside>
      </div>
    </div>
  );
}
