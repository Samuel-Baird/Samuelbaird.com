import { createHash, timingSafeEqual } from 'node:crypto';

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
  rights: 'Source, attribution and rights for this transfer verified',
  filename_and_destination: 'Filename and destination verified',
  format_preference: 'Original scan or publisher PDF preferred',
};
const sha = value => createHash('sha256').update(value).digest('hex');
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]));
const headers = {'Cache-Control':'private, no-store', 'X-Robots-Tag':'noindex, nofollow',
  'Referrer-Policy':'no-referrer', 'X-Content-Type-Options':'nosniff',
  'Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-src https://drive.google.com; frame-ancestors 'none'; base-uri 'none'"};
const response = (text, status=200, extra={}) => new Response(text, {status, headers:{...headers,...extra}});
const redirect = path => response(null,303,{Location:path});
const json = value => response(JSON.stringify(value),200,{'Content-Type':'application/json'});
function page(title, body) {
  return response(`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)} · GSA</title><style>
  *{box-sizing:border-box}body{margin:0;background:#f7f5ee;color:#222d27;font:16px/1.55 system-ui,sans-serif}header{border-bottom:1px solid #c6cbc1;padding:1rem max(5vw,calc((100vw - 60rem)/2));white-space:nowrap;color:#345344;font-weight:650}main{max-width:62rem;margin:3rem auto;padding:0 1.5rem}h1,h2{font-family:Georgia,serif;line-height:1.15}h1{font-size:clamp(2rem,5vw,3.5rem);font-weight:500}h2{font-size:1.55rem}section{padding:1.4rem 0;border-top:1px solid #c6cbc1}a{color:#245640}label{display:block;margin:.7rem 0}input{width:1rem;height:1rem;margin-right:.6rem}textarea{display:block;width:100%;max-width:40rem;padding:.6rem}button,.open{display:inline-block;background:#294f3c;color:white;padding:.65rem 1rem;border:0;border-radius:4px;margin:.5rem .6rem .5rem 0;font:inherit;cursor:pointer;text-decoration:none}button.secondary{background:#e2e5db;color:#243a2b}code{overflow-wrap:anywhere}small{color:#49564d}dl{display:grid;grid-template-columns:max-content 1fr;gap:.4rem 1rem}dd{margin:0;overflow-wrap:anywhere}@media(max-width:600px){dl{display:block}dd{margin-bottom:.7rem}}
  .pdf-review iframe{display:block;width:100%;height:72vh;border:1px solid #c6cbc1;background:white}
  @media(min-width:70rem){main:has(.pdf-review){max-width:98rem}.pdf-review{display:grid;grid-template-columns:minmax(0,3fr) minmax(20rem,2fr);gap:2rem;align-items:start}.pdf-review iframe{position:sticky;top:1rem;height:calc(100vh - 2rem)}}
  </style>
  <header>Gospel Scholar Archive</header><main>${body}</main></html>`,200,{'Content-Type':'text/html; charset=utf-8'});
}
function itemPage(item, actor) {
  const {packet:p, decisions, revision}=item;
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
  return page(p.title,`<a href="/gsa">← Review queue</a><h1>${esc(p.title)}</h1><p>${esc(p.citation)}</p><a class="open" href="${esc(p.pdf)}" target="_blank" rel="noreferrer">Open PDF in a new tab ↗</a> <a href="${esc(p.source)}" target="_blank" rel="noreferrer">Publisher source ↗</a>
  ${viewer ? '<div class="pdf-review">'+viewer+'<div>' : ''}
  <section><h2>Publication details</h2><dl>${Object.entries({'Filename':p.filename,'Destination':p.folder,'Rights evidence':p.rights,'Changelog entry':p.entry,'Automated checks':p.validation,'SHA-256':p.sha256}).map(([k,v])=>`<dt>${k}</dt><dd>${esc(v)}</dd>`).join('')}</dl></section>
  <section><h2>Reviewer decisions</h2><ul>${statuses}</ul></section>
  ${done ? '<p>Your decision is recorded for this version.</p>' : `<section><h2>Your review</h2><form method="post"><input type="hidden" name="revision" value="${revision}">${Object.entries(labels).map(([k,v])=>`<label><input type="checkbox" name="${k}">${v}</label>`).join('')}<label>Review notes<textarea name="note" rows="3" maxlength="2000"></textarea></label><button name="decision" value="Approved">Approve publication</button><button class="secondary" name="decision" value="Changes requested">Request changes</button></form></section>`}${viewer ? '</div></div>' : ''}`);
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
    if(request.method==='POST' && request.headers.get('Origin')!==new URL(request.url).origin) return response('Forbidden',403);
  }
  const forwarded=new Request(request);
  forwarded.headers.set('X-GSA-Actor',actor);
  return env.GSA_REVIEWS.get(env.GSA_REVIEWS.idFromName('reviews')).fetch(forwarded);
}

export class GsaReviews {
  constructor(state){this.storage=state.storage;}
  async fetch(req) {
    const path=new URL(req.url).pathname.replace(/\/$/,'');
    const actor=req.headers.get('X-GSA-Actor');
    if(path==='/gsa/operator' && actor==='operator'){
      const {action,id,packet}=await req.json();
      if(!/^[a-z0-9-]{1,80}$/.test(id)) return response('Invalid work ID',400);
      if(action==='get') return json(await this.storage.get(id) || null);
      if(action!=='put' || !packet || !/^[a-f0-9]{64}$/.test(packet.sha256) || ![packet.pdf,packet.source].every(v=>typeof v==='string' && v.startsWith('https://'))) return response('Invalid packet',400);
      const revision=sha(JSON.stringify(packet));
      await this.storage.transaction(async tx=>{
        const prior=await tx.get(id);
        if(prior?.revision!==revision) await tx.put(id,{packet,revision,decisions:{}});
      });
      return json({revision});
    }
    if(![...reviewers.values()].includes(actor)) return response('Forbidden',403);
    if(path==='/gsa' && req.method==='GET'){
      const items=await this.storage.list();
      return page('Review queue',`<small>Signed in as ${actor}</small><h1>Review queue</h1>${items.size ? [...items].map(([id,v])=>`<section><small>${Object.keys(v.decisions).length} of 2 reviewed</small><h2><a href="/gsa/work/${esc(id)}">${esc(v.packet.title)}</a></h2><p>${esc(v.packet.citation)}</p></section>`).join(''):'<p>No works are awaiting review.</p>'}`);
    }
    const id=path.match(/^\/gsa\/work\/([a-z0-9-]{1,80})$/)?.[1];
    if(!id) return response('Not found',404);
    const item=await this.storage.get(id);
    if(!item) return response('Work not found',404);
    if(req.method==='GET') return itemPage(item,actor);
    if(req.method!=='POST') return response('Method not allowed',405);
    const form=await req.formData();
    const decision=form.get('decision'), note=String(form.get('note')||'').trim();
    const checks=Object.fromEntries(Object.keys(labels).map(k=>[k,form.get(k)==='on']));
    if(!['Approved','Changes requested'].includes(decision) || note.length>2000 ||
      (decision==='Approved' ? !Object.values(checks).every(Boolean) : !note)) return response('Complete all checks to approve, or describe the requested changes. Go back to your review.',422);
    const saved=await this.storage.transaction(async tx=>{
      const current=await tx.get(id);
      if(current?.revision!==form.get('revision') || current.decisions[actor]) return false;
      current.decisions[actor]={decision,note,checks,at:new Date().toISOString()};
      await tx.put(id,current);return true;
    });
    return saved ? redirect(path) : response('This review has changed. Reload it before continuing.',409);
  }
}
