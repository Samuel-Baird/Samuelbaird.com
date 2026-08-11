"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <html lang="en">
      <body>
        <div
          style={{
            maxWidth: 560,
            margin: "0 auto",
            padding: "8rem 1.25rem",
            textAlign: "center",
            fontFamily: "ui-serif, Georgia, serif",
          }}
        >
          <p
            style={{
              fontSize: 12,
              fontWeight: 500,
              letterSpacing: "0.04em",
              textTransform: "uppercase",
              color: "#7c2d2d",
            }}
          >
            Error
          </p>
          <h1
            style={{
              marginTop: 16,
              fontSize: 36,
              fontWeight: 600,
              letterSpacing: "-0.01em",
            }}
          >
            Something went wrong.
          </h1>
          <p
            style={{
              marginTop: 20,
              fontSize: 16,
              lineHeight: 1.6,
              color: "#63605a",
              fontFamily: "ui-sans-serif, system-ui, sans-serif",
            }}
          >
            The site hit an unexpected error. Try again, or come back in a
            moment.
          </p>
          <button
            type="button"
            onClick={() => reset()}
            style={{
              marginTop: 32,
              height: 44,
              padding: "0 24px",
              borderRadius: 3,
              border: "none",
              background: "#1f4f7a",
              color: "white",
              fontSize: 14,
              fontWeight: 500,
              fontFamily: "ui-sans-serif, system-ui, sans-serif",
              cursor: "pointer",
            }}
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
