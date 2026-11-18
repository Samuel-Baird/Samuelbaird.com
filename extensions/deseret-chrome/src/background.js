// Background worker: owns the transliteration engine (the same one as Deseret MCP and the Deseret
// Wiki: CMU Pronouncing Dictionary + hand overrides), so each tab doesn't load a 3.6 MB dictionary.
// Chrome stops idle workers; the engine reloads in ~100 ms on the next request.
import './shared.js';
import { createEngine, parseDict } from './engine/dsrt.mjs';

let enginePromise;
function engine() {
  enginePromise ||= (async () => {
    const [tsv, overrides] = await Promise.all([
      fetch(chrome.runtime.getURL('engine/cmudict.tsv')).then((r) => r.text()),
      fetch(chrome.runtime.getURL('engine/overrides.json')).then((r) => r.json()),
    ]);
    const clean = Object.fromEntries(Object.entries(overrides).filter(([k]) => !k.startsWith('_')));
    return createEngine({ dict: parseDict(tsv), overrides: clean });
  })();
  return enginePromise;
}

// texts: string[] -> string[] in the same order. direction: 'dsrt' (Latin -> Deseret) | 'latin'.
async function convert({ texts, direction, strict }) {
  const e = await engine();
  const opts = { strict: !!strict };
  let words = 0, unknown = 0;
  const out = texts.map((t) => {
    if (direction === 'latin') return e.fromDeseret(t).latin;
    const r = e.text(t, opts);
    words += r.stats.words;
    unknown += r.stats.unknown;
    return r.deseret;
  });
  return { out, stats: { words, unknown } };
}

// Per-tab memory: once you switch a tab to Deseret, later pages on the same site in that tab load in
// Deseret too, until you switch it back or leave the site. Session storage survives worker restarts
// and is cleared when the browser closes.
const tabKey = (id) => `tab:${id}`;
chrome.tabs.onRemoved.addListener((id) => chrome.storage.session.remove(tabKey(id)));

chrome.runtime.onMessage.addListener((msg, sender, reply) => {
  if (msg?.type === 'convert') {
    convert(msg).then(reply, (err) => reply({ error: String(err?.message || err) }));
    return true; // async reply
  }
  const tabId = sender.tab?.id;
  if (msg?.type === 'tab-get' && tabId != null) {
    chrome.storage.session.get(tabKey(tabId)).then((r) => reply(r[tabKey(tabId)] || null));
    return true;
  }
  if (msg?.type === 'tab-set' && tabId != null) {
    const p = msg.active ? chrome.storage.session.set({ [tabKey(tabId)]: { host: msg.host, direction: msg.direction } }) : chrome.storage.session.remove(tabKey(tabId));
    p.then(() => reply(true));
    return true;
  }
  return false;
});

// Keyboard shortcut and context menu both just tell the tab's content script to toggle.
const toggleTab = (tabId) => chrome.tabs.sendMessage(tabId, { type: 'toggle' }).catch(() => {});
chrome.commands.onCommand.addListener((cmd, tab) => {
  if (!tab?.id) return;
  if (cmd === 'toggle-page') toggleTab(tab.id);
  if (cmd === 'cycle-captions') chrome.tabs.sendMessage(tab.id, { type: 'captions-cycle' }).catch(() => {});
});

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({ id: 'toggle-page', title: 'Switch page between Latin and Deseret', contexts: ['page', 'selection'] });
});
chrome.contextMenus.onClicked.addListener((info, tab) => { if (info.menuItemId === 'toggle-page' && tab?.id) toggleTab(tab.id); });
