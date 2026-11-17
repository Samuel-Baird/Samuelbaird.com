// The land below the sky: bands of engraved country down the page (a farm, a settlement, a lake,
// open hills), each in three depths that scroll at different rates for parallax. Life goes on in
// the nearest depth on the engraving's clock (clock.js):
//   by day   tumbleweeds, bees at the farm's skep, now and then a cricket and the gull that takes it;
//   by night lamplit windows, crops growing back.
// Every one to three days the crickets swarm the farm's wheat, as they did in the valley in 1848.
// A flock of gulls comes down on them; a gull that has eaten two or three flies to a ditch or the
// creek, drinks, and brings up the hard parts as a pellet, then goes back for more.
import { sunPhase, dayIndex, swarmDay, swarmAt } from './clock.js';
import { onSmoothScroll, smoothY } from './smooth.js';

const land = document.getElementById('land');
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const NS = 'http://www.w3.org/2000/svg';
const rand = (a, b) => a + Math.random() * (b - a);
const pick = (a) => a[Math.floor(Math.random() * a.length)];
const n1 = (n) => +n.toFixed(1);
const PAPER = '#16161A';
const SPEED = reduced ? { far: 1, mid: 1, near: 1 } : { far: 0.36, mid: 0.56, near: 0.8 };
const EXTRA = 160; // the ground's fill runs on below each band and fades out

let W = 0, H = 0, BH = 0, GY = 0, bands = [], uid = 0;

/* ---------- drawing helpers (engraver's strokes as path data) ---------- */
const line = (pts) => 'M' + pts.map(([x, y]) => `${n1(x)} ${n1(y)}`).join('L');
function ridge(base, amp, count, step) {
  const peaks = Array.from({ length: count }, () => [rand(-50, W + 50), rand(amp * 0.4, amp), rand(70, 190)]);
  const ph = rand(0, 6);
  const pts = [];
  for (let x = -30; x <= W + 30; x += step) {
    let y = base;
    for (const [px, h, pw] of peaks) y -= h * Math.exp(-(((x - px) / pw) ** 2));
    y -= amp * 0.07 * Math.sin(x / 23 + ph) + rand(-0.5, 0.5);
    pts.push([x, y]);
  }
  return pts;
}
function hatch(pts, spacing, len) { // short strokes down the faces that fall away to the right
  let d = '';
  for (let i = 1; i < pts.length; i++) {
    const [x0, y0] = pts[i - 1], [x1, y1] = pts[i];
    const slope = (y1 - y0) / (x1 - x0);
    if (slope <= 0.05) continue;
    for (let x = x0; x < x1; x += spacing) {
      const y = y0 + slope * (x - x0), l = len * Math.min(1, 0.35 + slope * 1.6) * rand(0.75, 1.15);
      d += `M${n1(x)} ${n1(y + 1)}l${n1(-l * 0.55)} ${n1(l * 0.8)}`;
    }
  }
  return d;
}
const fade = (id) => `<defs><linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${PAPER}" stop-opacity=".94"/><stop offset=".55" stop-color="${PAPER}" stop-opacity=".94"/><stop offset="1" stop-color="${PAPER}" stop-opacity="0"/></linearGradient></defs>`;
const filled = (pts, id) => `<path d="${line(pts)}L${W + 30} ${BH + EXTRA}L-30 ${BH + EXTRA}Z" fill="url(#${id})" stroke="none"/>`;

