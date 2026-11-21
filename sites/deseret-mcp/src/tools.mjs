// Tool definitions and the MCP JSON-RPC handler, shared by the hosted endpoint (api/mcp.js) and the
// local stdio server (bin/deseret-mcp.mjs). The local server adds deseret_file, which reads and writes
// files on the user's machine; the hosted one never touches a filesystem path given by a client.
import fs from 'node:fs';
import path from 'node:path';
import { load } from './load.mjs';
import { KINDS } from './wiki.mjs';

export const SITE = 'https://deseret.wiki';
export const VERSION = '0.1.0';
const VERSIONS = ['2025-11-25', '2025-06-18', '2025-03-26', '2024-11-05'];
const HOSTED_LIMIT = 100_000;

const INSTRUCTIONS =
  'Deseret Alphabet tools. TRANSLITERATE: to_deseret(text) writes English in the Deseret Alphabet from the CMU Pronouncing Dictionary ' +
  '(the method the Deseret Wiki uses), deseret_word(word) explains one word letter by letter, from_deseret(text) reads Deseret back into ' +
  'Latin letters. Every result lists the words it could not spell (left in Latin letters) and the ones it built from their parts; tell the ' +
  'user about both. ANSWER QUESTIONS: search_wiki(query) searches every source on deseret.wiki (the article, library, sermons, resources, ' +
  'videos, fonts, books, quotes, letter chart); read_wiki(id) returns the full text. Base answers on what these return and cite the ' +
  'deseret.wiki url (and source_url where given). Independent project, not affiliated with The Church of Jesus Christ of Latter-day Saints.';

const spellingsProp = {
  type: 'object',
  additionalProperties: { type: 'string' },
  description: 'Optional per-call spellings: word -> ARPAbet phones ("R EH1 D") or Deseret text. Use to fix a heteronym or a name.',
};
const formatProp = { type: 'string', enum: ['plain', 'markdown', 'html'], description: 'plain (default), markdown (keeps code, links, URLs, frontmatter and footnote marks) or html (text nodes only).' };
const styleProp = {
  type: 'object',
  properties: {
    ah: { type: 'string', enum: ['three', 'one'], description: 'three (default): 𐐂 cot, 𐐃 caught, 𐐉 Boston, as the dictionary gives them. one: every ah is 𐐂 (and "or" is 𐐬𐑉), as most American English says it.' },
    syllabic: { type: 'boolean', description: 'Default true: a word that sounds like a letter\'s name is that one letter (the 𐑄, a 𐐪, bee 𐐺, gay 𐑀). false spells them in full.' },
    initialisms: { type: 'boolean', description: 'Default true: initialisms (USA, FBI) are written with the first sound of each word they stand for (𐐧𐐝𐐊, 𐐙𐐒𐐆); acronyms said as words (NASA) are spelled by sound. false spells initialisms by their letters\' names.' },
  },
  additionalProperties: false,
  description: 'Optional spelling conventions (deseretalphabet.info, About: rules 1 and 10 and the note on the three ah letters).',
};
const strictProp = { type: 'boolean', description: 'Leave words built from their parts (e.g. un- + faithful + -ness) in Latin letters instead of spelling them. Default false.' };

function report(r, cap = 200) {
  const out = {
    stats: r.stats,
    unknown: r.unknown.slice(0, cap),
    derived: r.derived.slice(0, cap),
  };
  if (r.unknown.length > cap) out.unknown_truncated = r.unknown.length;
  if (r.derived.length > cap) out.derived_truncated = r.derived.length;
  if (r.heteronyms.length) out.heteronyms = r.heteronyms;
  out.note = r.unknown.length
    ? `${r.unknown.length} distinct word(s) had no Deseret spelling and were left in Latin letters (listed in "unknown"). Pass "spellings" to supply them.`
    : 'Every word was transliterated.';
  if (r.derived.length) out.note += ` ${r.derived.length} word(s) are not in the dictionary and were spelled from their parts (listed in "derived"); check them.`;
  return out;
}

const detectFormat = (p) => (/\.(md|markdown|mdx)$/i.test(p) ? 'markdown' : /\.x?html?$/i.test(p) ? 'html' : 'plain');

