# josephsmithpapers.org data sources

These notes cover what Peepstone reads. The endpoints are internal, so expect them to change. They were confirmed against the live site in November 2026 (Next.js build `r1Non2WYTuabf_S7ubtJt`).

## Search: `POST /api/v2-search-results`

```json
{
  "search": {
    "query": "temple",
    "perPage": 10,
    "sort": "relevance",
    "pageNumber": 1,
    "getRefinements": true,
    "documentURI": "",
    "refinements": {
      "dates": { "start": "1840-01-01", "end": "1842-12-31" },
      "locations": { "location": [{ "id": "placenauvoo,-illinois", "title": "Nauvoo, Illinois", "selected": true }] },
      "persons": { "person": [{ "id": "personhyrum-smith", "title": "Hyrum Smith", "selected": true }] },
      "subjects": { "subject": [{ "id": "topicnauvoo-legion", "title": "Nauvoo Legion", "selected": true }] },
      "types": { "type": [{ "id": "documents-papers-journals", "selected": true }] },
      "isSuggestion": false,
      "transcriptsOnly": false
    }
  }
}
```

- `sort`: `relevance` | `alphabetical` | `date`. `perPage` accepts any value from 1 to 50 (the site UI offers 10, 20 and 50).
- **People, place and subject facets are matched by `title`.** An `id` sent alone is ignored.
- Type ids:
  - `documents-papers`, plus the subtypes `-administrative`, `-documents`, `-legal`, `-financial`, `-histories`, `-journals`, `-revelations-and-translations`, `-introductions` and `-other-contemporary-papers`. Selecting the parent alone barely filters, so the site UI sends the parent together with every subtype.
  - `related-materials`, `biographical-directory`, `geographical-directory`, `glossary`, `event`.
- Response: `search.total` and `search.results.result[]` with `{title, link, summary (HTML with <mark>), summaryType, date, image, documentURI}`.
  - `summaryType` values: `documentText`, `footnote`, `personSummaryText`, `placeSummaryText`, `topicSummaryText`, `eventSummaryText`.
  - `search.refinements` holds the facets, with counts.

## Calendar of Documents: `POST /api/proxyToBackend`

```json
{ "headers": {}, "method": "GET",
  "url": "https://jsp-api.pvu.cf.churchofjesuschrist.org/jsp-api/v1/reference/calendar/search?startDate=1831-01-01&endDate=1831-01-31&keywords=" }
```
Returns `[{ id, heading, label, sortDate, calendar, content: [HTML version lines] }]`.

## Pages: `<script id="__NEXT_DATA__">` → `props.pageProps`

| Route | Key props |
|---|---|
| `/paper-summary/{slug}/{page}` | `summary` contains:<ul><li>`clearText` and `expandedText`</li><li>`footnotes`, `historicalIntro{text,footnotes}`, `sourceNotes{text,footnotes}`</li><li>`documentSeriesTitle`, `editorialPageNumber`, `numberOfPages`, `date`, `handwriting`, `scribes`, `classification`</li><li>`versions`, `images{small,medium,large,download}Url`, `dzUrlXml`</li></ul>The page itself also carries `gallery[]` and `tableOfContents[]`. |
| `/person/`, `/place/`, `/topic/`, `/event/{slug}` | `[kind].authority.refObject` contains `docDesc` and `documentInfo{abstract, classification, defaultUrl}`, and `[kind].description.summary` (HTML). `[kind]` also carries `altNames`, `geo`, `date`, `images[]` and `relatedlinks[{name, links[]}]`. |
| `/articles/`, `/intro/`, `/back/`, `/site/{slug}`, `/news` | `articleData{documentInfo, title, content, footnotes}` |
| `/the-papers/{series}/{volume}` | `docDetails.panes[].sections[].links[]` |
| `/reference/people`, `/reference/places` (and similar) | `entityList[{name, url}]`. The whole directory comes back in one response, and `?filter=x` is applied client-side. |
| `/reference/calendar-of-documents` | `titlesByMonth` (slugs only), so use the calendar API instead |

Images are served under `https://www.josephsmithpapers.org/bc-jsp/content/jsp/images/{accession}/…`.

### HTML conventions in transcripts and notes
- `aside.popup-wrapper` marks either an entity reference or an editorial footnote:
  - Entity reference: the trigger is `a.reference`, and `a.more` links to `/person/…` and similar pages.
  - Editorial footnote: the trigger is `a.editorial-note-static`, and the body is `.editorial-footnote`.
- `span.deleted` marks deletions, `span.line-break` marks manuscript line breaks, and `span.superscript` marks superscripts.
