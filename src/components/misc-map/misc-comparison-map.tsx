"use client";

import { Download, Minus, Plus, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { WorldMap } from "@/lib/world-map";

export type BananaItem = {
  name: string;
  lds_members: number;
  lds_congregations: number;
  lds_wards: number;
  lds_branches: number;
  lds_stakes: number;
  lds_districts: number;
  lds_missions: number;
  lds_temples: number;
  lds_family_history_centers: number;
  banana_tonnes: number | null;
  hospital_beds_per_1000: number | null;
  armed_forces: number | null;
  volcanoes: number | null;
  forest_area_1000_ha: number | null;
  nuclear_reactors: number | null;
  freshwater_withdrawals: number | null;
  cereal_production_mt: number | null;
  patent_applications: number | null;
  tourist_arrivals: number | null;
};

type LdsStat = keyof Omit<BananaItem, "name" | "banana_tonnes" | "hospital_beds_per_1000" | "armed_forces" | "volcanoes" | "forest_area_1000_ha" | "nuclear_reactors" | "freshwater_withdrawals" | "cereal_production_mt" | "patent_applications" | "tourist_arrivals">;

type Metric = {
  id: LdsStat;
  label: string;
  shortLabel: string;
};

const METRICS: Metric[] = [
  { id: "lds_members",               label: "Members",               shortLabel: "Members" },
  { id: "lds_congregations",         label: "Congregations",         shortLabel: "Congregations" },
  { id: "lds_wards",                 label: "Wards",                 shortLabel: "Wards" },
  { id: "lds_branches",              label: "Branches",              shortLabel: "Branches" },
  { id: "lds_stakes",                label: "Stakes",                shortLabel: "Stakes" },
  { id: "lds_districts",             label: "Districts",             shortLabel: "Districts" },
  { id: "lds_missions",              label: "Missions",              shortLabel: "Missions" },
  { id: "lds_temples",               label: "Temples",               shortLabel: "Temples" },
  { id: "lds_family_history_centers",label: "Family history centers",shortLabel: "FHCs" },
];

type ComparisonUnit = "banana_tonnes" | "hospital_beds" | "armed_forces" | "volcanoes" | "forest" | "nuclear" | "freshwater" | "cereal" | "patents" | "tourists";

type Props = {
  map: WorldMap;
  items: BananaItem[];
  title: string;
  source: string;
  filename: string;
};

const LDS_FILL    = "#1e3a5f";
const NO_DATA_FILL = "#efece5";

function getComparisonFill(unit: ComparisonUnit): string {
  switch (unit) {
    case "banana_tonnes": return "#f5d800"; // Yellow
    case "volcanoes": return "#dc2626"; // Red
    case "armed_forces": return "#16a34a"; // Green
    case "hospital_beds": return "#ea580c"; // Orange
    case "forest": return "#059669"; // Emerald
    case "nuclear": return "#db2777"; // Pink
    case "freshwater": return "#3b82f6"; // Blue
    case "cereal": return "#ca8a04"; // Yellow-Orange
    case "patents": return "#8b5cf6"; // Violet
    case "tourists": return "#14b8a6"; // Teal
    default: return "#f5d800";
  }
}

function getComparisonTextFill(unit: ComparisonUnit): string {
  if (unit === "banana_tonnes" || unit === "cereal") return "#b5a000";
  return getComparisonFill(unit);
}

const SITE  = "latterdaystats.samuelbaird.com";
const MIN_K = 1;
const MAX_K = 40;
const SERIF = "'Roboto Slab', Georgia, 'Times New Roman', serif";

type View = { k: number; x: number; y: number };

function clampView(v: View, w: number, h: number): View {
  const k = Math.min(MAX_K, Math.max(MIN_K, v.k));
  return {
    k,
    x: Math.min(0, Math.max(w - w * k, v.x)),
    y: Math.min(0, Math.max(h - h * k, v.y)),
  };
}
function esc(s: string) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function wrap(text: string, max: number): string[] {
  const out: string[] = [];
  let line = "";
  for (const word of text.split(" ")) {
    if ((line + " " + word).trim().length > max) { out.push(line); line = word; }
    else line = (line + " " + word).trim();
  }
  if (line) out.push(line);
  return out;
}

const nf  = new Intl.NumberFormat("en-US");
const nf1 = new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 });

