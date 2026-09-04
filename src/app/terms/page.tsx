import type { Metadata } from "next";
import Link from "next/link";
import { DeseretTitle } from "@/components/deseret-title";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";

export const metadata: Metadata = {
  title: "Terms of Service",
  description: "The terms that govern using Latter-day Stats.",
  alternates: { canonical: "/terms" },
};

const SECTIONS: { id: string; title: string }[] = [
  { id: "acceptance", title: "Acceptance of terms" },
  { id: "the-service", title: "What the site is" },
  { id: "eligibility", title: "Eligibility" },
  { id: "accounts", title: "Accounts" },
  { id: "acceptable-use", title: "Acceptable use" },
  { id: "content", title: "Content and ownership" },
  { id: "donations", title: "Donations and premium" },
  { id: "disclaimers", title: "Disclaimers" },
  { id: "liability", title: "Limitation of liability" },
  { id: "third-party-links", title: "Third-party links" },
  { id: "changes", title: "Changes to these terms" },
  { id: "termination", title: "Termination" },
  { id: "governing-law", title: "Governing law" },
  { id: "contact", title: "Contact" },
];

export default function TermsPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <header className="border-b border-[color:var(--border)] pb-10">
        <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
          Terms of Service
        </p>
        <h1 className="serif mt-4 max-w-4xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          <DeseretTitle text="Terms of Service." />
        </h1>
        <p className="mt-5 max-w-2xl text-sm text-[color:var(--muted)]">
          Last updated August 10, 2026.
        </p>
      </header>

      <div className="mt-10 lg:grid lg:grid-cols-[minmax(0,1fr)_18rem] lg:gap-14">
        <div className="max-w-2xl">
          <Section id="acceptance" title="Acceptance of terms">
            <p>
              By using Latter-day Stats (&ldquo;the site&rdquo;), you agree to
              these terms. If you don&apos;t agree, please don&apos;t use the
              site.
            </p>
          </Section>

          <Section id="the-service" title="What the site is">
            <p>
              Latter-day Stats is an independent, self-funded research and
              statistics site covering the Latter-day Saint community —
              creator statistics and curated academic studies. It has no
              institutional affiliation with The Church
              of Jesus Christ of Latter-day Saints, BYU, or any creator
              tracked on the site. Inclusion in the catalog does not imply
              endorsement of, or by, anyone listed. See the{" "}
              <Link
                href="/methodology"
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                methodology page
              </Link>{" "}
              for how content is selected.
            </p>
          </Section>

          <Section id="eligibility" title="Eligibility">
            <p>
              You must be at least 13 years old to create an account. The
              site is not directed at children, and accounts are gated on a
              13+ confirmation at sign-in. If you believe a child under 13
              has an account, contact us and we&apos;ll remove it.
            </p>
          </Section>

          <Section id="accounts" title="Accounts">
            <p>
              Accounts are created via Google sign-in — the site never
              collects or stores a password. You&apos;re responsible for
              activity under your account. You can export or permanently
              delete your account and its data at any time from{" "}
              <Link
                href="/me/settings"
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                account settings
              </Link>
              .
            </p>
          </Section>

          <Section id="acceptable-use" title="Acceptable use">
            <p>You agree not to:</p>
            <ul className="mt-3 list-disc space-y-1.5 pl-5">
              <li>
                Use the site to harass, defame, or misrepresent any person or
                organization mentioned on it.
              </li>
              <li>
                Attempt to bypass access controls, scrape the site at a scale
                that degrades it for others, or interfere with its normal
                operation.
              </li>
              <li>
                Submit false, abusive, or spam content through the contact
                form or any other input on the site.
              </li>
              <li>
                Use the site in a way that violates applicable law.
              </li>
            </ul>
          </Section>

          <Section id="content" title="Content and ownership">
            <p>
              Original writing, design, and site content belong to Latter-day
              Stats. Channel statistics are derived from the public YouTube
              Data API; channel names, thumbnails, and video content remain
              the property of their respective owners. Academic studies are
              hosted with attribution and a link back to the original
              source — the underlying works belong to their authors and
              publishers, not to this site. See the{" "}
              <Link
                href="/dmca"
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                copyright policy
              </Link>{" "}
              if you believe something here infringes your rights.
            </p>
          </Section>

          <Section id="donations" title="Donations and premium">
            <p>
              Donations are processed entirely off-site through PayPal or
              Venmo — this site never collects or stores payment
              information. Donations are voluntary support for hosting costs,
              not a purchase of goods or a guaranteed service. A one-time
              donation of $5 or more is currently used as the basis for
              granting premium features, which are added by hand after you
              send proof of your donation; see{" "}
              <Link
                href="/premium"
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                the premium page
              </Link>{" "}
              for current details. Donations are not tax-deductible unless
              stated otherwise, and are non-refundable.
            </p>
          </Section>

          <Section id="disclaimers" title="Disclaimers">
            <p>
              The site is provided &ldquo;as is,&rdquo; without warranties of
              any kind. Statistics and study summaries are provided for
              informational purposes and may contain errors, delays, or
              omissions — they are not professional, legal, medical, or
              religious advice. Content on the site, including flagged or
              critical perspectives, reflects the sources cited and does not
              represent an official position of any church, institution, or
              creator.
            </p>
          </Section>

          <Section id="liability" title="Limitation of liability">
            <p>
              To the fullest extent permitted by law, Latter-day Stats and
              its operator are not liable for any indirect, incidental, or
              consequential damages arising from your use of the site, or
              from reliance on any statistic, study summary, or other content
              published on it.
            </p>
          </Section>

          <Section id="third-party-links" title="Third-party links">
            <p>
              The site links to external sources — YouTube channels, academic
              publishers, PayPal, Venmo, and others. Those sites have their
              own terms and privacy practices, which this site doesn&apos;t
              control and isn&apos;t responsible for.
            </p>
          </Section>

          <Section id="changes" title="Changes to these terms">
            <p>
              These terms may be updated from time to time. Material changes
              will be reflected by updating the date at the top of this page.
              Continuing to use the site after a change means you accept the
              updated terms.
            </p>
          </Section>

          <Section id="termination" title="Termination">
            <p>
              You can stop using the site, or delete your account, at any
              time. We may suspend or remove access for accounts that violate
              these terms.
            </p>
          </Section>

          <Section id="governing-law" title="Governing law">
            <p>
              These terms are governed by the laws of the United States,
              without regard to conflict-of-law principles.
            </p>
          </Section>

          <Section id="contact" title="Contact">
            <p>
              Questions about these terms? Use the{" "}
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
              Related
            </h2>
            <ul className="mt-3 space-y-2 border-t border-[color:var(--border)] pt-3 text-sm">
              <li>
                <Link
                  href="/privacy"
                  className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
                >
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link
                  href="/dmca"
                  className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
                >
                  Copyright policy
                </Link>
              </li>
            </ul>
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
