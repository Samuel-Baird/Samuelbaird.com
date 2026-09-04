import type { Metadata } from "next";
import Link from "next/link";
import { DeseretTitle } from "@/components/deseret-title";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";

export const metadata: Metadata = {
  title: "Copyright Policy",
  description: "How to report a copyright concern about content on Latter-day Stats.",
  alternates: { canonical: "/dmca" },
};

const SECTIONS: { id: string; title: string }[] = [
  { id: "overview", title: "Overview" },
  { id: "reporting", title: "Reporting infringement" },
  { id: "counter-notice", title: "Counter-notification" },
  { id: "repeat-infringers", title: "Repeat infringers" },
  { id: "contact", title: "Contact" },
];

export default function DmcaPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <header className="border-b border-[color:var(--border)] pb-10">
        <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
          Copyright Policy
        </p>
        <h1 className="serif mt-4 max-w-4xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          <DeseretTitle text="Copyright policy." />
        </h1>
        <p className="mt-5 max-w-2xl text-sm text-[color:var(--muted)]">
          Last updated August 10, 2026.
        </p>
      </header>

      <div className="mt-10 lg:grid lg:grid-cols-[minmax(0,1fr)_18rem] lg:gap-14">
        <div className="max-w-2xl">
          <Section id="overview" title="Overview">
            <p>
              Latter-day Stats displays public YouTube channel statistics,
              thumbnails, and names retrieved through the YouTube Data API;
              hosts academic study PDFs and preview images with attribution
              and a link back to the original source; and publishes its own
              original writing (methodology and site copy). If you believe
              something on the site infringes your
              copyright, this page explains how to report it.
            </p>
          </Section>

          <Section id="reporting" title="Reporting infringement">
            <p>
              Send a notice to the email below. To help us act on it quickly,
              please include:
            </p>
            <ul className="mt-3 list-disc space-y-1.5 pl-5">
              <li>
                Identification of the copyrighted work you believe is
                infringed.
              </li>
              <li>
                The exact URL on Latter-day Stats where the material appears.
              </li>
              <li>
                Your contact information (name, email, and mailing address).
              </li>
              <li>
                A statement that you have a good-faith belief the use is not
                authorized by the copyright owner, its agent, or the law.
              </li>
              <li>
                A statement, under penalty of perjury, that the information
                in the notice is accurate and that you are the copyright
                owner or authorized to act on their behalf.
              </li>
              <li>Your physical or electronic signature.</li>
            </ul>
            <p className="mt-3">
              We review each report and remove or disable access to material
              we determine is infringing.
            </p>
          </Section>

          <Section id="counter-notice" title="Counter-notification">
            <p>
              If material of yours was removed and you believe that was a
              mistake or misidentification, you can send a counter-notice
              including: identification of the removed material and where it
              appeared before removal, a statement under penalty of perjury
              that you have a good-faith belief it was removed in error, your
              contact information, and your consent to the jurisdiction of
              the federal court in your district (or, if outside the US, an
              appropriate judicial district). We&apos;ll review counter-
              notices and may restore material based on them.
            </p>
          </Section>

          <Section id="repeat-infringers" title="Repeat infringers">
            <p>
              We remove content in response to properly submitted, valid
              notices. Accounts responsible for repeated, unresolved
              infringement may be terminated.
            </p>
          </Section>

          <Section id="contact" title="Contact">
            <p>
              Send copyright reports and counter-notices to{" "}
              <a
                href={mailto("Copyright notice")}
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                {CONTACT_EMAIL}
              </a>
              . For anything else, use the{" "}
              <Link
                href="/contact"
                className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
              >
                contact form
              </Link>
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
