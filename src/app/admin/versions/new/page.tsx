import Link from "next/link";
import { createChangelogDocument } from "@/app/actions/versions";
import { SubmitButton } from "@/components/submit-button";

export default function NewVersionsDocumentPage() {
  return (
    <div className="max-w-2xl">
      <Link
        href="/admin/versions"
        className="text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
      >
        ← All documents
      </Link>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight">
        New document
      </h1>
      <p className="mt-2 text-sm text-[color:var(--muted)]">
        Create the document, then add its editions and markdown sections on the
        next screen.
      </p>

      <form
        action={createChangelogDocument}
        className="mt-8 grid gap-5 rounded-2xl border border-[color:var(--border)] bg-white p-6"
      >
        <label className="block text-sm font-medium">
          Title
          <input
            name="title"
            required
            placeholder="e.g. General Handbook"
            className="mt-2 h-11 w-full rounded-full border border-[color:var(--border)] px-4 text-sm focus:border-[color:var(--accent)] focus:outline-none"
          />
        </label>
        <label className="block text-sm font-medium">
          Slug
          <span className="mt-1 block text-xs font-normal text-[color:var(--muted)]">
            Optional — defaults to a slug derived from the title.
          </span>
          <input
            name="slug"
            placeholder="general-handbook"
            className="mt-2 h-11 w-full rounded-full border border-[color:var(--border)] px-4 text-sm focus:border-[color:var(--accent)] focus:outline-none"
          />
        </label>
        <label className="block text-sm font-medium">
          Category
          <input
            name="category"
            placeholder="e.g. Handbook, Manual, Guide"
            className="mt-2 h-11 w-full rounded-full border border-[color:var(--border)] px-4 text-sm focus:border-[color:var(--accent)] focus:outline-none"
          />
        </label>
        <label className="block text-sm font-medium">
          Summary
          <textarea
            name="summary"
            rows={4}
            placeholder="Short neutral description of the document."
            className="mt-2 w-full rounded-2xl border border-[color:var(--border)] px-4 py-3 text-sm focus:border-[color:var(--accent)] focus:outline-none"
          />
        </label>
        <SubmitButton pendingLabel="Creating…">Create document</SubmitButton>
      </form>
    </div>
  );
}