function tools({ local }) {
  const T = [
    {
      name: 'to_deseret',
      title: 'English to Deseret',
      description:
        'Transliterate English text (a word, a passage or a whole document) into the Deseret Alphabet. Spellings come from the CMU Pronouncing ' +
        'Dictionary (126,052 words) mapped sound by sound to Deseret letters, with hand corrections, as on deseret.wiki; capitals are kept. ' +
        '"the" is the single letter 𐑄, "a" is 𐐪, and a word that sounds like a letter\'s name is that one letter (be 𐐺, tea 𐐻, gay 𐑀). ' +
        'Initialisms take the first sound of each word they stand for (USA 𐐧𐐝𐐊); acronyms said as words are spelled by sound (NASA 𐐤𐐈𐐝𐐊). ' +
        'Words the dictionary lacks are spelled from their parts where possible (listed in "derived"); words with no spelling stay in Latin ' +
        'letters and are listed in "unknown". This is a change of script, not a translation.',
      inputSchema: {
        type: 'object',
        properties: { text: { type: 'string', description: `English text (up to ${HOSTED_LIMIT.toLocaleString('en')} characters).` }, format: formatProp, strict: strictProp, spellings: spellingsProp, style: styleProp },
        required: ['text'],
      },
      run({ text, format, strict, spellings, style }) {
        const input = String(text ?? '');
        if (!input.trim()) throw new Error('text is required');
        if (input.length > HOSTED_LIMIT) throw new Error(`text is ${input.length} characters; the limit is ${HOSTED_LIMIT}. Split it${local ? ', or use deseret_file' : ''}.`);
        const r = load().engine.text(input, { format: format || 'plain', strict: !!strict, spellings, style });
        return { deseret: r.deseret, ...report(r) };
      },
    },
    {
      name: 'deseret_word',
      title: 'Explain one word',
      description:
        'Spell one English word in the Deseret Alphabet and explain it: the ARPAbet phones, each letter with its name, sound and key word, ' +
        'every dictionary pronunciation (for heteronyms such as read, live, lead) and, for words not in the dictionary, the parts it was built from.',
      inputSchema: { type: 'object', properties: { word: { type: 'string', description: 'One English word.' } }, required: ['word'] },
      run({ word }) {
        const w = String(word ?? '').trim();
        if (!w) throw new Error('word is required');
        if (/\s/.test(w)) throw new Error('one word only; use to_deseret for text');
        return load().engine.explain(w);
      },
    },
    {
      name: 'from_deseret',
      title: 'Deseret to English',
      description:
        'Read Deseret Alphabet text back into Latin letters by looking each word up in the reversed dictionary. Deseret writes sounds, so ' +
        'homophones are ambiguous (𐐺𐐴 is by, buy or bye): the most likely word is chosen and the alternatives are listed in "ambiguous". ' +
        'Words that match no dictionary spelling (older or personal spellings, names) are respelled letter by letter and listed in "respelled".',
      inputSchema: { type: 'object', properties: { text: { type: 'string', description: 'Text containing Deseret letters (U+10400 to U+1044F).' } }, required: ['text'] },
      run({ text }) {
        const input = String(text ?? '');
        if (!/[\u{10400}-\u{1044F}]/u.test(input)) throw new Error('text has no Deseret letters');
        if (input.length > HOSTED_LIMIT) throw new Error(`text is ${input.length} characters; the limit is ${HOSTED_LIMIT}.`);
        const r = load().engine.fromDeseret(input);
        return { latin: r.latin, stats: r.stats, ambiguous: r.ambiguous.slice(0, 100), respelled: r.respelled.slice(0, 100) };
      },
    },
    {
      name: 'search_wiki',
      title: 'Search the Deseret Wiki',
      description:
        'Search every source on deseret.wiki for a question about the Deseret Alphabet: the encyclopedia article (by section), the library ' +
        '(hosted PDFs, sermons and conference addresses, further reading), resources, videos, fonts, books & prints, quotes and the letter ' +
        'chart. Returns ranked hits with a snippet, the deseret.wiki url to cite and, where the wiki links out, the original source_url. ' +
        'Use read_wiki(id) for the full text.',
      inputSchema: {
        type: 'object',
        properties: {
          query: { type: 'string', description: 'Words to search for, in English or Deseret.' },
          kind: { type: 'string', enum: Object.keys(KINDS), description: 'Optional: limit to one kind of source.' },
          limit: { type: 'integer', minimum: 1, maximum: 25, description: 'Max results (default 8).' },
        },
        required: ['query'],
      },
      run({ query, kind, limit }) {
        const { engine, wiki } = load();
        let q = String(query ?? '');
        // a query in Deseret also searches its Latin reading
        if (/[\u{10400}-\u{1044F}]/u.test(q)) q += ' ' + engine.fromDeseret(q).latin.replace(/[\u{10400}-\u{1044F}]+/gu, ' ');
        const r = wiki.search(q, { kind, limit });
        return { ...r, query: String(query) };
      },
    },
    {
      name: 'read_wiki',
      title: 'Read a Deseret Wiki record',
      description:
        'Full text and details of one record from search_wiki or wiki_contents (an article section, library item, video, font, book, quote, ' +
        'letter...), with a ready-made citation, its deseret.wiki url, any source_url and licence. Article sections also give the previous and next section.',
      inputSchema: {
        type: 'object',
        properties: { id: { type: 'string', description: 'Record id, e.g. "article:wiki:deseret-alphabet#history".' }, max_chars: { type: 'integer', minimum: 500, maximum: 60000, description: 'Truncate long text (default 12000).' } },
        required: ['id'],
      },
      run({ id, max_chars }) {
        return load().wiki.read(id, { max_chars });
      },
    },
    {
      name: 'wiki_contents',
      title: 'Deseret Wiki contents',
      description: 'What the Deseret Wiki holds: with no kind, the kinds of source and their counts; with a kind, every record of it (id, title, url).',
      inputSchema: { type: 'object', properties: { kind: { type: 'string', enum: Object.keys(KINDS) } } },
      run({ kind }) {
        return load().wiki.contents(kind);
      },
    },
  ];
  if (local) {
    T.push({
      name: 'deseret_file',
      title: 'Transliterate a file',
      description:
        'Transliterate a whole text, Markdown or HTML file on this computer into the Deseret Alphabet and write the result next to it ' +
        '(name.dsrt.md, or output_path). Markdown frontmatter, code, links, URLs and footnote marks, and HTML tags, stay as they are. ' +
        'Returns the output path and the words it could not spell, not the text itself.',
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: false },
      inputSchema: {
        type: 'object',
        properties: {
          path: { type: 'string', description: 'Path of the file to read.' },
          output_path: { type: 'string', description: 'Where to write (default: beside the input, with .dsrt before the extension). An existing file is only replaced if overwrite is true.' },
          overwrite: { type: 'boolean', description: 'Replace output_path if it exists (default false).' },
          format: formatProp,
          strict: strictProp,
          spellings: spellingsProp,
          style: styleProp,
        },
        required: ['path'],
      },
      run({ path: p, output_path, overwrite, format, strict, spellings, style }) {
        const src = path.resolve(String(p ?? ''));
        if (!p || !fs.existsSync(src) || !fs.statSync(src).isFile()) throw new Error(`no such file: ${src}`);
        const fmt = format || detectFormat(src);
        const ext = path.extname(src);
        const out = path.resolve(output_path ? String(output_path) : src.slice(0, src.length - ext.length) + '.dsrt' + ext);
        if (out === src) throw new Error('output_path is the input file; choose another path');
        if (fs.existsSync(out) && !overwrite) throw new Error(`${out} already exists; pass overwrite: true to replace it`);
        const r = load().engine.text(fs.readFileSync(src, 'utf8'), { format: fmt, strict: !!strict, spellings, style });
        fs.mkdirSync(path.dirname(out), { recursive: true });
        fs.writeFileSync(out, r.deseret, 'utf8');
        return { ok: true, input_path: src, output_path: out, format: fmt, ...report(r) };
      },
    });
  }
  return T;
}

