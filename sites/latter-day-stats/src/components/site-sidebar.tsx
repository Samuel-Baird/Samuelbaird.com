"use client";

import {
  BarChart3,
  Bell,
  BookOpen,
  Bookmark,
  Heart,
  Home,
  Info,
  LogIn,
  LogOut,
  Mail,
  Settings,
  Shield,
  Sparkles,
  Users,
  type LucideIcon,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { AuthAvatar, type AuthMenuUser } from "@/components/auth-menu";

export type SidebarIcon =
  | "home"
  | "channels"
  | "studies"
  | "data"
  | "ai"
  | "about"
  | "contact"
  | "donate";

export type SidebarLink = {
  href: string;
  label: string;
  icon: SidebarIcon;
};

const ICONS: Record<SidebarIcon, LucideIcon> = {
  home: Home,
  channels: Users,
  studies: BookOpen,
  data: BarChart3,
  ai: Sparkles,
  about: Info,
  contact: Mail,
  donate: Heart,
};

type Props = {
  /** Main destinations, top of the sidebar. */
  primary: SidebarLink[];
  /** Secondary destinations, pinned above the account section. */
  secondary: SidebarLink[];
  user: AuthMenuUser | null;
  signOut: () => Promise<void>;
  /** Open (unresolved) contact messages, shown to admins only. */
  messageCount: number | null;
  brand: ReactNode;
  search: ReactNode;
};

function isActive(pathname: string, href: string) {
  return href === "/" ? pathname === "/" : pathname.startsWith(href);
}

const ROW =
  "flex w-full items-center gap-3 rounded-[var(--radius)] px-3 py-2 text-sm transition-colors";
const IDLE =
  "text-[color:var(--muted)] hover:bg-[color:var(--muted-soft)]/60 hover:text-[color:var(--foreground)]";
const ACTIVE = "bg-[color:var(--muted-soft)] font-medium text-[color:var(--foreground)]";

function NavItem({ link, pathname }: { link: SidebarLink; pathname: string }) {
  const Icon = ICONS[link.icon];
  const active = isActive(pathname, link.href);
  return (
    <li>
      <Link
        href={link.href}
        aria-current={active ? "page" : undefined}
        className={`${ROW} ${active ? ACTIVE : IDLE}`}
      >
        <Icon aria-hidden="true" size={16} className="shrink-0" />
        {link.label}
      </Link>
    </li>
  );
}

// Always-open left sidebar for large screens. Smaller screens use the top bar
// with its hamburger menu (site-nav-client.tsx).
export function SiteSidebar({
  primary,
  secondary,
  user,
  signOut,
  messageCount,
  brand,
  search,
}: Props) {
  const pathname = usePathname();

  return (
    <aside
      aria-label="Site"
      className="fixed inset-y-0 left-0 z-40 hidden w-64 flex-col border-r border-[color:var(--border)] bg-[color:var(--background)]/85 backdrop-blur lg:flex"
    >
      <div className="px-5 pb-4 pt-5">{brand}</div>
      <div className="px-3">{search}</div>

      <nav aria-label="Primary" className="mt-4 flex flex-1 flex-col overflow-y-auto px-3 pb-3">
        <ul className="space-y-0.5">
          {primary.map((link) => (
            <NavItem key={link.href} link={link} pathname={pathname} />
          ))}
        </ul>

        <ul className="mt-auto space-y-0.5 border-t border-[color:var(--border)] pt-3">
          {secondary.map((link) => (
            <NavItem key={link.href} link={link} pathname={pathname} />
          ))}
        </ul>
      </nav>

      <div className="border-t border-[color:var(--border)] p-3">
        {user ? (
          <>
            <div className="flex items-center gap-3 px-3 py-2">
              <AuthAvatar user={user} />
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-[color:var(--foreground)]">
                  {user.full_name || "Signed in"}
                </p>
                <p className="truncate text-xs text-[color:var(--muted)]">
                  {user.email}
                </p>
              </div>
            </div>
            <ul className="mt-1 space-y-0.5">
              <li>
                <Link href="/me/bookmarks" className={`${ROW} ${IDLE}`}>
                  <Bookmark aria-hidden="true" size={16} className="shrink-0" />
                  My bookmarks
                </Link>
              </li>
              <li>
                <Link href="/me/settings" className={`${ROW} ${IDLE}`}>
                  <Settings aria-hidden="true" size={16} className="shrink-0" />
                  My settings
                </Link>
              </li>
              {user.is_admin ? (
                <>
                  <li>
                    <Link href="/admin" className={`${ROW} ${IDLE}`}>
                      <Shield aria-hidden="true" size={16} className="shrink-0" />
                      Admin
                    </Link>
                  </li>
                  {messageCount ? (
                    <li>
                      <Link href="/admin/messages" className={`${ROW} ${IDLE}`}>
                        <Bell aria-hidden="true" size={16} className="shrink-0" />
                        Messages
                        <span className="ml-auto rounded-full bg-[color:var(--accent)] px-1.5 py-0.5 text-[10px] font-semibold tabular-nums text-[color:var(--background)]">
                          {messageCount}
                        </span>
                      </Link>
                    </li>
                  ) : null}
                </>
              ) : null}
              <li>
                <form action={signOut}>
                  <button type="submit" className={`${ROW} ${IDLE}`}>
                    <LogOut aria-hidden="true" size={16} className="shrink-0" />
                    Sign out
                  </button>
                </form>
              </li>
            </ul>
          </>
        ) : (
          <Link
            href={`/login?next=${encodeURIComponent(pathname || "/")}`}
            className={`${ROW} font-medium text-[color:var(--foreground)] hover:bg-[color:var(--muted-soft)]/60`}
          >
            <LogIn aria-hidden="true" size={16} className="shrink-0" />
            Sign in
          </Link>
        )}
      </div>
    </aside>
  );
}
