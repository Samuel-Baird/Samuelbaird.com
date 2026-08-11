import type { Metadata } from "next";
import Link from "next/link";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";

export const metadata: Metadata = {
  title: "Not Found",
  description: "No page, record, chart, or other inhabitant at this address.",
};

const ROWS: { label: string; value: number }[] = [
  { label: "Pages", value: 0 },
  { label: "Records", value: 0 },
  { label: "Charts", value: 0 },
  { label: "Inhabitants", value: 0 },
];

export default function NotFound() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
      <div className="mx-auto max-w-2xl">
        <div className="text-center">
          <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
            Deseret Census
          </p>
          <h1 className="serif mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
            <DeseretTitle text="Enumeration of Internet Settlements" />
          </h1>
        </div>

        <div className="dinkus mt-8 mb-0 text-xs">
          <BeehiveMark className="h-3.5 w-3.5" />
        </div>

        <div className="mt-2 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-6 sm:p-10">
          <div className="grid gap-6 border-b border-[color:var(--border)] pb-6 sm:grid-cols-2">
            <Field label="District" value="Latter-day Stats" />
            <Field label="Page" value="404" />
          </div>

          <table className="mt-6 w-full text-sm">
            <thead>
              <tr className="small-caps border-b border-[color:var(--border)] text-left text-xs text-[color:var(--muted)]">
                <th className="py-2 font-medium">Enumerated</th>
                <th className="py-2 text-right font-medium">Count</th>
              </tr>
            </thead>
            <tbody>
              {ROWS.map((row) => (
                <tr
                  key={row.label}
                  className="border-b border-dashed border-[color:var(--border)]"
                >
                  <td className="py-2.5">{row.label}</td>
                  <td className="serif-onum py-2.5 text-right tabular-nums">
                    {row.value}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="border-t-2 border-[color:var(--foreground)]">
                <td className="serif pt-3 font-semibold">Total Population</td>
                <td className="serif-onum pt-3 text-right font-semibold tabular-nums">
                  0
                </td>
              </tr>
            </tfoot>
          </table>

          <div className="mt-8 border-t border-[color:var(--border)] pt-6">
            <p className="small-caps text-xs font-medium text-[color:var(--muted)]">
              Enumerator&rsquo;s Remarks
            </p>
            <p className="serif mt-2 -rotate-1 leading-relaxed text-[color:var(--foreground)] italic">
              No page, record, chart, table, or other inhabitant could be
              located at this address.
            </p>
          </div>

          <div className="mt-10 flex justify-center">
            <div
              className="-rotate-3 select-none rounded-[var(--radius)] border-4 border-double border-[color:var(--oxblood)] px-8 py-4 text-center text-[color:var(--oxblood)]"
              role="img"
              aria-label="Stamp: Not Found"
            >
              <div
                aria-hidden="true"
                className="text-2xl leading-none tracking-wide"
                style={{ fontFamily: "var(--font-deseret), sans-serif" }}
              >
                𐐤𐐉𐐓 𐐙𐐀𐐊𐐤𐐔
              </div>
              <div className="small-caps mt-2 text-lg font-bold tracking-[0.2em]">
                Not Found
              </div>
            </div>
          </div>
        </div>

        <div className="mt-10 text-center">
          <Link
            href="/"
            className="small-caps inline-flex h-11 items-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-6 text-sm font-medium tracking-wide transition-colors hover:bg-[color:var(--muted-soft)]"
          >
            Return to the General Census
          </Link>
        </div>
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="small-caps text-[11px] font-medium text-[color:var(--muted)]">
        {label}
      </p>
      <p className="serif mt-1 border-b border-dashed border-[color:var(--border)] pb-1 text-lg font-medium tracking-tight">
        {value}
      </p>
    </div>
  );
}
