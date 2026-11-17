// Where the visitor's pointer is and how fast it is moving, for the critters that can be bumped.
// The backdrop layers ignore pointer events, so bumps are worked out from positions instead.
export const pointer = { x: -1e4, y: -1e4, vx: 0, vy: 0, t: -1e4, tap: -1e4 };
let lt = 0;
addEventListener('pointermove', (e) => {
  const now = performance.now();
  if (lt && now - lt < 200) {
    const dt = Math.max(8, now - lt) / 1000;
    pointer.vx = pointer.vx * 0.4 + ((e.clientX - pointer.x) / dt) * 0.6;
    pointer.vy = pointer.vy * 0.4 + ((e.clientY - pointer.y) / dt) * 0.6;
  } else { pointer.vx = pointer.vy = 0; }
  pointer.x = e.clientX; pointer.y = e.clientY; pointer.t = lt = now;
}, { passive: true });
addEventListener('pointerdown', (e) => { pointer.x = e.clientX; pointer.y = e.clientY; pointer.vx = pointer.vy = 0; pointer.tap = performance.now(); }, { passive: true });
/** the pointer is moving now, or was just pressed: either can bump something */
export const active = () => { const now = performance.now(); return now - pointer.t < 90 || now - pointer.tap < 160; };
export const speed = () => Math.hypot(pointer.vx, pointer.vy);
