import type { MetadataRoute } from "next";

const BASE = "https://latterdaystats.samuelbaird.com";

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
