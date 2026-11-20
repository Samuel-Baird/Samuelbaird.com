import { createHash, timingSafeEqual } from 'node:crypto';
import { reviewScript } from './gsa-client.mjs';

const reviewers = new Map([
  ['83014af03cb27f570f7caaf89183c64d91fe12c5203d6875d2f8ed95d8d398f7', 'Samuel'],
  ['215c611bd1c94ee36d2df92335c4e154ce52fd8b528fa146034a28be7999844a', 'David'],
]);
const operatorHash = '367465684ddb369024593a8b374e0383e3a9363980d55e2a30819ae2b3495f0c';
const labels = {
  bibliographic_match: 'Citation and edition match',
  first_and_last_pages: 'First and last pages inspected',
  body_spot_check: 'Interior pages checked for legibility and order',
  completeness: 'All pages and parts present',
  filename_and_destination: 'Filename and destination verified',
  format_preference: 'Original scan or publisher PDF preferred',
};
// Reviewer-editable packet fields. Any edit changes the review version, so recorded
// decisions reset and both reviewers approve the edited text.
const editable = {
  title: {label:'Title', max:300},
  citation: {label:'Citation and edition', max:1000, multiline:true},
  filename: {label:'Filename', max:200},
  entry: {label:'Changelog entry', max:2000, multiline:true},
};
const suffix = name => (String(name).match(/\.[a-z0-9]+$/i)?.[0] || '').toLowerCase();
function checkEdit(field, value, packet) {
  const spec = editable[field];
  if (!value) return spec.label + " can't be empty";
  if (value.length > spec.max) return `${spec.label} is limited to ${spec.max} characters`;
  if (/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(value) || (!spec.multiline && /[\r\n]/.test(value))) return spec.label + ' has characters that are not allowed';
  if (field === 'filename') {
    // Colons are fine in Drive and common in archive names ("Lastname, Title: Subtitle.pdf").
    if (/[\/\\]/.test(value) || value.startsWith('.')) return 'Filenames cannot contain / or \\ or start with a dot';
    if (suffix(value) !== suffix(packet.filename)) return `Keep the ${suffix(packet.filename) || 'original'} extension`;
  }
  return null;
}
const effective = item => ({...item.packet, ...Object.fromEntries(Object.entries(item.edits || {}).map(([k, e]) => [k, e.value]))});
const revisionOf = item => sha(JSON.stringify(effective(item)));
const isWorkKey = key => /^[a-z0-9-]{1,80}$/.test(key);
const folderKey = id => 'folder:' + id;

