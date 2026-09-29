"use client";

import { Download, Minus, Plus, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { WorldMap } from "@/lib/world-map";
import { NO_DATA_FILL, ZERO_FILL, classify } from "./classes";

export type MapItem = { name: string; value: number | null };

type Props = {
  map: WorldMap;
  items: MapItem[];
  format: (v: number) => string;
  /** Shown above the map and on the PNG. */
  title: string;
  /** One or two plain sentences saying exactly what the shading means. */
  subtitle: string;
  /** Short source line for the PNG footer, e.g. "Church facts and statistics, 2025". */
  source: string;
  filename: string;
  tooltip: (name: string) => React.ReactNode;
  /** Label for the ranked list on the PNG. */
  rankTitle?: string;
};

const SITE = "latterdaystats.samuelbaird.com";
const MIN_K = 1;
const MAX_K = 12;
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
    if ((line + " " + word).trim().length > max) {
      out.push(line);
      line = word;
    } else line = (line + " " + word).trim();
  }
  if (line) out.push(line);
  return out;
}

export function ChoroplethMap({
  map,
  items,
  format,
  title,
  subtitle,
  source,
  filename,
  tooltip,
  rankTitle = "Highest",
}: Props) {
  const [view, setView] = useState<View>({ k: 1, x: 0, y: 0 });
  const [active, setActive] = useState<{ name: string; x: number; y: number } | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const pointers = useRef(new Map<number, { x: number; y: number }>());
  const drag = useRef<{ moved: number } | null>(null);
  const pinch = useRef<number | null>(null);

  const values = useMemo(() => new Map(items.map((i) => [i.name, i.value])), [items]);
  const classing = useMemo(() => classify(items.map((i) => i.value)), [items]);
  const drawn = items.filter((i) => map.shapes[i.name]);
  const ranked = useMemo(
    () =>
      items
        .filter((i): i is { name: string; value: number } => i.value !== null && i.value > 0)
        .sort((a, b) => b.value - a.value),
    [items],
  );

  const W = map.width;
  const H = map.height;

  /** Client pixels -> SVG user units. */
  function toSvg(cx: number, cy: number) {
    const r = svgRef.current!.getBoundingClientRect();
    return { x: ((cx - r.left) / r.width) * W, y: ((cy - r.top) / r.height) * H };
  }

  function zoomAt(factor: number, ux: number, uy: number) {
    setView((v) => {
      const k = Math.min(MAX_K, Math.max(MIN_K, v.k * factor));
      const f = k / v.k;
      return clampView({ k, x: ux - (ux - v.x) * f, y: uy - (uy - v.y) * f }, W, H);
    });
  }

  // Ctrl/⌘ + wheel (also how trackpad pinch arrives) zooms; plain wheel keeps
  // scrolling the page. Needs a non-passive listener to cancel the default.
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
      const dx = ((cur.x - prev.x) / r.width) * W;
      const dy = ((cur.y - prev.y) / r.height) * H;
      setView((v) => clampView({ ...v, x: v.x + dx, y: v.y + dy }, W, H));
    }
  }

  function onPointerUp(e: React.PointerEvent) {
    pointers.current.delete(e.pointerId);
    if (pointers.current.size < 2) pinch.current = null;
  }

  /** A tap/click selects; a drag doesn't. */
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
    const CW = 1080;
    const CH = 1350;
    const INK = "#1a1a1a";
    const MUTED = "#6e6a63";
    const parts: string[] = [];
    parts.push(`<rect width="${CW}" height="${CH}" fill="#ffffff"/>`);

    const titleLines = wrap(title, 34);
    titleLines.forEach((l, i) =>
      parts.push(
        `<text x="54" y="${92 + i * 54}" font-family="${SERIF}" font-size="46" font-weight="700" fill="${INK}">${esc(l)}</text>`,
      ),
    );
    let y = 92 + (titleLines.length - 1) * 54 + 44;
    wrap(subtitle, 68).forEach((l, i) =>
      parts.push(
        `<text x="54" y="${y + i * 32}" font-family="${SERIF}" font-size="24" fill="${MUTED}">${esc(l)}</text>`,
      ),
    );
    y += wrap(subtitle, 68).length * 32 + 24;

    // The map, as currently zoomed.
    const mw = CW - 80;
    const mh = (mw * H) / W;
    const vb = `${-view.x / view.k} ${-view.y / view.k} ${W / view.k} ${H / view.k}`;
    const shapes = drawn
      .map((i) => {
        const s = map.shapes[i.name];
        const f = classing.fillFor(i.value);
        const circle = s.small
          ? `<circle cx="${s.cx}" cy="${s.cy}" r="${3 / view.k}" fill="${f}" stroke="${INK}" stroke-width="0.5" vector-effect="non-scaling-stroke"/>`
          : "";
        return `<path d="${s.d}" fill="${f}" stroke="#ffffff" stroke-width="0.4" vector-effect="non-scaling-stroke"/>${circle}`;
      })
      .join("");
    parts.push(
      `<svg x="40" y="${y}" width="${mw}" height="${mh}" viewBox="${vb}" preserveAspectRatio="xMidYMid meet">` +
        `<path d="${map.land}" fill="${NO_DATA_FILL}" stroke="#ffffff" stroke-width="0.4" vector-effect="non-scaling-stroke"/>${shapes}</svg>`,
    );
    y += mh + 34;

    // Legend, one row of swatches.
    const swatches: { fill: string; label: string }[] = [];
    if (classing.hasZero) swatches.push({ fill: ZERO_FILL, label: "0" });
    classing.classes.forEach((c) =>
      swatches.push({ fill: c.fill, label: c.min === c.max ? format(c.min) : `${format(c.min)}–${format(c.max)}` }),
    );
    swatches.push({ fill: NO_DATA_FILL, label: "No data" });
    const slot = (CW - 108) / swatches.length;
    swatches.forEach((s, i) => {
      const x = 54 + i * slot;
      parts.push(`<rect x="${x}" y="${y}" width="28" height="20" fill="${s.fill}" stroke="#d9d5cc"/>`);
      parts.push(
        `<text x="${x + 36}" y="${y + 16}" font-family="${SERIF}" font-size="16" fill="${INK}">${esc(s.label)}</text>`,
      );
    });
    y += 74;

    // Ranked list fills the space below the map and gives exact numbers.
    parts.push(
      `<text x="54" y="${y}" font-family="${SERIF}" font-size="26" font-weight="700" fill="${INK}">${esc(rankTitle)}</text>`,
    );
    y += 20;
    const top = ranked.slice(0, 10);
    const colW = (CW - 108) / 2;
    top.forEach((r, i) => {
      const col = Math.floor(i / 5);
      const row = i % 5;
      const x = 54 + col * colW;
      const yy = y + 40 + row * 46;
      parts.push(
        `<text x="${x}" y="${yy}" font-family="${SERIF}" font-size="24" fill="${INK}">${i + 1}. ${esc(r.name)}</text>`,
      );
      parts.push(
        `<text x="${x + colW - 40}" y="${yy}" text-anchor="end" font-family="${SERIF}" font-size="24" font-weight="700" fill="${INK}">${esc(format(r.value))}</text>`,
      );
    });

    parts.push(
      `<line x1="54" x2="${CW - 54}" y1="${CH - 74}" y2="${CH - 74}" stroke="#d9d5cc"/>`,
      `<text x="54" y="${CH - 40}" font-family="${SERIF}" font-size="21" font-weight="700" fill="${INK}">${esc(SITE)} | data: ${esc(source)}</text>`,
    );

    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${CW}" height="${CH}" viewBox="0 0 ${CW} ${CH}">${parts.join("")}</svg>`;
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = CW;
      canvas.height = CH;
      const ctx = canvas.getContext("2d")!;
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, CW, CH);
      ctx.drawImage(img, 0, 0);
      canvas.toBlob((blob) => {
        if (!blob) return;
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${filename}.png`;
        a.click();
        // Some browsers start the download asynchronously.
        setTimeout(() => URL.revokeObjectURL(url), 2000);
      }, "image/png");
    };
    img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
  }

  const tool =
    "inline-flex h-10 w-10 items-center justify-center rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--surface)] hover:border-[color:var(--accent)] hover:text-[color:var(--accent)]";
  const activeValue = active ? values.get(active.name) : null;

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="serif text-lg font-semibold">{title}</p>
          <p className="mt-1 max-w-2xl text-sm text-[color:var(--muted)]">{subtitle}</p>
        </div>
        <button
          type="button"
          onClick={downloadPng}
          className="inline-flex h-10 items-center gap-2 rounded-[var(--radius)] border border-[color:var(--border)] px-3 text-sm hover:border-[color:var(--accent)] hover:text-[color:var(--accent)]"
        >
          <Download aria-hidden="true" size={15} /> Save PNG
        </button>
      </div>

      <div className="relative mt-4 overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)]">
        <svg
          ref={svgRef}
          viewBox={`0 0 ${W} ${H}`}
          className="block w-full select-none bg-[color:var(--surface)]"
          style={{ touchAction: view.k > 1 ? "none" : "pan-y" }}
          role="group"
          aria-label={title}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerCancel={onPointerUp}
          onPointerLeave={() => setActive((a) => (a && pointers.current.size === 0 ? null : a))}
          onDoubleClick={(e) => {
            const { x, y } = toSvg(e.clientX, e.clientY);
            zoomAt(2, x, y);
          }}
        >
          <g transform={`translate(${view.x} ${view.y}) scale(${view.k})`}>
            <path d={map.land} fill={NO_DATA_FILL} stroke="var(--surface)" strokeWidth="0.4" vectorEffect="non-scaling-stroke" />
            {drawn.map((i) => {
              const s = map.shapes[i.name];
              const f = classing.fillFor(i.value);
              return (
                <g key={i.name}>
                  <path
                    d={s.d}
                    fill={f}
                    stroke="var(--surface)"
                    strokeWidth="0.4"
                    vectorEffect="non-scaling-stroke"
                    tabIndex={0}
                    aria-label={`${i.name}: ${i.value === null ? "no data" : format(i.value)}`}
                    className="cursor-pointer outline-none focus-visible:stroke-[color:var(--foreground)]"
                    onMouseMove={(e) => hoverAt(i.name, e)}
                    onClick={(e) => select(i.name, e)}
                    onFocus={(e) => focusOn(i.name, e.currentTarget)}
                    onBlur={() => setActive(null)}
                  />
                  {s.small ? (
                    <circle
                      cx={s.cx}
                      cy={s.cy}
                      r={3 / view.k}
                      fill={f}
                      stroke="var(--foreground)"
                      strokeWidth="0.5"
                      vectorEffect="non-scaling-stroke"
                      className="cursor-pointer"
                      onMouseMove={(e) => hoverAt(i.name, e)}
                      onClick={(e) => select(i.name, e)}
                    />
                  ) : null}
                </g>
              );
            })}
          </g>
        </svg>

        <div className="absolute right-2 top-2 flex flex-col gap-1.5">
          <button type="button" className={tool} aria-label="Zoom in" onClick={() => zoomAt(1.6, W / 2, H / 2)}>
            <Plus aria-hidden="true" size={16} />
          </button>
          <button type="button" className={tool} aria-label="Zoom out" onClick={() => zoomAt(1 / 1.6, W / 2, H / 2)}>
            <Minus aria-hidden="true" size={16} />
          </button>
          <button
            type="button"
            className={tool}
            aria-label="Reset zoom"
            onClick={() => setView({ k: 1, x: 0, y: 0 })}
          >
            <RotateCcw aria-hidden="true" size={15} />
          </button>
        </div>

        {active ? (
          <div
            role="status"
            className="pointer-events-none absolute z-10 hidden w-60 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--surface)] p-3 text-xs md:block"
            style={{ left: `min(${active.x + 14}px, calc(100% - 15rem))`, top: Math.min(active.y + 14, 9999) }}
          >
            {tooltip(active.name)}
          </div>
        ) : null}
      </div>

      {/* Phones: the selected country shows under the map instead of floating over it. */}
      <div className="mt-3 min-h-[3rem] rounded-[var(--radius)] border border-[color:var(--border)] p-3 text-xs md:hidden">
        {active ? (
          tooltip(active.name)
        ) : (
          <span className="text-[color:var(--muted)]">Tap a country for details. Use + to zoom, then drag.</span>
        )}
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs">
        {classing.hasZero ? <Swatch fill={ZERO_FILL} label="0" /> : null}
        {classing.classes.map((c) => (
          <Swatch
            key={c.fill}
            fill={c.fill}
            label={c.min === c.max ? format(c.min) : `${format(c.min)}–${format(c.max)}`}
          />
        ))}
        <Swatch fill={NO_DATA_FILL} label="No data" />
      </div>
      <p className="mt-2 text-xs text-[color:var(--muted)]">
        Countries are grouped into equal-sized bands from lowest to highest. Ctrl + scroll or pinch to
        zoom, then drag to move.
      </p>
      <span className="sr-only" aria-live="polite">
        {active ? `${active.name}: ${activeValue == null ? "no data" : format(activeValue)}` : ""}
      </span>
    </div>
  );
}

function Swatch({ fill, label }: { fill: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 tabular-nums text-[color:var(--muted)]">
      <span
        className="inline-block h-3.5 w-5 border border-[color:var(--border)]"
        style={{ background: fill }}
        aria-hidden="true"
      />
      {label}
    </span>
  );
}
