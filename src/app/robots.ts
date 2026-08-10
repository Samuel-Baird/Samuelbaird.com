import type { MetadataRoute } from "next";

const BASE = "https://latter-day-stats.vercel.app";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: ["/admin", "/api", "/me", "/login", "/auth"],
      },
    ],
    sitemap: `${BASE}/sitemap.xml`,
  };
}
