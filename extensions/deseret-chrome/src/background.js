// Background worker: owns the transliteration engine (the same one as Deseret MCP and the Deseret
// Wiki: CMU Pronouncing Dictionary + hand overrides), so each tab doesn't load a 3.6 MB dictionary.
// Chrome stops idle workers; the engine reloads in ~100 ms on the next request.
import './shared.js';
import { createEngine, parseDict, historical1868 } from './engine/dsrt.mjs';

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
async function convert({ texts, direction, spelling, strict }) {
  const e = await engine();
  const opts = { strict: !!strict, ...(spelling === 'historical' ? historical1868 : {}) };
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

chrome.runtime.onMessage.addListener((msg, _sender, reply) => {
  if (msg?.type === 'convert') {
    convert(msg).then(reply, (err) => reply({ error: String(err?.message || err) }));
    return true; // async reply
  }
  return false;
});

// Keyboard shortcut and context menu both just tell the tab's content script to toggle.
const toggleTab = (tabId) => chrome.tabs.sendMessage(tabId, { type: 'toggle' }).catch(() => {});
chrome.commands.onCommand.addListener((cmd, tab) => { if (cmd === 'toggle-page' && tab?.id) toggleTab(tab.id); });

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({ id: 'toggle-page', title: 'Switch page between Latin and Deseret', contexts: ['page', 'selection'] });
});
chrome.contextMenus.onClicked.addListener((info, tab) => { if (info.menuItemId === 'toggle-page' && tab?.id) toggleTab(tab.id); });
