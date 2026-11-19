// OpenNext (Cloudflare Workers) config. See wrangler.jsonc for the bindings.
//
// - incrementalCache (R2): stores ISR pages (`revalidate` on /about,
//   /feed.xml, /sitemap.xml) and unstable_cache data. R2 is strongly
//   consistent and the option OpenNext recommends; KV is eventually
//   consistent, and the static-assets cache cannot revalidate at all.
// - tagCache (D1): the site leans on revalidateTag/revalidatePath (admin
//   edits, Stripe webhook, stats refresh). Without a tag cache those calls are
//   no-ops and pages stay stale until their TTL. D1 is the simplest strongly
//   consistent option (the KV one lags up to 60s; the Durable Object one is for
//   high traffic). `opennextjs-cloudflare deploy`/`preview` creates its table.
// - queue (memory): time-based revalidation re-renders the stale route via the
//   WORKER_SELF_REFERENCE service binding, de-duplicated per isolate. Enough
//   for this traffic; the Durable Object queue is the upgrade path.
import { defineCloudflareConfig } from "@opennextjs/cloudflare";
import r2IncrementalCache from "@opennextjs/cloudflare/overrides/incremental-cache/r2-incremental-cache";
import d1NextTagCache from "@opennextjs/cloudflare/overrides/tag-cache/d1-next-tag-cache";
import memoryQueue from "@opennextjs/cloudflare/overrides/queue/memory-queue";

export default defineCloudflareConfig({
  incrementalCache: r2IncrementalCache,
  tagCache: d1NextTagCache,
  queue: memoryQueue,
});
