"use client";

import { ArrowBigUp } from "lucide-react";
import { usePathname, useSearchParams } from "next/navigation";
import { useState, useTransition } from "react";
import { toggleUpvote } from "@/app/actions/upvotes";
import { useAuthPrompt } from "@/components/auth-prompt";

type UpvoteButtonProps = {
  targetType: "channel" | "study";
  targetId: string;
  initialCount: number;
  initialUpvoted: boolean;
  signedIn: boolean;
  size?: "sm" | "md";
};

export function UpvoteButton({
  targetType,
  targetId,
  initialCount,
  initialUpvoted,
  signedIn,
  size = "md",
}: UpvoteButtonProps) {
  const [upvoted, setUpvoted] = useState(initialUpvoted);
  const [count, setCount] = useState(initialCount);
  const [pending, startTransition] = useTransition();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { requestLogin } = useAuthPrompt();
  const noun = targetType === "channel" ? "channel" : "study";
  const currentPath = `${pathname || "/"}${searchParams?.toString() ? `?${searchParams}` : ""}`;
  const title = upvoted ? "Remove upvote" : `Upvote ${noun}`;

  function onClick() {
    if (!signedIn) {
      requestLogin("Sign in to upvote channels and studies.");
      return;
    }
    const next = !upvoted;
    setUpvoted(next);
    setCount((c) => c + (next ? 1 : -1));
    startTransition(async () => {
      try {
        const result = await toggleUpvote({
          targetType,
          targetId,
          currentPath,
        });
        setUpvoted(result.upvoted);
      } catch {
        setUpvoted(!next);
        setCount((c) => c + (next ? -1 : 1));
      }
    });
  }

  const sizing =
    size === "sm"
      ? "h-10 min-w-10 px-2.5 text-xs"
      : "h-10 min-w-12 px-3 text-sm";
  const iconSize = size === "sm" ? "h-4 w-4" : "h-5 w-5";

  return (
    <button
      type="button"
      title={title}
      aria-label={title}
      aria-pressed={upvoted}
      disabled={pending}
      onClick={onClick}
      className={`${sizing} inline-flex shrink-0 items-center justify-center gap-1 rounded-full border border-[color:var(--border)] bg-white font-medium tabular-nums transition-colors hover:bg-[color:var(--muted-soft)] disabled:opacity-60 ${
        upvoted ? "border-[color:var(--accent)] text-[color:var(--accent)]" : ""
      }`}
    >
      <ArrowBigUp
        className={`${iconSize} ${upvoted ? "fill-[color:var(--accent)] text-[color:var(--accent)]" : ""}`}
      />
      <span>{count}</span>
    </button>
  );
}
