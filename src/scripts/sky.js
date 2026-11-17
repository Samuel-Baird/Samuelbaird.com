// The living backdrop: the real night sky over Great Salt Lake City, a sun and a waxing and waning moon
// that rise and set over the Wasatch panorama, honeybees by day, and engraved emblems in the margins.
//
// Stars: NASA HEASARC's Yale Bright Star Catalogue (public/stars.json, built by scripts/stars.mjs).
// Their positions are computed for the real time and place, so the sky turns at the Earth's true rate
// (one degree every four minutes) as you read. The sun is a separate, faster loop drawn into the
// engraving, so its rising and setting can be watched.
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const D = Math.PI / 180;
const LAT = 40.76 * D, LON = -111.89; // Great Salt Lake City
const VIEW_AZ = 95 * D, VIEW_ALT = 36 * D; // looking east, toward the Wasatch
import { sunPhase, moonPhase, moonLit } from './clock.js';
import { onSmoothScroll, smoothY } from './smooth.js';
import { pointer, active, speed } from './pointer.js';
const rand = (a, b) => a + Math.random() * (b - a);

/* ---------- light (the clock itself is in clock.js, shared with the land) ---------- */
let daylight = 0, sunLow = 0, moonlight = 0;

/* ---------- stars ---------- */
const canvas = document.getElementById('sky');
const ctx = canvas?.getContext('2d');
let stars = null, W = 0, H = 0, dpr = 1;
const dim = document.body.classList.contains('home') ? 1 : 0.6;

function resize() {
  dpr = Math.min(2, devicePixelRatio || 1);
  W = innerWidth; H = innerHeight;
  canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
}

function bvColor(bv) {
  // B−V to a muted star tint, pulled toward cream so it sits with the engraving.
  const stops = [[-0.4, [175, 196, 255]], [0, [222, 230, 255]], [0.6, [255, 246, 228]], [1.1, [255, 222, 176]], [2, [255, 190, 135]]];
  let i = 0; while (i < stops.length - 2 && bv > stops[i + 1][0]) i++;
  const [b0, c0] = stops[i], [b1, c1] = stops[i + 1];
  const t = Math.max(0, Math.min(1, (bv - b0) / (b1 - b0)));
  return c0.map((v, k) => Math.round(v + (c1[k] - v) * t));
}

function siderealDeg(ms) {
  const jd = ms / 86400000 + 2440587.5;
  const gmst = 280.46061837 + 360.98564736629 * (jd - 2451545);
  return ((gmst + LON) % 360 + 360) % 360;
}

// observer basis: forward, right, up (east, north, up coordinates)
const F = [Math.cos(VIEW_ALT) * Math.sin(VIEW_AZ), Math.cos(VIEW_ALT) * Math.cos(VIEW_AZ), Math.sin(VIEW_ALT)];
const R = [Math.cos(VIEW_AZ), -Math.sin(VIEW_AZ), 0];
const U = [R[1] * F[2] - R[2] * F[1], R[2] * F[0] - R[0] * F[2], R[0] * F[1] - R[1] * F[0]];

let prepared = null; // per-star constants
function prepare(flat) {
  const out = [];
  for (let i = 0; i < flat.length; i += 4) {
    const [ra, dec, mag, bv] = [flat[i], flat[i + 1], flat[i + 2], flat[i + 3]];
    const [r, g, b] = bvColor(bv);
    out.push({
      ra: ra * D, sd: Math.sin(dec * D), cd: Math.cos(dec * D), mag,
      rad: Math.max(0.45, 2.3 - 0.36 * mag), a: Math.max(0.18, Math.min(1, 1.05 - 0.13 * mag)),
      rgb: `${r},${g},${b}`, tw: rand(0, 6.28), tf: rand(0.6, 1.6),
    });
  }
  return out;
}

