import Link from "next/link";
import { notFound } from "next/navigation";
import {
  createChangelogSection,
  createChangelogVersion,
  deleteChangelogDocument,
  deleteChangelogSection,
  deleteChangelogVersion,
  updateChangelogDocument,
  updateChangelogSection,
  updateChangelogVersion,
} from "@/app/actions/versions";
import { SubmitButton } from "@/components/submit-button";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import type {
  ChangelogDocument,
  ChangelogSection,
  ChangelogVersion,
} from "@/lib/types";

const CONFIDENCE_OPTIONS = [
  { value: "official-digital", label: "Official digital source" },
  { value: "official-pdf", label: "Official PDF" },
  { value: "archived", label: "Archived official page" },
  { value: "printed-scan", label: "Printed scan" },
  { value: "ocr-derived", label: "OCR-derived text" },
  { value: "user-uploaded", label: "User-uploaded source" },
  { value: "unverified", label: "Unverified transcription" },
];

const inputClass =
  "mt-2 h-11 w-full rounded-full border border-[color:var(--border)] px-4 text-sm focus:border-[color:var(--accent)] focus:outline-none";
const areaClass =
  "mt-2 w-full rounded-2xl border border-[color:var(--border)] px-4 py-3 text-sm focus:border-[color:var(--accent)] focus:outline-none";

type RouteParams = { slug: string };

