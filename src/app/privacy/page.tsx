import type { Metadata } from "next";
import Link from "next/link";
import { DeseretTitle } from "@/components/deseret-title";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "What Latter-day Stats collects, why, and how to control it.",
  alternates: { canonical: "/privacy" },
};

const SECTIONS: { id: string; title: string }[] = [
  { id: "what-we-collect", title: "What we collect" },
  { id: "how-we-use-it", title: "How we use it" },
  { id: "cookies-analytics", title: "Cookies and analytics" },
  { id: "third-parties", title: "Third parties" },
  { id: "retention", title: "Data retention" },
  { id: "your-rights", title: "Your rights" },
  { id: "childrens-privacy", title: "Children's privacy" },
  { id: "international", title: "International users" },
  { id: "changes", title: "Changes to this policy" },
  { id: "contact", title: "Contact" },
];

export default function PrivacyPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <header className="border-b border-[color:var(--border)] pb-10">
        <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
          Privacy Policy
        </p>
        <h1 className="serif mt-4 max-w-4xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          <DeseretTitle text="Privacy Policy." />
        </h1>
        <p className="mt-5 max-w-2xl text-sm text-[color:var(--muted)]">
          Last updated August 10, 2026.
        </p>
      </header>

      <div className="mt-10 lg:grid lg:grid-cols-[minmax(0,1fr)_18rem] lg:gap-14">
        <div className="max-w-2xl">
          <Section id="what-we-collect" title="What we collect">
            <p>Most of the site works with no account and no data collection — browsing channels, studies, and timelines doesn&apos;t require signing in.</p>
            <p className="mt-3">If you create an account (via Google sign-in), we collect:</p>
            <ul className="mt-3 list-disc space-y-1.5 pl-5">
              <li>Your name, email address, and profile photo, from Google.</li>
              <li>
                A timestamp confirming you checked the &ldquo;I am at least
                13&rdquo; box at sign-up.
              </li>
              <li>
                Bookmarks, upvotes, and study reading progress you create on
                the site.
              </li>
              <li>Your newsletter subscription status, if you opt in.</li>
            </ul>
            <p className="mt-3">
              If you use the contact form, we collect your name, email, and
              the message you send, along with which page (if any) you were
              referencing.
            </p>
            <p className="mt-3">
              If you complete a quiz (such as &ldquo;How evangelical are
              you?&rdquo;), we store your answers and result, along with any
              optional demographics you chose to provide (age, gender,
              religious tradition), for aggregate research. For signed-out
              takers this is stored anonymously — under a random identifier
              held only in your browser, with no IP address or browser
              fingerprint. Every demographic question is skippable, and
              deleting your account deletes your quiz runs with it.
            </p>
          </Section>

          <Section id="how-we-use-it" title="How we use it">
            <p>
              To run your account (sign-in, bookmarks, reading progress), send
              the monthly newsletter if you&apos;ve opted in, respond to
              messages sent through the contact form, and grant premium
              access after a donation. We don&apos;t sell your data or use it
              for advertising — the site doesn&apos;t run ads.
            </p>
          </Section>

          <Section id="cookies-analytics" title="Cookies and analytics">
            <p>
              Signing in sets an essential session cookie (via Supabase Auth)
              so you stay signed in between visits — this isn&apos;t used for
              tracking. A theme preference (light/dark) is stored in your
              browser&apos;s local storage, not a cookie, and never leaves
              your device.
            </p>
            <p className="mt-3">
              The site uses Vercel Web Analytics for aggregate page-view
              counts. It doesn&apos;t use cookies or collect personally
              identifiable information — see{" "}
              <a
                href="https://vercel.com/docs/analytics/privacy-policy"
                target="_blank"
                rel="noopener noreferrer"
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                Vercel&apos;s analytics privacy documentation
              </a>{" "}
              for specifics.
            </p>
          </Section>

          <Section id="third-parties" title="Third parties">
            <p>The site relies on a small set of service providers:</p>
            <ul className="mt-3 list-disc space-y-1.5 pl-5">
              <li>
                <strong>Google</strong> — sign-in (OAuth). We never see or
                store your Google password.
              </li>
              <li>
                <strong>Supabase</strong> — database, authentication, and file
                storage for the site.
              </li>
              <li>
                <strong>Vercel</strong> — hosting and aggregate, cookieless
                analytics.
              </li>
              <li>
                <strong>Resend</strong> — delivers contact-form
                notifications and the opt-in newsletter.
              </li>
              <li>
                <strong>YouTube Data API</strong> — public channel statistics
                are pulled from YouTube; nothing about you is sent to
                YouTube.
              </li>
              <li>
                <strong>PayPal / Venmo</strong> — donations are handled
                entirely on their sites. This site never receives your
                payment details.
              </li>
            </ul>
            <p className="mt-3">
              We don&apos;t sell or rent your data to anyone.
            </p>
          </Section>

          <Section id="retention" title="Data retention">
            <p>
              Account data is kept for as long as your account exists.
              Contact-form messages are kept indefinitely as a record, with
              your account link removed if you delete your account (the
              message text and the name/email you provided at the time
              remain, since that&apos;s the record of what was reported).
            </p>
          </Section>

          <Section id="your-rights" title="Your rights">
            <p>
              You can view, export, or permanently delete your account and
              its data at any time from{" "}
              <Link
                href="/me/settings"
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                account settings
              </Link>
              . Deleting your account removes your profile, bookmarks,
              upvotes, reading progress, and newsletter subscription
              immediately and permanently. If you&apos;d rather we handle a
              request manually — including requests covered by GDPR, CCPA, or
              a similar law — email us and we&apos;ll take care of it.
            </p>
          </Section>

          <Section id="childrens-privacy" title="Children's privacy">
            <p>
              Latter-day Stats is not directed at children, and we don&apos;t
              knowingly collect personal information from anyone under 13.
              Accounts require confirming you&apos;re 13 or older before
              sign-in completes. If you believe a child under 13 has provided
              us with personal information, contact us and we&apos;ll delete
              it.
            </p>
          </Section>

          <Section id="international" title="International users">
            <p>
              The site is hosted in the United States. If you&apos;re
              visiting from outside the US, your information will be
              processed in the US, which may have different data protection
              laws than your home country.
            </p>
          </Section>

          <Section id="changes" title="Changes to this policy">
            <p>
              This policy may be updated from time to time. Material changes
              will be reflected by updating the date at the top of this page.
            </p>
          </Section>

          <Section id="contact" title="Contact">
            <p>
              Questions about this policy, or a data request you&apos;d like
              handled manually? Use the{" "}
              <Link
                href="/contact"
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                contact form
              </Link>{" "}
              or email{" "}
              <a
                href={mailto("Latter-day Stats")}
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                {CONTACT_EMAIL}
              </a>
              .
            </p>
          </Section>
        </div>

        <aside className="mt-14 lg:mt-0 lg:border-l lg:border-[color:var(--border)] lg:pl-8">
          <div className="lg:sticky lg:top-24">
            <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              On this page
            </h2>
            <ul className="mt-3 space-y-3 border-t border-[color:var(--border)] pt-3 text-sm leading-relaxed">
              {SECTIONS.map((section) => (
                <li key={section.id}>
                  <a
                    href={`#${section.id}`}
                    className="text-[color:var(--muted)] hover:text-[color:var(--accent)]"
                  >
                    {section.title}
                  </a>
                </li>
              ))}
            </ul>

            <h2 className="small-caps mt-8 text-xs font-medium text-[color:var(--muted)]">
              Manage your data
            </h2>
            <p className="mt-3 border-t border-[color:var(--border)] pt-3 text-sm leading-relaxed text-[color:var(--muted)]">
              Export or delete your account any time from{" "}
              <Link
                href="/me/settings"
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                account settings
              </Link>
              .
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}

function Section({
  id,
  title,
  children,
}: {
  id: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className="mt-12 scroll-mt-24 first:mt-0">
      <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
        {title}
      </h2>
      <div className="mt-4 text-base leading-relaxed text-[color:var(--foreground)]">
        {children}
      </div>
    </section>
  );
}
