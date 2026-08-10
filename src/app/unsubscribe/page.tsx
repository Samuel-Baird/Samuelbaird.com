import Link from "next/link";
import { redirect } from "next/navigation";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { getSubscriberByToken, unsubscribeByToken } from "@/lib/newsletter";

// Public — reached from an emailed link, no session available. Never caches:
// the token lookup must reflect the current subscription state.
export const dynamic = "force-dynamic";

type SearchParams = { token?: string; done?: string };

export default async function UnsubscribePage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;
  const token = params.token?.trim() ?? "";
  const done = params.done === "1";

  async function confirmUnsubscribe() {
    "use server";
    await unsubscribeByToken(createSupabaseServiceClient(), token);
    redirect(`/unsubscribe?token=${encodeURIComponent(token)}&done=1`);
  }

  const subscriber = token
    ? await getSubscriberByToken(createSupabaseServiceClient(), token)
    : null;

  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <div className="mx-auto max-w-xl rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-8 text-center">
        {!subscriber ? (
          <>
            <h1 className="serif text-2xl font-semibold tracking-tight">
              Link not valid
            </h1>
            <p className="mt-3 text-sm leading-relaxed text-[color:var(--muted)]">
              This unsubscribe link isn&apos;t valid, or the subscription it
              points to no longer exists. You can manage your subscription
              any time from account settings.
            </p>
            <Link
              href="/me/settings"
              className="mt-6 inline-flex h-11 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90"
            >
              Go to settings
            </Link>
          </>
        ) : done || !subscriber.subscribed ? (
          <>
            <h1 className="serif text-2xl font-semibold tracking-tight">
              You&apos;re unsubscribed
            </h1>
            <p className="mt-3 text-sm leading-relaxed text-[color:var(--muted)]">
              You won&apos;t receive any more monthly emails. You can
              resubscribe any time in account settings.
            </p>
            <Link
              href="/me/settings"
              className="mt-6 inline-flex h-11 items-center rounded-[var(--radius)] border border-[color:var(--border)] px-6 text-sm font-medium hover:bg-[color:var(--muted-soft)]"
            >
              Manage subscription
            </Link>
          </>
        ) : (
          <>
            <h1 className="serif text-2xl font-semibold tracking-tight">
              Unsubscribe from monthly updates?
            </h1>
            <p className="mt-3 text-sm leading-relaxed text-[color:var(--muted)]">
              You&apos;ll stop receiving the monthly email listing new
              channels and studies. You can resubscribe any time.
            </p>
            <form action={confirmUnsubscribe} className="mt-6">
              <button
                type="submit"
                className="inline-flex h-11 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90"
              >
                Unsubscribe
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
