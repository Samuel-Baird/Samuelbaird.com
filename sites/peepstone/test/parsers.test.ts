import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { canonicalPath, toPath } from "../src/jsp/client";
import { citation } from "../src/jsp/cite";
import { formatDocument, parseDocumentPage, parseDocumentRef } from "../src/jsp/document";
import { formatEntity, parseEntity } from "../src/jsp/entities";
import { htmlToMarkdown } from "../src/jsp/html";
import { formatArticle, formatBrowse, formatCalendar, parseCalendarEntry } from "../src/jsp/pages";
import { buildSearchBody, formatSearch, parseSearchResponse } from "../src/jsp/search";
import { windowText } from "../src/format";

const fixture = (name: string) =>
  JSON.parse(readFileSync(new URL(`./fixtures/${name}`, import.meta.url), "utf8"));

describe("url helpers", () => {
  it("normalizes slugs, paths and URLs", () => {
    expect(toPath("journal-1835-1836", "/paper-summary")).toBe("/paper-summary/journal-1835-1836");
    expect(toPath("/person/emma-hale-smith")).toBe("/person/emma-hale-smith");
    expect(toPath("https://www.josephsmithpapers.org/topic/nauvoo-legion?highlight=x")).toBe(
      "/topic/nauvoo-legion?highlight=x",
    );
    expect(toPath("josephsmithpapers.org/place/nauvoo-illinois")).toBe("/place/nauvoo-illinois");
  });
  it("refuses other hosts", () => {
    expect(() => toPath("https://example.com/paper-summary/x/1")).toThrow(/josephsmithpapers\.org/);
  });
  it("drops highlight params", () => {
    expect(canonicalPath("/back/x?p=1&highlight=Nauvoo")).toBe("/back/x?p=1");
    expect(canonicalPath("/topic/y?p=")).toBe("/topic/y");
  });
  it("parses document refs", () => {
    expect(parseDocumentRef("https://www.josephsmithpapers.org/paper-summary/journal-1835-1836/11")).toEqual({
      slug: "journal-1835-1836",
      page: 11,
    });
    expect(parseDocumentRef("journal-1835-1836", 4)).toEqual({ slug: "journal-1835-1836", page: 4 });
    expect(() => parseDocumentRef("/person/emma-hale-smith")).toThrow(/Not a document/);
  });
});

describe("htmlToMarkdown", () => {
  it("turns entity pop-ups into links and notes into footnotes", () => {
    const html = `<div>Br <aside class="popup-wrapper" id="1"><a href="#1" class="reference staticPopup">Samuel Smith</a><div class="popup-content"><div class="note-data"><p>Bio…</p><a class="more" href="/person/samuel-harrison-smith">View Full Bio</a></div></div></aside>s house.<aside class="popup-wrapper" id="2"><a href="#2" class="editorial-note-static staticPopup"><span>1</span></a><div class="popup-content"><div class="note-data editorial-footnote"><p>A note.</p><hr><div class="works-cited-links"><a href="/works-cited">Works</a></div></div></div></aside> <span class="deleted">gone</span> kept [d]</div>`;
    const r = htmlToMarkdown(html);
    expect(r.markdown).toBe(
      "Br [Samuel Smith](https://www.josephsmithpapers.org/person/samuel-harrison-smith)s house.[^1] ~~gone~~ kept [d]",
    );
    expect(r.footnotes).toEqual([{ marker: "1", text: "A note." }]);
    expect(htmlToMarkdown(html, { references: "text" }).markdown).toMatch(/^Br Samuel Smiths house/);
  });
});

