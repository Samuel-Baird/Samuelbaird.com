"use client";

import { useState } from "react";

type Study = {
  title: string;
  authors: string[];
  year: number | null;
  source: string | null;
  external_url: string | null;
};

function formatAPA(s: Study): string {
  const authors =
    s.authors.length === 0
      ? "Unknown"
      : s.authors
          .map((a) => {
            const parts = a.trim().split(/\s+/);
            if (parts.length === 1) return parts[0];
            const last = parts[parts.length - 1];
            const initials = parts
              .slice(0, -1)
              .map((p) => p[0].toUpperCase() + ".")
              .join(" ");
            return `${last}, ${initials}`;
          })
          .join(", ");
  const year = s.year ? `(${s.year})` : "(n.d.)";
  const source = s.source ? ` ${s.source}.` : "";
  const url = s.external_url ? ` ${s.external_url}` : "";
  return `${authors} ${year}. ${s.title}.${source}${url}`;
}

function formatBibTeX(s: Study, key: string): string {
  const author = s.authors.join(" and ") || "Unknown";
  const year = s.year ?? "n.d.";
  const source = s.source ? `\n  journal = {${s.source}},` : "";
  const url = s.external_url ? `\n  url = {${s.external_url}},` : "";
  return `@article{${key},\n  title = {${s.title}},\n  author = {${author}},\n  year = {${year}},${source}${url}\n}`;
}

function formatMLA(s: Study): string {
  const authors =
    s.authors.length === 0
      ? "Unknown"
      : s.authors.length === 1
        ? s.authors[0]
        : `${s.authors[0]}, et al.`;
  const year = s.year ? ` ${s.year}` : "";
  const source = s.source ? ` ${s.source},` : "";
  const url = s.external_url ? ` ${s.external_url}.` : ".";
  return `${authors}. "${s.title}."${source}${year}.${url}`;
}

export function CitationCopy({
  study,
  bibtexKey,
}: {
  study: Study;
  bibtexKey: string;
}) {
  const [copied, setCopied] = useState<string | null>(null);

  const formats: { id: string; label: string; text: string }[] = [
    { id: "apa", label: "APA", text: formatAPA(study) },
    { id: "mla", label: "MLA", text: formatMLA(study) },
    { id: "bibtex", label: "BibTeX", text: formatBibTeX(study, bibtexKey) },
  ];

  function copy(id: string, text: string) {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(id);
      setTimeout(() => setCopied(null), 2000);
    });
  }

  return (
    <section className="mt-12">
      <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
        Cite this study
      </h2>
      <div className="mt-3 space-y-3">
        {formats.map((f) => (
          <div key={f.id} className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white">
            <div className="flex items-center justify-between border-b border-[color:var(--border)] px-4 py-2">
              <span className="small-caps text-[11px] font-medium text-[color:var(--muted)]">
                {f.label}
              </span>
              <button
                onClick={() => copy(f.id, f.text)}
                className="inline-flex h-7 items-center rounded-[var(--radius)] border border-[color:var(--border)] px-3 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
              >
                {copied === f.id ? "Copied!" : "Copy"}
              </button>
            </div>
            <pre className="overflow-x-auto whitespace-pre-wrap px-4 py-3 text-xs leading-relaxed text-[color:var(--foreground)]">
              {f.text}
            </pre>
          </div>
        ))}
      </div>
    </section>
  );
}
