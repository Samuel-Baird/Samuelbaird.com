/**
 * Convert the XHTML fragments JSP embeds (transcripts, notes, biographies)
 * into compact Markdown suitable for an LLM.
 */
import * as cheerio from "cheerio";
import TurndownService from "turndown";
import { JSP_ORIGIN } from "./client";

export type Footnote = { marker: string; text: string };

export type HtmlToMarkdownOptions = {
  /**
   * How to render inline references to people/places/topics
   * (JSP wraps them in hover pop-ups):
   *  - "link": [text](https://www.josephsmithpapers.org/person/...)  (default)
   *  - "text": plain text only
   */
  references?: "link" | "text";
  /** Render manuscript line breaks (span.line-break) as newlines. */
  lineBreaks?: boolean;
};

export type MarkdownResult = { markdown: string; footnotes: Footnote[] };

const td = new TurndownService({
  headingStyle: "atx",
  bulletListMarker: "-",
  codeBlockStyle: "fenced",
  emDelimiter: "_",
});
// Historical transcripts are full of [brackets], *asterisks* and _underscores_
// that are meaningful text, not Markdown; don't backslash-escape them.
td.escape = (s: string) => s;
td.remove(["script", "style", "noscript", "input", "button", "svg"] as any);
td.addRule("deleted", {
  filter: (node) => hasClass(node, "deleted") || node.nodeName === "DEL" || node.nodeName === "S",
  replacement: (content) => (content.trim() ? `~~${content}~~` : ""),
});
td.addRule("inserted", {
  filter: (node) => hasClass(node, "inserted") || hasClass(node, "insertion"),
  replacement: (content) => `⟨${content}⟩`,
});
td.addRule("superscript", {
  filter: (node) => hasClass(node, "superscript") || node.nodeName === "SUP",
  replacement: (content) => `^${content}`,
});
td.addRule("mark", {
  filter: ["mark"],
  replacement: (content) => `**${content}**`,
});
td.addRule("underline", {
  filter: (node) => hasClass(node, "underline") || node.nodeName === "U",
  replacement: (content) => `<u>${content}</u>`,
});

function hasClass(node: any, cls: string): boolean {
  const c = typeof node.getAttribute === "function" ? node.getAttribute("class") : null;
  return !!c && c.split(/\s+/).includes(cls);
}

export function absolutize(href: string | undefined): string | undefined {
  if (!href) return href;
  if (href.startsWith("#") || /^(https?:|mailto:)/i.test(href)) {
    return href.replace(/^http:\/\/(www\.)?josephsmithpapers\.org/i, JSP_ORIGIN);
  }
  if (href.startsWith("/")) return JSP_ORIGIN + href;
  return href;
}

/** Plain text of an HTML fragment, whitespace-collapsed. */
export function htmlToText(html: string | null | undefined): string {
  if (!html) return "";
  const $ = cheerio.load(html);
  return $.root().text().replace(/\s+/g, " ").trim();
}

/**
 * Convert a JSP HTML fragment to Markdown.
 *
 * Editorial footnotes (pop-ups) are replaced by `[^n]` markers and returned
 * separately; person/place pop-ups become links to their JSP pages.
 */
export function htmlToMarkdown(
  html: string | null | undefined,
  opts: HtmlToMarkdownOptions = {},
): MarkdownResult {
  if (!html || !html.trim()) return { markdown: "", footnotes: [] };
  const references = opts.references ?? "link";
  const $ = cheerio.load(html);
  const footnotes: Footnote[] = [];

  $("head").remove();

  // Pop-up wrappers: either an editorial footnote or an entity reference.
  $("aside.popup-wrapper").each((_, el) => {
    const aside = $(el);
    const trigger = aside.children("a").first();
    const content = aside.find(".popup-content").first();
    const isNote =
      trigger.hasClass("editorial-note-static") ||
      content.find(".editorial-footnote").length > 0;

    if (isNote) {
      const marker = trigger.text().trim() || String(footnotes.length + 1);
      const note = content.find(".note-data").first().clone();
      note.find(".works-cited-links, .source-note, hr").remove();
      const noteMd = toMd($, note.html() ?? "");
      if (noteMd) footnotes.push({ marker, text: noteMd });
      aside.replaceWith(`[^${marker}]`);
      return;
    }

    const text = trigger.text();
    const more = content.find("a.more").attr("href");
    const href = absolutize(more || undefined);
    if (references === "link" && href && text.trim()) {
      aside.replaceWith($("<a>").attr("href", href).text(text));
    } else {
      aside.replaceWith(escapeHtml(text));
    }
  });

  // Footnote-style reference anchors that point at a hash: keep the text only.
  $("a.staticPopup").each((_, el) => {
    $(el).replaceWith(escapeHtml($(el).text()));
  });

  $("span.line-break").each((_, el) => {
    $(el).replaceWith(opts.lineBreaks ? "<br>" : " ");
  });

  // Strip anchors with no href (name targets) but keep their content.
  $("a").each((_, el) => {
    const a = $(el);
    const href = a.attr("href");
    if (!href || href.startsWith("#")) {
      a.replaceWith(a.html() ?? "");
    } else {
      a.attr("href", absolutize(href) ?? href);
    }
  });

  const markdown = toMd($, $("body").length ? $("body").html() ?? "" : $.root().html() ?? "");
  return { markdown, footnotes };
}

function toMd($: cheerio.CheerioAPI, fragment: string): string {
  if (!fragment.trim()) return "";
  let md = td.turndown(fragment);
  md = md
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .replace(/[ \t]{2,}/g, " ")
    .trim();
  return md;
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/** Render a list of footnotes as Markdown definitions. */
export function renderFootnotes(notes: Footnote[]): string {
  return notes.map((n) => `[^${n.marker}]: ${n.text.replace(/\n+/g, " ")}`).join("\n");
}

/** Convert a rendered page's main content to Markdown (generic fallback). */
export function pageHtmlToMarkdown(html: string): MarkdownResult {
  const $ = cheerio.load(html);
  $("script, style, noscript, header, footer, nav, dialog, svg, form").remove();
  const main = $("main").first();
  const root = main.length ? main : $("body");
  return htmlToMarkdown(root.html() ?? "");
}
