import Link from "next/link";
import { notFound } from "next/navigation";
import { deleteChannel, updateChannelDetails } from "@/app/admin/actions";
import { EditForm } from "@/components/edit-form";
import { Tag } from "@/components/tag";
import { TYPE_INK, inkForType } from "@/lib/channel-types";
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
    .from("channel_full")
    .select("*")
    .or(`slug.eq.${slug},youtube_channel_id.eq.${slug}`)
    .maybeSingle();
  if (error) throw error;
  if (!data) notFound();
  const channel = data as Channel;
  const types = Object.keys(TYPE_INK).sort();
  const selectedTypes = new Set(
    channel.channel_types?.length
      ? channel.channel_types
      : channel.channel_type
        ? [channel.channel_type]
        : [],
  );

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

      <EditForm
        action={action}
        className="mt-8 grid gap-5 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6"
      >
        <Field
          label="Tags"
          hint="Pick every tag that applies. The first selected tag (alphabetical) is used as the primary type for legacy displays."
        >
          <div className="mt-1 grid max-h-72 grid-cols-2 gap-1.5 overflow-y-auto rounded-md border border-[color:var(--border)] bg-white p-2 sm:grid-cols-3">
            {types.map((t) => {
              const checked = selectedTypes.has(t);
              return (
                <label
                  key={t}
                  className={`flex cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-xs transition-colors ${
                    checked ? "bg-[color:var(--muted-soft)]" : "hover:bg-[color:var(--muted-soft)]/50"
                  }`}
                >
                  <input
                    type="checkbox"
                    name="channel_types"
                    value={t}
                    defaultChecked={checked}
                    className="h-3.5 w-3.5"
                  />
                  <Tag ink={inkForType(t)}>{t}</Tag>
                </label>
              );
            })}
          </div>
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

        <fieldset className="grid gap-5 rounded-[var(--radius)] border border-[color:var(--border)] p-4">
          <legend className="px-1 text-xs uppercase tracking-wider text-[color:var(--muted)]">
            Other social profiles
          </legend>
          <p className="-mt-2 text-xs text-[color:var(--muted)]">
            Optional profile links only. These do not affect tracked stats.
          </p>
          <div className="grid gap-5 sm:grid-cols-2">
            <Field label="Facebook">
              <Input
                name="facebook_url"
                defaultValue={channel.facebook_url ?? ""}
                placeholder="https://facebook.com/..."
              />
            </Field>
            <Field label="Instagram">
              <Input
                name="instagram_url"
                defaultValue={channel.instagram_url ?? ""}
                placeholder="https://instagram.com/..."
              />
            </Field>
            <Field label="TikTok">
              <Input
                name="tiktok_url"
                defaultValue={channel.tiktok_url ?? ""}
                placeholder="https://tiktok.com/@..."
              />
            </Field>
            <Field label="X">
              <Input
                name="x_url"
                defaultValue={channel.x_url ?? ""}
                placeholder="https://x.com/..."
              />
            </Field>
          </div>
        </fieldset>

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

        <Link
          href={`/channels/${channel.slug}`}
          className="text-sm text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
        >
          View public page →
        </Link>
      </EditForm>

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
  placeholder,
}: {
  name: string;
  defaultValue?: string;
  placeholder?: string;
}) {
  return (
    <input
      name={name}
      defaultValue={defaultValue}
      placeholder={placeholder}
      className="h-10 w-full rounded-md border border-[color:var(--border)] bg-white px-3 text-sm focus:border-[color:var(--accent)] focus:outline-none"
    />
  );
}
