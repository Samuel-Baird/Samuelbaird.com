// OpenNext adapter config for Cloudflare Workers (https://opennext.js.org/cloudflare).
// Peepstone has no ISR or revalidation: the home page is prerendered and /mcp is dynamic, so the read-only
// static-assets cache is enough (no R2 bucket, KV or Durable Objects to provision).
import { defineCloudflareConfig } from "@opennextjs/cloudflare";
import staticAssetsIncrementalCache from "@opennextjs/cloudflare/overrides/incremental-cache/static-assets-incremental-cache";

export default defineCloudflareConfig({
  incrementalCache: staticAssetsIncrementalCache,
});
