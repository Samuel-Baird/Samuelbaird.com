import { getPublishedClaims, getRecentlyAdded } from "@/lib/data";
import { SITE_URL } from "@/lib/site";
import type { Claim } from "@/lib/types";

export const revalidate = 3600;

function escapeXml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

export async function GET() {
  // Degrade to an empty feed on a data-layer outage rather than 500 — an RSS
  // reader should see a valid (if empty) document, same as the command
  // palette degrades to an empty search index.
  let channels: Awaited<ReturnType<typeof getRecentlyAdded>>["channels"] = [];
  let studies: Awaited<ReturnType<typeof getRecentlyAdded>>["studies"] = [];
  let claims: Claim[] = [];
  try {
    ({ channels, studies } = await getRecentlyAdded(90, 20));
  } catch (error) {
    console.error("feed.xml: recently-added data unavailable:", error);
  }
  try {
    claims = (await getPublishedClaims()).slice(0, 20);
  } catch (error) {
    console.error("feed.xml: claims unavailable:", error);
  }

  const channelItems = channels.map((c) => ({
    title: `New channel: ${c.name}`,
    link: `${SITE_URL}/channels/${c.slug}`,
    description: c.description ?? `Now tracking ${c.name} on Latter-day Stats.`,
    pubDate: c.created_at,
  }));

  const studyItems = studies.map((s) => ({
    title: `New study: ${s.title}`,
    link: `${SITE_URL}/studies/${s.slug}`,
    description: s.abstract ?? `${s.title} was added to the Latter-day Stats research library.`,
    pubDate: s.created_at,
  }));

  const claimItems = claims
    .filter((c) => c.published_at)
    .map((c) => ({
      title: `New claim response: ${c.title}`,
      link: `${SITE_URL}/claims/${c.slug}`,
      description: c.claim_text,
      pubDate: c.published_at!,
    }));

  const items = [...channelItems, ...studyItems, ...claimItems].sort(
    (a, b) => new Date(b.pubDate).getTime() - new Date(a.pubDate).getTime(),
  );

  const itemsXml = items
    .map(
      (item) => `  <item>
    <title>${escapeXml(item.title)}</title>
    <link>${escapeXml(item.link)}</link>
    <guid>${escapeXml(item.link)}</guid>
    <description>${escapeXml(item.description)}</description>
    <pubDate>${new Date(item.pubDate).toUTCString()}</pubDate>
  </item>`,
    )
    .join("\n");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Latter-day Stats</title>
  <link>${SITE_URL}</link>
  <description>Newly added channels and studies on Latter-day Stats.</description>
  <language>en-us</language>
${itemsXml}
</channel>
</rss>`;

  return new Response(xml, {
    headers: { "Content-Type": "application/rss+xml; charset=utf-8" },
  });
}
