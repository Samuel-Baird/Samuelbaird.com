import type { MetadataRoute } from "next";

const BASE = "https://latterdaystats.samuelbaird.com";

// Search and AI crawlers are explicitly welcome on public pages; naming them
// makes the policy unambiguous to assistants that look for their own token.
const AI_AND_SEARCH_BOTS = [
  "Googlebot", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User",
  "ClaudeBot", "Claude-User", "Claude-SearchBot", "anthropic-ai",
  "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot",
  "Applebot-Extended", "DuckAssistBot", "Amazonbot", "MistralAI-User",
  "cohere-ai", "Meta-ExternalAgent", "CCBot", "YouBot",
];
const PRIVATE_PATHS = ["/admin", "/api", "/me", "/login", "/auth"];

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: AI_AND_SEARCH_BOTS,
        allow: "/",
        disallow: PRIVATE_PATHS,
      },
      {
        userAgent: "*",
        allow: "/",
        disallow: PRIVATE_PATHS,
      },
    ],
    sitemap: `${BASE}/sitemap.xml`,
  };
}