function getBaseValue(item: BananaItem, unit: ComparisonUnit): number | null {
  if (unit === "banana_tonnes") return item.banana_tonnes;
  if (unit === "hospital_beds") return item.hospital_beds_per_1000;
  if (unit === "armed_forces") return item.armed_forces;
  if (unit === "volcanoes") return item.volcanoes;
  if (unit === "forest") return item.forest_area_1000_ha;
  if (unit === "nuclear") return item.nuclear_reactors;
  if (unit === "freshwater") return item.freshwater_withdrawals;
  if (unit === "cereal") return item.cereal_production_mt;
  if (unit === "patents") return item.patent_applications;
  if (unit === "tourists") return item.tourist_arrivals;
  return null;
}

function comparisonValue(item: BananaItem, unit: ComparisonUnit, divisor: number): number | null {
  const val = getBaseValue(item, unit);
  if (val === null) return null;
  return val / divisor;
}

function getBaseLabel(unit: ComparisonUnit): string {
  if (unit === "banana_tonnes") return "Banana (Tonnes)";
  if (unit === "hospital_beds") return "Hospital beds (per 1k)";
  if (unit === "armed_forces") return "Armed forces personnel";
  if (unit === "volcanoes") return "Volcanoes";
  if (unit === "forest") return "Forest Area (1k ha)";
  if (unit === "nuclear") return "Nuclear Reactors";
  if (unit === "freshwater") return "Freshwater Withdrawals (Billion m³)";
  if (unit === "cereal") return "Cereal Production (MT)";
  if (unit === "patents") return "Patent Applications";
  if (unit === "tourists") return "International Tourists";
  return "";
}

function comparisonLabel(unit: ComparisonUnit, divisor: number, customUnit: string): string {
  if (customUnit.trim()) return customUnit.trim();
  const base = getBaseLabel(unit);
  return divisor !== 1 ? `${base} (÷${divisor})` : base;
}

function fillFor(item: BananaItem, metric: Metric, unit: ComparisonUnit, divisor: number): string {
  const ldsVal  = item[metric.id] as number;
  const banVal  = comparisonValue(item, unit, divisor);
  if (ldsVal === 0 && banVal === null) return NO_DATA_FILL;
  return ldsVal >= (banVal ?? 0) ? LDS_FILL : getComparisonFill(unit);
}

const pillOn  = "rounded-[var(--radius)] border border-[color:var(--accent)] bg-[color:var(--accent-soft)] px-3 py-1.5 text-sm font-medium text-[color:var(--accent)]";
const pillOff = "rounded-[var(--radius)] border border-[color:var(--border)] px-3 py-1.5 text-sm text-[color:var(--muted)] hover:border-[color:var(--accent)] hover:text-[color:var(--accent)]";
const tool    = "inline-flex h-10 w-10 items-center justify-center rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--surface)] hover:border-[color:var(--accent)] hover:text-[color:var(--accent)]";

