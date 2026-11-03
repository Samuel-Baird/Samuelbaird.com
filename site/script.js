// Latin / Deseret script toggle. Loads the Deseret transliteration package on first use
// (/deseret/lib/*.mjs + the word list) and rewrites English text nodes in place.
// Text marked lang="pt" / lang="es" (or any non-English lang), code, form fields and
// elements with [data-no-deseret] are never touched. Preference is kept in localStorage.
(function () {
  var KEY = 'urim:script';
  var btn = document.getElementById('scriptbtn');
  if (!btn) return;
  var root = document.documentElement;
  var engine = null, loading = null, observer = null, on = false;
  var original = new Map(); // text node -> original string, so the toggle can be undone
  var SKIP = /^(SCRIPT|STYLE|CODE|PRE|TEXTAREA|INPUT|SELECT|OPTION|SVG|NOSCRIPT|TITLE)$/;

  function store(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }

  function skipped(node) {
    for (var el = node.parentElement; el; el = el.parentElement) {
      if (SKIP.test(el.tagName.toUpperCase())) return true;
      if (el.hasAttribute('data-no-deseret')) return true;
      if (el.classList && (el.classList.contains('dz-word') || el.classList.contains('dz-over'))) return true;
      var lang = el.getAttribute('lang');
      if (lang && el !== root && !/^en(-|$)/i.test(lang)) return true;
    }
    return false;
  }

  function load() {
    if (engine) return Promise.resolve(engine);
    if (!loading) {
      loading = Promise.all([
        import('/deseret/lib/index.mjs'),
        fetch('/deseret/words.tsv').then(function (r) { return r.text(); }),
        fetch('/deseret/heteronyms.json').then(function (r) { return r.json(); }),
        fetch('/deseret/overrides.json').then(function (r) { return r.json(); })
      ]).then(function (a) {
        engine = a[0].createTransliterator({ words: a[0].parseWords(a[1]), heteronyms: a[2], overrides: a[3] });
        return engine;
      });
    }
    return loading;
  }

  function convert(scope) {
    if (!engine) return;
    var walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT);
    var nodes = [], n;
    while ((n = walker.nextNode())) nodes.push(n);
    nodes.forEach(function (node) {
      var v = node.nodeValue;
      if (original.has(node) || !/[A-Za-z]/.test(v) || skipped(node)) return;
      var out = engine.text(v);
      if (out !== v) { original.set(node, v); node.nodeValue = out; }
    });
  }

  function restore() {
    original.forEach(function (v, node) { if (node.isConnected) node.nodeValue = v; });
    original.clear();
  }

  function watch() {
    if (observer) return;
    observer = new MutationObserver(function (muts) {
      muts.forEach(function (m) {
        m.addedNodes.forEach(function (added) {
          if (added.nodeType === 1) convert(added);
          else if (added.nodeType === 3 && added.parentNode) convert(added.parentNode);
        });
      });
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  function set(next, persist) {
    on = next;
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    root.setAttribute('data-script', on ? 'deseret' : 'latin');
    if (persist) store(on ? 'deseret' : 'latin');
    if (on) {
      btn.setAttribute('aria-busy', 'true');
      load().then(function () {
        if (!on) return;
        convert(document.body);
        watch();
      }).catch(function () {
        on = false;
        btn.setAttribute('aria-pressed', 'false');
        root.setAttribute('data-script', 'latin');
      }).then(function () { btn.removeAttribute('aria-busy'); });
    } else {
      if (observer) { observer.disconnect(); observer = null; }
      restore();
    }
  }

  btn.addEventListener('click', function () { set(!on, true); });
  if (stored() === 'deseret') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { set(true, false); });
    else set(true, false);
  }
})();
