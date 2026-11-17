import { Suspense } from "react";
import {
  AdminMessageNotifications,
  type AdminMessagePreview,
} from "@/components/admin-message-notifications";
import { AuthMenu, type AuthMenuUser } from "@/components/auth-menu";
import { CommandPaletteHost } from "@/components/command-palette-host";
import { FAMILY_TOP } from "@/components/family-chrome.generated";
import { getCurrentUser, signOutAction } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

// Page links live in the family sidebar (packages/family/sites.mjs, "latter-day-stats").

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


  return (
    <>
      {/* Shared Samuel Baird family chrome: sidebar, top bar and panorama (packages/family). */}
      <div dangerouslySetInnerHTML={{ __html: FAMILY_TOP }} />
      <div className="lds-accountbar fam-wrap">
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