export function MiscComparisonMap({ map, items, title, source, filename }: Props) {
  const [metric, setMetric] = useState<Metric>(METRICS[0]);
  const [unit,   setUnit]   = useState<ComparisonUnit>("banana_tonnes");
  const [view,   setView]   = useState<View>({ k: 1, x: 0, y: 0 });
  const [active, setActive] = useState<{ name: string; x: number; y: number } | null>(null);
  const [animating, setAnimating] = useState(false);

  const [normFactorStr, setNormFactorStr] = useState<string>("1");
  const [normUnitStr, setNormUnitStr] = useState<string>("");

  const divisor = parseFloat(normFactorStr) || 1;

  const svgRef   = useRef<SVGSVGElement>(null);
  const pointers = useRef(new Map<number, { x: number; y: number }>());
  const drag     = useRef<{ moved: number } | null>(null);
  const pinch    = useRef<number | null>(null);

  const itemMap = useMemo(() => new Map(items.map((i) => [i.name, i])), [items]);
  const drawn   = items.filter((i) => map.shapes[i.name]);

  const W = map.width;
  const H = map.height;

  const activeLabel = comparisonLabel(unit, divisor, normUnitStr);

  function toSvg(cx: number, cy: number) {
    const r = svgRef.current!.getBoundingClientRect();
    return { x: ((cx - r.left) / r.width) * W, y: ((cy - r.top) / r.height) * H };
  }

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    setAnimating(!reduce);
    const t = setTimeout(() => setAnimating(false), 500);
    return () => clearTimeout(t);
  }, []);

  function zoomAt(factor: number, ux: number, uy: number) {
    setView((v) => {
      const k = Math.min(MAX_K, Math.max(MIN_K, v.k * factor));
      const f = k / v.k;
      return clampView({ k, x: ux - (ux - v.x) * f, y: uy - (uy - v.y) * f }, W, H);
    });
  }

  useEffect(() => {
    const el = svgRef.current;
    if (!el) return;
    const onWheel = (e: WheelEvent) => {
      if (!e.ctrlKey && !e.metaKey) return;
      e.preventDefault();
      const { x, y } = toSvg(e.clientX, e.clientY);
      zoomAt(Math.exp(-e.deltaY * 0.01), x, y);
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function onPointerDown(e: React.PointerEvent) {
    pointers.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
    drag.current = { moved: 0 };
    if (pointers.current.size === 2) {
      const [a, b] = [...pointers.current.values()];
      pinch.current = Math.hypot(a.x - b.x, a.y - b.y);
    }
  }
  function onPointerMove(e: React.PointerEvent) {
    const prev = pointers.current.get(e.pointerId);
    if (!prev) return;
    const cur = { x: e.clientX, y: e.clientY };
    pointers.current.set(e.pointerId, cur);
    if (drag.current) drag.current.moved += Math.abs(cur.x - prev.x) + Math.abs(cur.y - prev.y);
    if (pointers.current.size === 2 && pinch.current) {
      const [a, b] = [...pointers.current.values()];
      const d = Math.hypot(a.x - b.x, a.y - b.y);
      const mid = toSvg((a.x + b.x) / 2, (a.y + b.y) / 2);
      zoomAt(d / pinch.current, mid.x, mid.y);
      pinch.current = d;
    } else if (pointers.current.size === 1 && view.k > 1) {
      const r = svgRef.current!.getBoundingClientRect();
      setView((v) => clampView({ ...v, x: v.x + ((cur.x - prev.x) / r.width) * W, y: v.y + ((cur.y - prev.y) / r.height) * H }, W, H));
    }
  }
  function onPointerUp(e: React.PointerEvent) {
    pointers.current.delete(e.pointerId);
    if (pointers.current.size < 2) pinch.current = null;
  }
  function select(name: string, e: React.MouseEvent) {
    if (drag.current && drag.current.moved > 6) return;
    const box = svgRef.current!.getBoundingClientRect();
    setActive({ name, x: e.clientX - box.left, y: e.clientY - box.top });
  }
  function hoverAt(name: string, e: React.MouseEvent) {
    if (drag.current && pointers.current.size > 0) return;
    const box = svgRef.current!.getBoundingClientRect();
    setActive({ name, x: e.clientX - box.left, y: e.clientY - box.top });
  }
  function focusOn(name: string, el: SVGElement) {
    const box = el.getBoundingClientRect();
    const svg = svgRef.current!.getBoundingClientRect();
    setActive({ name, x: box.left - svg.left + box.width / 2, y: box.top - svg.top + box.height / 2 });
  }

  function downloadPng() {
    const CW = 1080; const CH = 1350;
    const INK = "#1a1a1a"; const MUTED = "#6e6a63";
    const parts: string[] = [];
    parts.push(`<rect width="${CW}" height="${CH}" fill="#ffffff"/>`);

    const titleLines = wrap(`LDS ${metric.label} vs. ${activeLabel}`, 32);
    titleLines.forEach((l, i) =>
      parts.push(`<text x="54" y="${92 + i * 54}" font-family="${SERIF}" font-size="46" font-weight="700" fill="${INK}">${esc(l)}</text>`)
    );
    let y = 92 + (titleLines.length - 1) * 54 + 44;
    const sub = `Dark blue: LDS ${metric.label.toLowerCase()} > ${activeLabel.toLowerCase()}. Bright yellow: ${activeLabel.toLowerCase()} wins. Data from LDS Church, World Bank, FAOSTAT, and Smithsonian GVP.`;
    wrap(sub, 68).forEach((l, i) =>
      parts.push(`<text x="54" y="${y + i * 38}" font-family="${SERIF}" font-size="28" fill="${MUTED}">${esc(l)}</text>`)
    );
    y += wrap(sub, 68).length * 38 + 24;

    const cropH = view.k === 1 ? H * 0.88 : H / view.k;
    const aspect = W / view.k / cropH;
    const maxMapH = CH - y - 48 - 74 - 380;
    const mh = Math.min((CW - 80) / aspect, maxMapH);
    const mw = mh * aspect;
    const vb = `${-view.x / view.k} ${-view.y / view.k} ${W / view.k} ${cropH}`;

    const shapes = drawn.map((i) => {
      const s = map.shapes[i.name];
      const f = fillFor(i, metric, unit, divisor);
      const c = s.small ? `<circle cx="${s.cx}" cy="${s.cy}" r="${3/view.k}" fill="${f}" stroke="${INK}" stroke-width="0.5" vector-effect="non-scaling-stroke"/>` : "";
      return `<path d="${s.d}" fill="${f}" stroke="#ffffff" stroke-width="0.4" vector-effect="non-scaling-stroke"/>${c}`;
    }).join("");
    parts.push(`<svg x="${(CW-mw)/2}" y="${y}" width="${mw}" height="${mh}" viewBox="${vb}" preserveAspectRatio="xMidYMid meet"><path d="${map.land}" fill="${NO_DATA_FILL}" stroke="#ffffff" stroke-width="0.4" vector-effect="non-scaling-stroke"/>${shapes}</svg>`);
    y += mh + 34;

    [{ fill: LDS_FILL, label: `More LDS ${metric.label.toLowerCase()}` }, { fill: getComparisonFill(unit), label: `More ${activeLabel.toLowerCase()}` }, { fill: NO_DATA_FILL, label: "No data" }].forEach((sw, idx) => {
      const currentY = y + idx * 36;
      parts.push(`<rect x="54" y="${currentY}" width="36" height="28" fill="${sw.fill}" stroke="#d9d5cc"/>`);
      parts.push(`<text x="100" y="${currentY + 23}" font-family="${SERIF}" font-size="26" fill="${INK}">${esc(sw.label)}</text>`);
    });
    
    const topLds = [...items].filter(i => (i[metric.id] as number) > 0).sort((a,b) => (b[metric.id] as number) - (a[metric.id] as number)).slice(0, 5);
    const topBanana = [...items].filter(i => comparisonValue(i, unit, divisor) !== null).sort((a,b) => (comparisonValue(b, unit, divisor)!) - (comparisonValue(a, unit, divisor)!)).slice(0, 5);

    const col2X = CW / 2 + 30;
    
    parts.push(`<text x="54" y="${y + 160}" font-family="${SERIF}" font-size="26" font-weight="700" fill="${INK}">Top 5: LDS ${metric.shortLabel}</text>`);
    parts.push(`<text x="${col2X}" y="${y + 160}" font-family="${SERIF}" font-size="26" font-weight="700" fill="${INK}">Top 5: ${activeLabel}</text>`);
    
    for (let i = 0; i < 5; i++) {
      const ldsItem = topLds[i];
      const banItem = topBanana[i];
      const rowY = y + 160 + 34 + i * 32;
      
      if (ldsItem) {
        parts.push(`<text x="54" y="${rowY}" font-family="${SERIF}" font-size="24" fill="${INK}">${i+1}. ${esc(ldsItem.name)}</text>`);
        parts.push(`<text x="${CW/2 - 30}" y="${rowY}" text-anchor="end" font-family="${SERIF}" font-size="24" font-weight="700" fill="${INK}">${nf.format(ldsItem[metric.id] as number)}</text>`);
      }
      if (banItem) {
        parts.push(`<text x="${col2X}" y="${rowY}" font-family="${SERIF}" font-size="24" fill="${INK}">${i+1}. ${esc(banItem.name)}</text>`);
        parts.push(`<text x="${CW - 54}" y="${rowY}" text-anchor="end" font-family="${SERIF}" font-size="24" font-weight="700" fill="${INK}">${nf1.format(comparisonValue(banItem, unit, divisor)!)}</text>`);
      }
    }
    
    y += 160 + 34 + 5 * 32 + 40;

    parts.push(
      `<line x1="54" x2="${CW-54}" y1="${CH-74}" y2="${CH-74}" stroke="#d9d5cc"/>`,
      `<text x="54" y="${CH-40}" font-family="${SERIF}" font-size="21" font-weight="700" fill="${INK}">${esc(SITE)} | ${esc(source)}</text>`,
    );

    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${CW}" height="${CH}" viewBox="0 0 ${CW} ${CH}">${parts.join("")}</svg>`;
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = CW; canvas.height = CH;
      const ctx = canvas.getContext("2d")!;
      ctx.fillStyle = "#ffffff"; ctx.fillRect(0, 0, CW, CH);
      ctx.drawImage(img, 0, 0);
      canvas.toBlob((blob) => {
        if (!blob) return;
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        const shortId = metric.id.replace("lds_", "").replace(/_/g, "-");
        a.download = `lds-${shortId}-vs-${unit}.png`;
        a.click();
        setTimeout(() => URL.revokeObjectURL(url), 2000);
      }, "image/png");
    };
    img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
  }

  function Tooltip({ name }: { name: string }) {
    const item = itemMap.get(name);
    if (!item) return (
      <>
        <p className="serif text-sm font-semibold">{name}</p>
        <p className="mt-1 text-xs text-[color:var(--muted)]">No data for this country.</p>
      </>
    );
    const ldsVal = item[metric.id] as number;
    const banVal = comparisonValue(item, unit, divisor);
    const ldsWins = ldsVal >= (banVal ?? 0);
    const winner = (ldsVal === 0 && banVal === null) ? "none"
      : ldsWins ? "lds" : "banana";

    return (
      <>
        <p className="serif text-sm font-semibold">{name}</p>
        <p className="mt-1 text-xs font-medium" style={{ color: winner === "lds" ? LDS_FILL : winner === "banana" ? getComparisonTextFill(unit) : "var(--muted)" }}>
          {winner === "none" ? "No data" : winner === "lds" ? `More LDS ${metric.label.toLowerCase()}` : `More ${activeLabel.toLowerCase()}`}
        </p>
        <dl className="mt-2 grid grid-cols-[1fr_auto] gap-x-3 gap-y-0.5 text-xs tabular-nums text-[color:var(--muted)]">
          <dt>LDS {metric.label.toLowerCase()}</dt>
          <dd className="text-right text-[color:var(--foreground)]">{nf.format(ldsVal)}</dd>
          <dt>{activeLabel}</dt>
          <dd className="text-right text-[color:var(--foreground)]">{banVal !== null ? nf1.format(banVal) : "—"}</dd>
          
          <dt className="col-span-2 mt-2 border-t border-[color:var(--border)] pt-2 font-medium text-[color:var(--foreground)]">All LDS stats</dt>
          {(["lds_members","lds_congregations","lds_wards","lds_branches","lds_stakes","lds_districts","lds_missions","lds_temples","lds_family_history_centers"] as LdsStat[]).map((k) => {
            const label = METRICS.find((m) => m.id === k)?.label ?? k;
            const val = item[k] as number;
            if (val === 0) return null;
            return (
              <div key={k} className="col-span-2 grid grid-cols-[1fr_auto] gap-x-3">
                <dt>{label}</dt>
                <dd className="text-right text-[color:var(--foreground)]">{nf.format(val)}</dd>
              </div>
            );
          })}
        </dl>
      </>
    );
  }

  const activeItem = active ? itemMap.get(active.name) : null;

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-4">
          <div>
            <p className="small-caps mb-1.5 text-[11px] font-medium text-[color:var(--muted)]">LDS stat to compare</p>
            <div className="flex flex-wrap gap-1.5">
              {METRICS.map((m) => (
                <button key={m.id} type="button" className={metric.id === m.id ? pillOn : pillOff} onClick={() => setMetric(m)}>
                  {m.shortLabel}
                </button>
              ))}
            </div>
          </div>
          <div>
            <p className="small-caps mb-1.5 text-[11px] font-medium text-[color:var(--muted)]">World stat to compare</p>
            <div className="flex flex-wrap gap-1.5">
              <button type="button" className={unit === "banana_tonnes" ? pillOn : pillOff} onClick={() => setUnit("banana_tonnes")}>
                Banana (Tonnes)
              </button>
              <button type="button" className={unit === "armed_forces" ? pillOn : pillOff} onClick={() => setUnit("armed_forces")}>
                Armed Forces Personnel
              </button>
              <button type="button" className={unit === "hospital_beds" ? pillOn : pillOff} onClick={() => setUnit("hospital_beds")}>
                Hospital Beds (per 1k)
              </button>
              <button type="button" className={unit === "volcanoes" ? pillOn : pillOff} onClick={() => setUnit("volcanoes")}>
                Volcanoes
              </button>
              <button type="button" className={unit === "forest" ? pillOn : pillOff} onClick={() => setUnit("forest")}>
                Forest Area (1k ha)
              </button>
              <button type="button" className={unit === "nuclear" ? pillOn : pillOff} onClick={() => setUnit("nuclear")}>
                Nuclear Reactors
              </button>
              <button type="button" className={unit === "freshwater" ? pillOn : pillOff} onClick={() => setUnit("freshwater")}>
                Freshwater (Billion m³)
              </button>
              <button type="button" className={unit === "cereal" ? pillOn : pillOff} onClick={() => setUnit("cereal")}>
                Cereal (MT)
              </button>
              <button type="button" className={unit === "patents" ? pillOn : pillOff} onClick={() => setUnit("patents")}>
                Patents
              </button>
              <button type="button" className={unit === "tourists" ? pillOn : pillOff} onClick={() => setUnit("tourists")}>
                Tourists
              </button>
            </div>
          </div>
          <div className="flex flex-col gap-1.5 pt-1">
            <p className="small-caps text-[11px] font-medium text-[color:var(--muted)]">Normalize data (optional)</p>
            <div className="flex items-center gap-2">
              <label className="flex items-center gap-1.5 text-sm text-[color:var(--muted)]">
                Divide by
                <input
                  type="number"
                  className="w-20 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--surface)] px-2 py-1 text-sm text-[color:var(--foreground)] placeholder:text-[color:var(--muted)]"
                  placeholder="1"
                  value={normFactorStr}
                  onChange={(e) => setNormFactorStr(e.target.value)}
                />
              </label>
              <label className="flex items-center gap-1.5 text-sm text-[color:var(--muted)]">
                Custom Unit
                <input
                  type="text"
                  className="w-32 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--surface)] px-2 py-1 text-sm text-[color:var(--foreground)] placeholder:text-[color:var(--muted)]"
                  placeholder="e.g. truckloads"
                  value={normUnitStr}
                  onChange={(e) => setNormUnitStr(e.target.value)}
                />
              </label>
              {(normFactorStr !== "1" || normUnitStr) && (
                <button
                  type="button"
                  className="text-xs text-[color:var(--accent)] hover:underline ml-2"
                  onClick={() => {
                    setNormFactorStr("1");
                    setNormUnitStr("");
                  }}
                >
                  Clear
                </button>
              )}
            </div>
          </div>
        </div>
        <button
          type="button"
          onClick={downloadPng}
          className="inline-flex h-10 items-center gap-2 rounded-[var(--radius)] border border-[color:var(--border)] px-3 text-sm hover:border-[color:var(--accent)] hover:text-[color:var(--accent)]"
        >
          <Download aria-hidden="true" size={15} /> Save PNG
        </button>
      </div>

      <p className="mt-4 text-sm text-[color:var(--muted)]">
        <span className="font-medium text-[color:var(--foreground)]">{metric.label}</span> vs.{" "}
        <span className="font-medium text-[color:var(--foreground)]">{activeLabel}</span> — dark blue means the country has more LDS {metric.label.toLowerCase()}; bright yellow means {activeLabel.toLowerCase()} wins.
      </p>

      <div className="relative mt-4 overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)]">
        <svg
          ref={svgRef}
          viewBox={`0 0 ${W} ${H}`}
          className="block w-full select-none bg-[color:var(--surface)]"
          style={{ touchAction: view.k > 1 ? "none" : "pan-y" }}
          role="group"
          aria-label={`${title}: ${metric.label} vs. ${activeLabel}`}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerCancel={onPointerUp}
          onPointerLeave={() => setActive((a) => (a && pointers.current.size === 0 ? null : a))}
          onDoubleClick={(e) => { const { x, y } = toSvg(e.clientX, e.clientY); zoomAt(2, x, y); }}
        >
          <g style={{ transform: `translate(${view.x}px,${view.y}px) scale(${view.k})`, transformOrigin: "0 0", transition: animating ? "transform 450ms ease" : "none" }}>
            <path d={map.land} fill={NO_DATA_FILL} stroke="var(--surface)" strokeWidth="0.4" vectorEffect="non-scaling-stroke" />
            {drawn.map((i) => {
              const s = map.shapes[i.name];
              const f = fillFor(i, metric, unit, divisor);
              const ldsVal = i[metric.id] as number;
              const banVal = comparisonValue(i, unit, divisor);
              const ldsWins = ldsVal >= (banVal ?? 0);
              const ariaLabel = `${i.name}: ${ldsWins ? nf.format(ldsVal) + " LDS " + metric.label.toLowerCase() : nf1.format(banVal ?? 0) + " " + activeLabel}`;
              return (
                <g key={i.name}>
                  <path
                    d={s.d}
                    fill={f}
                    stroke="var(--surface)"
                    strokeWidth="0.4"
                    vectorEffect="non-scaling-stroke"
                    tabIndex={0}
                    aria-label={ariaLabel}
                    className="cursor-pointer outline-none focus-visible:stroke-[color:var(--foreground)]"
                    onMouseMove={(e) => hoverAt(i.name, e)}
                    onClick={(e) => select(i.name, e)}
                    onFocus={(e) => focusOn(i.name, e.currentTarget)}
                    onBlur={() => setActive(null)}
                  />
                  {s.small && (
                    <circle cx={s.cx} cy={s.cy} r={3/view.k} fill={f} stroke="var(--foreground)" strokeWidth="0.5" vectorEffect="non-scaling-stroke"
                      className="cursor-pointer"
                      onMouseMove={(e) => hoverAt(i.name, e)}
                      onClick={(e) => select(i.name, e)}
                    />
                  )}
                </g>
              );
            })}
          </g>
        </svg>

        <div className="absolute right-2 top-2 flex flex-col gap-1.5">
          <button type="button" className={tool} aria-label="Zoom in"  onClick={() => zoomAt(1.6, W/2, H/2)}><Plus  aria-hidden="true" size={16}/></button>
          <button type="button" className={tool} aria-label="Zoom out" onClick={() => zoomAt(1/1.6, W/2, H/2)}><Minus aria-hidden="true" size={16}/></button>
          <button type="button" className={tool} aria-label="Reset zoom" onClick={() => setView({ k:1, x:0, y:0 })}><RotateCcw aria-hidden="true" size={15}/></button>
        </div>

        {active && (
          <div
            role="status"
            className="pointer-events-none absolute z-10 hidden w-64 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--surface)] p-3 text-sm md:block"
            style={{ left: `min(${active.x + 14}px, calc(100% - 17rem))`, top: Math.min(active.y + 14, 9999) }}
          >
            <Tooltip name={active.name} />
          </div>
        )}
      </div>

      <div className="mt-3 min-h-[4rem] rounded-[var(--radius)] border border-[color:var(--border)] p-3 text-sm md:hidden">
        {activeItem ? <Tooltip name={activeItem.name} /> : (
          <span className="text-[color:var(--muted)]">Tap a country for details.</span>
        )}
      </div>

      <p className="small-caps mt-5 text-xs font-medium text-[color:var(--muted)]">Key</p>
      <div className="mt-2 flex flex-wrap items-center gap-x-5 gap-y-2.5 text-sm">
        <Swatch fill={LDS_FILL}    label={`More LDS ${metric.label.toLowerCase()}`} />
        <Swatch fill={getComparisonFill(unit)} label={`More ${activeLabel.toLowerCase()}`} />
        <Swatch fill={NO_DATA_FILL} label="No data" />
      </div>

      <span className="sr-only" aria-live="polite">
        {activeItem ? `${activeItem.name}: ${nf.format(activeItem[metric.id] as number)} LDS ${metric.label.toLowerCase()}, ${comparisonValue(activeItem, unit, divisor) !== null ? nf1.format(comparisonValue(activeItem, unit, divisor)!) + " " + activeLabel : "no comparison data"}` : ""}
      </span>
    </div>
  );
}

function Swatch({ fill, label }: { fill: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-2 text-[color:var(--foreground)]">
      <span className="inline-block h-5 w-7 shrink-0 border border-[color:var(--border)]" style={{ background: fill }} aria-hidden="true" />
      {label}
    </span>
  );
}
