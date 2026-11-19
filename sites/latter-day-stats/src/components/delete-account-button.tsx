"use client";

import { useState } from "react";
import { deleteMyAccount } from "@/app/actions/account";
import { SubmitButton } from "@/components/submit-button";

export function DeleteAccountButton() {
  const [confirming, setConfirming] = useState(false);

  if (!confirming) {
    return (
      <button
        type="button"
        onClick={() => setConfirming(true)}
        className="inline-flex h-10 items-center rounded-[var(--radius)] border border-[color:var(--oxblood)]/40 bg-[color:var(--oxblood-soft)] px-4 text-sm font-medium text-[color:var(--oxblood)] hover:bg-[color:var(--oxblood)]/15"
      >
        Delete my account
      </button>
    );
  }

  return (
    <div className="rounded-[var(--radius)] border border-[color:var(--oxblood)]/40 bg-[color:var(--oxblood-soft)] p-4">
      <p className="text-sm text-[color:var(--foreground)]">
        This permanently deletes your account, bookmarks, upvotes and reading
        progress. It cannot be undone.
      </p>
      <div className="mt-4 flex flex-wrap gap-3">
        <form action={deleteMyAccount}>
          <SubmitButton
            pendingLabel="Deleting…"
            className="inline-flex h-10 items-center rounded-[var(--radius)] bg-[color:var(--oxblood)] px-4 text-sm font-medium text-white hover:opacity-90 disabled:opacity-60"
          >
            Yes, permanently delete my account
          </SubmitButton>
        </form>
        <button
          type="button"
          onClick={() => setConfirming(false)}
          className="inline-flex h-10 items-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 text-sm font-medium hover:bg-[color:var(--muted-soft)]"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
