// Browser script for the GSA review page, served at /gsa/review.js.
// The function below never runs in the Worker; it is serialized into the response.

function client() {
  const details = document.querySelector('.details[data-work]');
  if (!details) return;
  const work = details.dataset.work;
  const DEBOUNCE = 600;
  const pending = new Set();

  function indicator(control) {
    return control.closest('.row').querySelector('.saved');
  }
  function show(el, state, text) {
    clearTimeout(el._fade);
    el.className = 'saved show ' + state;
    el.textContent = text;
    // The check stays a few seconds, then fades; errors stay until the next save.
    if (state === 'ok') el._fade = setTimeout(() => el.classList.remove('show'), 3500);
  }

  async function post(field, value) {
    const res = await fetch('/gsa/work/' + encodeURIComponent(work) + '/edit', {
      method: 'POST', credentials: 'same-origin',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({field, value}),
    });
    let body = {};
    try { body = await res.json(); } catch { /* non-JSON error page */ }
    if (res.status === 401 || res.redirected) throw new Error('signed out; reload the page');
    if (!res.ok) throw new Error(body.error || 'server error ' + res.status);
    return body;
  }

  function applied(field, result) {
    // Keep the decision form bound to the version the reviewer is looking at.
    for (const input of document.querySelectorAll('input[name="revision"]')) input.value = result.revision;
    if (result.decisionsCleared) document.querySelector('.reset-note').hidden = false;
    if (field === 'title') { document.getElementById('page-title').textContent = result.value; document.title = result.value + ' · GSA'; }
    if (field === 'citation') document.getElementById('page-citation').textContent = result.value;
  }

  // One save in flight per field; only the latest typed value is sent next.
  function saver(field, control) {
    let timer = null, running = false, queued = null;
    async function run() {
      if (running || queued === null) return;
      running = true;
      const value = queued; queued = null;
      show(indicator(control), 'busy', 'Saving…');
      try {
        const result = await post(field, value);
        applied(field, result);
        if (queued === null) show(indicator(control), 'ok', 'Changes saved');
      } catch (error) {
        show(indicator(control), 'err', 'Not saved: ' + error.message);
      } finally {
        running = false;
        if (queued !== null) run(); else pending.delete(field);
      }
    }
    return {
      schedule(value, now) {
        queued = value; pending.add(field);
        clearTimeout(timer);
        if (now) run(); else timer = setTimeout(run, DEBOUNCE);
      },
      flush() { if (queued !== null) { clearTimeout(timer); run(); } },
    };
  }

  for (const control of details.querySelectorAll('[data-field]')) {
    const s = saver(control.dataset.field, control);
    let last = control.value;
    control.addEventListener('input', () => { if (control.value !== last) { last = control.value; s.schedule(control.value); } });
    control.addEventListener('blur', () => s.flush());
  }
  window.addEventListener('beforeunload', event => { if (pending.size) { event.preventDefault(); event.returnValue = ''; } });

  // ---- folder explorer -------------------------------------------------------------
  const browse = document.getElementById('browse');
  const panel = document.getElementById('explorer');
  const destination = document.getElementById('f-destination');
  if (!browse || !panel) return;
  const crumbs = panel.querySelector('.crumbs'), list = panel.querySelector('.folders');
  const filter = panel.querySelector('.filter'), snapshot = panel.querySelector('.snapshot');
  const selectButton = panel.querySelector('[data-act="select"]');
  const cache = new Map();
  let current = null;

  async function folder(id) {
    if (!cache.has(id)) {
      const res = await fetch('/gsa/folders/' + encodeURIComponent(id), {credentials: 'same-origin'});
      const body = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(body.error || 'Could not load folders');
      cache.set(id, body);
    }
    return cache.get(id);
  }
  function el(tag, props, text) {
    const node = document.createElement(tag);
    Object.assign(node, props || {});
    if (text != null) node.textContent = text;
    return node;
  }
  function renderList() {
    const q = filter.value.trim().toLowerCase();
    list.replaceChildren();
    const kids = current.children.filter(k => !q || k.name.toLowerCase().includes(q));
    if (!kids.length) list.append(el('li', {className: 'empty'}, q ? 'No folders match.' : 'No subfolders.'));
    for (const kid of kids) {
      const button = el('button', {type: 'button', title: 'Open ' + kid.name});
      button.setAttribute('role', 'option');
      button.append(el('span', {className: 'n'}, kid.name), el('span', {className: 'c'}, kid.count ? kid.count + ' ›' : ''));
      button.addEventListener('click', () => open(kid.id));
      const item = el('li');
      item.append(button);
      list.append(item);
    }
  }
  async function open(id) {
    list.replaceChildren(el('li', {className: 'empty'}, 'Loading…'));
    try {
      current = await folder(id);
    } catch (error) {
      list.replaceChildren(el('li', {className: 'empty'}, error.message));
      return;
    }
    crumbs.replaceChildren();
    current.trail.forEach((step, i) => {
      if (i) crumbs.append(el('span', {}, '/'));
      const b = el('button', {type: 'button'}, step.name);
      if (i === current.trail.length - 1) b.setAttribute('aria-current', 'location');
      b.addEventListener('click', () => open(step.id));
      crumbs.append(b);
    });
    filter.value = '';
    renderList();
    const isRoot = current.id === current.root;
    selectButton.disabled = isRoot;
    selectButton.textContent = isRoot ? 'Open a shelf to select it' : 'Select “' + current.name + '”';
    snapshot.textContent = 'Folder list as of ' + String(current.at).slice(0, 10);
  }
  function toggle(show) {
    panel.hidden = !show;
    browse.setAttribute('aria-expanded', String(show));
    if (show) {
      // Start in the folder's parent when the current destination is known.
      folder(destination.dataset.folderId).then(f => open(f.trail.length > 1 ? f.trail[f.trail.length - 2].id : 'root'), () => open('root'));
    }
  }
  browse.addEventListener('click', () => toggle(panel.hidden));
  panel.querySelector('[data-act="cancel"]').addEventListener('click', () => toggle(false));
  filter.addEventListener('input', renderList);
  selectButton.addEventListener('click', async () => {
    const chosen = current;
    toggle(false);
    show(indicator(destination), 'busy', 'Saving…');
    try {
      const result = await post('destination', chosen.id);
      destination.value = result.value;
      destination.dataset.folderId = chosen.id;
      applied('destination', result);
      show(indicator(destination), 'ok', 'Changes saved');
    } catch (error) {
      show(indicator(destination), 'err', 'Not saved: ' + error.message);
    }
  });
}

export const reviewScript = `(${client})();\n`;