const ok = (id, result) => ({ jsonrpc: '2.0', id, result });
const err = (id, code, message) => ({ jsonrpc: '2.0', id, error: { code, message } });

/** Build a JSON-RPC message handler. local: true adds the file tool (stdio server only). */
export function createHandler({ local = false } = {}) {
  const T = tools({ local });
  return async function handle(msg) {
    const { id, method, params } = msg || {};
    if (id === undefined || id === null) return null; // notification
    switch (method) {
      case 'initialize': {
        const want = params && params.protocolVersion;
        return ok(id, {
          protocolVersion: VERSIONS.includes(want) ? want : VERSIONS[0],
          capabilities: { tools: {} },
          serverInfo: { name: 'deseret', title: 'Deseret MCP: the Deseret Alphabet', version: VERSION, websiteUrl: SITE },
          instructions: INSTRUCTIONS,
        });
      }
      case 'ping':
        return ok(id, {});
      case 'tools/list':
        return ok(id, {
          tools: T.map(({ name, title, description, inputSchema, annotations }) => ({
            name, title, description, inputSchema,
            annotations: annotations || { readOnlyHint: true, openWorldHint: false },
          })),
        });
      case 'tools/call': {
        const tool = T.find((t) => t.name === (params && params.name));
        if (!tool) return err(id, -32602, `Unknown tool: ${params && params.name}`);
        try {
          const result = await tool.run((params && params.arguments) || {});
          return ok(id, { content: [{ type: 'text', text: JSON.stringify(result) }], structuredContent: result });
        } catch (e) {
          return ok(id, { isError: true, content: [{ type: 'text', text: String((e && e.message) || e) }] });
        }
      }
      default:
        return err(id, -32601, `Method not found: ${method}`);
    }
  };
}
