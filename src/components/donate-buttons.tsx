"use client";

import { X } from "lucide-react";
import { useEffect, useState } from "react";
import { CONTACT_EMAIL, mailto } from "@/lib/contact";
import { toDeseretText } from "@/lib/deseret";

const THANK_YOU = "Thank You!";
const THANK_YOU_DESERET = toDeseretText(THANK_YOU);
const CYCLE_MS = 2400;

export function DonateButtons({
  paypalUrl,
  venmoUrl,
}: {
  paypalUrl: string;
  venmoUrl: string;
}) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <div className="flex flex-wrap gap-3">
        <a
          href={paypalUrl}
          target="_blank"
          rel="noopener noreferrer"
          onClick={() => setOpen(true)}
          className="mt-2 inline-flex h-11 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90"
        >
          Donate via PayPal →
        </a>
        <a
          href={venmoUrl}
          target="_blank"
          rel="noopener noreferrer"
          onClick={() => setOpen(true)}
          className="mt-2 inline-flex h-11 items-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-6 text-sm font-medium text-[color:var(--foreground)] transition-colors hover:bg-[color:var(--muted-soft)]"
        >
          Donate via Venmo →
        </a>
      </div>
      {open && <ThankYouModal onClose={() => setOpen(false)} />}
    </>
  );
}

function ThankYouModal({ onClose }: { onClose: () => void }) {
  const [showDeseret, setShowDeseret] = useState(false);

  useEffect(() => {
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [onClose]);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const id = setInterval(() => {
      setShowDeseret((v) => !v);
    }, CYCLE_MS);
    return () => clearInterval(id);
  }, []);

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="donate-thanks-title"
    >
      <button
        type="button"
        aria-label="Close"
        onClick={onClose}
        className="absolute inset-0 bg-black/40"
      />
      <section
        style={{ animation: "modal-in 220ms ease-out both" }}
        className="relative w-full max-w-md rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--background)] p-7 text-center shadow-lg"
      >
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="absolute right-3 top-3 inline-flex h-9 w-9 items-center justify-center rounded-full text-[color:var(--muted)] hover:bg-[color:var(--muted-soft)] hover:text-[color:var(--foreground)]"
        >
          <X size={18} aria-hidden="true" />
        </button>

        <div className="grid h-16 place-items-center">
          <h2
            id="donate-thanks-title"
            aria-label={THANK_YOU}
            className={`serif [grid-area:1/1] text-3xl font-semibold tracking-tight text-[color:var(--honey)] transition-opacity duration-700 ${
              showDeseret ? "opacity-0" : "opacity-100"
            }`}
          >
            {THANK_YOU}
          </h2>
          <p
            aria-hidden="true"
            style={{ fontFamily: "var(--font-deseret), sans-serif" }}
            className={`[grid-area:1/1] text-3xl text-[color:var(--honey)] transition-opacity duration-700 ${
              showDeseret ? "opacity-100" : "opacity-0"
            }`}
          >
            {THANK_YOU_DESERET}
          </p>
        </div>

        <p className="mt-4 text-sm leading-relaxed text-[color:var(--muted)]">
          Your contribution helps make this website possible.
        </p>

        <div className="mt-5 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--muted-soft)] p-4 text-left text-sm leading-relaxed text-[color:var(--foreground)]">
          <p>
            To receive premium, forward your donation receipt to{" "}
            <a
              href={mailto("Premium access — donation receipt")}
              className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
            >
              {CONTACT_EMAIL}
            </a>
            , along with the email address on the account you&apos;d like it
            applied to.
          </p>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="mt-6 inline-flex h-10 items-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-5 text-sm font-medium hover:bg-[color:var(--muted-soft)]"
        >
          Close
        </button>
      </section>
    </div>
  );
}
