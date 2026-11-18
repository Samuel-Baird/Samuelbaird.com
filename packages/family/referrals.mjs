// One place for every referral program used across the family sites (ticket 0.3).
// Sites stay ad-free; referral links are how they earn. Every page that shows these links must say so
// (see DISCLOSURE) and mark the links rel="sponsored".
//
// Amazon Associates: tracking ID below (also baked into the Deseret Wiki's link.amazon short links).
// eBay Partner Network: set EBAY_CAMPAIGN_ID once the EPN account is approved
// (partnernetwork.ebay.com > Campaigns). Until then ebayUrl() returns plain links.

export const AMAZON_TAG = 'ithinkthereforeisam-20';
export const EBAY_CAMPAIGN_ID = null; // e.g. '5339012345'

export const DISCLOSURE = {
  amazon: 'As an Amazon Associate I earn from qualifying purchases.',
  ebay: 'eBay links are affiliate links; I may earn a commission.',
  both: 'Links to Amazon and eBay are affiliate links; I may earn a commission on purchases at no cost to you.',
};

/** Amazon product link with the tag. Extra params (e.g. wishlist ids) are kept. */
export function amazonUrl(asin, params = {}) {
  const q = new URLSearchParams({ ...params, tag: AMAZON_TAG });
  return `https://www.amazon.com/dp/${encodeURIComponent(asin)}?${q}`;
}

/** Adds the tag to any amazon.com URL (leaves link.amazon short links alone: they already carry it). */
export function tagAmazon(url) {
  try {
    const u = new URL(url);
    if (!/(^|\.)amazon\.com$/.test(u.hostname)) return url;
    u.searchParams.set('tag', AMAZON_TAG);
    return u.toString();
  } catch { return url; }
}

/**
 * eBay item or search URL with EPN tracking. `sub` is an optional custom id (shows in EPN reports),
 * e.g. 'collection' or 'scout', to see which page earned the click.
 */
export function ebayUrl(url, sub = '') {
  if (!EBAY_CAMPAIGN_ID) return url;
  try {
    const u = new URL(url);
    if (!/(^|\.)ebay\.com$/.test(u.hostname)) return url;
    for (const [k, v] of Object.entries({ mkcid: '1', mkrid: '711-53200-19255-0', siteid: '0', campid: EBAY_CAMPAIGN_ID, customid: sub, toolid: '10001', mkevt: '1' })) u.searchParams.set(k, v);
    return u.toString();
  } catch { return url; }
}
