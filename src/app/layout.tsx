import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/react";
import { Inter, Fraunces, Noto_Sans_Deseret } from "next/font/google";
import { Suspense } from "react";
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

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${fraunces.variable} ${notoDeseret.variable} h-full`}
      suppressHydrationWarning
    >
      <head>
        <script
          // Set theme before paint to avoid flash. Safe inline boot script.
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem('theme');if(!t){t=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}if(t==='dark'){document.documentElement.classList.add('dark');}}catch(e){}})();`,
          }}
        />
      </head>
      <body className="min-h-full flex flex-col">
        <Suspense fallback={null}>
          <AuthPromptProvider>
            <SiteNav />
            <main className="flex-1">{children}</main>
            <SiteFooter />
          </AuthPromptProvider>
        </Suspense>
        <Analytics />
      </body>
    </html>
  );
}
