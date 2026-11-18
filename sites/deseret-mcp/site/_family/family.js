// Shared sidebar behaviour for every Samuel Baird site (vanilla port of the Deseret Wiki's Sidebar.astro).
// The markup is pre-rendered by packages/family/render.mjs; this only opens, closes and marks the page.
(function () {
  if (window.__famInit) return; window.__famInit = true;
  function init() {
    var btn = document.querySelector('.fam-toggle');
    var panel = document.getElementById('fam-sidebar');
    var scrim = document.querySelector('.fam-scrim');
    if (!btn || !panel || !scrim) return;
    var closeBtn = panel.querySelector('.side-close');
    var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
    var lastFocus = null;

    // Mark the current page (the static render may not know it, e.g. on client-side navigation).
    function mark() {
      var p = location.pathname.replace(/\/index(\.html)?$/, '/').replace(/\.html$/, '').replace(/(.)\/$/, '$1');
      panel.querySelectorAll('.side-nav .side-list:not(.side-projects) a.side-link, .side-foot a.side-link').forEach(function (a) {
        var u; try { u = new URL(a.getAttribute('href'), location.href); } catch (e) { return; }
        if (u.origin !== location.origin) return;
        var h = u.pathname.replace(/(.)\/$/, '$1');
        var on = a.hasAttribute('data-exact') ? p === h : (p === h || p.indexOf(h + '/') === 0) && h !== '/';
        if (h === '/' && p === '/') on = true;
        if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
      });
    }
    mark();
    window.addEventListener('popstate', mark);

    function open() {
      lastFocus = document.activeElement;
      panel.hidden = false; scrim.hidden = false;
      requestAnimationFrame(function () { panel.classList.add('open'); scrim.classList.add('open'); });
      btn.setAttribute('aria-expanded', 'true');
      var f = panel.querySelector('[aria-current="page"]') || panel.querySelector('.side-link');
      if (f) f.focus({ preventScroll: true });
    }
    function close(restore) {
      panel.classList.remove('open'); scrim.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
      setTimeout(function () { panel.hidden = true; scrim.hidden = true; }, reduced ? 0 : 190);
      if (restore !== false) (lastFocus || btn).focus({ preventScroll: true });
    }
    function isOpen() { return btn.getAttribute('aria-expanded') === 'true'; }
    btn.addEventListener('click', function () { isOpen() ? close() : open(); });
    if (closeBtn) closeBtn.addEventListener('click', function () { close(); });
    scrim.addEventListener('click', function () { close(false); });
    panel.addEventListener('click', function (e) { if (e.target.closest('a')) { close(false); setTimeout(mark, 50); } });
    document.addEventListener('keydown', function (e) {
      if (!isOpen()) return;
      if (e.key === 'Escape') { e.preventDefault(); close(); }
      if (e.key === 'Tab') {
        var f = panel.querySelectorAll('a, button'), first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

// The sky, after the Deseret Wiki (sites/deseret-wiki/src/scripts/sky.js and clock.js): the real night sky
// over Great Salt Lake City behind every page, and a sun and a phased moon that cross the panorama.
// Stars: the Yale Bright Star Catalogue (stars.json, copied from the Deseret Wiki). The engraving's day is
// the wiki's clock (150 s per day, 8 days per lunation, on wall-clock time), so every site shows the same hour.
(function () {
  if (window.__famSky) return; window.__famSky = true;
  var SUN_CYCLE = 150000, DAY_SHARE = 0.62, LUNATION = 8;
  var D = Math.PI / 180, LAT = 40.76 * D, LON = -111.89, VIEW_AZ = 95 * D, VIEW_ALT = 36 * D;
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var me = document.currentScript || document.querySelector('script[src*="/_family/family.js"]');
  var starsUrl = me && me.src ? new URL('stars.json', me.src).href : '/_family/stars.json';

  function sunPhase(now) {
    var p = (now % SUN_CYCLE) / SUN_CYCLE;
    return p >= DAY_SHARE ? { up: false, p: (p - DAY_SHARE) / (1 - DAY_SHARE) } : { up: true, p: p / DAY_SHARE };
  }
  function moonPhase(now) { return (now / (SUN_CYCLE * LUNATION)) % 1; }
  function moonLit(ph) { return (1 - Math.cos(ph * 2 * Math.PI)) / 2; }

  var daylight = 0, sunLow = 0, moonlight = 0;
  var canvas, ctx, prepared = null, W = 0, H = 0, dpr = 1, panoramas = [];

  function resize() {
    dpr = Math.min(2, window.devicePixelRatio || 1);
    W = innerWidth; H = innerHeight;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
  }
  function bvColor(bv) { // B-V to a muted tint, pulled toward cream so it sits with the engraving
    var s = [[-0.4, [175, 196, 255]], [0, [222, 230, 255]], [0.6, [255, 246, 228]], [1.1, [255, 222, 176]], [2, [255, 190, 135]]];
    var i = 0; while (i < s.length - 2 && bv > s[i + 1][0]) i++;
    var t = Math.max(0, Math.min(1, (bv - s[i][0]) / (s[i + 1][0] - s[i][0])));
    return s[i][1].map(function (v, k) { return Math.round(v + (s[i + 1][1][k] - v) * t); }).join(',');
  }
  function sidereal(ms) {
    var jd = ms / 86400000 + 2440587.5;
    return (((280.46061837 + 360.98564736629 * (jd - 2451545) + LON) % 360) + 360) % 360;
  }
  // observer basis (east, north, up): forward, right, up
  var F = [Math.cos(VIEW_ALT) * Math.sin(VIEW_AZ), Math.cos(VIEW_ALT) * Math.cos(VIEW_AZ), Math.sin(VIEW_ALT)];
  var R = [Math.cos(VIEW_AZ), -Math.sin(VIEW_AZ), 0];
  var U = [R[1] * F[2] - R[2] * F[1], R[2] * F[0] - R[0] * F[2], R[0] * F[1] - R[1] * F[0]];
  function prepare(f) {
    var out = [];
    for (var i = 0; i < f.length; i += 4) {
      var mag = f[i + 2];
      out.push({ ra: f[i] * D, sd: Math.sin(f[i + 1] * D), cd: Math.cos(f[i + 1] * D), mag: mag,
        rad: Math.max(0.45, 2.3 - 0.36 * mag), a: Math.max(0.18, Math.min(1, 1.05 - 0.13 * mag)),
        rgb: bvColor(f[i + 3]), tw: Math.random() * 6.28, tf: 0.6 + Math.random() });
    }
    return out;
  }

  function drawSky(now) {
    var sl = Math.sin(LAT), cl = Math.cos(LAT), lst = sidereal(now) * D;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#0A0F16');
    g.addColorStop(0.65, '#141519');
    g.addColorStop(1, 'rgb(' + (21 + 34 * sunLow * daylight) + ',' + (21 + 18 * sunLow * daylight) + ',' + (24 + 2 * sunLow * daylight) + ')');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    if (daylight > 0) { ctx.fillStyle = 'rgba(60,72,92,' + 0.24 * daylight * (1 - sunLow) + ')'; ctx.fillRect(0, 0, W, H); }
    if (moonlight > 0) { ctx.fillStyle = 'rgba(70,82,104,' + 0.11 * moonlight + ')'; ctx.fillRect(0, 0, W, H); }
    if (!prepared) return;
    var s = Math.max(W, H * 0.9) / 2 / 1.155, cx = W / 2, cy = H * 0.6;
    var fade = (1 - 0.65 * daylight) * (1 - 0.22 * moonlight) * 0.6, t = now / 1000;
    for (var i = 0; i < prepared.length; i++) {
      var st = prepared[i], ha = lst - st.ra;
      var sinAlt = st.sd * sl + st.cd * cl * Math.cos(ha);
      if (sinAlt < 0) continue;
      var d0 = -st.cd * Math.sin(ha), d1 = st.sd * cl - st.cd * Math.cos(ha) * sl, d2 = sinAlt;
      var Z = d0 * F[0] + d1 * F[1] + d2 * F[2];
      if (Z < -0.1) continue;
      var k = 2 / (1 + Z);
      var px = cx + s * k * (d0 * R[0] + d1 * R[1]), py = cy - s * k * (d0 * U[0] + d1 * U[1] + d2 * U[2]);
      if (px < -4 || px > W + 4 || py < -4 || py > H + 4) continue;
      var tw = reduced ? 1 : 1 - (0.12 + 0.25 * (1 - sinAlt)) * (0.5 + 0.5 * Math.sin(t * st.tf * 2.2 + st.tw));
      var a = st.a * fade * tw * Math.min(1, sinAlt * 6);
      ctx.fillStyle = 'rgba(' + st.rgb + ',' + a + ')';
      ctx.beginPath(); ctx.arc(px, py, st.rad, 0, 6.2832); ctx.fill();
      if (st.mag < 1.2) { // engraver's glint on the brightest
        var l = 4 + (1.2 - st.mag) * 3;
        ctx.strokeStyle = 'rgba(' + st.rgb + ',' + a * 0.45 + ')'; ctx.lineWidth = 0.6;
        ctx.beginPath(); ctx.moveTo(px - l, py); ctx.lineTo(px + l, py); ctx.moveTo(px, py - l); ctx.lineTo(px, py + l); ctx.stroke();
      }
    }
  }

  // The lit part of a disc: the bright limb, closed by the terminator (a half-ellipse).
  function moonPath(ph, r) {
    var rx = (r * Math.abs(Math.cos(ph * 2 * Math.PI))).toFixed(2), waxing = ph < 0.5;
    var term = waxing ? (ph < 0.25 ? 0 : 1) : (ph < 0.75 ? 0 : 1);
    return 'M0 ' + -r + 'A' + r + ' ' + r + ' 0 0 ' + (waxing ? 1 : 0) + ' 0 ' + r + 'A' + rx + ' ' + r + ' 0 0 ' + term + ' 0 ' + -r + 'Z';
  }
  function drawSun(now) {
    var sp = sunPhase(now), up = sp.up, p = sp.p, h = up ? Math.sin(Math.PI * p) : 0;
    daylight = up ? Math.pow(h, 0.5) : 0;
    sunLow = up ? Math.pow(1 - h, 2) : 0;
    var ph = moonPhase(now), lit = moonLit(ph), mh = up ? 0 : Math.sin(Math.PI * p);
    moonlight = up ? 0 : Math.pow(mh, 0.6) * lit;
    for (var i = 0; i < panoramas.length; i++) {
      var svg = panoramas[i];
      var moon = svg.querySelector('.moon');
      if (moon) {
        moon.setAttribute('transform', 'translate(' + (110 + 980 * (up ? 0 : p)).toFixed(1) + ' ' + (172 - 132 * mh).toFixed(1) + ')');
        moon.style.opacity = up ? 0 : 1;
        var litEl = moon.querySelector('.moon-lit'), key = ph.toFixed(3);
        if (litEl && litEl.getAttribute('data-phase') !== key) { litEl.setAttribute('data-phase', key); litEl.setAttribute('d', moonPath(ph, 16)); }
        var halo = moon.querySelector('.moon-halo'); if (halo) halo.style.opacity = (0.25 + 0.75 * lit).toFixed(2);
        var marks = moon.querySelector('.moon-marks'); if (marks) marks.style.opacity = lit > 0.45 ? 1 : 0;
      }
      var sun = svg.querySelector('.sun'), glow = svg.querySelector('.sun-glow'), rays = svg.querySelector('.sun-rays');
      if (!sun) continue;
      var x = 90 + 1020 * (up ? p : 0), y = 168 - 138 * h;
      sun.setAttribute('transform', 'translate(' + x.toFixed(1) + ' ' + y.toFixed(1) + ')');
      sun.style.opacity = up ? 1 : 0;
      if (rays) rays.setAttribute('transform', 'rotate(' + ((now / 400) % 360).toFixed(1) + ')');
      if (glow) { glow.setAttribute('cx', x.toFixed(1)); glow.style.opacity = (up ? 0.25 + 0.55 * sunLow : 0).toFixed(3); }
    }
  }

  var last = -1e9;
  function frame(now) {
    if (now - last > (reduced ? 60000 : 50)) { // ~20 fps is plenty for drifting stars
      last = now;
      var ms = Date.now();
      drawSun(ms);
      if (ctx) drawSky(ms);
    }
    requestAnimationFrame(frame);
  }

  function findPanoramas() { panoramas = [].slice.call(document.querySelectorAll('.fam-pano .mountains')); }
  function init() {
    // Client-side navigation in the Next apps can swap the header, so look the panoramas up again now and then.
    findPanoramas(); setInterval(findPanoramas, 2000);
    canvas = document.getElementById('fam-sky');
    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.id = 'fam-sky';
      canvas.setAttribute('aria-hidden', 'true');
      document.body.prepend(canvas);
    }
    ctx = canvas.getContext && canvas.getContext('2d');
    if (ctx) {
      document.documentElement.classList.add('fam-sky-on');
      resize();
      addEventListener('resize', function () { resize(); drawSky(Date.now()); });
      var load = function () {
        fetch(starsUrl).then(function (r) { return r.json(); }).then(function (f) { prepared = prepare(f); }).catch(function () {});
      };
      if ('requestIdleCallback' in window) requestIdleCallback(load, { timeout: 1500 }); else setTimeout(load, 300);
    }
    requestAnimationFrame(frame);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
