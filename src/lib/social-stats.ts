export type SocialStats = {
  followers?: number;
  following?: number;
  posts?: number;
  likes?: number;
};

const UA =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36";

async function fetchHtml(url: string): Promise<string | null> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 5000);
  try {
    const res = await fetch(url, {
      headers: {
        "User-Agent": UA,
        Accept:
          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
      },
      signal: controller.signal,
      redirect: "follow",
    });
    if (!res.ok) return null;
    return await res.text();
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

function parseCompact(raw: string): number | undefined {
  const cleaned = raw.replace(/,/g, "").trim();
  const m = cleaned.match(/^([\d.]+)\s*([KMB]?)$/i);
  if (!m) {
    const n = Number(cleaned);
    return Number.isFinite(n) ? n : undefined;
  }
  const n = parseFloat(m[1]);
  const suffix = m[2].toUpperCase();
  const mult = suffix === "K" ? 1e3 : suffix === "M" ? 1e6 : suffix === "B" ? 1e9 : 1;
  return Math.round(n * mult);
}

export async function fetchInstagramStats(
  url: string,
): Promise<SocialStats | null> {
  const html = await fetchHtml(url);
  if (!html) return null;
  const og = html.match(
    /<meta[^>]+property=["']og:description["'][^>]+content=["']([^"']+)["']/i,
  );
  if (!og) return null;
  const desc = og[1];
  const m = desc.match(
    /([\d.,KMB]+)\s+Followers,\s+([\d.,KMB]+)\s+Following,\s+([\d.,KMB]+)\s+Posts/i,
  );
  if (!m) return null;
  return {
    followers: parseCompact(m[1]),
    following: parseCompact(m[2]),
    posts: parseCompact(m[3]),
  };
}

export async function fetchTikTokStats(
  url: string,
): Promise<SocialStats | null> {
  const html = await fetchHtml(url);
  if (!html) return null;
  const m = html.match(
    /<script[^>]+id=["']__UNIVERSAL_DATA_FOR_REHYDRATION__["'][^>]*>([\s\S]*?)<\/script>/i,
  );
  if (!m) return null;
  try {
    const data = JSON.parse(m[1]);
    const stats =
      data?.__DEFAULT_SCOPE__?.["webapp.user-detail"]?.userInfo?.stats ??
      data?.__DEFAULT_SCOPE__?.["webapp.user-detail"]?.userInfo?.statsV2;
    if (!stats) return null;
    const toNum = (v: unknown) => {
      if (typeof v === "number") return v;
      if (typeof v === "string") {
        const n = Number(v);
        return Number.isFinite(n) ? n : undefined;
      }
      return undefined;
    };
    return {
      followers: toNum(stats.followerCount),
      following: toNum(stats.followingCount),
      likes: toNum(stats.heartCount ?? stats.heart),
      posts: toNum(stats.videoCount),
    };
  } catch {
    return null;
  }
}

export async function fetchFacebookStats(
  url: string,
): Promise<SocialStats | null> {
  const html = await fetchHtml(url);
  if (!html) return null;
  const follow = html.match(/"follower_count":\s*(\d+)/);
  if (follow) return { followers: Number(follow[1]) };
  const og = html.match(
    /<meta[^>]+property=["']og:description["'][^>]+content=["']([^"']+)["']/i,
  );
  if (og) {
    const m = og[1].match(/([\d.,KMB]+)\s+(?:likes|followers)/i);
    if (m) return { followers: parseCompact(m[1]) };
  }
  return null;
}

// X (Twitter) returns HTTP 402 to unauthenticated bots; the free API tier
// no longer exposes user lookup. No free path exists.
export async function fetchXStats(_url: string): Promise<SocialStats | null> {
  return null;
}
