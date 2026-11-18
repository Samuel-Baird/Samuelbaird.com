// Build the Chrome extension into dist/ (load it with chrome://extensions > Load unpacked > dist)
// and dist.zip (upload to the Chrome Web Store). Run: node extensions/deseret-chrome/build.mjs
//
// The transliteration engine and dictionary are copied from sites/deseret-mcp, so the extension, the
// MCP server and the Deseret Wiki always spell alike. Fonts are copied from the Deseret Wiki, only
// those whose licenses allow redistribution (OFL, public domain), with their license texts.
// Icons are drawn here (a gold skep on lamplight paper, the family's mark). No dependencies.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '..', '..');
const SRC = path.join(HERE, 'src');
const DIST = path.join(HERE, 'dist');
const MCP = path.join(REPO, 'sites', 'deseret-mcp');
const WIKI_FONTS = path.join(REPO, 'sites', 'deseret-wiki', 'public', 'fonts', 'files');

fs.rmSync(DIST, { recursive: true, force: true });
fs.cpSync(SRC, DIST, { recursive: true });

// ---------- engine ----------
const eng = path.join(DIST, 'engine');
fs.mkdirSync(eng, { recursive: true });
fs.copyFileSync(path.join(MCP, 'src', 'dsrt.mjs'), path.join(eng, 'dsrt.mjs'));
for (const f of ['cmudict.tsv', 'overrides.json', 'CMUDICT-LICENSE']) fs.copyFileSync(path.join(MCP, 'data', f), path.join(eng, f));

// ---------- fonts ----------
const fonts = path.join(DIST, 'fonts');
fs.mkdirSync(fonts, { recursive: true });
fs.copyFileSync(path.join(REPO, 'sites', 'samuelbaird.com', '_family', 'NotoSansDeseret.ttf'), path.join(fonts, 'NotoSansDeseret.ttf'));
for (const f of ['analecta.ttf', 'mellifera.otf', 'desalph.otf', 'nomada.otf']) fs.copyFileSync(path.join(WIKI_FONTS, f), path.join(fonts, f));
// The OFL text, taken from the Noto Sans Deseret package (zip entry "LICENSE", stored or deflated).
function zipEntry(zipPath, name) {
  const b = fs.readFileSync(zipPath);
  for (let i = 0; i + 30 < b.length; ) {
    if (b.readUInt32LE(i) !== 0x04034b50) break;
    const method = b.readUInt16LE(i + 8), csize = b.readUInt32LE(i + 18), nlen = b.readUInt16LE(i + 26), xlen = b.readUInt16LE(i + 28);
    const n = b.toString('utf8', i + 30, i + 30 + nlen);
    const start = i + 30 + nlen + xlen;
    if (n === name) { const data = b.subarray(start, start + csize); return method === 8 ? zlib.inflateRawSync(data) : data; }
    i = start + csize;
  }
  throw new Error(`${name} not found in ${zipPath}`);
}
const ofl = zipEntry(path.join(WIKI_FONTS, 'noto-sans.zip'), 'LICENSE').toString('utf8');
fs.writeFileSync(path.join(fonts, 'OFL-NotoSansDeseret.txt'), ofl);
const OFL_BODY = ofl.slice(ofl.indexOf('-----------------------------------------------------------'));
const credit = {
  'mellifera.otf': 'Mellifera Deseret, by Sigilante. Licensed under the SIL Open Font License 1.1.',
  'desalph.otf': 'desalph, by Kenneth R. Beesley and Fredrick R. Brennan. Licensed under the SIL Open Font License 1.1.',
  'nomada.otf': 'IDC Nomada, by N. E. Davis / Illinois Deseret Consortium. Licensed under the SIL Open Font License 1.1.',
};
for (const [file, line] of Object.entries(credit)) fs.writeFileSync(path.join(fonts, `OFL-${file.replace(/\.\w+$/, '')}.txt`), `${line}\n\n${OFL_BODY}`);
fs.writeFileSync(path.join(fonts, 'README.txt'), [
  'Fonts bundled with this extension (all allow redistribution):',
  '- NotoSansDeseret.ttf: Noto Sans Deseret, The Noto Project Authors. SIL OFL 1.1 (OFL-NotoSansDeseret.txt).',
  '- analecta.ttf: Analecta, George Douros. Public domain.',
  '- mellifera.otf: Mellifera Deseret, Sigilante. SIL OFL 1.1 (OFL-mellifera.txt).',
  '- desalph.otf: desalph, Kenneth R. Beesley / Fredrick R. Brennan. SIL OFL 1.1 (OFL-desalph.txt).',
  '- nomada.otf: IDC Nomada, N. E. Davis / Illinois Deseret Consortium. SIL OFL 1.1 (OFL-nomada.txt).',
  'Sources: https://deseret.wiki/fonts/',
  '',
].join('\n'));

