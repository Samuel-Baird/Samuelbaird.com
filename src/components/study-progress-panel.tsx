"use client";

import { Check, NotebookPen } from "lucide-react";
import { usePathname, useSearchParams } from "next/navigation";
import { useState, useTransition } from "react";
import {
  saveStudyNote,
  toggleStudyRead,
} from "@/app/actions/study-progress";
import { useAuthPrompt } from "@/components/auth-prompt";

type Props = {
  studyId: string;
  signedIn: boolean;
  initialStatus: "read" | "unread";
  initialNotes: string;
};

export function StudyProgressPanel({
  studyId,
  signedIn,
  initialStatus,
  initialNotes,
}: Props) {
  const [status, setStatus] = useState(initialStatus);
  const [notes, setNotes] = useState(initialNotes);
  const [savedNotes, setSavedNotes] = useState(initialNotes);
  const [open, setOpen] = useState(initialNotes.length > 0);
  const [pending, startTransition] = useTransition();
  const [saved, setSaved] = useState(false);
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { requestLogin } = useAuthPrompt();
  const currentPath = `${pathname || "/"}${searchParams?.toString() ? `?${searchParams}` : ""}`;
  const isRead = status === "read";
  const dirty = notes !== savedNotes;

  function onToggleRead() {
    if (!signedIn) {
      requestLogin("Sign in to track which studies you've read.");
      return;
    }
    const next = isRead ? "unread" : "read";
    setStatus(next);
    startTransition(async () => {
      try {
        const result = await toggleStudyRead({ studyId, currentPath });
        setStatus(result.status);
      } catch {
        setStatus(isRead ? "read" : "unread");
      }
    });
  }

  function onSaveNote() {
    if (!signedIn) {
      requestLogin("Sign in to keep private notes on studies.");
      return;
    }
    startTransition(async () => {
      try {
        const result = await saveStudyNote({
          studyId,
          notes,
          currentPath,
        });
        setSavedNotes(result.notes);
        setNotes(result.notes);
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      } catch {
        // leave unsaved state
      }
    });
  }

  return (
    <section className="mt-10 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5 sm:p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
            Your progress
          </h2>
          <p className="mt-2 text-sm text-[color:var(--muted)]">
            {signedIn
              ? "Private to you — only visible when signed in."
              : "Sign in to track reading and keep private notes."}
          </p>
        </div>
        <button
          type="button"
          onClick={onToggleRead}
          disabled={pending}
          aria-pressed={isRead}
          className={
            "inline-flex h-11 items-center gap-2 rounded-[var(--radius)] px-5 text-sm font-medium transition-colors disabled:opacity-60 " +
            (isRead
              ? "bg-emerald-600 text-white hover:opacity-90"
              : "border border-[color:var(--border)] bg-white text-[color:var(--foreground)] hover:bg-[color:var(--muted-soft)]")
          }
        >
          <Check
            size={16}
            aria-hidden="true"
            className={isRead ? "" : "opacity-40"}
          />
          {isRead ? "Marked as read" : "Mark as read"}
        </button>
      </div>

      <div className="mt-5">
        <button
          type="button"
          onClick={() => {
            if (!signedIn) {
              requestLogin("Sign in to keep private notes on studies.");
              return;
            }
            setOpen((v) => !v);
          }}
          className="inline-flex items-center gap-2 text-sm font-medium text-[color:var(--accent)] hover:underline"
        >
          <NotebookPen size={16} aria-hidden="true" />
          {open ? "Hide notes" : savedNotes ? "Edit your notes" : "Add a private note"}
        </button>
        {open && signedIn && (
          <div className="mt-3">
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="What stood out? Quotes, page numbers, follow-ups…"
              maxLength={5000}
              rows={5}
              className="block w-full rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-3 text-sm leading-relaxed focus:border-[color:var(--accent)] focus:outline-none"
            />
            <div className="mt-2 flex items-center justify-between gap-3">
              <p className="text-xs text-[color:var(--muted)]">
                {notes.length}/5000 characters
              </p>
              <div className="flex items-center gap-3">
                {saved && (
                  <span className="text-xs text-emerald-700">Saved.</span>
                )}
                <button
                  type="button"
                  onClick={onSaveNote}
                  disabled={pending || !dirty}
                  className="inline-flex h-10 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-4 text-sm font-medium text-white transition-colors hover:opacity-90 disabled:opacity-50"
                >
                  Save note
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
