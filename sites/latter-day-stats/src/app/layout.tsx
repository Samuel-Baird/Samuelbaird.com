import type { Metadata, Viewport } from "next";
import { Libre_Baskerville, IM_Fell_English, Noto_Sans_Deseret } from "next/font/google";
import { FAMILY_CSS, FAMILY_FONTS, FAMILY_FOOT, FAMILY_JS } from "@/components/family-chrome.generated";
import Script from "next/script";
import { Suspense } from "react";
import { AgeGateModal } from "@/components/age-gate-modal";
import { AuthPromptProvider } from "@/components/auth-prompt";
import { SiteNav } from "@/components/site-nav";
import { SiteFooter } from "@/components/site-footer";
import { SITE_URL, BASE_PATH } from "@/lib/site";
import { sectionOgImage } from "@/lib/og-images";
import "./globals.css";

// Family style (packages/family): body in Libre Baskerville, display in IM Fell English. The variable
// names are historical (--font-inter / --font-fraunces) and used throughout the Tailwind theme.
const inter = Libre_Baskerville({
  variable: "--font-inter",
  weight: ["400", "700"],
  style: ["normal", "italic"],
  subsets: ["latin"],
  display: "swap",
});

const fraunces = IM_Fell_English({
  variable: "--font-fraunces",
  weight: "400",
  style: ["normal", "italic"],
  subsets: ["latin"],
  display: "swap",
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
  // public/icon.png, written by scripts/build-og-images.tsx. Absolute URL
  // because a root-relative one would skip the basePath.
  icons: { icon: [{ url: `${SITE_URL}/icon.png`, type: "image/png", sizes: "32x32" }] },
  // Default social card for every page that doesn't set its own.
  ...sectionOgImage("home", "Latter-day Stats"),
};

export const viewport: Viewport = {
  colorScheme: "dark",
  themeColor: "#16161a",
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
      url: "https://samuelbaird.com/",
      sameAs: [
        "https://samuelbaird.com/",
        "https://www.youtube.com/@ithinkthereforeisam",
        "https://ithinkisam.substack.com/",
        "https://github.com/Samuel-Baird",
      ],
      mainEntityOfPage: `${SITE_URL}/about`,
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
        <link rel="stylesheet" href={FAMILY_FONTS} />
        <link rel="stylesheet" href={FAMILY_CSS} />
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
            <main className="flex-1">{children}</main>
            <SiteFooter />
            <div dangerouslySetInnerHTML={{ __html: FAMILY_FOOT }} />
            <AgeGateModal />
          </AuthPromptProvider>
        </Suspense>
        <Script src={`${BASE_PATH}/bg/glyph-field.js`} strategy="afterInteractive" charSet="utf-8" />
        <Script src={FAMILY_JS} strategy="afterInteractive" />
      </body>
    </html>
  );
}
