/**
 * Low-level HTTP client for www.josephsmithpapers.org.
 *
 * The site is a Next.js app: every page embeds its data as JSON in
 * <script id="__NEXT_DATA__">, and search/calendar use internal JSON APIs.
 * We read those instead of scraping rendered HTML (whose CSS classes are
 * build hashes that change between deploys).
 */

export const JSP_ORIGIN = "https://www.josephsmithpapers.org";
export const IMAGE_BASE = `${JSP_ORIGIN}/bc-jsp/content/jsp/images`;

const USER_AGENT =
  "Peepstone-MCP/0.1 (+https://github.com/Samuel-Baird/peepstone)";
const TIMEOUT_MS = 25_000;
const MAX_CONCURRENT = 2;
const CACHE_TTL_MS = 10 * 60 * 1000;
const CACHE_MAX_ENTRIES = 40;

export class JspError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = "JspError";
  }
}

export class JspNotFoundError extends JspError {
  constructor(path: string) {
    super(`Not found on the Joseph Smith Papers: ${absUrl(path)}`, 404);
    this.name = "JspNotFoundError";
  }
}

// ---------------------------------------------------------------------------
// Small LRU cache with TTL (per server instance).

type Entry = { value: unknown; expires: number };
const cache = new Map<string, Entry>();

function cacheGet<T>(key: string): T | undefined {
  const hit = cache.get(key);
  if (!hit) return undefined;
  if (hit.expires < Date.now()) {
    cache.delete(key);
    return undefined;
  }
  cache.delete(key);
  cache.set(key, hit); // refresh recency
  return hit.value as T;
}

function cacheSet(key: string, value: unknown) {
  cache.set(key, { value, expires: Date.now() + CACHE_TTL_MS });
  while (cache.size > CACHE_MAX_ENTRIES) {
    cache.delete(cache.keys().next().value as string);
  }
}

/** Test hook. */
export function clearCache() {
  cache.clear();
}

// ---------------------------------------------------------------------------
// Concurrency limiter: be polite to the site.

let active = 0;
const waiting: Array<() => void> = [];

async function withSlot<T>(fn: () => Promise<T>): Promise<T> {
  if (active >= MAX_CONCURRENT) {
    await new Promise<void>((resolve) => waiting.push(resolve));
  }
  active++;
  try {
    return await fn();
  } finally {
    active--;
    waiting.shift()?.();
  }
}

async function request(url: string, init: RequestInit = {}): Promise<Response> {
  let lastErr: unknown;
  for (let attempt = 0; attempt < 3; attempt++) {
    if (attempt > 0) await new Promise((r) => setTimeout(r, 500 * 2 ** attempt));
    try {
      const res = await withSlot(() =>
        fetch(url, {
          ...init,
          redirect: "follow",
          signal: AbortSignal.timeout(TIMEOUT_MS),
          headers: {
            "user-agent": USER_AGENT,
            accept: "text/html,application/json;q=0.9,*/*;q=0.8",
            ...(init.headers ?? {}),
          },
        }),
      );
      if (res.status === 429 || res.status >= 500) {
        lastErr = new JspError(`JSP returned HTTP ${res.status} for ${url}`, res.status);
        continue;
      }
      return res;
    } catch (err) {
      lastErr = err;
    }
  }
  throw lastErr instanceof Error
    ? lastErr
    : new JspError(`Request to ${url} failed`);
}

// ---------------------------------------------------------------------------
// URL helpers.

