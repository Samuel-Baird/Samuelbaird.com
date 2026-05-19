import type { Metadata } from "next";
import Link from "next/link";
import { submitMessage } from "@/app/actions/messages";
import { SubmitButton } from "@/components/submit-button";
import { getCurrentUser } from "@/lib/auth";
import { CONTACT_EMAIL } from "@/lib/contact";

export const metadata: Metadata = {
  title: "Contact",
  description:
    "Get in touch, report an error, or suggest a channel or study for Latter-day Stats.",
};

type SearchParams = {
  sent?: string;
  error?: string;
  category?: string;
  ref?: string;
};

const CATEGORIES: { value: string; label: string }[] = [
  { value: "general", label: "General inquiry" },
  { value: "correction", label: "Report an error / correction" },
  { value: "channel_suggestion", label: "Suggest a channel" },
  { value: "study_suggestion", label: "Suggest a study" },
  { value: "bug", label: "Bug report" },
];

const ERROR_MESSAGES: Record<string, string> = {
  empty: "Message body is required.",
  too_long: "Message must be under 5,000 characters.",
  bad_email: "That email address doesn't look right.",
  rate_limited:
    "A few messages already came through from this account. Please try again later.",
};

export default async function ContactPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;
  const sent = params.sent === "1";
  const errorMsg = params.error ? ERROR_MESSAGES[params.error] : null;
  const defaultCategory = CATEGORIES.find((c) => c.value === params.category)
    ?.value ?? "general";
  const pageRef = params.ref ?? "";
  const auth = await getCurrentUser();
  const qs = new URLSearchParams();
  if (defaultCategory !== "general") qs.set("category", defaultCategory);
  if (pageRef) qs.set("ref", pageRef);
  const loginNext = `/contact${qs.toString() ? `?${qs.toString()}` : ""}`;

  return (
    <div className="mx-auto max-w-2xl px-5 py-14 sm:px-8 sm:py-20">
      <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
        Contact
      </p>
      <h1 className="serif mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        Get in touch.
      </h1>
      <p className="mt-5 max-w-xl text-base leading-relaxed text-[color:var(--muted)]">
        Spot an error? Have a channel or study to suggest? Want to chat about
        the project? Send a note below, or email{" "}
        <a
          href={`mailto:${CONTACT_EMAIL}`}
          className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
        >
          {CONTACT_EMAIL}
        </a>
        .
      </p>

      {sent && (
        <div className="mt-8 rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-sm text-emerald-900">
          Thanks - your message was received. We&apos;ll follow up if a reply is
          needed.
        </div>
      )}
      {errorMsg && (
        <div className="mt-8 rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-900">
          {errorMsg}
        </div>
      )}

      {!auth ? (
        <section className="mt-10 rounded-2xl border border-[color:var(--border)] bg-white p-6">
          <h2 className="serif text-2xl font-semibold tracking-tight">
            Sign in to send a message.
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-[color:var(--muted)]">
            The contact form is limited to signed-in visitors so the inbox stays
            useful and replyable. Google sign-in is enough; no password needed.
          </p>
          <Link
            href={`/login?next=${encodeURIComponent(loginNext)}`}
            className="mt-6 inline-flex h-11 items-center rounded-full bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90"
          >
            Sign in to contact
          </Link>
        </section>
      ) : (
        <form action={submitMessage} className="mt-10 space-y-5">
          <label className="sr-only" htmlFor="website">
            Website
          </label>
          <input
            id="website"
            name="website"
            type="text"
            tabIndex={-1}
            autoComplete="off"
            className="hidden"
          />
          <Field label="Category" htmlFor="category">
            <select
              id="category"
              name="category"
              defaultValue={defaultCategory}
              className="h-11 w-full rounded-xl border border-[color:var(--border)] bg-white px-3 text-sm"
            >
              {CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>
          </Field>

          <div className="grid gap-5 sm:grid-cols-2">
            <Field label="Your name (optional)" htmlFor="name">
              <input
                id="name"
                name="name"
                type="text"
                maxLength={120}
                className="h-11 w-full rounded-xl border border-[color:var(--border)] bg-white px-3 text-sm"
              />
            </Field>
            <Field label="Email (optional)" htmlFor="email">
              <input
                id="email"
                name="email"
                type="email"
                maxLength={200}
                placeholder="so we can follow up"
                className="h-11 w-full rounded-xl border border-[color:var(--border)] bg-white px-3 text-sm"
              />
            </Field>
          </div>

          {pageRef && (
            <div className="rounded-xl bg-[color:var(--muted-soft)] px-4 py-3 text-xs text-[color:var(--muted)]">
              Referencing:{" "}
              <code className="text-[color:var(--foreground)]">{pageRef}</code>
              <input type="hidden" name="page_ref" value={pageRef} />
            </div>
          )}

          <Field label="Message" htmlFor="body">
            <textarea
              id="body"
              name="body"
              required
              rows={8}
              maxLength={5000}
              className="w-full rounded-xl border border-[color:var(--border)] bg-white px-3 py-2 text-sm"
            />
          </Field>

          <SubmitButton
            pendingLabel="Sending..."
            className="inline-flex h-11 items-center rounded-full bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-60"
          >
            Send message
          </SubmitButton>
        </form>
      )}
    </div>
  );
}

function Field({
  label,
  htmlFor,
  children,
}: {
  label: string;
  htmlFor: string;
  children: React.ReactNode;
}) {
  return (
    <label htmlFor={htmlFor} className="block">
      <span className="text-[11px] font-medium uppercase tracking-wider text-[color:var(--muted)]">
        {label}
      </span>
      <div className="mt-1.5">{children}</div>
    </label>
  );
}
