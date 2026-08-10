import { logEvent } from "@/lib/log";

// Resend's REST API — no SDK, keeps the dependency list unchanged.
const RESEND_ENDPOINT = "https://api.resend.com/emails";

// Resend lets you send from onboarding@resend.dev without verifying a domain,
// but only to the address that owns the Resend account. Set EMAIL_FROM once a
// real domain is verified.
const DEFAULT_FROM = "Latter-day Stats <onboarding@resend.dev>";

export type SendEmailInput = {
  to: string;
  subject: string;
  html: string;
  text: string;
  replyTo?: string | null;
  // Extra headers, e.g. List-Unsubscribe / List-Unsubscribe-Post for the
  // monthly newsletter's one-click unsubscribe (RFC 8058).
  headers?: Record<string, string>;
};

/**
 * Sends an email via Resend. Never throws: notification email is a side effect
 * and must not fail the user action that triggered it. Returns false when the
 * send did not happen (missing key, API error) so callers can log it.
 */
export async function sendEmail(input: SendEmailInput): Promise<boolean> {
  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    logEvent("email.skipped", { reason: "no_api_key", subject: input.subject });
    return false;
  }

  try {
    const res = await fetch(RESEND_ENDPOINT, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: process.env.EMAIL_FROM || DEFAULT_FROM,
        to: [input.to],
        subject: input.subject,
        html: input.html,
        text: input.text,
        ...(input.replyTo ? { reply_to: input.replyTo } : {}),
        ...(input.headers ? { headers: input.headers } : {}),
      }),
    });

    if (!res.ok) {
      logEvent(
        "email.failed",
        { status: res.status, body: await res.text(), subject: input.subject },
        "error",
      );
      return false;
    }

    logEvent("email.sent", { to: input.to, subject: input.subject });
    return true;
  } catch (err) {
    logEvent(
      "email.failed",
      { error: err instanceof Error ? err.message : String(err) },
      "error",
    );
    return false;
  }
}

export function escapeHtml(value: string) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