function sage(x, y, s = 1) {
  let d = '';
  for (let i = 0; i < 6; i++) { const a = -Math.PI / 2 + rand(-1.1, 1.1), l = rand(4, 8) * s; d += `M${n1(x + rand(-3, 3) * s)} ${n1(y)}q${n1(Math.cos(a) * l * 0.3)} ${n1(-l * 0.6)} ${n1(Math.cos(a) * l)} ${n1(Math.sin(a) * l)}`; }
  return `<path d="${d}" stroke-width=".7" opacity=".75"/>`;
}
function cabin(x, y, s, smoke = true) {
  const w = 46 * s, h = 22 * s, r = 15 * s, cx = x + w * 0.72;
  let logs = ''; for (let i = 1; i < 5; i++) logs += `M${n1(x)} ${n1(y - (h * i) / 5)}H${n1(x + w)}`;
  return `<g class="cabin">
    <path d="M${n1(x)} ${n1(y)}V${n1(y - h)}L${n1(x + w / 2)} ${n1(y - h - r)}L${n1(x + w)} ${n1(y - h)}V${n1(y)}Z" fill="${PAPER}" stroke="none"/>
    <path d="M${n1(x)} ${n1(y)}V${n1(y - h)}H${n1(x + w)}V${n1(y)}${logs}" stroke-width=".8"/>
    <path d="M${n1(x - 5 * s)} ${n1(y - h)}L${n1(x + w / 2)} ${n1(y - h - r)}L${n1(x + w + 5 * s)} ${n1(y - h)}" stroke-width="1.1"/>
    <path d="M${n1(x + w * 0.2)} ${n1(y - h + 3 * s)}l${n1(w * 0.3)} ${n1(-r * 0.6)}M${n1(x + w * 0.5)} ${n1(y - h + 1 * s)}l${n1(w * 0.25)} ${n1(-r * 0.4)}" stroke-width=".5" opacity=".6"/>
    <path d="M${n1(cx)} ${n1(y - h - r * 0.45)}V${n1(y - h - r - 3 * s)}h${n1(5 * s)}V${n1(y - h - r * 0.62)}" fill="${PAPER}" stroke-width=".8"/>
    <rect x="${n1(x + w * 0.16)}" y="${n1(y - 14 * s)}" width="${n1(8 * s)}" height="${n1(14 * s)}" stroke-width=".8" fill="${PAPER}"/>
    <rect class="win" x="${n1(x + w * 0.56)}" y="${n1(y - h * 0.72)}" width="${n1(9 * s)}" height="${n1(7 * s)}" stroke="none"/>
    <path d="M${n1(x + w * 0.56)} ${n1(y - h * 0.72)}h${n1(9 * s)}v${n1(7 * s)}h${n1(-9 * s)}zM${n1(x + w * 0.56 + 4.5 * s)} ${n1(y - h * 0.72)}v${n1(7 * s)}" stroke-width=".7"/>
    ${smoke ? `<g class="smoke" stroke="none" fill="currentColor">${[0, 2, 4].map((d) => `<circle cx="${n1(cx + 2.5 * s)}" cy="${n1(y - h - r - 4 * s)}" r="${n1(2.2 * s)}" style="animation-delay:-${d}s"/>`).join('')}</g>` : ''}
  </g>`;
}
function meetinghouse(x, y, s) {
  const w = 62 * s, h = 30 * s, r = 16 * s, tx = x + w / 2;
  let wins = ''; for (let i = 0; i < 3; i++) wins += `<rect class="win" x="${n1(x + 8 * s + i * 17 * s)}" y="${n1(y - h + 8 * s)}" width="${n1(6 * s)}" height="${n1(11 * s)}" stroke="none"/><rect x="${n1(x + 8 * s + i * 17 * s)}" y="${n1(y - h + 8 * s)}" width="${n1(6 * s)}" height="${n1(11 * s)}" fill="none" stroke-width=".6"/>`;
  return `<g><path d="M${n1(x)} ${n1(y)}V${n1(y - h)}L${n1(tx)} ${n1(y - h - r)}L${n1(x + w)} ${n1(y - h)}V${n1(y)}Z" fill="${PAPER}" stroke="none"/>
    <path d="M${n1(tx - 6 * s)} ${n1(y - h - r + 3 * s)}V${n1(y - h - r - 12 * s)}H${n1(tx + 6 * s)}V${n1(y - h - r + 3 * s)}M${n1(tx - 8 * s)} ${n1(y - h - r - 12 * s)}L${n1(tx)} ${n1(y - h - r - 22 * s)}L${n1(tx + 8 * s)} ${n1(y - h - r - 12 * s)}" fill="${PAPER}" stroke-width=".8"/>
    <path d="M${n1(x)} ${n1(y)}V${n1(y - h)}H${n1(x + w)}V${n1(y)}M${n1(x - 4 * s)} ${n1(y - h)}L${n1(tx)} ${n1(y - h - r)}L${n1(x + w + 4 * s)} ${n1(y - h)}" stroke-width=".9"/>${wins}</g>`;
}
function bowery(x, y, s) {
  const w = 54 * s, h = 18 * s;
  let posts = ''; for (let i = 0; i <= 4; i++) posts += `M${n1(x + (w * i) / 4)} ${n1(y)}V${n1(y - h)}`;
  let brush = ''; for (let i = 0; i < 26; i++) brush += `M${n1(x - 3 + rand(0, w + 6))} ${n1(y - h - rand(0, 4) * s)}l${n1(rand(-3, 3))} ${n1(-rand(2, 5) * s)}`;
  return `<path d="${posts}M${n1(x - 4)} ${n1(y - h)}H${n1(x + w + 4)}" stroke-width=".8"/><path d="${brush}" stroke-width=".6" opacity=".8"/>`;
}
function fence(x0, x1, gy) {
  let d = '';
  for (let x = x0; x <= x1; x += 13) d += `M${n1(x)} ${n1(gy(x) + 1)}v-9`;
  d += line([[x0, gy(x0) - 6], [x1, gy(x1) - 6]]) + line([[x0, gy(x0) - 2.5], [x1, gy(x1) - 2.5]]);
  return `<path d="${d}" stroke-width=".6" opacity=".8"/>`;
}
function tree(x, y, s) { // a cottonwood by the water
  let crown = '';
  for (let i = 0; i < 16; i++) { const a = rand(0, 6.28), r = rand(4, 15) * s; const cx = x + Math.cos(a) * r * 1.2, cy = y - 34 * s + Math.sin(a) * r * 0.8; crown += `M${n1(cx - 4 * s)} ${n1(cy)}a${n1(4 * s)} ${n1(3.4 * s)} 0 1 1 ${n1(8 * s)} 0`; }
  return `<path d="M${n1(x)} ${n1(y)}C${n1(x + 1)} ${n1(y - 12 * s)} ${n1(x - 2)} ${n1(y - 20 * s)} ${n1(x - 6 * s)} ${n1(y - 28 * s)}M${n1(x)} ${n1(y - 14 * s)}l${n1(7 * s)} ${n1(-12 * s)}" stroke-width="1"/><path d="${crown}" stroke-width=".6" opacity=".85"/>`;
}
function wagon(x, y, s) {
  const w = 62 * s;
  return `<svg x="${n1(x)}" y="${n1(y - w * 0.64)}" width="${n1(w)}" height="${n1(w * 0.64)}" viewBox="0 0 100 64" overflow="visible"><use href="#i-wagon"/></svg>`;
}
// A creek coming down out of the hills, widening toward the viewer.
function creek(cx, gy, out) {
  const top = gy - 2, bot = BH + 30, ph = rand(0, 6), drift = rand(-60, 60);
  const L = [], R = [], mid = [];
  for (let i = 0; i <= 24; i++) {
    const t = i / 24, y = top + (bot - top) * t;
    const x = cx + drift * t * t + Math.sin(t * 5 + ph) * 14 * t;
    const w = 2 + 20 * t * t;
    L.push([x - w / 2, y]); R.push([x + w / 2, y]); mid.push([x, y]);
  }
  let water = '';
  for (let i = 3; i < 24; i += 2) { const [x, y] = mid[i], w = (R[i][0] - L[i][0]) * 0.32; water += `M${n1(x - w)} ${n1(y)}h${n1(w * 2)}`; }
  for (const i of [9, 13, 17]) out.push({ x: R[i][0] + 3, y: R[i][1] });
  return `<path d="${line(L)}${line(R)}" stroke-width=".7"/><path class="water" d="${water}" stroke-width=".6"/>`;
}
function ditch(x0, x1, y, out) { // an irrigation ditch along the front of the field, with its headgate
  let water = '';
  for (let x = x0 + 4; x < x1 - 6; x += rand(9, 16)) water += `M${n1(x)} ${n1(y + 2)}h${n1(rand(4, 8))}`;
  for (let k = 0; k < 4; k++) out.push({ x: x0 + 20 + (x1 - x0 - 40) * (k / 3), y: y - 1.5 });
  return `<path d="M${n1(x0)} ${n1(y)}H${n1(x1)}M${n1(x0 - 6)} ${n1(y + 4.5)}H${n1(x1 + 6)}" stroke-width=".7"/><path class="water" d="${water}" stroke-width=".55"/>
    <path d="M${n1(x1)} ${n1(y - 5)}v11M${n1(x1 + 5)} ${n1(y - 5)}v11M${n1(x1 - 1)} ${n1(y - 5)}h7" stroke-width=".9"/>`;
}
function lake(x0, x1, y0, out) {
  const y1 = y0 + 34, mx = (x0 + x1) / 2, rx = (x1 - x0) / 2;
  let water = '';
  for (let y = y0 + 4; y < y1 - 2; y += 4.5) {
    const half = rx * Math.sqrt(Math.max(0, 1 - ((y - y0 - 2) / (y1 - y0)) ** 2)) * 0.95;
    for (let x = mx - half; x < mx + half - 6; x += rand(12, 30)) water += `M${n1(x)} ${n1(y)}h${n1(Math.min(rand(6, 18), mx + half - x))}`;
  }
  let reeds = '';
  for (const ex of [x0 + 8, x1 - 14]) for (let i = 0; i < 8; i++) { const x = ex + rand(-6, 10), h = rand(8, 16); reeds += `M${n1(x)} ${n1(y0 + 2)}q${n1(rand(-2, 2))} ${n1(-h / 2)} ${n1(rand(-2, 3))} ${n1(-h)}`; }
  for (let k = 0; k < 4; k++) out.push({ x: x0 + 30 + (x1 - x0 - 60) * (k / 3), y: y0 - 1 });
  return `<path d="M${n1(x0)} ${n1(y0)}Q${n1(mx)} ${n1(y0 - 3)} ${n1(x1)} ${n1(y0)}Q${n1(x1 - 10)} ${n1(y1)} ${n1(mx)} ${n1(y1)}Q${n1(x0 + 6)} ${n1(y1)} ${n1(x0)} ${n1(y0)}Z" fill="${PAPER}" stroke-width=".8"/>
    <path class="water" d="${water}" stroke-width=".55"/><path d="${reeds}" stroke-width=".6" opacity=".85"/>`;
}

