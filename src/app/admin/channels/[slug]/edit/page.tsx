import Link from "next/link";
import { notFound } from "next/navigation";
import { deleteChannel, updateChannelDetails } from "@/app/admin/actions";
import { TYPE_COLORS } from "@/lib/channel-types";
import { COUNTRIES, LANGUAGES } from "@/lib/iso";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import type { Channel } from "@/lib/types";

type RouteParams = { slug: string };

export default async function AdminEditChannelPage({
  params,
}: {
  params: Promise<RouteParams>;
}) {
  const { slug } = await params;
  const supabase = createSupabaseServiceClient();
  const { data, error } = await supabase
    .from("channels")
    .select("*")
    .eq("slug", slug)
    .maybeSingle();
  if (error) throw error;
  if (!data) notFound();
  const channel = data as Channel;
  const types = Object.keys(TYPE_COLORS).sort();

  const action = updateChannelDetails.bind(null, channel.id);

  return (
    <div className="max-w-2xl">
      <Link
        href="/admin/channels"
        className="text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
      >
        ← All channels
      </Link>
      <h1 className="serif mt-4 text-4xl font-semibold tracking-tight">
        Edit {channel.name}
      </h1>
      <p className="mt-2 text-sm text-[color:var(--muted)]">
        YouTube ID:{" "}
        <code className="rounded bg-[color:var(--muted-soft)] px-1.5 py-0.5 text-xs">
          {channel.youtube_channel_id}
        </code>
      </p>

      <form
        action={action}
        className="mt-8 grid gap-5 rounded-2xl border border-[color:var(--border)] bg-white p-6"
      >
        <Field label="Type">
          <select
            name="channel_type"
            defaultValue={channel.channel_type ?? ""}
            className="h-10 w-full rounded-md border border-[color:var(--border)] bg-white px-3 text-sm"
          >
            <option value="">—</option>
            {types.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </Field>

        <div className="grid gap-5 sm:grid-cols-2">
          <Field label="Handle">
            <Input name="handle" defaultValue={channel.handle ?? ""} />
          </Field>
          <Field label="Owned by">
            <Input name="owned_by" defaultValue={channel.owned_by ?? ""} />
          </Field>
          <Field
            label="Country (override)"
            hint={
              channel.country
                ? `YouTube API value: ${channel.country}. Leave blank to use it.`
                : "YouTube API did not provide a country."
            }
          >
            <input
              name="country_manual"
              list="iso-countries"
              defaultValue={channel.country_manual ?? ""}
              placeholder="e.g. US"
              className="h-10 w-full rounded-md border border-[color:var(--border)] bg-white px-3 text-sm focus:border-[color:var(--accent)] focus:outline-none"
            />
          </Field>
          <Field
            label="Language (override)"
            hint={
              channel.language
                ? `YouTube API value: ${channel.language}. Leave blank to use it.`
                : "YouTube API did not provide a language."
            }
          >
            <input
              name="language_manual"
              list="iso-languages"
              defaultValue={channel.language_manual ?? ""}
              placeholder="e.g. en"
              className="h-10 w-full rounded-md border border-[color:var(--border)] bg-white px-3 text-sm focus:border-[color:var(--accent)] focus:outline-none"
            />
          </Field>
          <datalist id="iso-countries">
            {COUNTRIES.map((c) => (
              <option key={c.code} value={c.code}>
                {c.name}
              </option>
            ))}
          </datalist>
          <datalist id="iso-languages">
            {LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>
                {l.name}
              </option>
            ))}
          </datalist>
          <Field label="State / region">
            <Input name="state" defaultValue={channel.state ?? ""} />
          </Field>
          <Field label="City">
            <Input name="city" defaultValue={channel.city ?? ""} />
          </Field>
        </div>

        <div className="flex flex-wrap gap-6">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              name="featured"
              defaultChecked={channel.featured}
            />
            Featured
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              name="is_active"
              defaultChecked={channel.is_active}
            />
            Active
          </label>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button className="inline-flex h-10 items-center rounded-full bg-[color:var(--accent)] px-5 text-sm font-medium text-white hover:opacity-90">
            Save changes
          </button>
          <Link
            href={`/channels/${channel.slug}`}
            className="text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
          >
            View public page →
          </Link>
        </div>
      </form>

      <form
        action={deleteChannel.bind(null, channel.id)}
        className="mt-6"
      >
        <button className="text-sm text-red-700 hover:underline">
          Delete this channel
        </button>
      </form>
    </div>
  );
}

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
    <label className="block text-sm font-medium">
      <span className="block text-xs uppercase tracking-wider text-[color:var(--muted)]">
        {label}
      </span>
      <div className="mt-1.5">{children}</div>
      {hint && (
        <span className="mt-1 block text-xs font-normal text-[color:var(--muted)]">
          {hint}
        </span>
      )}
    </label>
  );
}

function Input({
  name,
  defaultValue,
}: {
  name: string;
  defaultValue?: string;
}) {
  return (
    <input
      name={name}
      defaultValue={defaultValue}
      className="h-10 w-full rounded-md border border-[color:var(--border)] bg-white px-3 text-sm focus:border-[color:var(--accent)] focus:outline-none"
    />
  );
}
