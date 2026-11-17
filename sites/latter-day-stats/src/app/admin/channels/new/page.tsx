import { addChannelByInput } from "@/app/admin/actions";
import { SubmitButton } from "@/components/submit-button";
import { requireAdmin } from "@/lib/auth";

export default async function NewChannelPage() {
  await requireAdmin();

  async function submit(formData: FormData) {
    "use server";
    await addChannelByInput(String(formData.get("channel") ?? ""));
  }

  return (
    <div className="max-w-xl">
      <h1 className="serif text-4xl font-semibold tracking-tight">
        New channel
      </h1>
      <form action={submit} className="mt-8 rounded-2xl border border-[color:var(--border)] bg-white p-6">
        <label className="block text-sm font-medium">
          YouTube handle, URL, or channel ID
          <input
            name="channel"
            required
            placeholder="@channel or UC..."
            className="mt-2 h-11 w-full rounded-full border border-[color:var(--border)] px-4 text-sm focus:border-[color:var(--accent)] focus:outline-none"
          />
        </label>
        <div className="mt-5">
          <SubmitButton pendingLabel="Adding…">Add channel</SubmitButton>
        </div>
      </form>
    </div>
  );
}