/* ---------- sprites ---------- */
const CRICKET = `<g class="ck"><path d="M-6 -3.2c2-2.6 8-2.8 10.5-.6c-2 2-8.6 2.4-10.5.6z" fill="#7C6D44" stroke="#C9B57A" stroke-width=".6"/><circle cx="5.4" cy="-3.6" r="1.7" fill="#7C6D44" stroke="#C9B57A" stroke-width=".5"/>
  <path d="M-1.5 -3.4L-5.5 -8.6L-8.6 -.2M1.6 -2.4l1.6 2.4M-.4 -2.4l-1.2 2.4M6.6 -4.8q4 -4.6 8.2 -3.4" fill="none" stroke="#C9B57A" stroke-width=".7" stroke-linecap="round"/></g>`;
const GULL = `<g class="g-fly"><path class="g-wing" d="M-17 -1Q-10 -10 -1 -.5Q8 -10 17 -1.5" fill="none" stroke="#EEE8DA" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M-15.5 -2.6l-1.8 1.4M15.6 -3.2l1.8 1.4" stroke="#3B3A3A" stroke-width="1.3" stroke-linecap="round"/>
  <ellipse cx="0" cy="0" rx="7.5" ry="2.7" fill="#EEE8DA"/><circle cx="7.4" cy="-1.2" r="2.3" fill="#EEE8DA"/><path d="M9.4 -1.4l3.4.7-3.4.8z" fill="#D9B46A"/><path d="M-6.5 -.6l-4.4-1.6v3.4z" fill="#EEE8DA"/></g>
  <g class="g-stand" style="display:none"><g class="g-head"><circle cx="6.6" cy="-12" r="2.7" fill="#EEE8DA"/><path d="M9 -12.2l3.6.8-3.6.9z" fill="#D9B46A"/></g>
  <path d="M-9 -7.6Q-2 -12.4 6 -10.2L5 -5Q-3 -2.6 -9 -7.6z" fill="#EEE8DA"/><path d="M-8.6 -7.4Q-1 -10.4 4.4 -8.4" fill="none" stroke="#8E8A82" stroke-width="1.2"/><path d="M-1 -4.6v4.6M2 -4.8v4.8" stroke="#D9B46A" stroke-width=".8"/></g>`;
const svgEl = (tag, attrs = {}) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); return e; };

