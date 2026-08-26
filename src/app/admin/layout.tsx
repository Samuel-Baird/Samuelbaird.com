import Link from "next/link";
import { requireAdmin } from "@/lib/auth";

const links = [
  { href: "/admin", label: "Dashboard" },
  { href: "/admin/analytics", label: "Analytics" },
  { href: "/admin/quizzes", label: "Quizzes" },
  { href: "/admin/channels", label: "Channels" },
  { href: "/admin/studies", label: "Studies" },
  { href: "/admin/access", label: "Access & Roles" },
  { href: "/admin/messages", label: "Messages" },
  { href: "/admin/refresh", label: "Refresh stats" },
];

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  await requireAdmin();

  return (
    <div className="mx-auto grid max-w-6xl gap-8 px-5 py-10 sm:px-8 md:grid-cols-[220px_1fr]">
      <aside className="md:sticky md:top-24 md:self-start">
        <nav className="flex gap-2 overflow-x-auto border-b border-[color:var(--border)] pb-3 md:flex-col md:border-b-0 md:pb-0">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="whitespace-nowrap rounded-md px-3 py-2 text-sm text-[color:var(--muted)] hover:bg-[color:var(--muted-soft)] hover:text-[color:var(--foreground)]"
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </aside>
      <section>{children}</section>
    </div>
  );
}
