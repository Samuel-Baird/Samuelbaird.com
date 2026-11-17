import { requireUser } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { NewsletterToggle } from "@/components/newsletter-toggle";
import { DeleteAccountButton } from "@/components/delete-account-button";
import { BASE_PATH } from "@/lib/site";

export const dynamic = "force-dynamic";

export default async function SettingsPage() {
  const { user, profile } = await requireUser();

  const { data: subscriber, error } = await createSupabaseServiceClient()
    .from("newsletter_subscribers")
    .select("unsubscribed_at")
    .eq("user_id", user.id)
    .maybeSingle();
  if (error) throw error;
  const subscribed = subscriber !== null && subscriber.unsubscribed_at === null;

  const name = profile?.full_name ?? "Signed-in user";
  const email = profile?.email ?? user.email ?? "(no email on account)";

  return (
    <div>
      <h1 className="serif text-4xl font-semibold tracking-tight">Settings</h1>

      <section className="mt-8 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6">
        <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
          Account
        </h2>
        <p className="mt-3 text-sm font-medium text-[color:var(--foreground)]">
          {name}
        </p>
        <p className="mt-1 text-sm text-[color:var(--muted)]">{email}</p>
        <p className="mt-3 text-xs text-[color:var(--muted)]">
          Sign-in is via Google; your name and email come from your Google
          account.
        </p>
      </section>

      <section className="mt-6 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6">
        <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
          Email updates
        </h2>
        <p className="mt-3 text-sm leading-relaxed text-[color:var(--muted)]">
          A monthly email listing channels and studies added to the site.
          Unsubscribe any time from the email itself or here.
        </p>
        <div className="mt-4">
          <NewsletterToggle initial={subscribed} />
        </div>
      </section>

      <section className="mt-6 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6">
        <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
          Your data
        </h2>
        <p className="mt-3 text-sm leading-relaxed text-[color:var(--muted)]">
          Download a copy of everything tied to your account — bookmarks,
          upvotes, reading progress, newsletter subscription, and messages
          you&apos;ve sent.
        </p>
        <div className="mt-4">
          <a
            href={`${BASE_PATH}/api/me/export`}
            className="inline-flex h-10 items-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 text-sm font-medium hover:bg-[color:var(--muted-soft)]"
          >
            Export my data
          </a>
        </div>
      </section>

      <section className="mt-6 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6">
        <h2 className="small-caps text-xs font-medium text-[color:var(--oxblood)]">
          Delete account
        </h2>
        <p className="mt-3 text-sm leading-relaxed text-[color:var(--muted)]">
          Permanently delete your account and everything tied to it.
        </p>
        <div className="mt-4">
          <DeleteAccountButton />
        </div>
      </section>
    </div>
  );
}
