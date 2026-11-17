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
