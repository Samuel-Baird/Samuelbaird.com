import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  BookOpen,
  Globe2,
  Sparkles,
  Users,
  type LucideIcon,
} from "lucide-react";

export type HomeFeature = {
  href: string;
  title: string;
  description: string;
  /** The live number or preview line shown at the foot of the card. */
  figure: string;
  icon: HomeFeatureIcon;
};

export type HomeFeatureIcon =
  | "channels"
  | "studies"
  | "data"
  | "map"
  | "ai";

const ICONS: Record<HomeFeatureIcon, LucideIcon> = {
  channels: Users,
  studies: BookOpen,
  data: BarChart3,
  map: Globe2,
  ai: Sparkles,
};

export function HomeFeatureGrid({ features }: { features: HomeFeature[] }) {
  return (
    <section aria-labelledby="home-features" className="mt-16">
      <h2
        id="home-features"
        className="serif text-2xl font-semibold tracking-tight sm:text-3xl"
      >
        What&apos;s here
      </h2>
      <ul className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((f) => {
          const Icon = ICONS[f.icon];
          return (
            <li key={f.href}>
              <Link
                href={f.href}
                className="group flex h-full flex-col rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5 transition-colors hover:border-[color:var(--accent)]"
              >
                <div className="flex items-center gap-2.5 text-[color:var(--honey)]">
                  <Icon aria-hidden="true" size={18} />
                  <h3 className="serif text-lg font-semibold tracking-tight text-[color:var(--foreground)] group-hover:text-[color:var(--accent)]">
                    {f.title}
                  </h3>
                </div>
                <p className="mt-3 flex-1 text-sm leading-relaxed text-[color:var(--muted)]">
                  {f.description}
                </p>
                <div className="mt-4 flex items-center justify-between gap-3 border-t border-[color:var(--border)] pt-3">
                  <span className="small-caps text-xs font-medium tabular-nums text-[color:var(--foreground)]">
                    {f.figure}
                  </span>
                  <span className="inline-flex items-center gap-1 text-xs font-medium text-[color:var(--accent)]">
                    Open
                    <ArrowRight aria-hidden="true" size={13} />
                  </span>
                </div>
              </Link>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
