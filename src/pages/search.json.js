// Client-side search index: every page, plus each section of the wiki articles.
import buy from '../data/buy.json';
const pages = [
  { url: '/', title: 'Deseret Wiki', where: 'Front page', text: 'Deseret alphabet library encyclopedia primer' },
  { url: '/fonts/', title: 'Fonts', where: 'Fonts', text: 'Noto Sans Deseret typefaces download specimen' },
  { url: '/resources/', title: 'Resources', where: 'Resources', text: 'community links games trainer' },
  { url: '/videos/', title: 'Videos', where: 'Videos', text: 'video youtube' },
  { url: '/buy/', title: 'Books & Prints', where: 'Books & Prints', text: 'buy books amazon Deseret alphabet editions' },
  { url: '/about/', title: 'About', where: 'About', text: 'about this site' },
];
const slug = (s) => s.toLowerCase().replace(/[^\w\s-]/g, '').trim().replace(/\s+/g, '-');
export async function GET() {
  const out = [...pages];
  const articles = import.meta.glob('./wiki/*.md', { eager: true });
  for (const [file, mod] of Object.entries(articles)) {
    const url = file.replace('./', '/').replace(/\.md$/, '/');
    const title = mod.frontmatter.heading ?? mod.frontmatter.title;
    // split the source at headings so each section's prose is searchable on its own
    const plain = (s) => s.replace(/!?\[([^\]]*)\]\([^)]*\)/g, '$1').replace(/[*_`|>#]/g, ' ').replace(/\s+/g, ' ').trim();
    const chunks = mod.rawContent().split(/^#{2,3} .*$/m);
    const heads = mod.getHeadings().filter((h) => h.depth === 2 || h.depth === 3);
    out.push({ url, title, where: 'Article', text: plain(chunks[0] ?? '') });
    heads.forEach((h, i) => out.push({ url: `${url}#${h.slug}`, title: h.text, where: title, text: plain(chunks[i + 1] ?? '') }));
  }
  for (const b of buy) out.push({ url: '/buy/', title: b.title, where: 'Books & Prints', text: b.author });
  return new Response(JSON.stringify(out), { headers: { 'Content-Type': 'application/json' } });
}
