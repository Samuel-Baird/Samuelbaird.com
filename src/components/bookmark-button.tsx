"use client";

import { Bookmark, BookmarkCheck } from "lucide-react";
import { usePathname, useSearchParams } from "next/navigation";
import { useState, useTransition } from "react";
import { toggleBookmark } from "@/app/actions/bookmarks";
import { useAuthPrompt } from "@/components/auth-prompt";

type BookmarkButtonProps = {
  targetType: "channel" | "study";
  targetId: string;
  initial: boolean;
  signedIn: boolean;
  size?: "sm" | "md";
  label?: "icon" | "inline";
};

export function BookmarkButton({
  targetType,
  targetId,
  initial,
  signedIn,
  size = "md",
  label = "icon",
}: BookmarkButtonProps) {
  const [bookmarked, setBookmarked] = useState(initial);
  const [pending, startTransition] = useTransition();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { requestLogin } = useAuthPrompt();
  const noun = targetType === "channel" ? "channel" : "study";
  const title = bookmarked ? "Saved" : `Save ${noun}`;
  const currentPath = `${pathname || "/"}${searchParams?.toString() ? `?${searchParams}` : ""}`;
  const Icon = bookmarked ? BookmarkCheck : Bookmark;

  function onClick() {
    if (!signedIn) {
      requestLogin(`Sign in to save ${noun}s to your bookmarks.`);
      return;
    }

    const next = !bookmarked;
    setBookmarked(next);
    startTransition(async () => {
      try {
        const result = await toggleBookmark({
          targetType,
          targetId,
          currentPath,
        });
        setBookmarked(result.bookmarked);
      } catch {
        setBookmarked(!next);
      }
    });
  }

  const iconSize = size === "sm" ? "h-4 w-4" : "h-5 w-5";

  if (label === "inline") {
    return (
      <button
        type="button"
        title={title}
        aria-label={title}
        aria-pressed={bookmarked}
        disabled={pending}
        onClick={onClick}
        className="inline-flex h-10 items-center gap-2 rounded-full border border-[color:var(--border)] bg-white px-4 text-sm font-medium transition-colors hover:bg-[color:var(--muted-soft)] disabled:opacity-60"
      >
        <Icon
          className={`${iconSize} ${bookmarked ? "fill-[color:var(--accent)] text-[color:var(--accent)]" : ""}`}
        />
        {bookmarked ? "Saved" : "Save"}
      </button>
    );
  }

  const box = size === "sm" ? "h-10 w-10 md:h-9 md:w-9" : "h-10 w-10";

  return (
    <button
      type="button"
      title={title}
      aria-label={title}
      aria-pressed={bookmarked}
      disabled={pending}
      onClick={onClick}
      className={`${box} inline-flex shrink-0 items-center justify-center rounded-full border border-[color:var(--border)] bg-white transition-colors hover:bg-[color:var(--muted-soft)] disabled:opacity-60`}
    >
      <Icon
        className={`${iconSize} ${bookmarked ? "fill-[color:var(--accent)] text-[color:var(--accent)]" : ""}`}
      />
    </button>
  );
}
