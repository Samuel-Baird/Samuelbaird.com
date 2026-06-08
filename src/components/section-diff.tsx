"use client";

import { diffWords } from "diff";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// ---------------------------------------------------------------------------
// Footnote extraction
// ---------------------------------------------------------------------------

type FootnoteMap = Record<string, string>;

/**
 * Pull [^id]: content definitions out of a markdown string.
 * Handles single-line and multi-line definitions (indented continuation lines).
 */
function extractFootnotes(md: string): FootnoteMap {
  const map: FootnoteMap = {};
  // Match [^id]: followed by content until the next [^id]: or end of string
  const re = /^\[\^([^\]]+)\]:\s*([\s\S]*?)(?=^\[\^[^\]]+\]:|\z)/gm;
  let match: RegExpExecArray | null;
  while ((match = re.exec(md)) !== null) {
    map[match[1].trim()] = match[2].trim();
  }
  return map;
}

/**
 * Remove the ## Footnotes section and all [^id]: definitions from markdown
 * so they don't render as a list at the bottom.
 */
function stripFootnoteDefs(md: string): string {
  return md
    // Remove the whole ## Footnotes heading + everything after it that is definitions
    .replace(/^##\s*Footnotes\s*\n([\s\S]*)/im, (_, rest) =>
      // Keep any non-definition lines that might follow (unlikely but safe)
      rest
        .split("\n")
        .filter((l: string) => !/^\[\^[^\]]+\]:/.test(l.trim()))
        .join("\n"),
    )
    // Remove bare [^id]: lines outside the section too
    .replace(/^\[\^[^\]]+\]:.*(\n[ \t]+.*)*\n?/gm, "")
    .trim();
}

// ---------------------------------------------------------------------------
// Footnote tooltip component
// ---------------------------------------------------------------------------

function FootnoteTooltip({
  label,
  content,
}: {
  label: string;
  content: string;
}) {
  return (
    <span className="group relative inline-block">
      <sup
        className="cursor-help text-[10px] font-semibold text-[color:var(--accent)] underline decoration-dotted underline-offset-2"
        aria-label={`Footnote ${label}: ${content}`}
      >
        [{label}]
      </sup>
      {/* Tooltip */}
      <span
        className="
          pointer-events-none absolute bottom-full left-1/2 z-30 mb-1.5
          w-72 -translate-x-1/2 rounded-xl border border-[color:var(--border)]
          bg-white px-3 py-2.5 text-xs leading-relaxed text-[color:var(--foreground)]
          shadow-lg opacity-0 transition-opacity duration-150
          group-hover:opacity-100
        "
        role="tooltip"
      >
        <span className="mb-1 block text-[10px] font-semibold uppercase tracking-wide text-[color:var(--accent)]">
          Note {label}
        </span>
        {content}
        {/* Arrow */}
        <span className="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-[color:var(--border)]" />
      </span>
    </span>
  );
}

// ---------------------------------------------------------------------------
// Build component map (needs footnote lookup closure)
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
    strong: ({ children }) => (
      <strong className="font-semibold">{children}</strong>
    ),
    em: ({ children }) => <em className="italic">{children}</em>,
    hr: () => <hr className="my-4 border-[color:var(--border)]" />,

    // Footnote references render as <a href="#user-content-fn-ID">
    a: ({ href, children }) => {
      const fnMatch = href?.match(/^#user-content-fn-(.+)$/);
      if (fnMatch) {
        const id = fnMatch[1];
        const content = footnotes[id];
        if (content) {
          return <FootnoteTooltip label={id} content={content} />;
        }
        // Fallback if definition not found
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

    // Suppress the rendered footnotes section at the bottom
    section: ({ node, children, ...props }) => {
      const dataType = (node as { properties?: Record<string, unknown> })
        ?.properties?.["dataFootnotes"];
      if (dataType) return null;
      return <section {...props}>{children}</section>;
    },
  };
}

// ---------------------------------------------------------------------------
// Strip markdown syntax to plain text for diffing
// ---------------------------------------------------------------------------

function markdownToPlain(md: string): string {
  return md
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/\*{1,3}([^*]+)\*{1,3}/g, "$1")
    .replace(/_{1,3}([^_]+)_{1,3}/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    // Remove footnote references
    .replace(/\[\^[^\]]+\]/g, "")
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

function DiffText({
  left,
  right,
  side,
}: {
  left: string;
  right: string;
  side: "left" | "right";
}) {
  const changes = diffWords(left, right);
  return (
    <p className="text-sm leading-relaxed">
      {changes.map((change, i) => {
        if (change.added) {
          if (side === "right") {
            return (
              <mark
                key={i}
                className="rounded bg-emerald-100 px-0.5 text-emerald-900 not-italic"
              >
                {change.value}
              </mark>
            );
          }
          return null;
        }
        if (change.removed) {
          if (side === "left") {
            return (
              <mark
                key={i}
                className="rounded bg-red-100 px-0.5 text-red-900 line-through not-italic"
              >
                {change.value}
              </mark>
            );
          }
          return null;
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
    const plain = markdownToPlain(markdown);
    const counterPlain = markdownToPlain(counterpart);
    return <DiffText left={plain} right={counterPlain} side={side} />;
  }

  const footnotes = extractFootnotes(markdown);
  const cleaned = stripFootnoteDefs(markdown);
  const components = makeMdComponents(footnotes);

  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {cleaned}
    </ReactMarkdown>
  );
}
