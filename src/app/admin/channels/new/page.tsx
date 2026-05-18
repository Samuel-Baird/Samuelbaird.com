import { addChannelByInput } from "@/app/admin/actions";

export default function NewChannelPage() {
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
        <button className="mt-5 inline-flex h-10 items-center rounded-full bg-[color:var(--accent)] px-4 text-sm font-medium text-white hover:opacity-90">
          Add channel
        </button>
      </form>
    </div>
  );
}
