import { requireUser } from "@/lib/auth";
import { MeTabs } from "@/components/me-tabs";

export default async function MeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  await requireUser();

  return (
    <div className="mx-auto max-w-6xl px-5 py-10 sm:px-8">
      <MeTabs />
      {children}
    </div>
  );
}
