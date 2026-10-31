import type { Metadata, Viewport } from "next";
import { Analytics } from "@vercel/analytics/react";
import { Inter, Fraunces, Noto_Sans_Deseret } from "next/font/google";
import Script from "next/script";
import { Suspense } from "react";
import { AgeGateModal } from "@/components/age-gate-modal";
import { AuthPromptProvider } from "@/components/auth-prompt";
import { SiteNav } from "@/components/site-nav";
import { SiteFooter } from "@/components/site-footer";
import { SITE_URL } from "@/lib/site";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  display: "swap",
  axes: ["opsz"],
});

// Decorative only — the title reveal in <DeseretTitle>. Not preloaded: the
// component waits on document.fonts before animating, and a missed reveal is
// cheaper than blocking on a font no page needs to render its content.
const notoDeseret = Noto_Sans_Deseret({
  variable: "--font-deseret",
  weight: "400",
  subsets: ["deseret"],
  display: "swap",
  preload: false,
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Latter-day Stats",
    template: "%s · Latter-day Stats",
  },
  description:
    "Statistics, research, and creator data on the Latter-day Saint community.",
};

export const viewport: Viewport = {
  colorScheme: "dark",
  themeColor: "#0f1115",
};

// Site-wide structured data. Kept minimal and factual — no aggregate
// ratings, no org logo claims, nothing that overstates what the site is.
const JSON_LD = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": `${SITE_URL}/#website`,
      url: SITE_URL,
      name: "Latter-day Stats",
      description:
        "Statistics, research, and creator data on the Latter-day Saint community.",
      publisher: { "@id": `${SITE_URL}/#publisher` },
    },
    {
      "@type": "Person",
      "@id": `${SITE_URL}/#publisher`,
      name: "Samuel Baird",
      url: `${SITE_URL}/about`,
    },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${fraunces.variable} ${notoDeseret.variable} dark h-full`}
      suppressHydrationWarning
    >
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(JSON_LD) }}
        />
        {/* Plain <link>, not the metadata API's alternates.types — a
            page-level `alternates` (added for canonical URLs) fully replaces
            this layout's alternates object rather than merging into it, so
            feed discovery would silently vanish on every page that sets
            its own canonical. */}
        <link
          rel="alternate"
          type="application/rss+xml"
          title="Latter-day Stats"
          href={`${SITE_URL}/feed.xml`}
        />
      </head>
      <body className="min-h-full flex flex-col">
        <Suspense fallback={null}>
          <AuthPromptProvider>
            <SiteNav />
            <main className="flex-1 lg:pl-64">{children}</main>
            <SiteFooter />
            <AgeGateModal />
          </AuthPromptProvider>
        </Suspense>
        <Analytics />
        <Script src="/bg/glyph-field.js" strategy="afterInteractive" charSet="utf-8" />
      </body>
    </html>
  );
}