function drawSky(now) {
  const sl = Math.sin(LAT), cl = Math.cos(LAT);
  const lst = siderealDeg(now) * D;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  // sky wash: deep night above, warm at the horizon, gilded when the sun is low
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#0A0F16');
  g.addColorStop(0.65, '#141519');
  g.addColorStop(1, `rgb(${21 + 34 * sunLow * daylight},${21 + 18 * sunLow * daylight},${24 + 2 * sunLow * daylight})`);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
  if (daylight > 0) { ctx.fillStyle = `rgba(60,72,92,${0.24 * daylight * (1 - sunLow)})`; ctx.fillRect(0, 0, W, H); }
  // a bright moon lifts the night a little; a new moon leaves it at its darkest
  if (moonlight > 0) { ctx.fillStyle = `rgba(70,82,104,${0.11 * moonlight})`; ctx.fillRect(0, 0, W, H); }
  if (!prepared) return;

  const s = Math.max(W, H * 0.9) / 2 / 1.155; // ±60° across the wider side
  const cx = W / 2, cy = H * 0.6;
  const fade = (1 - 0.65 * daylight) * (1 - 0.22 * moonlight) * dim;
  const t = now / 1000;
  for (const st of prepared) {
    const ha = lst - st.ra;
    const sinAlt = st.sd * sl + st.cd * cl * Math.cos(ha);
    if (sinAlt < 0) continue; // below the horizon
    // direction in east / north / up
    const d0 = -st.cd * Math.sin(ha), d1 = st.sd * cl - st.cd * Math.cos(ha) * sl, d2 = sinAlt;
    const Z = d0 * F[0] + d1 * F[1] + d2 * F[2];
    if (Z < -0.1) continue;
    const k = 2 / (1 + Z);
    const px = cx + s * k * (d0 * R[0] + d1 * R[1]);
    const py = cy - s * k * (d0 * U[0] + d1 * U[1] + d2 * U[2]);
    if (px < -4 || px > W + 4 || py < -4 || py > H + 4) continue;
    // twinkle, stronger near the horizon
    const tw = reduced ? 1 : 1 - (0.12 + 0.25 * (1 - sinAlt)) * (0.5 + 0.5 * Math.sin(t * st.tf * 2.2 + st.tw));
    const a = st.a * fade * tw * Math.min(1, sinAlt * 6);
    ctx.fillStyle = `rgba(${st.rgb},${a})`;
    ctx.beginPath(); ctx.arc(px, py, st.rad, 0, 6.2832); ctx.fill();
    if (st.mag < 1.2) { // engraver's glint on the brightest
      const l = 4 + (1.2 - st.mag) * 3;
      ctx.strokeStyle = `rgba(${st.rgb},${a * 0.45})`; ctx.lineWidth = 0.6;
      ctx.beginPath(); ctx.moveTo(px - l, py); ctx.lineTo(px + l, py); ctx.moveTo(px, py - l); ctx.lineTo(px, py + l); ctx.stroke();
    }
  }
}

/* ---------- sun and moon in the panorama ---------- */
const panoramas = [...document.querySelectorAll('.mountains')];
// The lit part of a disc of radius r: the bright limb, closed by the terminator (a half-ellipse).
function moonPath(phase, r) {
  const rx = (r * Math.abs(Math.cos(phase * 2 * Math.PI))).toFixed(2);
  const waxing = phase < 0.5;
  const limb = waxing ? 1 : 0; // lit on the right while waxing, on the left while waning
  const term = waxing ? (phase < 0.25 ? 0 : 1) : (phase < 0.75 ? 0 : 1);
  return `M0 ${-r}A${r} ${r} 0 0 ${limb} 0 ${r}A${rx} ${r} 0 0 ${term} 0 ${-r}Z`;
}
function drawSun(now) {
  const { up, p } = sunPhase(now);
  const h = up ? Math.sin(Math.PI * p) : 0;
  daylight = up ? Math.pow(h, 0.5) : 0;
  sunLow = up ? Math.pow(1 - h, 2) : 0;
  const phase = moonPhase(now), lit = moonLit(phase);
  const mh = up ? 0 : Math.sin(Math.PI * p);
  moonlight = up ? 0 : Math.pow(mh, 0.6) * lit;
  for (const svg of panoramas) {
    const moon = svg.querySelector('.moon');
    if (moon) {
      const mx = 110 + 980 * (up ? 0 : p), my = 172 - 132 * mh;
      moon.setAttribute('transform', `translate(${mx.toFixed(1)} ${my.toFixed(1)})`);
      moon.style.opacity = up ? 0 : 1;
      const litEl = moon.querySelector('.moon-lit');
      if (litEl && litEl.dataset.phase !== phase.toFixed(3)) { litEl.dataset.phase = phase.toFixed(3); litEl.setAttribute('d', moonPath(phase, 16)); }
      const halo = moon.querySelector('.moon-halo');
      if (halo) halo.style.opacity = (0.25 + 0.75 * lit).toFixed(2);
      const marks = moon.querySelector('.moon-marks');
      if (marks) marks.style.opacity = lit > 0.45 ? 1 : 0;
    }
    const sun = svg.querySelector('.sun'), glow = svg.querySelector('.sun-glow'), rays = svg.querySelector('.sun-rays');
    if (!sun) continue;
    const x = 90 + 1020 * (up ? p : 0), y = 168 - 138 * h;
    sun.setAttribute('transform', `translate(${x.toFixed(1)} ${y.toFixed(1)})`);
    sun.style.opacity = up ? 1 : 0;
    rays?.setAttribute('transform', `rotate(${((now / 400) % 360).toFixed(1)})`);
    if (glow) {
      glow.setAttribute('cx', x.toFixed(1));
      glow.style.opacity = (up ? 0.25 + 0.55 * sunLow : 0).toFixed(3);
    }
  }
}

