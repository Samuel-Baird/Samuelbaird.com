import { createStudy } from "@/app/admin/actions";

export default function NewStudyPage() {
  return (
    <div className="max-w-2xl">
      <h1 className="serif text-4xl font-semibold tracking-tight">New study</h1>
      <form
        action={createStudy}
        className="mt-8 grid gap-5 rounded-2xl border border-[color:var(--border)] bg-white p-6"
      >
        <TextField name="title" label="Title" required />
        <TextField name="authors" label="Authors" placeholder="Comma-separated" />
        <TextField name="year" label="Year" type="number" />
        <TextField name="source" label="Source" />
        <label className="block text-sm font-medium">
          Abstract
          <textarea
            name="abstract"
            rows={6}
            className="mt-2 w-full rounded-2xl border border-[color:var(--border)] px-4 py-3 text-sm focus:border-[color:var(--accent)] focus:outline-none"
          />
        </label>
        <TextField name="tags" label="Tags" placeholder="Comma-separated" />
        <label className="flex items-center gap-2 text-sm">
          <input name="featured" type="checkbox" className="h-4 w-4" />
          Featured
        </label>
        <label className="block text-sm font-medium">
          PDF
          <input
            name="pdf"
            type="file"
            accept="application/pdf"
            required
            className="mt-2 block w-full text-sm"
          />
        </label>
        <button className="inline-flex h-10 w-fit items-center rounded-full bg-[color:var(--accent)] px-4 text-sm font-medium text-white hover:opacity-90">
          Create study
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
}: {
  name: string;
  label: string;
  type?: string;
  required?: boolean;
  placeholder?: string;
}) {
  return (
    <label className="block text-sm font-medium">
      {label}
      <input
        name={name}
        type={type}
        required={required}
        placeholder={placeholder}
        className="mt-2 h-11 w-full rounded-full border border-[color:var(--border)] px-4 text-sm focus:border-[color:var(--accent)] focus:outline-none"
      />
    </label>
  );
}