/* ---------- the bands ---------- */
function buildBand(type, i) {
  const id = `ld${++uid}`, s = BH / 260, gy = GY;
  const ph = rand(0, 6), ph2 = rand(0, 6);
  const ground = (x) => gy + 4 * Math.sin(x / 150 + ph) + 2.4 * Math.sin(x / 53 + ph2);
  const narrow = W < 700, zw = narrow ? 0.46 : 0.29;
  const L0 = W * 0.025, L1 = W * zw, R0 = W * (1 - zw), R1 = W * 0.975;
  const water = [];

  // far: the high range; mid: foothills
  const farPts = ridge(BH * 0.4, BH * 0.2, 5, 7);
  const midPts = ridge(BH * 0.6, BH * 0.09, 6, 6);
  const far = `${fade(id + 'f')}${filled(farPts, id + 'f')}<path d="${hatch(farPts, 3.4, 11)}" stroke-width=".5" opacity=".55"/><path d="${line(farPts)}" stroke-width=".9"/>`;
  const mid = `${fade(id + 'm')}${filled(midPts, id + 'm')}<path d="${hatch(midPts, 3, 8)}" stroke-width=".55" opacity=".6"/><path d="${line(midPts)}" stroke-width="1"/>`;

  // near: the ground and whatever is on it
  const gpts = []; for (let x = -30; x <= W + 30; x += 8) gpts.push([x, ground(x)]);
  const contours = [9, 21, 38].map((dy) => line(gpts.filter((_, k) => k % 2 === 0).map(([x, y]) => [x, y + dy + Math.sin(x / 47 + dy) * 2]))).join('');
  let near = `${fade(id + 'n')}${filled(gpts, id + 'n')}<path d="${line(gpts)}" stroke-width="1.1"/><path d="${contours}" stroke-width=".4" opacity=".35"/>`;
  let feat = '', back = '';
  for (let k = 0; k < (narrow ? 4 : 8); k++) { const x = k % 2 ? rand(L0, L1) : rand(R0, R1); feat += sage(x, ground(x) + rand(4, 30), rand(0.8, 1.2)); }

  const band = { type, i, ground, water, crops: [], field: null, skep: null };
  if (type === 'farm') {
    const fx0 = L0 + 6, fx1 = L1 - 8, fy0 = gy + 9, fy1 = gy + 50 * s;
    band.field = { x0: fx0, x1: fx1, y0: fy0, y1: fy1 };
    let furrows = '';
    for (let r = 0; r < 6; r++) { const y = fy0 + ((fy1 - fy0) * r) / 5; furrows += `M${n1(fx0 + r * 2)} ${n1(y)}H${n1(fx1 - r * 2)}`; }
    feat += `<path d="${furrows}" stroke-width=".5" opacity=".55"/>`;
    feat += fence(fx0, fx1, ground);
    feat += ditch(fx0 - 4, fx1 + 10, fy1 + 10, water);
    const cx = Math.min(fx1 - 60 * s, fx0 + (fx1 - fx0) * 0.55);
    back += cabin(cx, ground(cx) - 1, s);
    const sx = cx + 54 * s, sy = ground(sx);
    band.skep = { x: sx + 8 * s, y: sy - 10 * s };
    back += `<path d="M${n1(sx - 2)} ${n1(sy)}v-5h${n1(20 * s)}v5" stroke-width=".7"/><svg x="${n1(sx)}" y="${n1(sy - 22 * s)}" width="${n1(18 * s)}" height="${n1(18 * s)}" viewBox="0 0 64 64" overflow="visible"><use href="#i-skep"/></svg>`;
    back += tree(fx0 + 10, ground(fx0 + 10), s * 0.9);
    feat += creek(R0 + (R1 - R0) * 0.45, gy, water);
    feat += tree(R0 + (R1 - R0) * 0.2, ground(R0 + (R1 - R0) * 0.2), s);
    feat += `<path d="M${n1(R1 - 60)} ${n1(ground(R1 - 60))}q14 -26 28 0z" fill="${PAPER}" stroke-width=".8"/><path d="M${n1(R1 - 55)} ${n1(ground(R1 - 55) - 6)}q9 -14 18 0M${n1(R1 - 50)} ${n1(ground(R1 - 50) - 12)}q4 -8 9 0" stroke-width=".5" opacity=".7"/>`;
  } else if (type === 'settlement') {
    let x = L0 + 4;
    for (let k = 0; k < (narrow ? 2 : 3); k++) { back += cabin(x, ground(x) - 1, s * rand(0.8, 1), k !== 1); x += 62 * s + rand(4, 16); }
    feat += fence(L0, x - 8, (xx) => ground(xx) + 14);
    if (!narrow) back += bowery(x + 4, ground(x + 4), s);
    const mx = R0 + (R1 - R0) * 0.45;
    back += meetinghouse(mx, ground(mx) - 1, s);
    feat += creek(R0 + 8, gy, water);
    feat += tree(R1 - 18, ground(R1 - 18), s);
    feat += wagon(L1 - 70 * s, ground(L1 - 40 * s) + 18, s * 0.8);
  } else if (type === 'lake') {
    feat += lake(L0 + 4, L1 - 4, gy + 6, water);
    back += tree(L1 - 4, ground(L1 - 4), s * 1.1);
    back += cabin(R0 + 16, ground(R0 + 16) - 1, s);
    feat += creek(R0 + (R1 - R0) * 0.72, gy, water);
    feat += wagon(R0 + 24, ground(R0 + 50) + 22, s * 0.75);
  } else { // open hills: the trail west
    const tx = L0 + (L1 - L0) * 0.5;
    feat += `<path d="M${n1(tx - 4)} ${n1(gy + 1)}C${n1(tx - 20)} ${n1(gy + 20)} ${n1(tx - 40)} ${n1(gy + 40)} ${n1(tx - 90)} ${n1(BH + 30)}M${n1(tx + 4)} ${n1(gy + 1)}C${n1(tx + 2)} ${n1(gy + 20)} ${n1(tx - 4)} ${n1(gy + 40)} ${n1(tx - 30)} ${n1(BH + 30)}" stroke-width=".6" opacity=".7"/>`;
    feat += wagon(tx - 70 * s, gy + 34 * s, s);
    feat += creek(R0 + (R1 - R0) * 0.4, gy, water);
    feat += tree(R0 + (R1 - R0) * 0.62, ground(R0 + (R1 - R0) * 0.62), s);
    feat += tree(R0 + (R1 - R0) * 0.18, ground(R0 + (R1 - R0) * 0.18), s * 0.8);
  }

  const layers = {};
  for (const [depth, body] of [['far', far], ['mid', mid], ['near', `<g class="scenery">${back}${near}${feat}</g>`]]) {
    const div = document.createElement('div');
    div.className = 'layer';
    div.innerHTML = `<svg width="${W}" height="${BH + EXTRA}" viewBox="0 0 ${W} ${BH + EXTRA}" fill="none" stroke="currentColor" stroke-linecap="round">${body}</svg>`;
    land.querySelector(`.d-${depth}`).append(div);
    layers[depth] = div;
  }
  const nsvg = layers.near.firstElementChild;
  band.layers = layers; band.svg = nsvg;
  if (band.field) { // the wheat, one stalk at a time so the crickets can eat it
    const g = svgEl('g', { class: 'crops', 'stroke-width': '.7' });
    const { x0, x1, y0, y1 } = band.field;
    for (let r = 0; r < 6; r++) {
      const y = y0 + ((y1 - y0) * r) / 5, hh = (7 + r * 1.6) * s;
      for (let x = x0 + 6 + (r % 2) * 5; x < x1 - 6; x += 10) {
        const p = svgEl('path', { d: `M0 0V${n1(-hh)}M0 ${n1(-hh * 0.7)}l-2 -2.4M0 ${n1(-hh * 0.7)}l2 -2.4M0 ${n1(-hh)}v-2.6`, transform: `translate(${n1(x)} ${n1(y)})` });
        g.append(p);
        band.crops.push({ el: p, x, y, h: 1, shown: 1 });
      }
    }
    nsvg.querySelector('.scenery').append(g);
  }
  if (band.skep) {
    const g = svgEl('g', { class: 'hive-bees' });
    for (let k = 0; k < 4; k++) {
      const r = rand(7, 16) * s, c = svgEl('circle', { cx: n1(band.skep.x + r), cy: n1(band.skep.y - rand(0, 6)), r: '.9', fill: '#E3BD6A', stroke: 'none' });
      c.style.cssText = `transform-origin:${n1(band.skep.x)}px ${n1(band.skep.y)}px;animation-duration:${rand(2.2, 4.4).toFixed(1)}s;animation-delay:-${rand(0, 4).toFixed(1)}s;${k % 2 ? 'animation-direction:reverse' : ''}`;
      g.append(c);
    }
    nsvg.append(g);
  }
  band.life = svgEl('g', { class: 'life' });
  nsvg.append(band.life);
  return band;
}

