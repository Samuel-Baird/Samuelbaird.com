(async () => {
  const { FONTS, getSettings, setSettings } = self.DSRT_SHARED;
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  let s = await getSettings();

  async function preview() {
    const pick = FONTS.find((f) => f.id === s.font) || FONTS[0];
    let fam = 'system-ui';
    try {
      const src = pick.file ? `url(${pick.file})` : null;
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


  $('everywhere').checked = s.everywhere;
  $('strict').checked = s.strict;
  $('font').innerHTML = FONTS.map((f) => `<option value="${f.id}">${esc(f.name)}${f.style ? ` (${esc(f.style)})` : ''}</option>`).join('');
  $('font').value = s.font;
  $('size').value = s.size;
  $('size-out').textContent = `${s.size}%`;
  $('font-credits').textContent = FONTS.filter((f) => f.file).map((f) => `${f.name} (${f.license})`).join(', ');

  $('everywhere').addEventListener('change', () => setSettings({ everywhere: $('everywhere').checked }));
  $('strict').addEventListener('change', () => setSettings({ strict: $('strict').checked }));
  $('font').addEventListener('change', () => { s.font = $('font').value; setSettings({ font: s.font }); preview(); });
  $('size').addEventListener('input', () => { s.size = +$('size').value; $('size-out').textContent = `${s.size}%`; preview(); });
  $('size').addEventListener('change', () => setSettings({ size: s.size }));


  chrome.storage.onChanged.addListener(async (_c, area) => { if (area === 'sync') { s = await getSettings(); renderSites(); } });
  renderSites();
  preview();
})();
