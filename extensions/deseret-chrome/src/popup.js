(async () => {
  const { FONTS, getSettings, setSettings } = self.DSRT_SHARED;
  const $ = (id) => document.getElementById(id);
  let settings = await getSettings();
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  // ---------- fonts (preview uses the same files the page will) ----------
  const fontFaces = new Map();
  async function previewFont() {
    const pick = FONTS.find((f) => f.id === settings.font) || FONTS[0];
    let fam = 'system-ui';
    try {
      if (pick.file || pick.id === 'custom') {
        if (!fontFaces.has(pick.id)) {
          let src;
          if (pick.id === 'custom') {
            const { customFont } = await chrome.storage.local.get('customFont');
            if (customFont?.data) src = Uint8Array.from(atob(customFont.data), (c) => c.charCodeAt(0)).buffer;
          } else src = `url(${pick.file})`;
          if (src) { const f = new FontFace(`p-${pick.id}`, src); document.fonts.add(f); await f.load(); fontFaces.set(pick.id, f); }
        }
        if (fontFaces.has(pick.id)) fam = `"p-${pick.id}"`;
      }
    } catch { /* fall back to system */ }
    for (const el of document.querySelectorAll('.preview, .output')) {
      el.style.fontFamily = `${fam}, "Segoe UI Historic", system-ui`;
      el.style.fontSize = `${(settings.size / 100) * 1.1}rem`;
    }
  }

  $('font').innerHTML = FONTS.map((f) => `<option value="${f.id}">${f.name}${f.style ? ` (${f.style})` : ''}</option>`).join('');
  $('font').value = settings.font;
  $('size').value = settings.size;
  $('size-out').textContent = `${settings.size}%`;
  for (const r of document.querySelectorAll('input[name=spelling]')) r.checked = r.value === settings.spelling;

  $('font').addEventListener('change', async () => { settings.font = $('font').value; await setSettings({ font: settings.font }); previewFont(); });
  $('size').addEventListener('input', () => { $('size-out').textContent = `${$('size').value}%`; settings.size = +$('size').value; previewFont(); });
  $('size').addEventListener('change', () => setSettings({ size: +$('size').value }));
  for (const r of document.querySelectorAll('input[name=spelling]')) {
    r.addEventListener('change', async () => { settings.spelling = r.value; await setSettings({ spelling: r.value }); convertBox(); });
  }
  previewFont();

  // ---------- this page ----------
  let host = '';
  let native = 'latin'; // the script the page is written in, captured before we change anything
  const send = (msg) => chrome.tabs.sendMessage(tab.id, msg);
  function showStatus(st) {
    const shown = !st.active ? native : st.direction === 'latin' ? 'latin' : 'dsrt';
    $('to-latin').setAttribute('aria-pressed', String(shown === 'latin'));
    $('to-dsrt').setAttribute('aria-pressed', String(shown === 'dsrt'));
    $('page-status').textContent = !st.active ? (native === 'dsrt' ? 'This page is written in Deseret. Choose Latin to read it in Latin letters.' : '')
      : st.direction === 'latin' ? 'Showing Deseret text in Latin letters.'
      : `${st.stats.words.toLocaleString()} words in Deseret${st.stats.unknown ? `, ${st.stats.unknown.toLocaleString()} left in Latin (not in the dictionary)` : ''}.`;
  }
  try {
    const st = await send({ type: 'status' });
    host = st.host;
    native = st.active ? (st.direction === 'latin' ? 'dsrt' : 'latin') : st.suggested === 'latin' ? 'dsrt' : 'latin';
    $('host').textContent = host || 'this site';
    $('always').checked = settings.sites[host] === true;
    showStatus(st);
    // On a Deseret page, the "Latin" button converts Deseret -> Latin instead of switching off.
    $('to-latin').addEventListener('click', async () => showStatus(await send(native === 'dsrt' ? { type: 'set', direction: 'latin' } : { type: 'set' })));
    $('to-dsrt').addEventListener('click', async () => showStatus(await send(native === 'dsrt' ? { type: 'set' } : { type: 'set', direction: 'dsrt' })));
    $('always').addEventListener('change', async () => {
      const sites = { ...settings.sites };
      if ($('always').checked) sites[host] = true; else delete sites[host];
      settings.sites = sites;
      await setSettings({ sites });
      if ($('always').checked) showStatus(await send({ type: 'set', direction: 'dsrt' }));
    });
  } catch {
    for (const id of ['to-latin', 'to-dsrt', 'always']) $(id).disabled = true;
    $('page-status').textContent = 'Chrome doesn’t let extensions change this page (browser pages and the Web Store). Reload the tab if you just installed the extension.';
  }

  // ---------- YouTube captions ----------
  const capBtns = [...document.querySelectorAll('[data-cap]')];
  const showCap = (m) => capBtns.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.cap === m)));
  showCap(settings.captions);
  capBtns.forEach((b) => b.addEventListener('click', async () => {
    showCap(b.dataset.cap);
    await setSettings({ captions: b.dataset.cap });
    chrome.tabs.sendMessage(tab.id, { type: 'captions-set', mode: b.dataset.cap }).catch(() => {}); // turns YouTube's CC on
  }));

  // ---------- converter box ----------
  let t;
  async function convertBox() {
    const text = $('input').value;
    if (!text.trim()) { $('output').textContent = ''; $('copy').disabled = true; $('conv-note').textContent = ''; return; }
    const direction = /[\u{10400}-\u{1044F}]/u.test(text) && !/\p{Script=Latin}/u.test(text) ? 'latin' : 'dsrt';
    const res = await chrome.runtime.sendMessage({ type: 'convert', texts: [text], direction, spelling: settings.spelling, strict: settings.strict });
    if (res?.error) { $('conv-note').textContent = res.error; return; }
    $('output').textContent = res.out[0];
    $('copy').disabled = false;
    $('conv-note').textContent = direction === 'latin' ? 'Deseret → Latin' : res.stats.unknown ? `${res.stats.unknown} word(s) not in the dictionary, left in Latin.` : 'English → Deseret';
  }
  $('input').addEventListener('input', () => { clearTimeout(t); t = setTimeout(convertBox, 200); });
  $('copy').addEventListener('click', async () => {
    await navigator.clipboard.writeText($('output').textContent);
    $('copy').textContent = 'Copied';
    setTimeout(() => { $('copy').textContent = 'Copy'; }, 1200);
  });
  $('input').focus();
})();