/* ---------- loop ---------- */
let last = 0;
function frame(now) {
  const ms = Date.now();
  if (now - last > (reduced ? 60000 : 50)) { // ~20 fps is plenty for drifting stars
    last = now;
    drawSun(ms);
    if (ctx) drawSky(ms);
  }
  requestAnimationFrame(frame);
}
if (ctx) {
  resize();
  addEventListener('resize', () => { resize(); drawSky(Date.now()); });
  const load = () => fetch('/stars.json').then((r) => r.json()).then((f) => { stars = f; prepared = prepare(f); }).catch(() => {});
  ('requestIdleCallback' in window) ? requestIdleCallback(load, { timeout: 1500 }) : setTimeout(load, 300);
}
requestAnimationFrame(frame);

/* ---------- honeybees, out by day (tumbleweeds, crickets and gulls are in land.js) ---------- */
const layer = document.getElementById('critters');

const BEE = `<svg viewBox="0 0 32 32" width="26" height="26" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
<path class="wing" d="M14.5 15C9 14 5.5 7 9.5 4.5C13.5 2.2 17 9 14.5 15Z" stroke-width=".9"/><path class="wing" d="M16.5 15C16.5 9 21.5 3.6 25 5.4C28.4 7.6 22.5 13.6 16.5 15Z" stroke-width=".9"/>
<g clip-path="url(#bee-abdomen)" fill="currentColor" stroke="none"><rect x="7" y="13" width="2.1" height="14"/><rect x="10.8" y="13" width="2.1" height="14"/><rect x="14.6" y="13" width="2.1" height="14"/></g>
<ellipse cx="11.5" cy="19.5" rx="8" ry="5.4" stroke-width="1.1"/><circle cx="21.6" cy="18.4" r="3.6" fill="url(#hatch)" stroke-width="1"/><circle cx="26.6" cy="17.2" r="2.6" stroke-width="1"/>
<path d="M27.8 14.9c.8-2.1 2-3.1 3.4-3.3M26.4 14.8c.3-2.3 1.1-3.5 2.3-4.1" stroke-width=".7"/></g></svg>`;

// Each bee holds a course across the screen, wandering about it. Bump one with the pointer and it
// veers off on a new course, away from the bump and along the way the pointer was moving.
const bees = [];
function flyBee(force = false) {
  if (!force && (document.hidden || !sunPhase().up)) return;
  const el = document.createElement('div');
  el.className = 'sky-bee';
  el.innerHTML = BEE;
  layer.append(el);
  const ltr = Math.random() < 0.6;
  const course = (ltr ? 0 : Math.PI) + rand(-0.25, 0.25);
  bees.push({ el, x: ltr ? -40 : innerWidth + 40, y: innerHeight * rand(0.1, 0.45), course, th: course, v: rand(80, 120), cruise: 0, ph: rand(0, 6), t: 0, bumped: -1e4 });
  if (bees.length === 1) requestAnimationFrame(stepBees);
}
const wrapA = (a) => Math.atan2(Math.sin(a), Math.cos(a));
let beeLast = 0;
function stepBees(now) {
  const dt = Math.min(0.06, (now - (beeLast || now)) / 1000); beeLast = now;
  for (const b of bees) {
    b.t += dt;
    const cx = b.x + 13, cy = b.y + 13;
    if (active() && now - b.bumped > 450 && Math.hypot(pointer.x - cx, pointer.y - cy) < 34) {
      b.bumped = now;
      let ax = cx - pointer.x, ay = cy - pointer.y; const al = Math.hypot(ax, ay) || 1; ax /= al; ay /= al;
      const sp = speed();
      if (sp > 40) { ax += (pointer.vx / sp) * 0.9; ay += (pointer.vy / sp) * 0.9; }
      b.course = Math.atan2(ay, ax);
      b.cruise = 1; // startled: faster, and turning hard
    }
    b.cruise = Math.max(0, b.cruise - dt * 0.7);
    const want = b.course + Math.sin(b.t * 2.1 + b.ph) * 0.55 + Math.sin(b.t * 7.3) * 0.12; // wander about the course
    b.th += wrapA(want - b.th) * Math.min(1, dt * (2.2 + 9 * b.cruise));
    const v = b.v * (1 + 1.4 * b.cruise);
    b.x += Math.cos(b.th) * v * dt; b.y += Math.sin(b.th) * v * dt;
    const face = Math.cos(b.th) >= 0 ? 1 : -1;
    const tilt = Math.max(-40, Math.min(40, (wrapA(face === 1 ? b.th : Math.PI - b.th) * 180) / Math.PI));
    b.el.style.transform = `translate(${b.x.toFixed(1)}px, ${b.y.toFixed(1)}px) scaleX(${face}) rotate(${tilt.toFixed(1)}deg)`;
    if (b.x < -80 || b.x > innerWidth + 80 || b.y < -80 || b.y > innerHeight + 80) { b.el.remove(); b.gone = true; }
  }
  for (let i = bees.length - 1; i >= 0; i--) if (bees[i].gone) bees.splice(i, 1);
  if (bees.length) requestAnimationFrame(stepBees); else beeLast = 0;
}

