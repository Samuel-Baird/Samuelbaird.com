import { CONTACT_EMAIL } from "@/lib/contact";
import { escapeHtml, sendEmail } from "@/lib/email";
import { SITE_URL } from "@/lib/site";

export const CATEGORY_LABELS: Record<string, string> = {
  general: "General",
  correction: "Correction",
  channel_suggestion: "Channel",
  study_suggestion: "Study",
  bug: "Bug",
};

export function categoryLabel(category: string) {
  return CATEGORY_LABELS[category] ?? category;
}

export type NotifiableMessage = {
  id: string;
  category: string;
  name: string | null;
  email: string | null;
  page_ref: string | null;
  body: string;
  created_at: string;
};

function notifyAddress() {
  return process.env.MESSAGE_NOTIFY_EMAIL || CONTACT_EMAIL;
}

function sender(message: Pick<NotifiableMessage, "name" | "email">) {
  return message.name || message.email || "Signed-in visitor";
}

function adminLink(id: string) {
  return `${SITE_URL}/admin/messages#message-${id}`;
}

const WRAPPER_STYLE =
  "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;" +
  "font-size:15px;line-height:1.6;color:#1c1c1c;max-width:640px";
const META_STYLE = "color:#6b6b6b;font-size:13px;margin:0 0 4px";

/** Emailed the moment a visitor submits the contact form. */
export async function sendNewMessageEmail(message: NotifiableMessage) {
  const label = categoryLabel(message.category);
  const from = sender(message);

  const text = [
    `${label} message from ${from}`,
    message.email ? `Email: ${message.email}` : null,
    message.page_ref ? `Page: ${message.page_ref}` : null,
    "",
    message.body,
    "",
    `Open in admin: ${adminLink(message.id)}`,
  ]
    .filter((line) => line !== null)
    .join("\n");

  const html = `<div style="${WRAPPER_STYLE}">
  <p style="${META_STYLE}"><strong>${escapeHtml(label)}</strong> &middot; ${escapeHtml(from)}</p>
  ${message.email ? `<p style="${META_STYLE}">${escapeHtml(message.email)}</p>` : ""}
  ${message.page_ref ? `<p style="${META_STYLE}">Page: ${escapeHtml(message.page_ref)}</p>` : ""}
  <div style="white-space:pre-line;border-left:3px solid #e4e4e4;padding-left:14px;margin:18px 0">${escapeHtml(message.body)}</div>
  <p><a href="${adminLink(message.id)}" style="color:#0f6b5c">Open in admin &rarr;</a></p>
</div>`;

  return sendEmail({
    to: notifyAddress(),
    subject: `[Latter-day Stats] ${label} from ${from}`,
    text,
    html,
    // Replying to the notification replies to the visitor when they left an address.
    replyTo: message.email,
  });
}

export type DigestInput = {
  since: string;
  recent: NotifiableMessage[];
  openCount: number;
};

/**
 * Emailed once a day. Returns false when there was nothing worth reporting,
 * so an empty inbox stays quiet.
 */
export async function sendDailyDigestEmail({
  since,
  recent,
  openCount,
}: DigestInput) {
  if (recent.length === 0 && openCount === 0) return false;

  const byCategory = new Map<string, number>();
  for (const m of recent) {
    byCategory.set(m.category, (byCategory.get(m.category) ?? 0) + 1);
  }
  const breakdown = [...byCategory.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([category, count]) => `${categoryLabel(category)}: ${count}`);

  const newLabel =
    recent.length === 1 ? "1 new message" : `${recent.length} new messages`;
  const openLabel = openCount === 1 ? "1 open" : `${openCount} open`;

  const textLines = [
    `${newLabel} since ${new Date(since).toLocaleString("en-US")}.`,
    `${openLabel} in total.`,
    breakdown.length ? `\n${breakdown.join(" · ")}` : null,
    "",
    ...recent.map((m) =>
      [
        `— ${categoryLabel(m.category)} from ${sender(m)}`,
        m.page_ref ? `  Page: ${m.page_ref}` : null,
        `  ${preview(m.body, 240)}`,
        `  ${adminLink(m.id)}`,
      ]
        .filter((line) => line !== null)
        .join("\n"),
    ),
    "",
    `All messages: ${SITE_URL}/admin/messages`,
  ].filter((line) => line !== null);

  const rows = recent
    .map(
      (m) => `<li style="margin:0 0 18px">
    <p style="${META_STYLE}"><strong>${escapeHtml(categoryLabel(m.category))}</strong> &middot; ${escapeHtml(sender(m))}</p>
    ${m.page_ref ? `<p style="${META_STYLE}">Page: ${escapeHtml(m.page_ref)}</p>` : ""}
    <p style="margin:6px 0">${escapeHtml(preview(m.body, 240))}</p>
    <a href="${adminLink(m.id)}" style="color:#0f6b5c;font-size:13px">Open &rarr;</a>
  </li>`,
    )
    .join("\n");

  const html = `<div style="${WRAPPER_STYLE}">
  <h2 style="font-size:18px;margin:0 0 6px">${escapeHtml(newLabel)}</h2>
  <p style="${META_STYLE}">${escapeHtml(openLabel)} in total${breakdown.length ? ` &middot; ${escapeHtml(breakdown.join(" · "))}` : ""}</p>
  ${recent.length ? `<ul style="list-style:none;padding:0;margin:20px 0">${rows}</ul>` : "<p style=\"margin:20px 0\">No new messages in the last day.</p>"}
  <p><a href="${SITE_URL}/admin/messages" style="color:#0f6b5c">All messages &rarr;</a></p>
</div>`;

  return sendEmail({
    to: notifyAddress(),
    subject: `[Latter-day Stats] Daily summary — ${newLabel}, ${openLabel}`,
    text: textLines.join("\n"),
    html,
  });
}

function preview(body: string, max: number) {
  const text = body.replace(/\s+/g, " ").trim();
  return text.length > max ? `${text.slice(0, max - 3)}...` : text;
}
