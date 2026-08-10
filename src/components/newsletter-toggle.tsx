"use client";

import { useTransition } from "react";
import { setNewsletterSubscription } from "@/app/actions/newsletter";

export function NewsletterToggle({ initial }: { initial: boolean }) {
  const [pending, startTransition] = useTransition();

  function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    const enabled = e.target.checked;
    const fd = new FormData();
    fd.set("enabled", enabled ? "true" : "false");
    startTransition(() => {
      setNewsletterSubscription(fd);
    });
  }

  return (
    <label className="inline-flex items-center gap-3 text-sm">
      <input
        type="checkbox"
        defaultChecked={initial}
        onChange={onChange}
        disabled={pending}
        className="h-4 w-4 accent-[color:var(--accent)]"
      />
      <span>
        Email me monthly updates
        <span className="ml-2 text-xs text-[color:var(--muted)]">
          (new channels and studies added to the site)
        </span>
      </span>
      {pending ? (
        <span className="text-xs text-[color:var(--muted)]">Saving…</span>
      ) : null}
    </label>
  );
}