function layout() {
  if (!land) return;
  const swarming = !!swarm; // a relayout (resize, late fonts) redraws the land; the swarm starts over in it
  clearLife();
  for (const d of land.querySelectorAll('.depth')) d.replaceChildren();
  W = document.documentElement.clientWidth; H = innerHeight;
  BH = Math.round(Math.max(200, Math.min(300, H * 0.32)));
  GY = Math.round(BH * 0.7);
  const maxScroll = Math.max(0, document.documentElement.scrollHeight - H);
  const home = document.body.classList.contains('home');
  const start = home ? H * 0.95 : H * 0.3, step = H * 1.15;
  const focus = [];
  for (let f = start; f <= maxScroll + H * 0.2; f += step) focus.push(f);
  if (!focus.length) focus.push(Math.min(start, maxScroll));
  const kinds = ['settlement', 'lake', 'hills'];
  bands = focus.map((f, i) => Object.assign(buildBand(i === 0 ? 'farm' : kinds[(i - 1) % 3], i), { focus: f }));
  place();
  if (swarming && !night) startSwarm();
}

// Each depth sits at the same spot when the page is scrolled to its band, and drifts at its own rate either side.
function place(sy = smoothY()) {
  const anchor = H * 0.72 - GY;
  for (const b of bands) for (const d in b.layers) {
    const y = anchor + (b.focus - sy) * SPEED[d];
    b.layers[d].style.transform = `translate3d(0, ${y.toFixed(1)}px, 0)`;
    if (d === 'near') b.y = y;
  }
}
const onScreen = (b) => b.y + GY > 30 && b.y + GY < H - 10;

/* ---------- life ---------- */
let crickets = [], gulls = [], pellets = [], swarm = null, night = false;

function clearLife() {
  crickets = []; gulls = []; pellets = []; swarm = null;
}

function addCricket(band, x, y, opts = {}) {
  const g = svgEl('g', { class: 'cricket' });
  g.innerHTML = CRICKET;
  band.life.append(g);
  const c = { band, g, x, y, face: 1, state: 'rest', t: rand(0.05, 0.6), hop: null, alive: true, goal: null, ...opts };
  crickets.push(c); drawCricket(c);
  return c;
}
function drawCricket(c) {
  let x = c.x, y = c.y, tilt = 0;
  if (c.hop) { const { x0, y0, x1, y1, h, t } = c.hop; x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t - h * 4 * t * (1 - t); tilt = (0.5 - t) * -40; }
  c.g.setAttribute('transform', `translate(${n1(x)} ${n1(y)}) scale(${c.face} 1) rotate(${n1(tilt)})`);
  c.px = x; c.py = y;
}
function hopTo(c, x, y) {
  c.face = x >= c.x ? 1 : -1;
  c.hop = { x0: c.x, y0: c.y, x1: x, y1: y, h: rand(7, 16), t: 0, dur: rand(0.26, 0.4) };
  c.state = 'hop';
}
function stepCricket(c, dt) {
  if (c.state === 'hop') {
    c.hop.t += dt / c.hop.dur;
    if (c.hop.t >= 1) { c.x = c.hop.x1; c.y = c.hop.y1; c.hop = null; c.state = 'rest'; c.t = c.swarm ? rand(0.3, 1.6) : rand(0.6, 2.2); }
  } else if (c.state === 'rest') {
    c.t -= dt;
    if (c.swarm && c.band.crops.length) { // eat the wheat it is standing in
      for (const cr of c.band.crops) if (Math.abs(cr.x - c.x) < 7 && Math.abs(cr.y - c.y) < 6) cr.h = Math.max(0.12, cr.h - dt * 0.35);
    }
    const near = gulls.find((g) => g.state === 'dive' && Math.hypot(g.x - c.x, g.y - c.y) < 46);
    if (near && Math.random() < dt * 3) c.t = 0; // a gull coming down: jump for it
    if (c.t <= 0) {
      const f = c.swarm && c.field;
      if (c.goal) {
        const dx = c.goal.x - c.x, dy = c.goal.y - c.y, dist = Math.hypot(dx, dy), stepL = Math.min(dist, rand(22, 42));
        if (dist < 4) { c.goal = null; c.t = rand(0.3, 1); return; }
        hopTo(c, c.x + (dx / dist) * stepL, c.y + (dy / dist) * stepL);
      } else if (f) {
        hopTo(c, Math.max(f.x0, Math.min(f.x1, c.x + rand(-34, 34))), Math.max(f.y0, Math.min(f.y1, c.y + rand(-10, 10))));
      } else {
        const x = c.x + rand(-20, 20); hopTo(c, x, c.band.ground(x) + rand(2, 6));
      }
    }
  } else if (c.state === 'hide') {
    c.t -= dt; c.g.style.opacity = Math.max(0, c.t / 1.5);
    if (c.t <= 0) kill(c);
  }
  drawCricket(c);
}
function kill(c) { c.alive = false; c.g.remove(); }

