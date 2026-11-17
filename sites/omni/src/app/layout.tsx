export const metadata = {
  title: "Omni MCP",
  description: "One MCP endpoint for several LDS research servers.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "system-ui", maxWidth: 640, margin: "3rem auto", padding: "0 1rem", lineHeight: 1.5 }}>
        {children}
      </body>
    </html>
  );
}
