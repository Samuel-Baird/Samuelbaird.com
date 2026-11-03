# Webmaster tools and analytics: setup steps

Do these once. Total time: about 15 minutes. They need your own Google, Microsoft and Vercel logins, so they can't be done for you.

## 1. Vercel Web Analytics (see which AI assistants send visitors)

The tracking snippet is already in every page (added in the build). You only need to switch it on:

1. Open https://vercel.com/samuel-bairds-projects/samuelbaird-com/analytics
2. Click **Enable** (Web Analytics). The Hobby plan includes it.
3. Redeploy is not needed once the snippet has been merged and deployed. Visit https://samuelbaird.com, then check the dashboard after a few minutes.
4. To see AI referrals: **Analytics > Referrers**. Look for `chatgpt.com`, `perplexity.ai`, `claude.ai`, `copilot.microsoft.com`, `gemini.google.com`, `bing.com`, `duckduckgo.com`.

It is cookie-free, so no consent banner is needed.

Latter-day Stats already includes `<Analytics />` in its layout. Enable it for that project too at https://vercel.com/samuel-bairds-projects/latter-day-stats/analytics

## 2. Google Search Console

Link: https://search.google.com/search-console

1. Click **Add property** and choose **Domain**. Enter `samuelbaird.com`. (A Domain property covers www and all subdomains, including `latterdaystats.samuelbaird.com`.)
2. Google gives you a TXT record. Add it in the DNS for the domain.
   - If the domain's nameservers are Vercel's: https://vercel.com/dashboard/domains > `samuelbaird.com` > Add record > Type `TXT`, Name `@`, Value = the string Google gave you.
   - Otherwise add it at your registrar's DNS page.
3. Back in Search Console click **Verify** (DNS can take a few minutes).
4. **Sitemaps** (left menu): submit `sitemap.xml`. The full URL is https://samuelbaird.com/sitemap.xml
5. **URL inspection** (top bar): paste each of these and click **Request indexing**:
   - https://samuelbaird.com/
   - https://samuelbaird.com/faq
   - https://samuelbaird.com/data
   - https://samuelbaird.com/sacred-sites/sites
   - https://samuelbaird.com/about
6. Repeat step 1 only if you ever want a separate property for the Latter-day Stats subdomain. The Domain property already includes it, so you can instead submit https://latterdaystats.samuelbaird.com/sitemap.xml under **Sitemaps** in the same property.
7. Check later: **Indexing > Pages** (what is indexed, and why anything is not) and **Enhancements** (structured data: FAQ, Dataset, Breadcrumbs).

## 3. Bing Webmaster Tools (also feeds Microsoft Copilot and several AI search engines)

Link: https://www.bing.com/webmasters

1. Sign in with a Microsoft account.
2. Easiest: click **Import from Google Search Console** and authorise. This brings in the verified property and sitemaps in one step.
   - Manual alternative: **Add a site**, enter `https://samuelbaird.com`, verify with the DNS CNAME record Bing shows (add it the same way as the Google TXT record).
3. **Sitemaps > Submit sitemap**: https://samuelbaird.com/sitemap.xml
4. **URL Submission**: submit the five pages listed above.
5. Optional, faster re-indexing after changes: **IndexNow** (https://www.indexnow.org). Generate a key at https://www.bing.com/indexnow/getstarted, save it as `<key>.txt` at the site root, and ping the URLs you changed. Supported by Bing, Yandex and others (Google does not use it).

## 4. Check it worked

- https://samuelbaird.com/robots.txt lists the AI crawlers as allowed.
- https://samuelbaird.com/llms.txt loads as plain text.
- Rich results test: https://search.google.com/test/rich-results (enter /faq and /data).
- Schema validator: https://validator.schema.org (enter any page URL).

## 5. Monthly routine (5 minutes)

1. Vercel Analytics > Referrers: note AI referrals.
2. Search Console > Performance: top queries and pages.
3. Ask ChatGPT, Claude, Perplexity and Gemini the prompts in `docs/GEO.md`, and log whether samuelbaird.com is cited and correct.
4. If Latter-day Stats or Pulpit figures changed, update the `EXT` block in `scripts/build.mjs`, run `node scripts/build.mjs`, commit and push.