function addGull(band, x, y, opts = {}) {
  const g = svgEl('g', { class: 'gull' });
  g.innerHTML = GULL;
  band.life.append(g);
  const gull = { band, g, x, y, vx: rand(-40, 40), vy: 90, face: 1, state: 'hunt', eaten: 0, cap: 2 + (Math.random() < 0.5 ? 1 : 0), t: 0, prey: null, flap: rand(0, 6), ...opts };
  gull.fly = g.querySelector('.g-fly'); gull.stand = g.querySelector('.g-stand'); gull.wing = g.querySelector('.g-wing'); gull.head = g.querySelector('.g-head');
  gulls.push(gull);
  return gull;
}
function preyFor(gull) {
  const pool = crickets.filter((c) => c.alive && c.band === gull.band && c.state !== 'hide' && (gull.solo ? c === gull.solo : c.swarm));
  if (!pool.length) return null;
  const free = pool.filter((c) => !gulls.some((o) => o !== gull && o.prey === c));
  const from = free.length ? free : pool;
  return from.reduce((a, c) => (Math.hypot(c.x - gull.x, c.y - gull.y) < Math.hypot(a.x - gull.x, a.y - gull.y) ? c : a));
}
function steer(gull, tx, ty, speed, dt, k = 2.6) {
  const dx = tx - gull.x, dy = ty - gull.y, d = Math.hypot(dx, dy) || 1;
  const v = Math.min(speed, d * 3);
  gull.vx += ((dx / d) * v - gull.vx) * Math.min(1, dt * k);
  gull.vy += ((dy / d) * v - gull.vy) * Math.min(1, dt * k);
  gull.x += gull.vx * dt; gull.y += gull.vy * dt;
  return d;
}
function landed(gull, on) {
  gull.fly.style.display = on ? 'none' : ''; gull.stand.style.display = on ? '' : 'none';
}
function stepGull(gull, dt) {
  gull.t += dt;
  const fullUp = () => (gull.eaten >= gull.cap || (gull.eaten && !preyFor(gull)));
  switch (gull.state) {
    case 'hunt': {
      if (!gull.prey || !gull.prey.alive) gull.prey = preyFor(gull);
      if (!gull.prey) { gull.state = gull.eaten ? 'toWater' : 'leave'; break; }
      const c = gull.prey;
      // wheel over the prey a moment before dropping on it
      const d = steer(gull, (c.px ?? c.x) + Math.cos(gull.t * 3) * 22, (c.py ?? c.y) - 50 + Math.sin(gull.t * 3) * 8, 150, dt);
      if (d < 34) { gull.hover = (gull.hover || 0) + dt; if (gull.hover > (gull.wait ??= rand(0.6, 1.6))) { gull.state = 'dive'; gull.hover = 0; gull.wait = undefined; } }
      break;
    }
    case 'dive': {
      const c = gull.prey;
      if (!c || !c.alive) { gull.state = 'hunt'; break; }
      const d = steer(gull, c.px, c.py - 2, 250, dt, 4);
      if (d < 6) {
        kill(c); gull.eaten++; gull.prey = null;
        gull.state = 'rise'; gull.t = 0; gull.rx = gull.x + rand(-70, 70); gull.ry = gull.y - rand(40, 70);
      }
      break;
    }
    case 'rise':
      steer(gull, gull.rx, gull.ry, 160, dt);
      if (gull.t > 0.7) gull.state = gull.solo ? 'leave' : fullUp() ? 'toWater' : 'hunt';
      break;
    case 'toWater': {
      if (!gull.spot) {
        const w = gull.band.water; if (!w.length) { gull.state = 'leave'; break; }
        // usually the nearest water, sometimes the creek across the way
        const sorted = [...w].sort((a, b) => Math.hypot(a.x - gull.x, a.y - gull.y) - Math.hypot(b.x - gull.x, b.y - gull.y));
        gull.spot = Math.random() < 0.6 ? sorted[0] : pick(sorted);
        gull.spot = { x: gull.spot.x + rand(-6, 6), y: gull.spot.y };
      }
      const d = steer(gull, gull.spot.x, gull.spot.y, 180, dt, 3);
      if (d < 5) { gull.x = gull.spot.x; gull.y = gull.spot.y; gull.vx = gull.vy = 0; landed(gull, true); gull.state = 'drink'; gull.t = 0; }
      break;
    }
    case 'drink': { // dip to the water, then the heave that brings the pellet up
      const t = gull.t;
      const bob = t < 2 ? Math.max(0, Math.sin(t * 5)) * 4 : t < 3.4 ? Math.abs(Math.sin(t * 9)) * 2.4 : 0;
      gull.head.setAttribute('transform', `translate(${n1(bob * 0.5)} ${n1(bob)})`);
      if (t > 3.2 && !gull.coughed) { gull.coughed = true; dropPellet(gull); }
      if (t > 4.8) {
        gull.head.removeAttribute('transform'); landed(gull, false);
        gull.eaten = 0; gull.coughed = false; gull.spot = null; gull.vy = -120;
        gull.state = preyFor(gull) ? 'rise' : 'leave'; gull.t = 0; gull.rx = gull.x + rand(-40, 40); gull.ry = gull.y - 80;
      }
      break;
    }
    case 'leave': {
      steer(gull, gull.exitX ??= (gull.x < W / 2 ? -80 : W + 80), -gull.band.y - 120, 190, dt, 1.6);
      if (gull.y < -gull.band.y - 60 || gull.x < -60 || gull.x > W + 60) { gull.g.remove(); gull.gone = true; }
      break;
    }
  }
  if (gull.state !== 'drink') {
    if (Math.abs(gull.vx) > 8) gull.face = gull.vx > 0 ? 1 : -1;
    gull.flap += dt * (gull.state === 'dive' ? 6 : 13);
    const f = gull.state === 'dive' ? 0.75 : Math.sin(gull.flap);
    gull.wing.setAttribute('transform', `scale(1 ${n1(f)})`);
  }
  const tilt = gull.state === 'drink' ? 0 : Math.max(-25, Math.min(25, gull.vy * 0.08)) * gull.face;
  gull.g.setAttribute('transform', `translate(${n1(gull.x)} ${n1(gull.y)}) scale(${gull.face} 1) rotate(${n1(tilt * gull.face)})`);
}
function dropPellet(gull) {
  const k = 0.8 + gull.eaten * 0.2;
  const x = gull.x + gull.face * 11, y = gull.y;
  const g = svgEl('g', { class: 'pellet' });
  g.innerHTML = `<ellipse cx="0" cy="-1.6" rx="${n1(2.4 * k)}" ry="${n1(1.6 * k)}" fill="#8F877A" stroke="#C9BFA8" stroke-width=".4"/><path d="M-1.6 -2.6l-1.6 -1.6M.6 -3l.6 -1.8M1.6 -1l2 -.6" stroke="#C9BFA8" stroke-width=".45" stroke-linecap="round"/>`;
  gull.band.life.prepend(g);
  pellets.push({ g, x, y, t: 0, y0: y - 10 });
  if (pellets.length > 40) { const old = pellets.shift(); old.g.remove(); }
}
function stepPellet(p, dt) {
  p.t += dt;
  const fall = Math.min(1, p.t / 0.35);
  p.g.setAttribute('transform', `translate(${n1(p.x)} ${n1(p.y0 + (p.y - p.y0) * fall * fall)})`);
  if (p.t > 200) p.g.style.opacity = Math.max(0, 1 - (p.t - 200) / 20);
  if (p.t > 220) { p.g.remove(); p.dead = true; }
}