export default async function AdminEditVersionsDocumentPage({
  params,
}: {
  params: Promise<RouteParams>;
}) {
  const { slug } = await params;
  const supabase = createSupabaseServiceClient();
  const { data: docData, error: docError } = await supabase
    .from("changelog_documents")
    .select("*")
    .eq("slug", slug)
    .maybeSingle();
  if (docError) throw docError;
  if (!docData) notFound();
  const doc = docData as ChangelogDocument;

  const { data: versionData, error: versionError } = await supabase
    .from("changelog_versions")
    .select("*")
    .eq("document_id", doc.id)
    .order("ordinal", { ascending: true });
  if (versionError) throw versionError;
  const versions = (versionData ?? []) as ChangelogVersion[];

  const versionIds = versions.map((v) => v.id);
  let sections: ChangelogSection[] = [];
  if (versionIds.length > 0) {
    const { data: sectionData, error: sectionError } = await supabase
      .from("changelog_sections")
      .select("*")
      .in("version_id", versionIds)
      .order("ordinal", { ascending: true });
    if (sectionError) throw sectionError;
    sections = (sectionData ?? []) as ChangelogSection[];
  }
  const sectionsByVersion = new Map<string, ChangelogSection[]>();
  for (const section of sections) {
    const list = sectionsByVersion.get(section.version_id) ?? [];
    list.push(section);
    sectionsByVersion.set(section.version_id, list);
  }

  return (
    <div className="max-w-3xl">
      <Link
        href="/admin/versions"
        className="text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
      >
        ← All documents
      </Link>
      <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
        <h1 className="serif text-4xl font-semibold tracking-tight">
          Edit document
        </h1>
        <Link
          href={`/versions/${doc.slug}`}
          className="text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
        >
          View public page →
        </Link>
      </div>

      {/* Document fields */}
      <form
        action={updateChangelogDocument.bind(null, doc.id)}
        className="mt-8 grid gap-5 rounded-2xl border border-[color:var(--border)] bg-white p-6"
      >
        <label className="block text-sm font-medium">
          Title
          <input
            name="title"
            required
            defaultValue={doc.title}
            className={inputClass}
          />
        </label>
        <label className="block text-sm font-medium">
          Slug
          <input name="slug" defaultValue={doc.slug} className={inputClass} />
        </label>
        <label className="block text-sm font-medium">
          Category
          <input
            name="category"
            defaultValue={doc.category ?? ""}
            className={inputClass}
          />
        </label>
        <label className="block text-sm font-medium">
          Summary
          <textarea
            name="summary"
            rows={4}
            defaultValue={doc.summary ?? ""}
            className={areaClass}
          />
        </label>
        <SubmitButton pendingLabel="Saving…">Save document</SubmitButton>
      </form>

      {/* Versions */}
      <section className="mt-12">
        <h2 className="serif text-2xl font-semibold tracking-tight">Editions</h2>

        <div className="mt-6 space-y-6">
          {versions.map((version) => {
            const versionSections = sectionsByVersion.get(version.id) ?? [];
            return (
              <div
                key={version.id}
                className="rounded-2xl border border-[color:var(--border)] bg-white p-6"
              >
                <form
                  action={updateChangelogVersion.bind(
                    null,
                    version.id,
                    doc.slug,
                  )}
                  className="grid gap-4 sm:grid-cols-2"
                >
                  <label className="block text-sm font-medium sm:col-span-2">
                    Label
                    <input
                      name="label"
                      required
                      defaultValue={version.label}
                      placeholder="e.g. 2023 edition"
                      className={inputClass}
                    />
                  </label>
                  <label className="block text-sm font-medium">
                    Published on
                    <input
                      name="published_on"
                      type="date"
                      defaultValue={version.published_on ?? ""}
                      className={inputClass}
                    />
                  </label>
                  <label className="block text-sm font-medium">
                    Order
                    <input
                      name="ordinal"
                      type="number"
                      defaultValue={version.ordinal}
                      className={inputClass}
                    />
                  </label>
                  <label className="block text-sm font-medium">
                    Source type
                    <input
                      name="source_type"
                      defaultValue={version.source_type}
                      placeholder="markdown"
                      className={inputClass}
                    />
                  </label>
                  <label className="block text-sm font-medium">
                    Confidence
                    <select
                      name="confidence"
                      defaultValue={version.confidence ?? ""}
                      className={inputClass}
                    >
                      <option value="">— unset —</option>
                      {CONFIDENCE_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="block text-sm font-medium sm:col-span-2">
                    Source URL
                    <input
                      name="source_url"
                      type="url"
                      defaultValue={version.source_url ?? ""}
                      className={inputClass}
                    />
                  </label>
                  <div className="sm:col-span-2">
                    <SubmitButton pendingLabel="Saving…">
                      Save edition
                    </SubmitButton>
                  </div>
                </form>

                {/* Sections within this version */}
                <div className="mt-6 border-t border-[color:var(--border)] pt-6">
                  <p className="text-xs font-medium uppercase tracking-[0.18em] text-[color:var(--accent)]">
                    Sections
                  </p>

                  <div className="mt-4 space-y-4">
                    {versionSections.map((section) => (
                      <form
                        key={section.id}
                        action={updateChangelogSection.bind(
                          null,
                          section.id,
                          doc.slug,
                        )}
                        className="rounded-xl border border-[color:var(--border)] bg-[color:var(--muted-soft)]/30 p-4"
                      >
                        <div className="grid gap-3 sm:grid-cols-[1fr_120px]">
                          <label className="block text-sm font-medium">
                            Heading
                            <input
                              name="heading"
                              defaultValue={section.heading ?? ""}
                              className={inputClass}
                            />
                          </label>
                          <label className="block text-sm font-medium">
                            Order
                            <input
                              name="ordinal"
                              type="number"
                              defaultValue={section.ordinal}
                              className={inputClass}
                            />
                          </label>
                        </div>
                        <label className="mt-3 block text-sm font-medium">
                          Body (markdown)
                          <textarea
                            name="body_markdown"
                            rows={6}
                            defaultValue={section.body_markdown ?? ""}
                            className={`${areaClass} font-mono`}
                          />
                        </label>
                        <div className="mt-3 flex items-center gap-4">
                          <SubmitButton pendingLabel="Saving…">
                            Save section
                          </SubmitButton>
                          <button
                            formAction={deleteChangelogSection.bind(
                              null,
                              section.id,
                              doc.slug,
                            )}
                            className="text-xs text-red-700 hover:underline"
                          >
                            Delete section
                          </button>
                        </div>
                      </form>
                    ))}
                  </div>

                  {/* Add section */}
                  <form
                    action={createChangelogSection.bind(
                      null,
                      version.id,
                      doc.slug,
                    )}
                    className="mt-4 rounded-xl border border-dashed border-[color:var(--border)] p-4"
                  >
                    <p className="text-sm font-medium">Add a section</p>
                    <input
                      name="heading"
                      placeholder="Heading (optional)"
                      className={inputClass}
                    />
                    <textarea
                      name="body_markdown"
                      rows={4}
                      placeholder="Markdown body…"
                      className={`${areaClass} font-mono`}
                    />
                    <div className="mt-3">
                      <SubmitButton pendingLabel="Adding…">
                        + Add section
                      </SubmitButton>
                    </div>
                  </form>
                </div>

                {/* Delete version */}
                <form
                  action={deleteChangelogVersion.bind(null, version.id, doc.slug)}
                  className="mt-6 border-t border-[color:var(--border)] pt-4"
                >
                  <button className="text-xs text-red-700 hover:underline">
                    Delete this edition (and its sections)
                  </button>
                </form>
              </div>
            );
          })}
        </div>

        {/* Add version */}
        <form
          action={createChangelogVersion.bind(null, doc.id, doc.slug)}
          className="mt-6 grid gap-4 rounded-2xl border border-dashed border-[color:var(--border)] p-6 sm:grid-cols-2"
        >
          <p className="text-sm font-medium sm:col-span-2">Add an edition</p>
          <label className="block text-sm font-medium sm:col-span-2">
            Label
            <input
              name="label"
              required
              placeholder="e.g. 2004 edition"
              className={inputClass}
            />
          </label>
          <label className="block text-sm font-medium">
            Published on
            <input name="published_on" type="date" className={inputClass} />
          </label>
          <label className="block text-sm font-medium">
            Confidence
            <select name="confidence" defaultValue="" className={inputClass}>
              <option value="">— unset —</option>
              {CONFIDENCE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm font-medium sm:col-span-2">
            Source URL
            <input name="source_url" type="url" className={inputClass} />
          </label>
          <div className="sm:col-span-2">
            <SubmitButton pendingLabel="Adding…">+ Add edition</SubmitButton>
          </div>
        </form>
      </section>

      {/* Delete document */}
      <form
        action={deleteChangelogDocument.bind(null, doc.id)}
        className="mt-12 border-t border-[color:var(--border)] pt-6"
      >
        <button className="text-sm text-red-700 hover:underline">
          Delete this document (and all editions)
        </button>
      </form>
    </div>
  );
}
