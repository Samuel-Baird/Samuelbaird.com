"use client";

import Link from "next/link";
import { useState, useTransition } from "react";
import { Tag } from "@/components/tag";
import {
  attachHubClaimToClaim,
  detachHubClaim,
  promoteToNewClaim,
  setClaimStatus,
} from "@/app/actions/claims";
import type { HubClaim } from "@/lib/types";

export type PromotableClaim = {
  id: string;
  slug: string;
  title: string;
  status: "draft" | "published";
};

// A hub claim, plus whichever canonical claim it has already been promoted to.
export type HubClaimWithLink = HubClaim & {
  claim_id: string | null;
  linked: PromotableClaim | null;
};

export function PromoteClaimPanel({
  claims,
  library,
  currentPath,
}: {
  claims: HubClaimWithLink[];
  library: PromotableClaim[];
  currentPath: string;
}) {
  if (claims.length === 0) {
    return (
      <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5">
        <h2 className="serif text-lg font-semibold tracking-tight">
          Claim library
        </h2>
        <p className="mt-2 text-sm text-[color:var(--muted)]">
          Once this video has analyzed claims, you can promote them into the
          public claim library from here.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5">
      <h2 className="serif text-lg font-semibold tracking-tight">
        Claim library
      </h2>
      <p className="mt-2 text-sm leading-relaxed text-[color:var(--muted)]">
        Promote a claim from this video into the public library, or attach it to
        a claim that is already there. Nothing goes public until you publish it.
      </p>

      <ul className="mt-4 space-y-4">
        {claims.map((claim) => (
          <li
            key={claim.id}
            className="border-t border-[color:var(--border)] pt-4 first:border-t-0 first:pt-0"
          >
            <PromoteRow
              claim={claim}
              library={library}
              currentPath={currentPath}
            />
          </li>
        ))}
      </ul>
    </div>
  );
}

function PromoteRow({
  claim,
  library,
  currentPath,
}: {
  claim: HubClaimWithLink;
  library: PromotableClaim[];
  currentPath: string;
}) {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<"idle" | "new" | "attach">("idle");
  const [title, setTitle] = useState(claim.claim_summary);
  const [claimText, setClaimText] = useState(claim.excerpt);
  const [response, setResponse] = useState(claim.response);
  const [topicTags, setTopicTags] = useState("");
  const [attachTo, setAttachTo] = useState("");

  function run(fn: () => Promise<unknown>) {
    setError(null);
    startTransition(async () => {
      try {
        await fn();
        setMode("idle");
      } catch (e) {
        setError(e instanceof Error ? e.message : "Something went wrong.");
      }
    });
  }

  if (claim.linked) {
    return (
      <div>
        <p className="text-sm font-medium">{claim.claim_summary}</p>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <Tag ink={claim.linked.status === "published" ? "accent" : "muted"}>
            {claim.linked.status === "published" ? "Published" : "Draft"}
          </Tag>
          <Link
            href={`/claims/${claim.linked.slug}`}
            className="text-sm text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
          >
            {claim.linked.title}
          </Link>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {claim.linked.status === "draft" ? (
            <button
              type="button"
              disabled={isPending}
              onClick={() =>
                run(() =>
                  setClaimStatus({
                    claimId: claim.linked!.id,
                    status: "published",
                    currentPath,
                  }),
                )
              }
              className="inline-flex h-9 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-4 text-xs font-medium text-white hover:opacity-90 disabled:opacity-50"
            >
              Publish
            </button>
          ) : (
            <button
              type="button"
              disabled={isPending}
              onClick={() =>
                run(() =>
                  setClaimStatus({
                    claimId: claim.linked!.id,
                    status: "draft",
                    currentPath,
                  }),
                )
              }
              className="inline-flex h-9 items-center rounded-[var(--radius)] border border-[color:var(--border)] px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)] disabled:opacity-50"
            >
              Unpublish
            </button>
          )}
          <button
            type="button"
            disabled={isPending}
            onClick={() =>
              run(() => detachHubClaim({ hubClaimId: claim.id, currentPath }))
            }
            className="inline-flex h-9 items-center rounded-[var(--radius)] border border-[color:var(--border)] px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)] disabled:opacity-50"
          >
            Unlink
          </button>
        </div>
        {error && (
          <p className="mt-2 text-xs text-[color:var(--oxblood)]">{error}</p>
        )}
      </div>
    );
  }

  return (
    <div>
      <p className="text-sm font-medium">{claim.claim_summary}</p>

      {mode === "idle" && (
        <div className="mt-2 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setMode("new")}
            className="inline-flex h-9 items-center rounded-[var(--radius)] border border-[color:var(--border)] px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
          >
            Promote as new claim
          </button>
          {library.length > 0 && (
            <button
              type="button"
              onClick={() => setMode("attach")}
              className="inline-flex h-9 items-center rounded-[var(--radius)] border border-[color:var(--border)] px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
            >
              Attach to existing
            </button>
          )}
        </div>
      )}

      {mode === "new" && (
        <div className="mt-3 space-y-3">
          <Field label="Title">
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className={inputClass}
            />
          </Field>
          <Field
            label="The claim, at its strongest"
            hint="State it as a critic would, not a version that's easy to answer."
          >
            <textarea
              value={claimText}
              onChange={(e) => setClaimText(e.target.value)}
              rows={3}
              className={inputClass}
            />
          </Field>
          <Field label="Response">
            <textarea
              value={response}
              onChange={(e) => setResponse(e.target.value)}
              rows={5}
              className={inputClass}
            />
          </Field>
          <Field label="Topic tags" hint="Comma separated.">
            <input
              value={topicTags}
              onChange={(e) => setTopicTags(e.target.value)}
              placeholder="Book of Mormon, translation"
              className={inputClass}
            />
          </Field>
          <p className="text-xs text-[color:var(--muted)]">
            {claim.sources.length === 0
              ? "This hub claim has no sources — you'll need to add some before the claim can be published."
              : `${claim.sources.length} source${claim.sources.length === 1 ? "" : "s"} will be copied across.`}
          </p>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              disabled={isPending}
              onClick={() =>
                run(() =>
                  promoteToNewClaim({
                    hubClaimId: claim.id,
                    title,
                    claimText,
                    response,
                    topicTags: topicTags
                      .split(",")
                      .map((t) => t.trim())
                      .filter(Boolean),
                    sources: claim.sources,
                    currentPath,
                  }),
                )
              }
              className="inline-flex h-9 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-4 text-xs font-medium text-white hover:opacity-90 disabled:opacity-50"
            >
              Create draft
            </button>
            <button
              type="button"
              onClick={() => setMode("idle")}
              className="inline-flex h-9 items-center rounded-[var(--radius)] border border-[color:var(--border)] px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {mode === "attach" && (
        <div className="mt-3 space-y-3">
          <Field label="Existing claim">
            <select
              value={attachTo}
              onChange={(e) => setAttachTo(e.target.value)}
              className={inputClass}
            >
              <option value="">Select a claim…</option>
              {library.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title} {c.status === "draft" ? "(draft)" : ""}
                </option>
              ))}
            </select>
          </Field>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              disabled={isPending || !attachTo}
              onClick={() =>
                run(() =>
                  attachHubClaimToClaim({
                    hubClaimId: claim.id,
                    claimId: attachTo,
                    currentPath,
                  }),
                )
              }
              className="inline-flex h-9 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-4 text-xs font-medium text-white hover:opacity-90 disabled:opacity-50"
            >
              Attach
            </button>
            <button
              type="button"
              onClick={() => setMode("idle")}
              className="inline-flex h-9 items-center rounded-[var(--radius)] border border-[color:var(--border)] px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {error && (
        <p className="mt-2 text-xs text-[color:var(--oxblood)]">{error}</p>
      )}
    </div>
  );
}

const inputClass =
  "w-full rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 py-2 text-sm focus:border-[color:var(--accent)] focus:outline-none";

function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="small-caps text-xs font-medium text-[color:var(--muted)]">
        {label}
      </span>
      {hint && (
        <span className="mt-0.5 block text-xs text-[color:var(--muted)]">
          {hint}
        </span>
      )}
      <span className="mt-1.5 block">{children}</span>
    </label>
  );
}
