import { unstable_cache } from "next/cache";
import {
  fetchFacebookStats,
  fetchInstagramStats,
  fetchTikTokStats,
  fetchXStats,
  type SocialStats,
} from "./social-stats";

const SIX_HOURS = 60 * 60 * 6;

export const getInstagramStats = unstable_cache(
  async (url: string) => fetchInstagramStats(url),
  ["social-stats", "instagram"],
  { revalidate: SIX_HOURS, tags: ["social-stats"] },
);

export const getTikTokStats = unstable_cache(
  async (url: string) => fetchTikTokStats(url),
  ["social-stats", "tiktok"],
  { revalidate: SIX_HOURS, tags: ["social-stats"] },
);

export const getFacebookStats = unstable_cache(
  async (url: string) => fetchFacebookStats(url),
  ["social-stats", "facebook"],
  { revalidate: SIX_HOURS, tags: ["social-stats"] },
);

export const getXStats = unstable_cache(
  async (url: string) => fetchXStats(url),
  ["social-stats", "x"],
  { revalidate: SIX_HOURS, tags: ["social-stats"] },
);

export type PlatformKey = "facebook" | "instagram" | "tiktok" | "x";

export async function getAllSocialStats(urls: {
  facebook?: string | null;
  instagram?: string | null;
  tiktok?: string | null;
  x?: string | null;
}): Promise<Record<PlatformKey, SocialStats | null>> {
  const [facebook, instagram, tiktok, x] = await Promise.all([
    urls.facebook ? getFacebookStats(urls.facebook) : Promise.resolve(null),
    urls.instagram ? getInstagramStats(urls.instagram) : Promise.resolve(null),
    urls.tiktok ? getTikTokStats(urls.tiktok) : Promise.resolve(null),
    urls.x ? getXStats(urls.x) : Promise.resolve(null),
  ]);
  return { facebook, instagram, tiktok, x };
}
