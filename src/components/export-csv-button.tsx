"use client";

import { Download } from "lucide-react";
import { useAuthPrompt } from "@/components/auth-prompt";

type Props = {
  href: string;
  rowCount: number;
  signedIn: boolean;
  label?: string;
};

export function ExportCsvButton({
  href,
  rowCount,
  signedIn,
  label = "Export CSV",
}: Props) {
  const { requestLogin } = useAuthPrompt();

  function requestExportLogin() {
    requestLogin("Sign in to download channel data as a CSV.");
  }

  if (!signedIn) {
    return (
      <button
        type="button"
        onClick={requestExportLogin}
        className="inline-flex h-11 items-center gap-2 rounded-full border border-[color:var(--border)] bg-white px-4 text-sm font-medium hover:bg-[color:var(--muted-soft)]"
        title="Sign in to export channel data"
      >
        <Download aria-hidden="true" size={16} />
        {label}
        <span className="text-xs text-[color:var(--muted)]">({rowCount})</span>
      </button>
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