window.deseretSky = { bee: () => flyBee(true) }; // for the console

function every(fn, first, min, max) {
  setTimeout(function tick() { fn(); setTimeout(tick, rand(min, max)); }, first);
}
if (layer && !reduced) {
  every(flyBee, rand(5000, 12000), 16000, 34000);
}

/* ---------- engraved emblems in the margins, with parallax ---------- */
const margins = document.getElementById('margins');
// The wagon, the Deseret primer and the skep, and the symbols drawn in components/Emblems.astro.
const SQ = '0 0 64 64';
const EMBLEMS = [
  ['i-wagon', '0 0 100 64'], ['i-primer', '0 0 64 48'], ['i-skep', SQ],
  ...['daystar', 'hexagram', 'octagram', 'sun', 'moon', 'squaredcircle', 'squarecompass', 'wheat', 'cup', 'grapes',
    'olive', 'waters', 'flame', 'horn', 'crown', 'serpent', 'dove', 'ox', 'tree', 'keystone', 'keyring', 'handclasp'].map((n) => [`e-${n}`, SQ]),
];
function shuffled(a) { a = [...a]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
let items = [];
function layoutMargins() {
  if (!margins) return;
  margins.replaceChildren(); items = [];
  if (innerWidth < 900) return;
  const content = document.querySelector('main .article, main .wrap');
  const cw = content ? Math.min(content.getBoundingClientRect().width, innerWidth) : 1088;
  const gutter = (innerWidth - cw) / 2;
  const docH = document.documentElement.scrollHeight;
  const start = document.body.classList.contains('home') ? innerHeight * 1.05 : 340;
  let y = start, i = 0, side = 0;
  const deck = shuffled(EMBLEMS);
  while (y < docH * 0.6 + innerHeight) {
    const [id, vb] = deck[i++ % deck.length];
    const size = rand(86, 130);
    const speed = rand(0.42, 0.62);
    const x = Math.max(-size * 0.4, gutter / 2 - size / 2 + rand(-12, 12));
    const el = document.createElement('div');
    el.className = 'emblem';
    el.style.cssText = `width:${size}px;${side ? 'right' : 'left'}:${x.toFixed(0)}px;opacity:${rand(0.08, 0.14).toFixed(2)}`;
    // two slow motions on their own clocks: a rise and fall, and a sway back and forth
    el.innerHTML = `<div class="bob" style="animation-duration:${rand(9, 15).toFixed(1)}s;animation-delay:-${rand(0, 15).toFixed(1)}s"><div class="sway" style="animation-duration:${rand(11, 19).toFixed(1)}s;animation-delay:-${rand(0, 19).toFixed(1)}s"><svg viewBox="${vb}" style="transform:rotate(${rand(-9, 9).toFixed(1)}deg)"><use href="#${id}"/></svg></div></div>`;
    margins.append(el);
    items.push({ el, y, speed });
    side ^= 1;
    y += rand(460, 640);
  }
  place();
}
function place(sy = smoothY()) {
  for (const it of items) it.el.style.transform = `translate3d(0, ${(it.y - sy * it.speed).toFixed(1)}px, 0)`;
}
onSmoothScroll(place);
if (margins) {
  addEventListener('load', layoutMargins);
  let rt; addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(layoutMargins, 200); });
  layoutMargins();
}
