"use client";

import { Download } from "lucide-react";
import { useState } from "react";

type Props = {
  href: string;
  rowCount: number;
  premium: boolean;
  label?: string;
};

export function ExportCsvButton({
  href,
  rowCount,
  premium,
  label = "Export CSV",
}: Props) {
  const [showModal, setShowModal] = useState(false);

  if (!premium) {
    return (
      <>
        <button
          type="button"
          onClick={() => setShowModal(true)}
          className="inline-flex h-11 items-center gap-2 rounded-full border border-amber-400/60 bg-amber-50 px-4 text-sm font-medium text-amber-700 hover:bg-amber-100"
          title="Premium feature"
        >
          <Download aria-hidden="true" size={16} />
          {label}
          <span className="text-xs text-amber-700/70">({rowCount})</span>
        </button>
        {showModal ? (
          <PremiumModal
            feature="CSV download"
            onClose={() => setShowModal(false)}
          />
        ) : null}
      </>
    );
  }

  return (
    <a
      href={href}
      className={`inline-flex h-11 items-center gap-2 rounded-full border border-[color:var(--border)] bg-white px-4 text-sm font-medium hover:bg-[color:var(--muted-soft)] ${
        rowCount === 0 ? "pointer-events-none opacity-60" : ""
      }`}
      title={`${label} (${rowCount} rows)`}
      aria-disabled={rowCount === 0}
    >
      <Download aria-hidden="true" size={16} />
      {label}
      <span className="text-xs text-[color:var(--muted)]">({rowCount})</span>
    </a>
  );
}

function PremiumModal({
  feature,
  onClose,
}: {
  feature: string;
  onClose: () => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
    >
      <div
        className="w-full max-w-md rounded-2xl border border-amber-300 bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="serif text-xl font-semibold tracking-tight text-amber-700">
          {feature} is a premium feature
        </h2>
        <p className="mt-3 text-sm leading-relaxed text-[color:var(--foreground)]">
          Please contact Sam if you would like to become a premium user.
        </p>
        <div className="mt-5 flex flex-wrap gap-3">
          <a
            href="mailto:b13llama@gmail.com?subject=Premium%20access"
            className="inline-flex h-10 items-center rounded-full bg-amber-500 px-4 text-sm font-medium text-white hover:bg-amber-400"
          >
            Email Sam
          </a>
          <a
            href="/premium"
            className="inline-flex h-10 items-center rounded-full border border-[color:var(--border)] bg-white px-4 text-sm font-medium hover:bg-[color:var(--muted-soft)]"
          >
            Learn more
          </a>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-10 items-center rounded-full px-4 text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
