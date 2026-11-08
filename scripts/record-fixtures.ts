/**
 * Re-record the small JSON fixtures used by the unit tests:
 *   npm run record-fixtures
 * Fixtures are trimmed page data (not full HTML) to keep the repo small.
 */
import { mkdirSync, writeFileSync } from "node:fs";
import { getPageData, postJson } from "../src/jsp/client";
import { buildSearchBody } from "../src/jsp/search";

const dir = new URL("../test/fixtures/", import.meta.url);
mkdirSync(dir, { recursive: true });
const save = (name: string, data: unknown) =>
  writeFileSync(new URL(name, dir), JSON.stringify(data, null, 1) + "\n");

const trimLinks = (props: any, key: string, n = 3) => {
  for (const g of props[key]?.relatedlinks ?? []) g.links = g.links.slice(0, n);
  return props;
};

const doc = (await getPageData("/paper-summary/journal-1835-1836/11")).pageProps;
doc.gallery = doc.gallery.slice(0, 12);
doc.tableOfContents = doc.tableOfContents.slice(0, 12);
doc.summary.historicalIntro.text = doc.summary.historicalIntro.text.slice(0, 4000) + "</div></body></html>";
doc.summary.historicalIntro.footnotes = doc.summary.historicalIntro.footnotes.slice(0, 3);
save("document.json", { route: "/paper-summary/[uri]/[page]", pageProps: doc });

save("person.json", { route: "/person/[uri]", pageProps: trimLinks((await getPageData("/person/emma-hale-smith")).pageProps, "person") });
save("topic.json", { route: "/topic/[uri]", pageProps: trimLinks((await getPageData("/topic/nauvoo-legion")).pageProps, "topic") });
save("event.json", { route: "/event/[uri]", pageProps: (await getPageData("/event/reorganization-of-nauvoo-house-association")).pageProps });
save("browse.json", { route: "/the-papers/[[...uri]]", pageProps: { docDetails: (await getPageData("/the-papers/journals/jsppj1")).pageProps.docDetails } });

const article = (await getPageData("/articles/introduction-to-calendar-of-documents")).pageProps;
save("article.json", { route: "/articles/[articleUri]", pageProps: { articleData: article.articleData } });

const sr: any = await postJson("/api/v2-search-results", buildSearchBody({ query: "Nauvoo", perPage: 10 }));
for (const [k, item] of [["persons", "person"], ["locations", "location"], ["subjects", "subject"]]) {
  sr.search.refinements[k][item] = sr.search.refinements[k][item].slice(0, 15);
}
save("search.json", sr);
save(
  "calendar.json",
  await postJson("/api/proxyToBackend", {
    headers: {},
    method: "GET",
    url: "https://jsp-api.pvu.cf.churchofjesuschrist.org/jsp-api/v1/reference/calendar/search?startDate=1831-01-01&endDate=1831-01-31&keywords=",
  }),
);
console.log("fixtures written to", dir.pathname);
