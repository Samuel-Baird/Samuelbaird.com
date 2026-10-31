import Link from "next/link";
import { Suspense } from "react";
import { BeehiveStatsMark } from "@/components/beehive-stats-mark";
import { DeseretTitle } from "@/components/deseret-title";
import {
  AdminMessageNotifications,
  type AdminMessagePreview,
} from "@/components/admin-message-notifications";
import { AuthMenu, type AuthMenuUser } from "@/components/auth-menu";
import { CommandPaletteHost } from "@/components/command-palette-host";
import { SiteNavClient, type SiteNavLink } from "@/components/site-nav-client";
import { SiteSidebar, type SidebarLink } from "@/components/site-sidebar";
import { getCurrentUser, signOutAction } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

const BASE_LINKS: SiteNavLink[] = [
  { href: "/channels", label: "Channels" },
  { href: "/studies", label: "Studies" },
  { href: "/data-explorer", label: "Data Explorer" },
  { href: "/connect", label: "Use with AI" },
  { href: "/about", label: "About" },
  { href: "/contact", label: "Contact" },
  { href: "/donate", label: "Donate" },
];

// Large screens get the always-open sidebar; everything below lg uses the top
// bar and its hamburger menu (BASE_LINKS).
const SIDEBAR_PRIMARY: SidebarLink[] = [
  { href: "/", label: "Home", icon: "home" },
  { href: "/channels", label: "Channels", icon: "channels" },
  { href: "/studies", label: "Studies", icon: "studies" },
  { href: "/data-explorer", label: "Data Explorer", icon: "data" },
];
const SIDEBAR_SECONDARY: SidebarLink[] = [
  { href: "/connect", label: "Use with AI", icon: "ai" },
  { href: "/about", label: "About", icon: "about" },
  { href: "/contact", label: "Contact", icon: "contact" },
  { href: "/donate", label: "Donate", icon: "donate" },
];

export async function SiteNav() {
  const auth = await getCurrentUser();
  const user: AuthMenuUser | null = auth
    ? {
        id: auth.user.id,
        email: auth.profile?.email ?? auth.user.email ?? null,
        full_name:
          auth.profile?.full_name ??
          (auth.user.user_metadata.full_name as string | undefined) ??
          null,
        avatar_url:
          auth.profile?.avatar_url ??
          (auth.user.user_metadata.avatar_url as string | undefined) ??
          null,
        is_admin: auth.profile?.is_admin === true,
      }
    : null;
  const messageNotifications = user?.is_admin
    ? await getOpenMessageNotifications()
    : null;

  const wordmark = (
    <Link
      href="/"
      className="flex items-center gap-2.5 text-[color:var(--foreground)]"
    >
      <BeehiveStatsMark
        title="Latter-day Stats"
        className="h-6 w-6 shrink-0"
      />
      <DeseretTitle
        text="Latter-day Stats"
        replay="session"
        sessionKey="wordmark"
        className="serif text-xl font-semibold tracking-tight sm:text-2xl"
      />
    </Link>
  );

  return (
    <>
      <header className="sticky top-0 z-40 border-b border-[color:var(--border)] bg-[color:var(--background)]/85 backdrop-blur lg:hidden">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-5 py-4 sm:px-8">
          {wordmark}

          <div className="flex items-center gap-3">
            <SiteNavClient links={BASE_LINKS} user={user} signOut={signOutAction} />
            <Suspense fallback={null}>
              <CommandPaletteHost />
            </Suspense>
            {messageNotifications ? (
              <AdminMessageNotifications
                openCount={messageNotifications.openCount}
                previews={messageNotifications.previews}
              />
            ) : null}
            <AuthMenu user={user} signOut={signOutAction} />
          </div>
        </div>
      </header>

      <SiteSidebar
        primary={SIDEBAR_PRIMARY}
        secondary={SIDEBAR_SECONDARY}
        user={user}
        signOut={signOutAction}
        messageCount={messageNotifications?.openCount ?? null}
        brand={wordmark}
        search={
          <Suspense fallback={null}>
            <CommandPaletteHost variant="sidebar" />
          </Suspense>
        }
      />
    </>
  );
}

async function getOpenMessageNotifications(): Promise<{
  openCount: number;
  previews: AdminMessagePreview[];
}> {
  const supabase = createSupabaseServiceClient();
  const { data, count, error } = await supabase
    .from("messages")
    .select("id, category, body, created_at, page_ref, name, email", {
      count: "exact",
    })
    .eq("resolved", false)
    .order("created_at", { ascending: false })
    .limit(5);

  if (error) {
    console.error("open message notification query failed:", error);
    return { openCount: 0, previews: [] };
  }

  return {
    openCount: count ?? data?.length ?? 0,
    previews: (data ?? []) as AdminMessagePreview[],
  };
}
