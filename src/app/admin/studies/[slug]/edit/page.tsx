import Link from "next/link";
import { notFound } from "next/navigation";
import {
  deleteStudy,
  regenerateStudyPreview,
  updateStudy,
} from "@/app/admin/actions";
import { EditForm } from "@/components/edit-form";
import { PreviewImageField } from "@/components/preview-image-field";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import type { Study } from "@/lib/types";

type RouteParams = { slug: string };

export default async function AdminEditStudyPage({
  params,
}: {
  params: Promise<RouteParams>;
}) {
  const { slug } = await params;
  const supabase = createSupabaseServiceClient();
  const { data, error } = await supabase
    .from("studies")
    .select("*")
    .eq("slug", slug)
    .maybeSingle();
  if (error) throw error;
  if (!data) notFound();
  const study = data as Study;
  const action = updateStudy.bind(null, study.id);

  return (
    <div className="max-w-2xl">
      <Link
        href="/admin/studies"
        className="text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
      >
        ← All studies
      </Link>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight">
        Edit study
      </h1>

      <EditForm
        action={action}
        className="mt-8 grid gap-5 rounded-2xl border border-[color:var(--border)] bg-white p-6"
      >
        <TextField name="title" label="Title" defaultValue={study.title} required />
        <TextField
          name="authors"
          label="Authors"
          placeholder="Comma-separated"
          defaultValue={study.authors.join(", ")}
        />
        <TextField
          name="year"
          label="Year"
          type="number"
          defaultValue={study.year?.toString() ?? ""}
        />
        <TextField
          name="source"
          label="Source"
          defaultValue={study.source ?? ""}
        />
        <Textarea
          name="abstract"
          label="Abstract"
          rows={6}
          defaultValue={study.abstract ?? ""}
        />
        <Textarea
          name="findings"
          label="Findings for Latter-day Saints"
          rows={6}
          hint="One per line."
          defaultValue={(study.findings ?? []).join("\n")}
        />
        <Textarea
          name="limitations"
          label="Limitations in methodology"
          rows={5}
          defaultValue={study.limitations ?? ""}
        />
        <Textarea
          name="context_note"
          label="Context note (neutral)"
          rows={4}
          hint="Additional context for studies easy to misunderstand but not methodologically flagged."
          defaultValue={study.context_note ?? ""}
        />
        <TextField
          name="tags"
          label="Tags"
          placeholder="Comma-separated"
          defaultValue={study.tags.join(", ")}
        />
        <PreviewImageField
          currentPath={study.preview_image_path}
          currentSource={study.preview_image_source}
          currentCaption={study.preview_image_caption}
          isAi={study.preview_image_is_ai ?? false}
        />
        <fieldset className="rounded-2xl border border-red-200 bg-red-50/40 p-4">
          <label className="flex items-center gap-2 text-sm font-medium text-red-900">
            <input
              name="flagged_problematic"
              type="checkbox"
              defaultChecked={study.flagged_problematic ?? false}
              className="h-4 w-4"
            />
            Flag as problematic methodology
          </label>
          <label className="mt-3 block text-sm font-medium">
            Flag reason
            <textarea
              name="flag_reason"
              rows={3}
              defaultValue={study.flag_reason ?? ""}
              className="mt-2 w-full rounded-2xl border border-[color:var(--border)] px-4 py-3 text-sm focus:border-[color:var(--accent)] focus:outline-none"
            />
          </label>
        </fieldset>
        <Link
          href={`/studies/${study.slug}`}
          className="text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
        >
          View public page →
        </Link>
      </EditForm>

      <form
        action={regenerateStudyPreview.bind(null, study.id)}
        className="mt-6"
      >
        <button className="inline-flex h-9 items-center rounded-full border border-[color:var(--border)] px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)]">
          Regenerate preview (auto)
        </button>
        <p className="mt-1 text-xs text-[color:var(--muted)]">
          Runs the PDF → URL → AI-dataviz cascade. Replaces any existing preview.
        </p>
      </form>

      <form action={deleteStudy.bind(null, study.id)} className="mt-6">
        <button className="text-sm text-red-700 hover:underline">
          Delete this study
        </button>
      </form>
    </div>
  );
}

function TextField({
  name,
  label,
  type = "text",
  required = false,
  placeholder,
  defaultValue,
}: {
  name: string;
  label: string;
  type?: string;
  required?: boolean;
  placeholder?: string;
  defaultValue?: string;
}) {
  return (
    <label className="block text-sm font-medium">
      {label}
      <input
        name={name}
        type={type}
        required={required}
        placeholder={placeholder}
        defaultValue={defaultValue}
        className="mt-2 h-11 w-full rounded-full border border-[color:var(--border)] px-4 text-sm focus:border-[color:var(--accent)] focus:outline-none"
      />
    </label>
  );
}

function Textarea({
  name,
  label,
  rows = 5,
  hint,
  defaultValue,
}: {
  name: string;
  label: string;
  rows?: number;
  hint?: string;
  defaultValue?: string;
}) {
  return (
    <label className="block text-sm font-medium">
      {label}
      {hint && (
        <span className="mt-1 block text-xs font-normal text-[color:var(--muted)]">
          {hint}
        </span>
      )}
      <textarea
        name={name}
        rows={rows}
        defaultValue={defaultValue}
        className="mt-2 w-full rounded-2xl border border-[color:var(--border)] px-4 py-3 text-sm focus:border-[color:var(--accent)] focus:outline-none"
      />
    </label>
  );
}
