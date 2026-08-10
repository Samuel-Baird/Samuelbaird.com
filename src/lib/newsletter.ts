import "server-only";

import type { SupabaseClient } from "@supabase/supabase-js";
import { escapeHtml, sendEmail } from "@/lib/email";
import { logEvent } from "@/lib/log";
import { SITE_URL } from "@/lib/site";
import { uuidSchema } from "@/lib/validation";

// Space sends out to stay well under Resend's free-tier 2 req/s.
const SEND_DELAY_MS = 550;

const WRAPPER_STYLE =
  "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;" +
  "font-size:15px;line-height:1.6;color:#1c1c1c;max-width:640px";
const META_STYLE = "color:#6b6b6b;font-size:13px;margin:0 0 4px";

export type MonthlyWindow = {
  sinceIso: string;
  untilIso: string;
  monthKey: string;
  monthLabel: string;
};

/**
 * The calendar month before `now`, in UTC. Called on the 1st, so this is
 * "last month" — the month that just closed.
 */
export function monthlyWindow(now: Date = new Date()): MonthlyWindow {
  const y = now.getUTCFullYear();
  const m = now.getUTCMonth(); // 0-indexed; "this month" start
  const since = new Date(Date.UTC(y, m - 1, 1));
  const until = new Date(Date.UTC(y, m, 1));
  const monthKey = `${since.getUTCFullYear()}-${String(since.getUTCMonth() + 1).padStart(2, "0")}`;
  const monthLabel = since.toLocaleString("en-US", {
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  });
  return {
    sinceIso: since.toISOString(),
    untilIso: until.toISOString(),
    monthKey,
    monthLabel,
  };
}

type NewsletterChannel = {
  slug: string;
  name: string;
  channel_types: string[] | null;
};

type NewsletterStudy = {
  slug: string;
  title: string;
  authors: string[] | null;
  year: number | null;
  source_type: string | null;
  category: string | null;
};

export async function fetchMonthlyContent(
  sb: SupabaseClient,
  w: MonthlyWindow,
): Promise<{ channels: NewsletterChannel[]; studies: NewsletterStudy[] }> {
  const [channelsRes, studiesRes] = await Promise.all([
    sb
      .from("channel_full")
      .select("slug, name, channel_types")
      .eq("is_active", true)
      .gte("created_at", w.sinceIso)
      .lt("created_at", w.untilIso)
      .order("created_at", { ascending: false }),
    sb
      .from("studies")
      .select("slug, title, authors, year, source_type, category")
      .gte("created_at", w.sinceIso)
      .lt("created_at", w.untilIso)
      .order("created_at", { ascending: false }),
  ]);
  if (channelsRes.error) throw channelsRes.error;
  if (studiesRes.error) throw studiesRes.error;

  // Critical-tagged channels are held back from the public homepage feed;
  // keep the newsletter consistent with that default.
  const channels = ((channelsRes.data ?? []) as NewsletterChannel[]).filter(
    (c) => !(c.channel_types ?? []).includes("Critical"),
  );
  const studies = (studiesRes.data ?? []) as NewsletterStudy[];

  return { channels, studies };
}

export type NewsletterContent = {
  channels: NewsletterChannel[];
  studies: NewsletterStudy[];
};

export function buildMonthlyNewsletter(
  content: NewsletterContent,
  monthLabel: string,
): {
  subject: string;
  render: (unsubscribeUrl: string) => { html: string; text: string };
} | null {
  const { channels, studies } = content;
  if (channels.length === 0 && studies.length === 0) return null;

  const parts: string[] = [];
  if (channels.length) parts.push(`${channels.length} channel${channels.length === 1 ? "" : "s"}`);
  if (studies.length) parts.push(`${studies.length} stud${studies.length === 1 ? "y" : "ies"}`);
  const subject = `[Latter-day Stats] New in ${monthLabel} — ${parts.join(", ")}`;

  function render(unsubscribeUrl: string) {
    const textLines = [
      `New on Latter-day Stats in ${monthLabel}:`,
      "",
      ...(channels.length
        ? [
            "Channels:",
            ...channels.map((c) => `- ${c.name} — ${SITE_URL}/channels/${c.slug}`),
            "",
          ]
        : []),
      ...(studies.length
        ? [
            "Studies:",
            ...studies.map(
              (s) =>
                `- ${s.title}${s.year ? ` (${s.year})` : ""} — ${SITE_URL}/studies/${s.slug}`,
            ),
            "",
          ]
        : []),
      `Browse everything: ${SITE_URL}/channels · ${SITE_URL}/studies`,
      "",
      "---",
      "You're receiving this because you subscribed to monthly updates at Latter-day Stats.",
      `Unsubscribe: ${unsubscribeUrl}`,
      `Manage your subscription: ${SITE_URL}/me/settings`,
    ];

    const channelRows = channels
      .map(
        (c) => `<li style="margin:0 0 10px">
      <a href="${SITE_URL}/channels/${escapeHtml(c.slug)}" style="color:#0f6b5c;font-weight:600;text-decoration:none">${escapeHtml(c.name)}</a>
    </li>`,
      )
      .join("\n");
    const studyRows = studies
      .map(
        (s) => `<li style="margin:0 0 10px">
      <a href="${SITE_URL}/studies/${escapeHtml(s.slug)}" style="color:#0f6b5c;font-weight:600;text-decoration:none">${escapeHtml(s.title)}</a>
      ${s.year ? `<span style="${META_STYLE}"> (${s.year})</span>` : ""}
    </li>`,
      )
      .join("\n");

    const html = `<div style="${WRAPPER_STYLE}">
  <h2 style="font-size:18px;margin:0 0 16px">New on Latter-day Stats in ${escapeHtml(monthLabel)}</h2>
  ${channels.length ? `<p style="${META_STYLE}"><strong>Channels</strong></p><ul style="list-style:none;padding:0;margin:0 0 20px">${channelRows}</ul>` : ""}
  ${studies.length ? `<p style="${META_STYLE}"><strong>Studies</strong></p><ul style="list-style:none;padding:0;margin:0 0 20px">${studyRows}</ul>` : ""}
  <p><a href="${SITE_URL}/channels" style="color:#0f6b5c">Browse channels</a> &middot; <a href="${SITE_URL}/studies" style="color:#0f6b5c">Browse studies</a></p>
  <hr style="border:none;border-top:1px solid #e4e4e4;margin:28px 0" />
  <p style="${META_STYLE}">
    You're receiving this because you subscribed to monthly updates at Latter-day Stats.
    <a href="${unsubscribeUrl}" style="color:#6b6b6b">Unsubscribe</a>
    &middot; <a href="${SITE_URL}/me/settings" style="color:#6b6b6b">Manage subscription</a>
  </p>
</div>`;

    return { html, text: textLines.join("\n") };
  }

  return { subject, render };
}