// ---------- icons ----------
const crcTable = Array.from({ length: 256 }, (_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c >>> 0; });
const crc32 = (buf) => { let c = 0xffffffff; for (const b of buf) c = crcTable[(c ^ b) & 0xff] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
function png(size, rgba) {
  const chunk = (type, data) => { const len = Buffer.alloc(4); len.writeUInt32BE(data.length); const td = Buffer.concat([Buffer.from(type), data]); const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(td)); return Buffer.concat([len, td, crc]); };
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(size, 0); ihdr.writeUInt32BE(size, 4); ihdr[8] = 8; ihdr[9] = 6;
  const raw = Buffer.alloc((size * 4 + 1) * size);
  for (let y = 0; y < size; y++) { raw[y * (size * 4 + 1)] = 0; rgba.copy(raw, y * (size * 4 + 1) + 1, y * size * 4, (y + 1) * size * 4); }
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw, { level: 9 })), chunk('IEND', Buffer.alloc(0))]);
}
// Coverage of one point (unit square coords) -> [r,g,b,a]
const PAPER = [0x16, 0x16, 0x1a], GOLD = [0xd9, 0xb4, 0x6a];
function shade(x, y) {
  const r = 0.18; // rounded-square background
  const dx = Math.max(r - x, 0, x - (1 - r)), dy = Math.max(r - y, 0, y - (1 - r));
  if (dx * dx + dy * dy > r * r) return null;
  // Skep: a dome from y=0.16 to 0.84, half-width growing like a parabola, in 5 bands.
  const top = 0.16, bot = 0.84;
  if (y >= top && y <= bot) {
    const t = (y - top) / (bot - top);
    const half = 0.12 + 0.24 * Math.sqrt(t);
    const band = (t * 5) % 1;
    const inBand = band > 0.16;
    const door = Math.hypot(x - 0.5, y - 0.84) < 0.11;
    if (Math.abs(x - 0.5) <= half && inBand && !door) return GOLD;
  }
  return PAPER;
}
function icon(size) {
  const ss = 4, out = Buffer.alloc(size * size * 4);
  for (let py = 0; py < size; py++) for (let px = 0; px < size; px++) {
    let r = 0, g = 0, b = 0, a = 0;
    for (let sy = 0; sy < ss; sy++) for (let sx = 0; sx < ss; sx++) {
      const c = shade((px + (sx + 0.5) / ss) / size, (py + (sy + 0.5) / ss) / size);
      if (c) { r += c[0]; g += c[1]; b += c[2]; a += 255; }
    }
    const n = ss * ss, i = (py * size + px) * 4, cov = a / 255;
    out[i] = cov ? r / cov : 0; out[i + 1] = cov ? g / cov : 0; out[i + 2] = cov ? b / cov : 0; out[i + 3] = a / n;
  }
  return png(size, out);
}
fs.mkdirSync(path.join(DIST, 'icons'), { recursive: true });
for (const s of [16, 32, 48, 128]) fs.writeFileSync(path.join(DIST, 'icons', `${s}.png`), icon(s));

// ---------- zip for the Web Store ----------
function zip(dir, outFile) {
  const files = [];
  const walk = (d) => { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); e.isDirectory() ? walk(p) : files.push(p); } };
  walk(dir);
  const parts = [], central = [];
  let offset = 0;
  for (const f of files.sort()) {
    const name = Buffer.from(path.relative(dir, f).split(path.sep).join('/'));
    const data = fs.readFileSync(f), comp = zlib.deflateRawSync(data, { level: 9 }), crc = crc32(data);
    const local = Buffer.alloc(30); local.writeUInt32LE(0x04034b50, 0); local.writeUInt16LE(20, 4); local.writeUInt16LE(0x0800, 6); local.writeUInt16LE(8, 8);
    local.writeUInt32LE(crc, 14); local.writeUInt32LE(comp.length, 18); local.writeUInt32LE(data.length, 22); local.writeUInt16LE(name.length, 26);
    const cen = Buffer.alloc(46); cen.writeUInt32LE(0x02014b50, 0); cen.writeUInt16LE(20, 4); cen.writeUInt16LE(20, 6); cen.writeUInt16LE(0x0800, 8); cen.writeUInt16LE(8, 10);
    cen.writeUInt32LE(crc, 16); cen.writeUInt32LE(comp.length, 20); cen.writeUInt32LE(data.length, 24); cen.writeUInt16LE(name.length, 28); cen.writeUInt32LE(offset, 42);
    parts.push(local, name, comp); central.push(cen, name);
    offset += 30 + name.length + comp.length;
  }
  const cdir = Buffer.concat(central);
  const end = Buffer.alloc(22); end.writeUInt32LE(0x06054b50, 0); end.writeUInt16LE(files.length, 8); end.writeUInt16LE(files.length, 10); end.writeUInt32LE(cdir.length, 12); end.writeUInt32LE(offset, 16);
  fs.writeFileSync(outFile, Buffer.concat([...parts, cdir, end]));
  return files.length;
}
const n = zip(DIST, path.join(HERE, 'dist.zip'));
const version = JSON.parse(fs.readFileSync(path.join(SRC, 'manifest.json'), 'utf8')).version;
console.log(`built ${path.relative(REPO, DIST)} (v${version}, ${n} files) and dist.zip (${(fs.statSync(path.join(HERE, 'dist.zip')).size / 1024 / 1024).toFixed(1)} MB)`);
