// Gives wiki articles their printed furniture:
//  - a leading paragraph that is only <em> becomes the .attribution slip,
//  - the first table becomes the infobox (a framed archival record),
//  - the first real paragraph after those gets the drop cap (.lede).
const isEl = (n, tag) => n && n.type === 'element' && (!tag || n.tagName === tag);
const onlyEm = (p) => p.children.filter((c) => !(c.type === 'text' && !c.value.trim())).every((c) => isEl(c, 'em'));
const addClass = (n, c) => { n.properties ||= {}; const cur = n.properties.className || []; n.properties.className = [...cur, c]; };

export default function rehypeArchival() {
  return (tree) => {
    const kids = tree.children;
    let tableDone = false, ledeDone = false;
    for (let i = 0; i < kids.length; i++) {
      const n = kids[i];
      if (!isEl(n)) continue;
      if (n.tagName === 'h2') break; // only the article's opening
      if (n.tagName === 'p' && !ledeDone && onlyEm(n)) { addClass(n, 'attribution'); continue; }
      if (n.tagName === 'table' && !tableDone) {
        tableDone = true;
        // the header row is "Name | (empty)": span the name across both columns
        const thead = n.children.find((c) => isEl(c, 'thead'));
        const tr = thead?.children.find((c) => isEl(c, 'tr'));
        if (tr) {
          const ths = tr.children.filter((c) => isEl(c, 'th'));
          if (ths.length === 2 && !ths[1].children.length) {
            tr.children = tr.children.filter((c) => c !== ths[1]);
            ths[0].properties = { ...ths[0].properties, colSpan: 2 };
          }
        }
        // flattened Wikipedia lineage lists ("A * B + C - D") read as a chain
        const tidy = (node) => {
          if (node.type === 'text') node.value = node.value.replace(/\s+[*+-]\s+/g, ' → ').replace(/^\s*[*+-]\s+/, '→ ');
          node.children?.forEach(tidy);
        };
        n.children.filter((c) => isEl(c, 'tbody')).forEach(tidy);
        kids[i] = {
          type: 'element', tagName: 'aside', properties: { className: ['infobox'], ariaLabel: 'Summary' },
          children: [
            { type: 'element', tagName: 'div', properties: { className: ['infobox-head'] }, children: [
              { type: 'element', tagName: 'span', properties: { className: ['smallcaps'] }, children: [{ type: 'text', value: 'Archival Record · No. I' }] },
            ] },
            n,
          ],
        };
        continue;
      }
      if (n.tagName === 'p' && !ledeDone) { addClass(n, 'lede'); ledeDone = true; }
    }
  };
}