type SubscriberRow = {
  user_id: string;
  email: string;
  token: string;
  profiles: { email: string | null } | { email: string | null }[] | null;
};

function resolveEmail(row: SubscriberRow): string | null {
  const profile = Array.isArray(row.profiles) ? row.profiles[0] : row.profiles;
  return profile?.email ?? row.email ?? null;
}

export async function runMonthlyNewsletter(
  sb: SupabaseClient,
  w: MonthlyWindow,
): Promise<{
  status: "sent" | "empty" | "already_sent";
  sent: number;
  failed: number;
}> {
  const { error: insertError } = await sb.from("newsletter_sends").insert({
    month_key: w.monthKey,
    window_start: w.sinceIso,
    window_end: w.untilIso,
  });
  if (insertError) {
    if (insertError.code === "23505") {
      logEvent("newsletter.already_sent", { monthKey: w.monthKey });
      return { status: "already_sent", sent: 0, failed: 0 };
    }
    throw insertError;
  }

  const content = await fetchMonthlyContent(sb, w);
  const built = buildMonthlyNewsletter(content, w.monthLabel);

  if (!built) {
    await sb
      .from("newsletter_sends")
      .update({
        status: "empty",
        channel_count: content.channels.length,
        study_count: content.studies.length,
        completed_at: new Date().toISOString(),
      })
      .eq("month_key", w.monthKey);
    logEvent("newsletter.empty", { monthKey: w.monthKey });
    return { status: "empty", sent: 0, failed: 0 };
  }

  const { data: subscriberRows, error: subError } = await sb
    .from("newsletter_subscribers")
    .select("user_id, email, token, profiles(email)")
    .is("unsubscribed_at", null);
  if (subError) throw subError;

  const subscribers = (subscriberRows ?? []) as SubscriberRow[];

  let sent = 0;
  let failed = 0;
  for (let i = 0; i < subscribers.length; i++) {
    const row = subscribers[i];
    const to = resolveEmail(row);
    if (!to) {
      failed++;
      continue;
    }

    const unsubscribeUrl = `${SITE_URL}/unsubscribe?token=${row.token}`;
    const oneClickUrl = `${SITE_URL}/api/newsletter/unsubscribe?token=${row.token}`;
    const { html, text } = built.render(unsubscribeUrl);

    const ok = await sendEmail({
      to,
      subject: built.subject,
      html,
      text,
      headers: {
        "List-Unsubscribe": `<${oneClickUrl}>`,
        "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
      },
    });
    if (ok) sent++;
    else failed++;

    if (i < subscribers.length - 1) {
      await new Promise((resolve) => setTimeout(resolve, SEND_DELAY_MS));
    }
  }

  await sb
    .from("newsletter_sends")
    .update({
      status: "sent",
      channel_count: content.channels.length,
      study_count: content.studies.length,
      recipient_count: sent,
      failed_count: failed,
      completed_at: new Date().toISOString(),
    })
    .eq("month_key", w.monthKey);

  logEvent("newsletter.sent", { monthKey: w.monthKey, sent, failed });
  return { status: "sent", sent, failed };
}

export async function getSubscriberByToken(
  sb: SupabaseClient,
  token: string,
): Promise<{ subscribed: boolean } | null> {
  if (!uuidSchema.safeParse(token).success) return null;
  const { data, error } = await sb
    .from("newsletter_subscribers")
    .select("unsubscribed_at")
    .eq("token", token)
    .maybeSingle();
  if (error) throw error;
  if (!data) return null;
  return { subscribed: data.unsubscribed_at === null };
}

/**
 * Never throws to callers that shouldn't 500 a public unsubscribe link —
 * returns whether a row actually matched and was updated.
 */
export async function unsubscribeByToken(
  sb: SupabaseClient,
  token: string,
): Promise<boolean> {
  if (!uuidSchema.safeParse(token).success) return false;
  try {
    const { data, error } = await sb
      .from("newsletter_subscribers")
      .update({ unsubscribed_at: new Date().toISOString() })
      .eq("token", token)
      .is("unsubscribed_at", null)
      .select("user_id")
      .maybeSingle();
    if (error) throw error;
    return data !== null;
  } catch (err) {
    logEvent(
      "newsletter.unsubscribe_failed",
      { error: err instanceof Error ? err.message : String(err) },
      "error",
    );
    return false;
  }
}