describe("documents", () => {
  const { pageProps } = fixture("document.json");
  const d = parseDocumentPage(pageProps, { slug: "journal-1835-1836", page: 11 });
  it("extracts metadata", () => {
    expect(d.title).toBe("Journal, 1835–1836");
    expect(d.editorialPageNumber).toBe("10");
    expect(d.numberOfPages).toBe(196);
    expect(d.previous).toMatch(/journal-1835-1836\/10$/);
    expect(d.next).toMatch(/journal-1835-1836\/12$/);
    expect(d.images?.large).toMatch(/^https:\/\/www\.josephsmithpapers\.org\/bc-jsp\/content\/jsp\/images\/6663\//);
    expect(d.citation).toMatch(/^Journal, 1835–1836, p\. 10, The Joseph Smith Papers, accessed .+, https:\/\/www\.josephsmithpapers\.org\/paper-summary\/journal-1835-1836\/11$/);
  });
  it("renders the transcript without HTML", () => {
    expect(d.transcript).toContain("oblieged to sell his cow");
    expect(d.transcript).not.toMatch(/<\/?(div|span|aside)/);
    expect(d.footnotes.length).toBeGreaterThan(0);
  });
  it("formats requested sections", () => {
    const md = formatDocument(d, ["transcript", "footnotes", "historicalIntro"]);
    expect(md).toContain("## Historical Introduction");
    expect(md).toContain("## Transcript");
    expect(md).toContain("### Footnotes");
    expect(formatDocument(d)).not.toContain("## Historical Introduction");
  });
  it("expanded text marks deletions", () => {
    const x = parseDocumentPage(pageProps, { slug: "journal-1835-1836", page: 11 }, { text: "expanded" });
    expect(x.transcript).toContain("~~Lawsuit,~~");
  });
});

describe("entities", () => {
  it("parses a person", () => {
    const e = parseEntity(fixture("person.json").pageProps, "person", "/person/emma-hale-smith");
    expect(e.name).toBe("Smith, Emma Hale");
    expect(e.url).toBe("https://www.josephsmithpapers.org/person/emma-hale-smith");
    expect(e.altNames).toContain("Bidamon, Emma Hale");
    expect(e.description).toMatch(/^10 July 1804\[\^1\]/);
    expect(e.footnotes.length).toBeGreaterThan(5);
    expect(e.related[0].links.length).toBeGreaterThan(0);
    expect(formatEntity(e)).toContain("**Mentions in the papers:**");
  });
  it("parses a glossary topic and an event", () => {
    const t = parseEntity(fixture("topic.json").pageProps, "topic", "/topic/nauvoo-legion");
    expect(t.name).toBe("Nauvoo Legion");
    expect(t.description).toContain("Illinois state militia");
    const ev = parseEntity(fixture("event.json").pageProps, "event", "/event/reorganization-of-nauvoo-house-association");
    expect(ev.date).toBe("7 April 1845");
  });
});

describe("search", () => {
  it("builds the request the site expects", () => {
    const b = buildSearchBody({ query: "temple", types: ["papers"], people: ["Hyrum Smith"], startDate: "1840-01-01" });
    expect(b.search.refinements.persons.person).toEqual([
      { id: "personhyrum-smith", title: "Hyrum Smith", selected: true },
    ]);
    const typeIds = b.search.refinements.types.type.map((t: any) => t.id);
    expect(typeIds).toContain("documents-papers");
    expect(typeIds).toContain("documents-papers-journals");
    expect(b.search.refinements.dates.start).toBe("1840-01-01");
  });
  it("parses and formats results", () => {
    const r = parseSearchResponse(fixture("search.json"), { query: "Nauvoo" });
    expect(r.total).toBeGreaterThan(1000);
    expect(r.hits).toHaveLength(10);
    expect(r.hits[0].url).toMatch(/^https:\/\/www\.josephsmithpapers\.org\//);
    expect(r.hits[0].url).not.toContain("highlight=");
    expect(r.hits.some((h) => h.snippet.includes("**Nauvoo**"))).toBe(true);
    expect(r.facets?.people.length).toBeGreaterThan(0);
    const md = formatSearch(r);
    expect(md).toContain("# Search: “Nauvoo”");
    expect(md).toContain("- people:");
  });
});

describe("pages", () => {
  it("formats browse panes", () => {
    const md = formatBrowse(fixture("browse.json").pageProps, "/the-papers/journals/jsppj1");
    expect(md).toContain("# Journals, 1832–1839");
    expect(md).toContain("https://www.josephsmithpapers.org/paper-summary/journal-1835-1836");
  });
  it("formats articles", () => {
    const md = formatArticle(fixture("article.json").pageProps, "/articles/introduction-to-calendar-of-documents");
    expect(md).toContain("# Calendar of Documents");
    expect(md).toContain("chronological order");
  });
  it("parses the calendar", () => {
    const entries = (fixture("calendar.json") as any[]).map(parseCalendarEntry);
    expect(entries).toHaveLength(4);
    expect(entries[0].heading).toMatch(/D&C 38/);
    const md = formatCalendar(entries, { startDate: "1831-01-01" }, 0, 2);
    expect(md).toContain("1831-01-01 to 1831-01-31");
    expect(md).toContain("offset=2");
  });
});

describe("output helpers", () => {
  it("windows long text with continuation hints", () => {
    const text = "line\n".repeat(10_000);
    const first = windowText(text, 0, 1000);
    expect(first).toMatch(/call again with offset=\d+/);
    const next = Number(first.match(/offset=(\d+)/)![1]);
    expect(windowText(text, next, 1000)).toMatch(/^_\(continuing from character/);
  });
  it("builds citations", () => {
    expect(citation({ title: "Nauvoo Legion", url: "https://x", accessed: new Date("2026-11-08T18:00:00Z") })).toBe(
      "Nauvoo Legion, The Joseph Smith Papers, accessed November 8, 2026, https://x",
    );
  });
});
