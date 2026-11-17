// /connect: Claude / ChatGPT tabs (deep link #claude, #chatgpt) and copy buttons.
(function () {
  var tabs = ['claude', 'chatgpt'];
  function show(id) {
    tabs.forEach(function (t) {
      var on = t === id;
      var tab = document.getElementById('tab-' + t), panel = document.getElementById('panel-' + t);
      if (!tab || !panel) return;
      tab.setAttribute('aria-selected', on ? 'true' : 'false');
      panel.hidden = !on;
    });
  }
  tabs.forEach(function (t) {
    var el = document.getElementById('tab-' + t);
    if (el) el.addEventListener('click', function () {
      show(t);
      try { history.replaceState(null, '', '#' + t); } catch (e) {}
    });
  });
  function sync() { var h = location.hash.slice(1); if (tabs.indexOf(h) > -1) show(h); }
  window.addEventListener('hashchange', sync);
  sync();

  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var status = b.parentNode.querySelector('[role=status]');
      function done() {
        b.textContent = 'Copied';
        if (status) status.textContent = 'Copied to clipboard';
        setTimeout(function () { b.textContent = 'Copy'; if (status) status.textContent = ''; }, 1800);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(b.getAttribute('data-copy')).then(done, function () {});
      }
    });
  });
})();
