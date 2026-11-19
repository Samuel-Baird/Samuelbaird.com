// OpenNext (Cloudflare Workers) config. See wrangler.jsonc for the bindings.
//
// - incrementalCache (Workers KV): stores ISR pages (`revalidate` on /about,
//   /feed.xml, /sitemap.xml) and unstable_cache data. R2 is the option
//   OpenNext recommends (strongly consistent), but R2 is not enabled on the
//   account (it needs a payment method). KV is on the free plan; it is
//   eventually consistent (a write can take up to ~60s to show everywhere),
//   which is fine for this site. The static-assets cache cannot revalidate.
// - tagCache (D1): the site leans on revalidateTag/revalidatePath (admin
//   edits, Stripe webhook, stats refresh). Without a tag cache those calls are
//   no-ops and pages stay stale until their TTL. D1 is the simplest strongly
//   consistent option (the KV one lags up to 60s; the Durable Object one is for
//   high traffic). `opennextjs-cloudflare deploy`/`preview` creates its table.
// - queue (memory): time-based revalidation re-renders the stale route via the
//   WORKER_SELF_REFERENCE service binding, de-duplicated per isolate. Enough
//   for this traffic; the Durable Object queue is the upgrade path.
import { defineCloudflareConfig } from "@opennextjs/cloudflare";
import kvIncrementalCache from "@opennextjs/cloudflare/overrides/incremental-cache/kv-incremental-cache";
import d1NextTagCache from "@opennextjs/cloudflare/overrides/tag-cache/d1-next-tag-cache";
import memoryQueue from "@opennextjs/cloudflare/overrides/queue/memory-queue";

export default defineCloudflareConfig({
  incrementalCache: kvIncrementalCache,
  tagCache: d1NextTagCache,
  queue: memoryQueue,
});