/* ---------- the swarm ---------- */
function startSwarm(opts = {}) {
  const band = opts.band || bands.find((b) => b.type === 'farm');
  if (!band || swarm) return;
  swarm = { band, field: opts.field || band.field, t: 0, spawned: 0, total: opts.total ?? (W < 700 ? 22 : 34), sent: 0, flock: opts.flock ?? (W < 700 ? 4 : 6), raid: !!opts.raid };
}
function stepSwarm(dt) {
  const s = swarm; s.t += dt;
  const f = s.field;
  while (s.spawned < s.total * Math.min(1, s.t / (s.raid ? 6 : 5))) { // they come hopping in over the fence and out of the brush
    s.spawned++;
    const fromLeft = Math.random() < 0.6;
    const x = s.raid ? (fromLeft ? -rand(10, 140) : W + rand(10, 140)) : fromLeft ? f.x0 - rand(10, 90) : f.x1 + rand(10, 70), y = rand(f.y0, f.y1);
    addCricket(s.band, x, y, { swarm: true, field: f, goal: { x: rand(f.x0 + 8, f.x1 - 8), y: rand(f.y0, f.y1) } });
  }
  const gullsAt = s.raid ? 4 : 10, gap = s.raid ? 0.45 : 1.6;
  if (s.t > gullsAt && s.sent < s.flock && s.t > gullsAt + s.sent * gap) { // then the gulls, out of the west
    s.sent++;
    addGull(s.band, rand(W * 0.05, W * 0.5), -s.band.y - rand(40, 120));
  }
  const alive = crickets.some((c) => c.alive && c.swarm);
  if (s.t > 8 && !alive && !gulls.some((g) => g.band === s.band && !g.gone && !g.solo)) swarm = null;
}
function nightfall() {
  for (const c of crickets) if (c.alive && c.state !== 'hide') { c.state = 'hide'; c.hop = null; c.t = 1.5; }
  for (const g of gulls) if (!g.gone && g.state !== 'drink') g.state = g.eaten ? 'toWater' : 'leave';
  swarm = null;
}

/* ↑ ↑ ↓ ↓ ← → ← → B A: a cricket raid on whatever ground is in view */
let looping = false;
function raid() {
  if (!bands.length) return;
  const mid = H * 0.6;
  const b = bands.filter(onScreen)[0] || bands.reduce((a, c) => (Math.abs(c.y + GY - mid) < Math.abs(a.y + GY - mid) ? c : a));
  if (!onScreen(b)) scrollTo({ top: b.focus, behavior: 'smooth' });
  swarm = null; // a raid overrides a swarm already under way; its gulls will hunt the stragglers too
  startSwarm({ band: b, field: { x0: W * 0.03, x1: W * 0.97, y0: GY + 8, y1: GY + (50 * BH) / 260 }, total: W < 700 ? 40 : 90, flock: W < 700 ? 7 : 14, raid: true });
  if (!looping) { looping = true; requestAnimationFrame(frame); }
  const note = document.createElement('div');
  note.className = 'raid-note';
  note.setAttribute('role', 'status');
  note.innerHTML = '<span class="smallcaps">Extra</span> The crickets are upon the wheat! Send for the gulls.';
  document.body.append(note);
  setTimeout(() => note.classList.add('gone'), 4200);
  setTimeout(() => note.remove(), 5200);
}
const CODE = 'ArrowUp ArrowUp ArrowDown ArrowDown ArrowLeft ArrowRight ArrowLeft ArrowRight b a';
let keys = [];
addEventListener('keydown', (e) => {
  if (e.target.closest?.('input, textarea, select, [contenteditable]')) return;
  keys = [...keys, e.key.length === 1 ? e.key.toLowerCase() : e.key].slice(-10);
  if (keys.join(' ') === CODE) { keys = []; raid(); }
});

