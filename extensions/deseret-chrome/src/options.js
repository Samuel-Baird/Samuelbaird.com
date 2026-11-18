(async () => {
  const { FONTS, getSettings, setSettings } = self.DSRT_SHARED;
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  let s = await getSettings();
  const MAX = 8 * 1024 * 1024;

  async function preview() {
    const pick = FONTS.find((f) => f.id === s.font) || FONTS[0];
    let fam = 'system-ui';
    try {
      let src;
      if (pick.id === 'custom') {
        const { customFont } = await chrome.storage.local.get('customFont');
        if (customFont?.data) src = Uint8Array.from(atob(customFont.data), (c) => c.charCodeAt(0)).buffer;
      } else if (pick.file) src = `url(${pick.file})`;
      if (src) { const f = new FontFace(`o-${pick.id}-${Date.now()}`, src); document.fonts.add(f); await f.load(); fam = `"${f.family}"`; }
    } catch { /* system fallback */ }
    $('preview').style.fontFamily = `${fam}, "Segoe UI Historic", system-ui`;
    $('preview').style.fontSize = `${(s.size / 100) * 1.4}rem`;
  }

  function renderSites() {
    const entries = Object.entries(s.sites).sort(([a], [b]) => a.localeCompare(b));
    $('no-sites').hidden = entries.length > 0;
    $('sites').innerHTML = entries.map(([h, v]) => `<li><span>${esc(h)}</span> <span class="muted">${v ? 'always' : 'never'}</span> <button type="button" class="small-btn" data-host="${esc(h)}">Remove</button></li>`).join('');
  }
  $('sites').addEventListener('click', async (e) => {
    const h = e.target.dataset.host;
    if (!h) return;
    delete s.sites[h];
    await setSettings({ sites: s.sites });
    renderSites();
  });

  async function renderCustom() {
    const { customFont } = await chrome.storage.local.get('customFont');
    $('custom-status').textContent = customFont ? `Using ${customFont.name} (${Math.round(customFont.size / 1024)} KB).` : 'No font uploaded.';
    $('font-remove').hidden = !customFont;
  }

  $('everywhere').checked = s.everywhere;
  $('strict').checked = s.strict;
  for (const r of document.querySelectorAll('input[name=spelling]')) r.checked = r.value === s.spelling;
  $('font').innerHTML = FONTS.map((f) => `<option value="${f.id}">${esc(f.name)}${f.style ? ` (${esc(f.style)})` : ''}</option>`).join('');
  $('font').value = s.font;
  $('size').value = s.size;
  $('size-out').textContent = `${s.size}%`;
  $('font-credits').textContent = FONTS.filter((f) => f.file).map((f) => `${f.name} (${f.license})`).join(', ');

  $('everywhere').addEventListener('change', () => setSettings({ everywhere: $('everywhere').checked }));
  $('strict').addEventListener('change', () => setSettings({ strict: $('strict').checked }));
  for (const r of document.querySelectorAll('input[name=spelling]')) r.addEventListener('change', () => setSettings({ spelling: r.value }));
  $('font').addEventListener('change', () => { s.font = $('font').value; setSettings({ font: s.font }); preview(); });
  $('size').addEventListener('input', () => { s.size = +$('size').value; $('size-out').textContent = `${s.size}%`; preview(); });
  $('size').addEventListener('change', () => setSettings({ size: s.size }));

  $('font-file').addEventListener('change', async () => {
    const file = $('font-file').files[0];
    if (!file) return;
    if (file.size > MAX) { $('custom-status').textContent = 'That file is over 8 MB.'; return; }
    const buf = await file.arrayBuffer();
    try {
      const test = new FontFace('upload-test', buf);
      await test.load();
    } catch {
      $('custom-status').textContent = 'That file isn’t a font Chrome can read.';
      return;
    }
    let bin = '';
    const bytes = new Uint8Array(buf);
    for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
    await chrome.storage.local.set({ customFont: { name: file.name, size: file.size, data: btoa(bin) } });
    s.font = 'custom';
    $('font').value = 'custom';
    await setSettings({ font: 'custom' });
    $('font-file').value = '';
    renderCustom();
    preview();
  });
  $('font-remove').addEventListener('click', async () => {
    await chrome.storage.local.remove('customFont');
    if (s.font === 'custom') { s.font = 'noto'; $('font').value = 'noto'; await setSettings({ font: 'noto' }); }
    renderCustom();
    preview();
  });

  chrome.storage.onChanged.addListener(async (_c, area) => { if (area === 'sync') { s = await getSettings(); renderSites(); } });
  renderSites();
  renderCustom();
  preview();
})();
