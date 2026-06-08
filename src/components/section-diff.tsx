"use client";

import { diffWords } from "diff";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// ---------------------------------------------------------------------------
// Footnote extraction (for tooltip content lookup)
// ---------------------------------------------------------------------------

type FootnoteMap = Record<string, string>;

function extractFootnotes(md: string): FootnoteMap {
  const map: FootnoteMap = {};
  // Match [^id]: content — handles multi-line definitions with indented continuation
  const re = /^\[\^([^\]]+)\]:\s*([\s\S]*?)(?=^\[\^[^\]]+\]:|\z)/gm;
  let match: RegExpExecArray | null;
  while ((match = re.exec(md)) !== null) {
    map[match[1].trim()] = match[2].trim();
  }
  return map;
}

// ---------------------------------------------------------------------------
// Footnote tooltip
// ---------------------------------------------------------------------------

function FootnoteTooltip({ label, content }: { label: string; content: string }) {
  return (
    <span className="group relative inline-block">
      <sup
        className="cursor-help text-[10px] font-semibold text-[color:var(--accent)] underline decoration-dotted underline-offset-2"
        aria-label={`Footnote ${label}: ${content}`}
      >
        [{label}]
      </sup>
      <span
        className="
          pointer-events-none absolute bottom-full left-1/2 z-30 mb-2
          w-72 -translate-x-1/2 rounded-xl border border-[color:var(--border)]
          bg-white px-3 py-2.5 text-xs leading-relaxed text-[color:var(--foreground)]
          shadow-lg opacity-0 transition-opacity duration-150 group-hover:opacity-100
        "
        role="tooltip"
      >
        <span className="mb-1 block text-[10px] font-semibold uppercase tracking-wide text-[color:var(--accent)]">
          Note {label}
        </span>
        {content}
        <span className="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-[color:var(--border)]" />
      </span>
    </span>
  );
}

// ---------------------------------------------------------------------------
// Component map
// ---------------------------------------------------------------------------

function makeMdComponents(
  footnotes: FootnoteMap,
): React.ComponentProps<typeof ReactMarkdown>["components"] {
  return {
    h1: ({ children }) => (
      <h1 className="serif mb-3 mt-5 text-xl font-semibold leading-snug tracking-tight first:mt-0">
        {children}
      </h1>
    ),
    h2: ({ children }) => (
      <h2 className="serif mb-2 mt-4 text-lg font-semibold leading-snug tracking-tight first:mt-0">
        {children}
      </h2>
    ),
    h3: ({ children }) => (
      <h3 className="serif mb-2 mt-3 text-base font-semibold leading-snug first:mt-0">
        {children}
      </h3>
    ),
    p: ({ children }) => (
      <p className="mb-3 text-sm leading-relaxed last:mb-0">{children}</p>
    ),
    ul: ({ children }) => (
      <ul className="mb-3 list-disc pl-5 text-sm leading-relaxed last:mb-0">
        {children}
      </ul>
    ),
    ol: ({ children }) => (
      <ol className="mb-3 list-decimal pl-5 text-sm leading-relaxed last:mb-0">
        {children}
      </ol>
    ),
    li: ({ children }) => <li className="mb-1">{children}</li>,
    blockquote: ({ children }) => (
      <blockquote className="mb-3 border-l-2 border-[color:var(--accent)] pl-4 text-sm italic text-[color:var(--muted)] last:mb-0">
        {children}
      </blockquote>
    ),
    strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
    em: ({ children }) => <em className="italic">{children}</em>,
    hr: () => <hr className="my-4 border-[color:var(--border)]" />,

    // Intercept footnote reference links → tooltip; pass other links through normally
    a: ({ href, children }) => {
      const fnRef = href?.match(/^#user-content-fn-(.+)$/);
      if (fnRef) {
        const id = fnRef[1];
        const content = footnotes[id];
        if (content) return <FootnoteTooltip label={id} content={content} />;
        return <sup className="text-[color:var(--accent)]">[{id}]</sup>;
      }
      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
        >
          {children}
        </a>
      );
    },

    // Style the footnotes section at the bottom
    section: ({ node, children, ...props }) => {
      const isFootnotes = (
        node as { properties?: Record<string, unknown> }
      )?.properties?.dataFootnotes;
      if (isFootnotes) {
        return (
          <section
            className="mt-6 border-t border-[color:var(--border)] pt-4"
            {...props}
          >
            <p className="mb-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-[color:var(--muted)]">
              Notes
            </p>
            {children}
          </section>
        );
      }
      return <section {...props}>{children}</section>;
    },
  };
}

// ---------------------------------------------------------------------------
// Plain-text stripper for diff mode
// ---------------------------------------------------------------------------

function markdownToPlain(md: string): string {
  return md
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/\*{1,3}([^*]+)\*{1,3}/g, "$1")
    .replace(/_{1,3}([^_]+)_{1,3}/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/\[\^[^\]]+\]/g, "")
    .replace(/^\[\^[^\]]+\]:.*$/gm, "")
    .replace(/^>\s*/gm, "")
    .replace(/^[-*+]\s+/gm, "")
    .replace(/^\d+\.\s+/gm, "")
    .replace(/^[-*_]{3,}\s*$/gm, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

// ---------------------------------------------------------------------------
// Diff renderer
// ---------------------------------------------------------------------------

function DiffText({ left, right, side }: { left: string; right: string; side: "left" | "right" }) {
  const changes = diffWords(left, right);
  return (
    <p className="text-sm leading-relaxed">
      {changes.map((change, i) => {
        if (change.added) {
          return side === "right" ? (
            <mark key={i} className="rounded bg-emerald-100 px-0.5 text-emerald-900 not-italic">
              {change.value}
            </mark>
          ) : null;
        }
        if (change.removed) {
          return side === "left" ? (
            <mark key={i} className="rounded bg-red-100 px-0.5 text-red-900 line-through not-italic">
              {change.value}
            </mark>
          ) : null;
        }
        return <span key={i}>{change.value}</span>;
      })}
    </p>
  );
}

// ---------------------------------------------------------------------------
// Public component
// ---------------------------------------------------------------------------

export function SectionBodyWithDiff({
  markdown,
  counterpart,
  diffMode,
  side,
}: {
  markdown: string;
  counterpart: string | null | undefined;
  diffMode: boolean;
  side: "left" | "right";
}) {
  if (diffMode && counterpart != null) {
    return (
      <DiffText
        left={markdownToPlain(markdown)}
        right={markdownToPlain(counterpart)}
        side={side}
      />
    );
  }

  const footnotes = extractFootnotes(markdown);
  const components = makeMdComponents(footnotes);

  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {markdown}
    </ReactMarkdown>
  );
}
