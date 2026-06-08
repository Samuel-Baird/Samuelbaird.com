"use client";

import { diffWords } from "diff";
import ReactMarkdown from "react-markdown";

// ---------------------------------------------------------------------------
// Strip markdown syntax to plain text for diffing.
// We diff plain text so markup tokens don't create spurious change noise.
// ---------------------------------------------------------------------------
function markdownToPlain(md: string): string {
  return md
    // Remove headings markers
    .replace(/^#{1,6}\s+/gm, "")
    // Remove bold/italic
    .replace(/\*{1,3}([^*]+)\*{1,3}/g, "$1")
    .replace(/_{1,3}([^_]+)_{1,3}/g, "$1")
    // Remove inline code
    .replace(/`([^`]+)`/g, "$1")
    // Remove links, keep text
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    // Remove blockquote markers
    .replace(/^>\s*/gm, "")
    // Remove list markers
    .replace(/^[-*+]\s+/gm, "")
    .replace(/^\d+\.\s+/gm, "")
    // Remove horizontal rules
    .replace(/^[-*_]{3,}\s*$/gm, "")
    // Collapse extra blank lines
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

// ---------------------------------------------------------------------------
// Renders plain text with word-level diff highlights applied.
// side="left"  → show only removed tokens (red bg), equal tokens plain
// side="right" → show only added tokens (green bg), equal tokens plain
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
          // Don't show additions on the left side
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
          // Don't show removals on the right side
          return null;
        }
        return <span key={i}>{change.value}</span>;
      })}
    </p>
  );
}

// ---------------------------------------------------------------------------
// Public components
// ---------------------------------------------------------------------------

const mdComponents: React.ComponentProps<typeof ReactMarkdown>["components"] = {
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
};

/**
 * Renders a section body. When diffMode is on and a counterpart is provided,
 * renders plain-text word-level diff. Otherwise renders full markdown.
 */
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
  return <ReactMarkdown components={mdComponents}>{markdown}</ReactMarkdown>;
}
