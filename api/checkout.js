// Creates a Stripe Checkout session for a donation and redirects to it.
// Ported from latter-day-stats (src/app/actions/donate.ts): same limits,
// one-time vs monthly, submit_type "donate". Uses Stripe's REST API directly
// so the site stays dependency-free. Needs STRIPE_SECRET_KEY.
const MIN_CENTS = 100;
const MAX_CENTS = 1_000_000;

function originFor(req) {
  const host = String(req.headers.host || "");
  const ok = /^(samuelbaird\.com|www\.samuelbaird\.com|[a-z0-9-]+\.vercel\.app|localhost:\d+)$/.test(host);
  const proto = host.startsWith("localhost") ? "http" : "https";
  return ok ? `${proto}://${host}` : "https://samuelbaird.com";
}

async function readForm(req) {
  if (req.body && typeof req.body === "object") return req.body;
  let raw = "";
  for await (const chunk of req) raw += chunk;
  return Object.fromEntries(new URLSearchParams(raw));
}

module.exports = async function handler(req, res) {
  const origin = originFor(req);
  const back = (code) => {
    res.statusCode = 303;
    res.setHeader("Location", `${origin}/donate/?error=${code}#give`);
    res.end();
  };
  if (req.method !== "POST") {
    res.statusCode = 405;
    res.setHeader("Allow", "POST");
    return res.end("Method not allowed");
  }

  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) return back("config");

  const form = await readForm(req);
  const cents = Math.round(Number(form.amount) * 100);
  if (!Number.isFinite(cents) || cents < MIN_CENTS || cents > MAX_CENTS) {
    return back("amount");
  }
  const monthly = form.frequency === "monthly";

  const p = new URLSearchParams();
  p.set("mode", monthly ? "subscription" : "payment");
  p.set("line_items[0][quantity]", "1");
  p.set("line_items[0][price_data][currency]", "usd");
  p.set("line_items[0][price_data][unit_amount]", String(cents));
  p.set(
    "line_items[0][price_data][product_data][name]",
    monthly ? "Monthly donation to Samuel Baird" : "Donation to Samuel Baird",
  );
  if (monthly) p.set("line_items[0][price_data][recurring][interval]", "month");
  else p.set("submit_type", "donate");
  p.set("success_url", `${origin}/donate/thanks/?session_id={CHECKOUT_SESSION_ID}`);
  p.set("cancel_url", `${origin}/donate/`);

  try {
    const r = await fetch("https://api.stripe.com/v1/checkout/sessions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${key}`,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: p,
    });
    const s = await r.json();
    if (!r.ok || !s.url) {
      console.error("stripe checkout create failed:", s && s.error && s.error.message);
      return back("stripe");
    }
    res.statusCode = 303;
    res.setHeader("Location", s.url);
    res.end();
  } catch (e) {
    console.error("stripe checkout create failed:", e);
    back("stripe");
  }
};
