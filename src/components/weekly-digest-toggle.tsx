"use client";

import { useTransition } from "react";
import { setWeeklyNotification } from "@/app/actions/notifications";

export function WeeklyDigestToggle({ initial }: { initial: boolean }) {
  const [pending, startTransition] = useTransition();

  function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    const enabled = e.target.checked;
    const fd = new FormData();
    fd.set("enabled", enabled ? "true" : "false");
    startTransition(() => {
      setWeeklyNotification(fd);
    });
  }

  return (
    <label className="inline-flex items-center gap-3 text-sm">
      <input
        type="checkbox"
        defaultChecked={initial}
        onChange={onChange}
        disabled={pending}
        className="h-4 w-4 accent-amber-500"
      />
      <span>
        Email me the weekly digest
        <span className="ml-2 text-xs text-[color:var(--muted)]">
          (new studies, new channels, trend research)
        </span>
      </span>
      {pending ? (
        <span className="text-xs text-[color:var(--muted)]">Saving…</span>
      ) : null}
    </label>
  );
}
