"use client";

import { LayoutDashboard } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { fmtNumber, fmtRelative } from "@/lib/format";

export type HubAdminStats = {
  totalCriticalChannels: number;
  channelsScanned: number;
  channelsNeverScanned: number;
  lastScrapeRun: string | null;
  totalVideos: number;
  incompleteVideos: number;
  lastAnalysisRun: string | null;
  hiddenVideos: number;
  relevanceUndetermined: number;
};

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4 py-1.5">
      <dt className="text-sm text-[color:var(--muted)]">{label}</dt>
      <dd className="tabular-nums text-sm font-medium text-[color:var(--foreground)]">
        {value}
      </dd>
    </div>
  );
}

export function HubAdminStatsMenu({ stats }: { stats: HubAdminStats }) {
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;

    function onMouseDown(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }

    document.addEventListener("mousedown", onMouseDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onMouseDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  const lastScrape = fmtRelative(stats.lastScrapeRun);
  const lastAnalysis = fmtRelative(stats.lastAnalysisRun);

  return (
    <div ref={menuRef} className="relative">
      <button
        type="button"
        aria-haspopup="dialog"
        aria-expanded={open}
        aria-label="Hub admin stats"
        title="Hub admin stats"
        onClick={() => setOpen((value) => !value)}
        className="inline-flex h-10 w-10 items-center justify-center rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--background)] text-[color:var(--muted)] transition-colors hover:bg-[color:var(--muted-soft)] hover:text-[color:var(--foreground)]"
      >
        <LayoutDashboard className="h-4 w-4" />
      </button>

      {open ? (
        <div
          role="dialog"
          aria-label="Hub admin stats"
          className="absolute right-0 top-12 z-50 w-80 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--background)] p-4"
        >
          <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
            Ingest status
          </p>

          <dl className="mt-2 divide-y divide-[color:var(--border)]">
            <Row
              label="Critical channels tracked"
              value={fmtNumber(stats.totalCriticalChannels)}
            />
            <Row
              label="Channels never scanned"
              value={`${fmtNumber(stats.channelsNeverScanned)} of ${fmtNumber(stats.totalCriticalChannels)}`}
            />
            <Row label="Last scrape run" value={lastScrape.text} />
            <Row label="Total videos ingested" value={fmtNumber(stats.totalVideos)} />
            <Row
              label="Awaiting analysis"
              value={fmtNumber(stats.incompleteVideos)}
            />
            <Row label="Last analysis run" value={lastAnalysis.text} />
            <Row
              label="Hidden (not LDS-relevant)"
              value={fmtNumber(stats.hiddenVideos)}
            />
            <Row
              label="Relevance undetermined"
              value={fmtNumber(stats.relevanceUndetermined)}
            />
          </dl>
        </div>
      ) : null}
    </div>
  );
}