const sha = value => createHash('sha256').update(value).digest('hex');
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]));
const headers = {'Cache-Control':'private, no-store', 'X-Robots-Tag':'noindex, nofollow',
  'Referrer-Policy':'same-origin', 'X-Content-Type-Options':'nosniff',
  'Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; img-src data:; script-src 'self'; connect-src 'self'; form-action 'self'; frame-src https://drive.google.com; frame-ancestors 'none'; base-uri 'none'"};
const response = (text, status=200, extra={}) => new Response(text, {status, headers:{...headers,...extra}});
const redirect = path => response(null,303,{Location:path});
const json = value => response(JSON.stringify(value),200,{'Content-Type':'application/json'});
function page(title, body) {
  return response(`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)} · GSA</title><style>
  *{box-sizing:border-box}body{margin:0;background:#f7f5ee;color:#222d27;font:16px/1.55 system-ui,sans-serif}header{border-bottom:1px solid #c6cbc1;padding:1rem max(5vw,calc((100vw - 60rem)/2));white-space:nowrap;color:#345344;font-weight:650}main{max-width:62rem;margin:3rem auto;padding:0 1.5rem}h1,h2{font-family:Georgia,serif;line-height:1.15}h1{font-size:clamp(2rem,5vw,3.5rem);font-weight:500}h2{font-size:1.55rem}section{padding:1.4rem 0;border-top:1px solid #c6cbc1}a{color:#245640}label{display:block;margin:.7rem 0}input{width:1rem;height:1rem;margin-right:.6rem}textarea{display:block;width:100%;max-width:40rem;padding:.6rem}button,.open{display:inline-block;background:#294f3c;color:white;padding:.65rem 1rem;border:0;border-radius:4px;margin:.5rem .6rem .5rem 0;font:inherit;cursor:pointer;text-decoration:none}button.secondary{background:#e2e5db;color:#243a2b}code{overflow-wrap:anywhere}small{color:#49564d}dl{display:grid;grid-template-columns:max-content 1fr;gap:.4rem 1rem}dd{margin:0;overflow-wrap:anywhere}@media(max-width:600px){dl{display:block}dd{margin-bottom:.7rem}}
  .field{margin:1rem 0}.field>label{font-weight:600;margin:0 0 .3rem}.row{display:flex;align-items:flex-start;gap:.6rem;flex-wrap:wrap}.row input[type=text],.row textarea{flex:1 1 18rem;max-width:40rem;width:auto;height:auto;margin:0;padding:.55rem .65rem;border:1px solid #aeb5aa;border-radius:4px;font:inherit;background:white;color:inherit}.row input[readonly]{background:#eef0e9}.row button{margin:0}
  .saved{display:inline-flex;align-items:center;gap:.35rem;min-height:2.4rem;font-size:.9rem;opacity:0;transition:opacity .4s}.saved.show{opacity:1}.saved.ok{color:#1d7a3e;font-weight:600}.saved.ok::before{content:"";width:1.25rem;height:1.25rem;border-radius:50%;background:#1d7a3e url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3.5 8.5l3 3 6-7' fill='none' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/80% no-repeat}.saved.busy{color:#49564d}.saved.err{color:#a3261b;font-weight:600}
  .edited{display:block;margin-top:.25rem}.reset-note{background:#fff4d6;border:1px solid #e3c46b;padding:.6rem .8rem;border-radius:4px}
  .explorer{margin-top:.6rem;max-width:40rem;border:1px solid #aeb5aa;border-radius:6px;background:white}.crumbs{display:flex;flex-wrap:wrap;gap:.1rem;padding:.5rem .6rem;border-bottom:1px solid #dde1d8;font-size:.92rem}.crumbs button,.folders button{background:none;color:#245640;border:0;margin:0;padding:.2rem .35rem;border-radius:3px;font:inherit;cursor:pointer;text-align:left}.crumbs button:hover,.folders button:hover{background:#eef3ec}.crumbs span{color:#8a9388;padding:.2rem 0}.explorer .filter{display:block;width:calc(100% - 1.2rem);height:auto;margin:.5rem .6rem;padding:.4rem .5rem;border:1px solid #c6cbc1;border-radius:4px;font:inherit}
  .folders{list-style:none;margin:0;padding:.2rem .3rem;max-height:18rem;overflow:auto}.folders li button{display:flex;width:100%;gap:.5rem;align-items:center;padding:.4rem .5rem;color:#222d27}.folders li button::before{content:"";flex:none;width:1.1rem;height:.85rem;border-radius:2px;background:#c99a3b;box-shadow:inset 0 .22rem 0 #e0b65a}.folders li button .n{flex:1}.folders li button .c{color:#8a9388;font-size:.85rem}.folders .empty{padding:.6rem;color:#69746b}.folders .error{color:#a3261b;font-weight:600}
  .explorer-foot{display:flex;justify-content:space-between;align-items:center;gap:.6rem;flex-wrap:wrap;padding:.5rem .6rem;border-top:1px solid #dde1d8}.explorer-foot button{margin:0 0 0 .4rem}
  .pdf-review iframe{display:block;width:100%;height:72vh;border:1px solid #c6cbc1;background:white}
  @media(min-width:70rem){main:has(.pdf-review){max-width:98rem}.pdf-review{display:grid;grid-template-columns:minmax(0,3fr) minmax(20rem,2fr);gap:2rem;align-items:start}.pdf-review iframe{position:sticky;top:1rem;height:calc(100vh - 2rem)}}
  </style>
  <header>Gospel Scholar Archive</header><main>${body}</main></html>`,200,{'Content-Type':'text/html; charset=utf-8'});
}
function fieldInput(key, value, edit) {
  const spec = editable[key], id = 'f-' + key;
  const control = spec.multiline
    ? `<textarea id="${id}" data-field="${key}" rows="3" maxlength="${spec.max}">${esc(value)}</textarea>`
    : `<input id="${id}" type="text" data-field="${key}" maxlength="${spec.max}" value="${esc(value)}" autocomplete="off" spellcheck="${key === 'filename' ? 'false' : 'true'}">`;
  return `<div class="field"><label for="${id}">${spec.label}</label><div class="row">${control}<span class="saved" role="status" aria-live="polite"></span></div>${edit ? `<small class="edited">Edited by ${esc(edit.by)} · ${esc(edit.at.slice(0, 16).replace('T', ' '))} UTC</small>` : ''}</div>`;
}
function publishedSection(item) {
  const pub = item.published, approved = Object.values(item.decisions || {}).some(d => d.decision === 'Approved');
  return `<section class="published" data-approved="${approved ? 'yes' : 'no'}"><h2>Published to Google Drive</h2>
  <div class="row"><input type="text" id="published-link" readonly value="${esc(pub?.file_url || '')}" placeholder="The Drive link appears here once the file is published" aria-label="Drive link to the published file">
  <a class="open" id="published-file" href="${esc(pub?.file_url || '#')}" target="_blank" rel="noreferrer"${pub ? '' : ' hidden'}>Open file ↗</a><a id="published-folder" href="${esc(pub?.folder_url || '#')}" target="_blank" rel="noreferrer"${pub ? '' : ' hidden'}>Open folder ↗</a></div>
  <small id="published-status">${pub ? 'Published ' + esc(pub.at.slice(0, 16).replace('T', ' ')) + ' UTC as ' + esc(pub.name) + '. Open it to double-check the file and folder.' : approved ? 'Approved. Waiting for the worker to publish; this fills in by itself.' : 'Fills in after approval, once the worker has published the file.'}</small></section>`;
}

function itemPage(id, item, actor) {
  const {decisions, revision}=item;
  const p = effective(item), edits = item.edits || {};
  const pdf = URL.canParse(p.pdf) ? new URL(p.pdf) : null;
  const file = pdf?.origin === 'https://drive.google.com' && pdf.pathname.match(/^\/file\/d\/([\w-]+)(?:\/(?:view|preview))?\/?$/);
  let viewer = '';
  if (file) {
    const preview = new URL('https://drive.google.com/file/d/' + file[1] + '/preview');
    if (pdf.searchParams.has('resourcekey')) preview.searchParams.set('resourcekey', pdf.searchParams.get('resourcekey'));
    viewer = `<iframe src="${esc(preview.href)}" title="Reviewer PDF: ${esc(p.title)}" allowfullscreen></iframe>`;
  }
  const done=decisions[actor];
  const statuses=[...reviewers.values()].map(name=>`<li>${name} · ${esc(decisions[name]?.decision || 'Pending')}${decisions[name]?.note ? ' — '+esc(decisions[name].note):''}</li>`).join('');
  const destEdit = edits.destination;
  const destination = `<div class="field"><label for="f-destination">Destination folder</label><div class="row"><input id="f-destination" type="text" readonly value="${esc(p.folder)}" data-folder-id="${esc(p.destination)}"><button type="button" class="secondary" id="browse" aria-controls="explorer" aria-expanded="false">Browse…</button><span class="saved" role="status" aria-live="polite"></span></div>${destEdit ? `<small class="edited">Edited by ${esc(destEdit.by)} · ${esc(destEdit.at.slice(0, 16).replace('T', ' '))} UTC</small>` : ''}
  <div id="explorer" class="explorer" hidden><div class="crumbs" aria-label="Folder path"></div><input type="search" class="filter" placeholder="Filter this folder" aria-label="Filter folders"><ul class="folders" role="listbox" aria-label="Folders"></ul><div class="explorer-foot"><small class="snapshot"></small><span><button type="button" class="secondary" data-act="cancel">Cancel</button><button type="button" data-act="select">Select this folder</button></span></div></div></div>`;
  return page(p.title,`<a href="/gsa">← Review queue</a><h1 id="page-title">${esc(p.title)}</h1><p id="page-citation">${esc(p.citation)}</p><a class="open" href="${esc(p.pdf)}" target="_blank" rel="noreferrer">Open PDF in a new tab ↗</a> <a href="${esc(p.source)}" target="_blank" rel="noreferrer">Publisher source ↗</a>
  ${viewer ? '<div class="pdf-review">'+viewer+'<div>' : ''}
  <section class="details" data-work="${esc(id)}"><h2>Publication details</h2><p><small>Changes save as you type. Any change resets recorded decisions, so both reviewers approve the edited version.</small></p>
  <p class="reset-note" hidden>Your edit reset the recorded decisions. Reload the page to review this version.</p>
  ${['title','citation','filename'].map(k=>fieldInput(k,p[k],edits[k])).join('')}${destination}${fieldInput('entry',p.entry,edits.entry)}
  <dl>${Object.entries({'Automated checks':p.validation,'SHA-256':p.sha256}).map(([k,v])=>`<dt>${k}</dt><dd>${esc(v)}</dd>`).join('')}</dl></section>
  <section><h2>Reviewer decisions</h2><ul>${statuses}</ul></section>
  ${done ? '<p>Your decision is recorded for this version.</p>' : `<section><h2>Your review</h2><form method="post"><input type="hidden" name="revision" value="${revision}">${Object.entries(labels).map(([k,v])=>`<label><input type="checkbox" name="${k}">${v}</label>`).join('')}<label>Review notes<textarea name="note" rows="3" maxlength="2000"></textarea></label><button name="decision" value="Approved">Approve publication</button><button class="secondary" name="decision" value="Changes requested">Request changes</button></form></section>`}${publishedSection(item)}${viewer ? '</div></div>' : ''}<script src="/gsa/review.js" defer></script>`);
}

// A same-page form POST can carry Origin: null under a strict referrer policy; the browser's
// Sec-Fetch-Site still says whether it came from this site.
function sameOrigin(request) {
  const origin=request.headers.get('Origin');
  if (origin && origin!=='null') return origin===new URL(request.url).origin;
  return request.headers.get('Sec-Fetch-Site')==='same-origin';
}

export async function gsaRoute(request,env,session) {
  const path=new URL(request.url).pathname.replace(/\/$/,'');
  let actor;
  if(path==='/gsa/operator') {
    if(request.method!=='POST') return response('Method not allowed',405);
    const auth=request.headers.get('Authorization')||'';
    if(!auth.startsWith('Bearer ') || !timingSafeEqual(Buffer.from(sha(auth.slice(7))),Buffer.from(operatorHash))) return response('Forbidden',403);
    actor='operator';
  } else {
    if(!session.configured()) return response('Login service unavailable',503);
    const token=session.readSession(request.headers.get('Cookie'))?.access_token;
    if(!token) return redirect('/latter-day-stats/login?return_to='+encodeURIComponent(path));
    const user=await session.asUser(token,'/auth/v1/user');
    if(user.status===401 || user.status===403) return redirect('/latter-day-stats/login?return_to='+encodeURIComponent(path));
    if(user.status!==200) return response('Login service unavailable',503);
    const email=(user.json?.email||'').toLowerCase();
    actor=user.json?.email_confirmed_at && reviewers.get(sha(email));
    if(!actor) return response('This account does not have GSA reviewer access.',403);
    if(request.method==='POST' && !sameOrigin(request)) return response('Forbidden',403);
  }
  if(path==='/gsa/review.js') return response(reviewScript,200,{'Content-Type':'text/javascript; charset=utf-8'});
  const forwarded=new Request(request);
  forwarded.headers.set('X-GSA-Actor',actor);
  return env.GSA_REVIEWS.get(env.GSA_REVIEWS.idFromName('reviews')).fetch(forwarded);
}

export class GsaReviews {
  constructor(state){this.storage=state.storage;}
  async operator(req) {
    const body=await req.json();
    if(body.action==='folders') return this.putFolders(body);
    const {action,id,packet}=body;
    if(!isWorkKey(String(id))) return response('Invalid work ID',400);
    if(action==='get') return json(await this.storage.get(id) || null);
    // Removes a queued packet with its edits, history and decisions (sandbox clean-up, withdrawn works).
    // The worker reports the verified Drive file after publishing, for the reviewer's double check.
    if(action==='published') {
      const {file_url,folder_url,name}=body;
      if(!/^https:\/\/drive\.google\.com\/file\/d\/[\w-]+\/view(\?[\w=&.-]*)?$/.test(file_url||'') || !/^https:\/\/drive\.google\.com\/drive\/folders\/[\w-]+$/.test(folder_url||'')) return response('Invalid Drive links',400);
      const ok=await this.storage.transaction(async tx=>{const item=await tx.get(id); if(!item) return false; item.published={file_url,folder_url,name:String(name||'').slice(0,300),at:new Date().toISOString()}; await tx.put(id,item); return true;});
      return ok ? json({published:true}) : response('Work not found',404);
    }
    if(action==='delete') return json({deleted:await this.storage.transaction(async tx=>{const had=await tx.get(id)!==undefined; if(had) await tx.delete(id); return had;})});
    if(action!=='put' || !packet || !/^[a-f0-9]{64}$/.test(packet.sha256) || ![packet.pdf,packet.source].every(v=>typeof v==='string' && v.startsWith('https://'))) return response('Invalid packet',400);
    const revision=await this.storage.transaction(async tx=>{
      const prior=await tx.get(id);
      // Reviewer edits survive a re-queue until the operator's packet carries the same value.
      const edits={...(prior?.edits||{})};
      for(const [k,e] of Object.entries(edits)) if(packet[k]===e.value || (k==='folder' && packet.destination===edits.destination?.value)) delete edits[k];
      if(!edits.destination) delete edits.folder;
      const next={packet,edits,history:prior?.history||[],decisions:prior?.decisions||{},...(prior?.published?{published:prior.published}:{})};
      next.revision=revisionOf(next);
      if(prior?.revision!==next.revision) next.decisions={};
      await tx.put(id,next);
      return next.revision;
    });
    return json({revision});
  }
  async putFolders({root,folders,at,source}) {
    // Snapshot of the archive's folder tree, pushed by the worker Mac (the site has no Drive access).
    if(!root || !/^[\w-]{1,100}$/.test(root.id) || !Array.isArray(folders) || folders.length>50000) return response('Invalid folder snapshot',400);
    const byId=new Map([[root.id,{id:root.id,name:String(root.name||'Archive').slice(0,300),children:[]}]]);
    for(const f of folders){
      if(!/^[\w-]{1,100}$/.test(f?.id) || typeof f.name!=='string' || !/^[\w-]{1,100}$/.test(f.parent)) return response('Invalid folder entry',400);
      if(!byId.has(f.id)) byId.set(f.id,{id:f.id,name:f.name.slice(0,300),parent:f.parent,children:[]});
    }
    for(const f of byId.values()) if(f.parent) byId.get(f.parent)?.children.push(f.id);
    // Keep only folders reachable from the archive root, each with its trail of ancestors.
    const out=new Map(), queue=[[byId.get(root.id),[]]];
    while(queue.length){
      const [f,trail]=queue.shift();
      if(out.has(f.id)) continue;
      const here=[...trail,{id:f.id,name:f.name}];
      const kids=f.children.map(id=>byId.get(id)).sort((a,b)=>a.name.localeCompare(b.name,undefined,{numeric:true,sensitivity:'base'}));
      out.set(f.id,{id:f.id,name:f.name,trail:here,children:kids.map(k=>({id:k.id,name:k.name,count:k.children.length}))});
      for(const k of kids) queue.push([k,here]);
    }
    const old=[...(await this.storage.list({prefix:'folder:'})).keys()].filter(k=>k.startsWith('folder:'));
    for(let i=0;i<old.length;i+=128) await this.storage.delete(old.slice(i,i+128));
    const entries=[...out.values()].map(f=>[folderKey(f.id),f]);
    for(let i=0;i<entries.length;i+=128) await this.storage.put(Object.fromEntries(entries.slice(i,i+128)));
    await this.storage.put('meta:folders',{root:root.id,at:String(at||new Date().toISOString()),count:out.size,source:String(source||'Drive').slice(0,40)});
    return json({folders:out.size});
  }
  async fetch(req) {
    const path=new URL(req.url).pathname.replace(/\/$/,'');
    const actor=req.headers.get('X-GSA-Actor');
    if(path==='/gsa/operator' && actor==='operator') return this.operator(req);
    if(![...reviewers.values()].includes(actor)) return response('Forbidden',403);
    if(path==='/gsa' && req.method==='GET'){
      const items=[...(await this.storage.list())].filter(([k])=>isWorkKey(k));
      return page('Review queue',`<small>Signed in as ${actor}</small><h1>Review queue</h1>${items.length ? items.map(([id,v])=>{const p=effective(v);return `<section><small>${Object.keys(v.decisions).length} of 2 reviewed</small><h2><a href="/gsa/work/${esc(id)}">${esc(p.title)}</a></h2><p>${esc(p.citation)}</p></section>`}).join(''):'<p>No works are awaiting review.</p>'}`);
    }
    const folder=path.match(/^\/gsa\/folders\/(root|[\w-]{1,100})$/)?.[1];
    if(folder && req.method==='GET'){
      const meta=await this.storage.get('meta:folders');
      if(!meta) return response(JSON.stringify({error:'The folder list hasn\'t been loaded yet. Ask the operator to run review_portal.py folders on the worker Mac.'}),404,{'Content-Type':'application/json'});
      const entry=await this.storage.get(folderKey(folder==='root'?meta.root:folder));
      return entry ? json({...entry,root:meta.root,at:meta.at,source:meta.source||'Drive'}) : response(JSON.stringify({error:'Folder not found'}),404,{'Content-Type':'application/json'});
    }
    const match=path.match(/^\/gsa\/work\/([a-z0-9-]{1,80})(\/edit|\/status)?$/);
    if(!match) return response('Not found',404);
    const id=match[1];
    if(match[2]==='/status') {
      if(req.method!=='GET') return response('Method not allowed',405);
      const item=await this.storage.get(id);
      return item ? json({published:item.published||null}) : response('Work not found',404);
    }
    if(match[2]) return req.method==='POST' ? this.edit(req,id,actor) : response('Method not allowed',405);
    const item=await this.storage.get(id);
    if(!item) return response('Work not found',404);
    if(req.method==='GET') return itemPage(id,item,actor);
    if(req.method!=='POST') return response('Method not allowed',405);
    const form=await req.formData();
    const decision=form.get('decision'), note=String(form.get('note')||'').trim();
    const checks=Object.fromEntries(Object.keys(labels).map(k=>[k,form.get(k)==='on']));
    if(!['Approved','Changes requested'].includes(decision) || note.length>2000 ||
      (decision==='Approved' ? !Object.values(checks).every(Boolean) : !note)) return response('Complete all checks to approve, or describe the requested changes. Go back to your review.',422);
    const saved=await this.storage.transaction(async tx=>{
      const current=await tx.get(id);
      if(current?.revision!==form.get('revision') || current.decisions[actor] || current.published) return false;
      current.decisions[actor]={decision,note,checks,at:new Date().toISOString()};
      await tx.put(id,current);return true;
    });
    return saved ? redirect(path) : response('This review has changed. Reload it before continuing.',409);
  }
  async edit(req,id,actor) {
    const fail=(error,status=422)=>response(JSON.stringify({error}),status,{'Content-Type':'application/json'});
    if(!(req.headers.get('Content-Type')||'').startsWith('application/json')) return fail('Expected JSON',415);
    let body; try { body=await req.json(); } catch { return fail('Invalid JSON',400); }
    const field=String(body?.field||''), raw=typeof body?.value==='string' ? body.value : null;
    if(raw===null || raw.length>5000) return fail('Invalid value',400);
    let changes;
    if(field==='destination'){
      const meta=await this.storage.get('meta:folders');
      const folder=/^[\w-]{1,100}$/.test(raw) && await this.storage.get(folderKey(raw));
      if(!meta || !folder) return fail('That folder is not in the archive folder list');
      if(folder.id===meta.root) return fail('Choose a shelf inside the archive, not the archive root');
      if(folder.id.startsWith('toc-')) return fail('That folder only holds other folders. Open it and choose the folder inside.');
      changes={destination:folder.id,folder:folder.trail.map(t=>t.name).join(' / ')};
    } else if(editable[field]) {
      changes={[field]:raw.trim()};
    } else return fail('That field cannot be edited',400);
    const at=new Date().toISOString();
    const result=await this.storage.transaction(async tx=>{
      const item=await tx.get(id);
      if(!item) return {error:'Work not found',status:404};
      if(item.published) return {error:'Already published to Drive; edits are closed',status:409};
      if(field!=='destination'){const problem=checkEdit(field,changes[field],item.packet); if(problem) return {error:problem};}
      item.edits={...(item.edits||{})};
      const current=effective(item);
      for(const [k,v] of Object.entries(changes)){
        if(item.packet[k]===v) delete item.edits[k]; else item.edits[k]={value:v,by:actor,at};
        if(current[k]!==v) item.history=[...(item.history||[]),{field:k,from:current[k],to:v,by:actor,at}].slice(-200);
      }
      const revision=revisionOf(item);
      const cleared=revision!==item.revision && Object.keys(item.decisions).length>0;
      if(revision!==item.revision) item.decisions={};
      item.revision=revision;
      await tx.put(id,item);
      return {revision,decisionsCleared:cleared,value:changes[field==='destination'?'folder':field],at};
    });
    return result.error ? fail(result.error,result.status) : json(result);
  }
}
