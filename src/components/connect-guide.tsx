"use client";

import { useEffect, useState } from "react";
import { CopyField } from "@/components/copy-field";
import { MCP_URL } from "@/lib/mcp";

type Which = "claude" | "chatgpt";

const NAME = "Latter-day Stats";

function Step({
  n,
  title,
  children,
}: {
  n: number;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <li className="grid grid-cols-[2.25rem_minmax(0,1fr)] gap-x-3 border-t border-[color:var(--border)] py-6 first:border-t-0">
      <span className="serif text-2xl font-semibold text-[color:var(--honey)]">
        {n}
      </span>
      <div>
        <h3 className="serif text-lg font-semibold tracking-tight">{title}</h3>
        <div className="mt-2 space-y-3 text-sm leading-relaxed text-[color:var(--muted)]">
          {children}
        </div>
      </div>
    </li>
  );
}

const B = ({ children }: { children: React.ReactNode }) => (
  <strong className="font-semibold text-[color:var(--foreground)]">
    {children}
  </strong>
);

function ClaudeSteps() {
  return (
    <ol>
      <Step n={1} title="Open Customize">
        <p>
          In the sidebar on the left, click <B>Customize</B>.
        </p>
      </Step>
      <Step n={2} title="Choose “Add custom connector”">
        <p>
          Click the <B>Connectors</B> tab, then the <B>+ Add</B> button, then{" "}
          <B>Add custom connector</B>.
        </p>
      </Step>
      <Step n={3} title="Name it and paste the address">
        <p>
          Type <B>{NAME}</B> in the first box. Copy the address below and paste
          it into the second box. Then click <B>Continue</B>.
        </p>
        <CopyField value={MCP_URL} />
      </Step>
      <Step n={4} title="Leave “No sign-in” and click Add">
        <p>
          Claude checks the address and picks <B>No sign-in</B> for you. That is
          correct: the data is free and needs no account. Don&apos;t change
          anything else, then click <B>Add</B>.
        </p>
        <p>
          A yellow warning appears for every connector that has no sign-in. It
          doesn&apos;t mean anything is wrong.
        </p>
      </Step>
      <Step n={5} title="Check it’s switched on">
        <p>
          Start a new chat. Click the <B>+</B> below the message box, then{" "}
          <B>Connectors</B>. The switch next to {NAME} should be on. It usually
          already is, and it stays that way for new chats.
        </p>
      </Step>
    </ol>
  );
}

function ChatGptSteps() {
  return (
    <ol>
      <Step n={1} title="Open Plugins">
        <p>
          In the sidebar on the left, click <B>Plugins</B>.
        </p>
      </Step>
      <Step n={2} title="Choose “Add custom MCP server”">
        <p>
          Click <B>Add</B> in the top-right corner, then{" "}
          <B>Add custom MCP server</B>. MCP is just the technical name for this
          kind of connection.
        </p>
      </Step>
      <Step n={3} title="Fill in the form">
        <p>Work down the form from top to bottom:</p>
        <ol className="list-decimal space-y-1 pl-5">
          <li>
            <B>Name:</B> type {NAME}. Leave Description empty.
          </li>
          <li>
            <B>Connection:</B> paste the address below.
          </li>
          <li>
            <B>Authentication:</B> change OAuth to <B>No authentication</B>.
          </li>
          <li>
            Tick <B>I understand and want to continue</B>.
          </li>
          <li>
            Click <B>Create as a plugin</B>.
          </li>
        </ol>
        <CopyField value={MCP_URL} />
        <p>
          The step people miss is Authentication. It starts on OAuth. If you
          leave it there, ChatGPT will ask you to sign in somewhere and fail.
          Pick No authentication.
        </p>
      </Step>
      <Step n={4} title={`Click “Connect ${NAME}”`}>
        <p>
          ChatGPT checks the address for a few seconds and then asks you to
          confirm. Click <B>Connect {NAME}</B>. A green message says it is now
          connected, and a new icon appears under Installed.
        </p>
      </Step>
      <Step n={5} title="Ask for it by name">
        <p>
          Say “use {NAME}” in your message. To be sure it&apos;s used, type{" "}
          <B>@</B> and the first letters of the name and pick it from the list.
        </p>
      </Step>
    </ol>
  );
}

export function ConnectGuide() {
  const [which, setWhich] = useState<Which>("claude");

  // Deep link: /connect#chatgpt
  useEffect(() => {
    const sync = () => {
      if (window.location.hash === "#chatgpt") setWhich("chatgpt");
      else if (window.location.hash === "#claude") setWhich("claude");
    };
    const frame = requestAnimationFrame(sync);
    window.addEventListener("hashchange", sync);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("hashchange", sync);
    };
  }, []);

  function pick(next: Which) {
    setWhich(next);
    window.history.replaceState(null, "", `#${next}`);
  }

  return (
    <div>
      <p className="small-caps text-xs font-medium text-[color:var(--muted)]">
        Which AI do you use?
      </p>
      <div
        role="tablist"
        aria-label="Which AI do you use?"
        className="mt-3 grid grid-cols-2 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-1"
      >
        {(["claude", "chatgpt"] as const).map((id) => (
          <button
            key={id}
            role="tab"
            type="button"
            id={`tab-${id}`}
            aria-selected={which === id}
            aria-controls={`panel-${id}`}
            onClick={() => pick(id)}
            className={`h-11 rounded-[var(--radius)] text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)] ${
              which === id
                ? "bg-[color:var(--muted-soft)] text-[color:var(--foreground)]"
                : "text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
            }`}
          >
            {id === "claude" ? "Claude" : "ChatGPT"}
          </button>
        ))}
      </div>

      <section
        role="tabpanel"
        id={`panel-${which}`}
        aria-labelledby={`tab-${which}`}
        className="mt-6"
      >
        <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--muted-soft)] p-5 text-sm leading-relaxed">
          <p className="font-semibold">Before you start</p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-[color:var(--muted)]">
            {which === "claude" ? (
              <>
                <li>
                  Do this <B>on a computer</B>, in the Claude app or at
                  claude.ai. It carries over to your phone.
                </li>
                <li>The free plan allows one custom connector.</li>
                <li>
                  On a <B>work or school</B> account, only an admin can add
                  connectors.
                </li>
              </>
            ) : (
              <>
                <li>
                  Do this <B>on a computer</B>, at chatgpt.com. It carries over
                  to your phone.
                </li>
                <li>Works on the free plan.</li>
                <li>
                  On a <B>work or school</B> account, only an admin can add
                  plugins.
                </li>
              </>
            )}
          </ul>
        </div>
        <div className="mt-2">
          {which === "claude" ? <ClaudeSteps /> : <ChatGptSteps />}
        </div>
      </section>
    </div>
  );
}
