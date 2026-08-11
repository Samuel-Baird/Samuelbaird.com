import type { Metadata } from "next";
import Link from "next/link";
import { submitMessage } from "@/app/actions/messages";
import { SubmitButton } from "@/components/submit-button";
import { DeseretTitle } from "@/components/deseret-title";
import { getCurrentUser } from "@/lib/auth";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";

export const metadata: Metadata = {
  title: "Contact",
  description:
    "Get in touch, report an error, or suggest a channel or study for Latter-day Stats.",
  alternates: { canonical: "/contact" },
};

type SearchParams = {
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
  rate_limited:
    "A few messages already came through from this account. Please try again later.",
};

export default async function ContactPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;
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
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <header className="border-b border-[color:var(--border)] pb-10">
        <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
          Contact
        </p>
        <h1 className="serif mt-4 max-w-4xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          <DeseretTitle text="Get in touch." />
        </h1>
        <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
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
      </header>

      <div className="mt-10 lg:grid lg:grid-cols-[minmax(0,1fr)_20rem] lg:gap-14">
        <div className="max-w-xl">
          {errorMsg && (
            <div className="rounded-[var(--radius)] border border-[color:var(--oxblood)]/30 bg-[color:var(--oxblood-soft)] px-5 py-4 text-sm text-[color:var(--oxblood)]">
              {errorMsg}
            </div>
          )}

          {!auth ? (
            <section className="mt-8 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6 first:mt-0">
              <h2 className="serif text-2xl font-semibold tracking-tight">
                Sign in to send a message.
              </h2>
              <p className="mt-3 text-sm leading-relaxed text-[color:var(--muted)]">
                The contact form is limited to signed-in visitors so the inbox
                stays useful and replyable. Google sign-in is enough; no
                password needed.
              </p>
              <Link
                href={`/login?next=${encodeURIComponent(loginNext)}`}
                className="mt-6 inline-flex h-11 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90"
              >
                Sign in to contact
              </Link>
            </section>
          ) : (
            <form action={submitMessage} className="mt-8 space-y-5 first:mt-0">
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
                  className="h-11 w-full rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 text-sm"
                >
                  {CATEGORIES.map((c) => (
                    <option key={c.value} value={c.value}>
                      {c.label}
                    </option>
                  ))}
                </select>
              </Field>

              <div className="rounded-[var(--radius)] bg-[color:var(--muted-soft)] px-4 py-3 text-xs text-[color:var(--muted)]">
                Sending as{" "}
                <span className="font-medium text-[color:var(--foreground)]">
                  {auth.profile?.full_name ?? "Signed-in user"}
                </span>{" "}
                ({auth.profile?.email ?? auth.user.email})
              </div>

              {pageRef && (
                <div className="rounded-[var(--radius)] bg-[color:var(--muted-soft)] px-4 py-3 text-xs text-[color:var(--muted)]">
                  Referencing:{" "}
                  <code className="text-[color:var(--foreground)]">
                    {pageRef}
                  </code>
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
                  className="w-full rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 py-2 text-sm"
                />
              </Field>

              <SubmitButton
                pendingLabel="Sending..."
                className="inline-flex h-11 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-60"
              >
                Send message
              </SubmitButton>
            </form>
          )}
        </div>

        <aside className="mt-14 lg:mt-0 lg:border-l lg:border-[color:var(--border)] lg:pl-10">
          <div className="space-y-8">
            <section>
              <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
                What to expect
              </h2>
              <ul className="mt-3 space-y-3 border-t border-[color:var(--border)] pt-3 text-sm leading-relaxed text-[color:var(--muted)]">
                <li>
                  Messages are read by the site editor, not a support team.
                  We usually respond within 48 hours.
                </li>
                <li>
                  Corrections are the fastest to act on — include a link to the
                  page and what looks wrong.
                </li>
                <li>
                  Channel and study suggestions are reviewed against the
                  published selection criteria before anything is added.
                </li>
              </ul>
            </section>

            <section>
              <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
                Email directly
              </h2>
              <p className="mt-3 border-t border-[color:var(--border)] pt-3 text-sm leading-relaxed text-[color:var(--muted)]">
                Prefer your own mail client? Write to{" "}
                <a
                  href={mailto("Latter-day Stats")}
                  className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
                >
                  {CONTACT_EMAIL}
                </a>
                .
              </p>
            </section>

            <section className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5 text-sm">
              <p className="font-medium text-[color:var(--foreground)]">
                Before you write
              </p>
              <p className="mt-2 text-[color:var(--muted)]">
                How channels are chosen, how stats are collected, and who runs
                the site are all documented already.
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                <Link
                  href="/methodology"
                  className="small-caps inline-flex h-9 items-center rounded-[var(--radius)] border border-[color:var(--border)] px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
                >
                  Methodology →
                </Link>
                <Link
                  href="/about"
                  className="small-caps inline-flex h-9 items-center rounded-[var(--radius)] border border-[color:var(--border)] px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
                >
                  About →
                </Link>
              </div>
            </section>
          </div>
        </aside>
      </div>
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
      <span className="small-caps text-[11px] font-medium text-[color:var(--muted)]">
        {label}
      </span>
      <div className="mt-1.5">{children}</div>
    </label>
  );
}