/* a single cricket hops on, and a gull swoops down for it */
function lone() {
  if (document.hidden || night || swarm) return;
  const vis = bands.filter(onScreen);
  if (!vis.length) return;
  const band = pick(vis), left = Math.random() < 0.5;
  const x = left ? rand(W * 0.04, W * 0.2) : rand(W * 0.8, W * 0.96);
  const c = addCricket(band, left ? -14 : W + 14, band.ground(0) + 4, { goal: { x, y: band.ground(x) + rand(3, 8) } });
  c.y = band.ground(c.x) + 4;
  setTimeout(() => { if (c.alive && !night) addGull(band, left ? rand(W * 0.2, W * 0.5) : rand(W * 0.5, W * 0.8), -band.y - 80, { solo: c, cap: 1 }); }, rand(2600, 4200));
}

/* tumbleweeds, now and then by day, along the ground of whatever band is in view */
function tumbleweedSvg(size) {
  const svg = svgEl('svg', { viewBox: '-50 -50 100 100', width: size, height: size });
  let d = '';
  for (let i = 0; i < 34; i++) {
    const a1 = rand(0, 6.28), a2 = a1 + rand(1.2, 3.2), r1 = rand(18, 46), r2 = rand(18, 46);
    d += `M${n1(r1 * Math.cos(a1))} ${n1(r1 * Math.sin(a1))}Q${n1(rand(-40, 40))} ${n1(rand(-40, 40))} ${n1(r2 * Math.cos(a2))} ${n1(r2 * Math.sin(a2))}`;
  }
  svg.append(svgEl('path', { d, fill: 'none', stroke: 'currentColor', 'stroke-width': '1.4', 'stroke-linecap': 'round' }));
  return svg;
}
function rollTumbleweed() {
  if (document.hidden || night) return;
  const vis = bands.filter(onScreen);
  const size = rand(30, 54);
  const el = document.createElement('div');
  el.className = 'tumbleweed';
  el.append(tumbleweedSvg(size));
  if (vis.length) { const b = pick(vis); el.style.cssText = `top:${(GY + rand(4, 26) - size * 0.85).toFixed(0)}px;bottom:auto`; b.layers.near.append(el); }
  else document.getElementById('critters')?.append(el);
  const dist = W + size * 2 + 80, dur = (dist / rand(110, 170)) * 1000, turns = (dist / (Math.PI * size)) * 360;
  const frames = [], hops = Math.max(2, Math.round(dist / rand(160, 260)));
  for (let i = 0; i <= hops * 4; i++) {
    const t = i / (hops * 4), q = (i % 4) / 4, hop = Math.sin(Math.PI * q) * size * rand(0.35, 0.8) * (1 - t * 0.4);
    frames.push({ transform: `translate(${(-size - 40 + dist * t).toFixed(1)}px, ${(-hop).toFixed(1)}px) rotate(${(turns * t).toFixed(0)}deg)`, offset: t });
  }
  el.animate(frames, { duration: dur, easing: 'linear' }).finished.then(() => el.remove());
}

/* ---------- the clock and the loop ---------- */
let lastSwarmDay = -1;
function tickClock() {
  const now = Date.now(), { up, p } = sunPhase(now), n = dayIndex(now);
  const isNight = !up;
  if (isNight !== night) { night = isNight; land.classList.toggle('night', night); if (night) nightfall(); }
  if (up && !swarm && lastSwarmDay !== n && swarmDay(n) && p >= swarmAt(n) && p < swarmAt(n) + 0.35) { lastSwarmDay = n; startSwarm(); }
}
let last = 0;
function frame(now) {
  const dt = Math.min(0.1, (now - (last || now)) / 1000); last = now;
  if (swarm) stepSwarm(dt);
  if (crickets.length) { for (const c of crickets) if (c.alive) stepCricket(c, dt); crickets = crickets.filter((c) => c.alive); }
  if (gulls.length) { for (const g of gulls) if (!g.gone) stepGull(g, dt); gulls = gulls.filter((g) => !g.gone); }
  if (pellets.length) { for (const p of pellets) stepPellet(p, dt); pellets = pellets.filter((p) => !p.dead); }
  // crops: eaten down in the swarm, growing back by night
  for (const b of bands) for (const cr of b.crops) {
    if (night && cr.h < 1) cr.h = Math.min(1, cr.h + dt * 0.03);
    if (Math.abs(cr.h - cr.shown) > 0.03) { cr.shown = cr.h; cr.el.setAttribute('transform', `translate(${n1(cr.x)} ${n1(cr.y)}) scale(1 ${cr.h.toFixed(2)})`); cr.el.style.opacity = (0.4 + 0.6 * cr.h).toFixed(2); }
  }
  requestAnimationFrame(frame);
}

function every(fn, first, min, max) { setTimeout(function tick() { fn(); setTimeout(tick, rand(min, max)); }, first); }

if (land) {
  land.innerHTML = '<div class="depth d-far"></div><div class="depth d-mid"></div><div class="depth d-near"></div>';
  layout();
  onSmoothScroll(place);
  let rt, lastW = innerWidth, lastH = document.documentElement.scrollHeight;
  const relayout = () => { clearTimeout(rt); rt = setTimeout(() => { if (innerWidth !== lastW || document.documentElement.scrollHeight !== lastH) { lastW = innerWidth; lastH = document.documentElement.scrollHeight; layout(); } else { H = innerHeight; place(); } }, 250); };
  addEventListener('resize', relayout);
  addEventListener('load', relayout);
  tickClock(); setInterval(tickClock, 1000);
  if (!reduced) {
    looping = true; requestAnimationFrame(frame);
    every(rollTumbleweed, rand(8000, 16000), 30000, 60000);
    every(lone, rand(10000, 22000), 32000, 70000);
    if (new URLSearchParams(location.search).has('swarm')) setTimeout(startSwarm, 800);
  }
  // for poking at from the console: deseretLand.swarm(), deseretLand.cricket()
  window.deseretLand = { swarm: startSwarm, raid, cricket: lone, tumbleweed: rollTumbleweed };
}