/** Turn a JSP path (or full URL) into an absolute https URL. */
export function absUrl(pathOrUrl: string): string {
  if (/^https?:\/\//i.test(pathOrUrl)) return pathOrUrl;
  return JSP_ORIGIN + (pathOrUrl.startsWith("/") ? "" : "/") + pathOrUrl;
}

/**
 * Normalize user input (full URL, path, or bare slug) to a site path.
 * Rejects URLs on other hosts so the server can't be used as an open proxy.
 */
export function toPath(input: string, defaultPrefix?: string): string {
  const s = input.trim();
  if (/^https?:\/\//i.test(s) || /^(www\.)?josephsmithpapers\.org\//i.test(s)) {
    const u = new URL(/^https?:/i.test(s) ? s : `https://${s}`);
    if (!/(^|\.)josephsmithpapers\.org$/i.test(u.hostname)) {
      throw new JspError(
        `Only josephsmithpapers.org URLs are supported (got ${u.hostname}).`,
      );
    }
    return u.pathname + u.search;
  }
  if (s.startsWith("/")) return s;
  if (defaultPrefix) return `${defaultPrefix.replace(/\/$/, "")}/${s}`;
  return `/${s}`;
}

/** Drop the search-highlight parameter so URLs are canonical/citable. */
export function canonicalPath(path: string): string {
  const [p, q] = path.split("?");
  if (!q) return p;
  const params = new URLSearchParams(q);
  params.delete("highlight");
  if (params.get("p") === "") params.delete("p");
  const rest = params.toString();
  return rest ? `${p}?${rest}` : p;
}

// ---------------------------------------------------------------------------
// Fetchers.

export async function getHtml(path: string): Promise<string> {
  const key = `html:${path}`;
  const hit = cacheGet<string>(key);
  if (hit !== undefined) return hit;
  const res = await request(absUrl(path));
  if (res.status === 404) throw new JspNotFoundError(path);
  if (!res.ok) throw new JspError(`JSP returned HTTP ${res.status} for ${absUrl(path)}`, res.status);
  const html = await res.text();
  // Only cache small pages as raw HTML; large ones are cached as parsed props.
  if (html.length < 400_000) cacheSet(key, html);
  return html;
}

export type NextData = {
  page: string;
  buildId: string;
  query: Record<string, unknown>;
  props: { pageProps: Record<string, any> };
};

export function extractNextData(html: string): NextData | null {
  const m = html.match(
    /<script id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/,
  );
  if (!m) return null;
  try {
    return JSON.parse(m[1]) as NextData;
  } catch {
    return null;
  }
}

/** Props we never need and that are large (site-wide UI strings). */
const NOISE_PROPS = ["env", "metaStrings", "layoutStrings"];

export type PageData = {
  /** Next.js route pattern, e.g. "/person/[uri]". */
  route: string;
  pageProps: Record<string, any>;
  /** Rendered HTML (only kept when the caller asks for it). */
  html?: string;
};

export async function getPageData(
  path: string,
  opts: { keepHtml?: boolean } = {},
): Promise<PageData> {
  const key = `page:${path}:${opts.keepHtml ? 1 : 0}`;
  const hit = cacheGet<PageData>(key);
  if (hit) return hit;

  const res = await request(absUrl(path));
  if (res.status === 404) throw new JspNotFoundError(path);
  if (!res.ok) throw new JspError(`JSP returned HTTP ${res.status} for ${absUrl(path)}`, res.status);
  const html = await res.text();
  const nd = extractNextData(html);
  if (!nd) throw new JspError(`Could not read page data from ${absUrl(path)}`);
  const pageProps = { ...nd.props.pageProps };
  for (const k of NOISE_PROPS) delete pageProps[k];
  if (pageProps.is404 === true || pageProps.statusCode === 404 || nd.page === "/404" || nd.page === "/_error") {
    throw new JspNotFoundError(path);
  }
  const data: PageData = { route: nd.page, pageProps, html: opts.keepHtml ? html : undefined };
  cacheSet(key, data);
  return data;
}

export async function postJson<T>(path: string, body: unknown): Promise<T> {
  const payload = JSON.stringify(body);
  const key = `post:${path}:${payload}`;
  const hit = cacheGet<T>(key);
  if (hit !== undefined) return hit;
  const res = await request(absUrl(path), {
    method: "POST",
    body: payload,
    headers: { "content-type": "application/json", accept: "application/json" },
  });
  if (!res.ok) {
    throw new JspError(`JSP API ${path} returned HTTP ${res.status}`, res.status);
  }
  const json = (await res.json()) as T;
  cacheSet(key, json);
  return json;
}
