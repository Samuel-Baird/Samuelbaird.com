import type { ReactNode } from "react";

export const metadata = {
  title: "Peepstone",
  description: "An MCP server for searching and reading the Joseph Smith Papers.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "system-ui, sans-serif", maxWidth: 680, margin: "48px auto", padding: "0 16px", lineHeight: 1.6 }}>
        {children}
      </body>
    </html>
  );
}
