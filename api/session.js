// Thank-you page helper: returns just the amount/frequency of a Checkout
// session (never the key or customer details).
module.exports = async function handler(req, res) {
  res.setHeader("Content-Type", "application/json");
  res.setHeader("Cache-Control", "no-store");
  const key = process.env.STRIPE_SECRET_KEY;
  const id = String((req.query && req.query.session_id) || "");
  if (!key || !/^cs_[A-Za-z0-9_]+$/.test(id)) return res.end("{}");
  try {
    const r = await fetch(`https://api.stripe.com/v1/checkout/sessions/${id}`, {
      headers: { Authorization: `Bearer ${key}` },
    });
    const s = await r.json();
    if (!r.ok) return res.end("{}");
    res.end(JSON.stringify({
      amountCents: s.amount_total || 0,
      monthly: s.mode === "subscription",
      paid: s.payment_status === "paid",
    }));
  } catch {
    res.end("{}");
  }
};
