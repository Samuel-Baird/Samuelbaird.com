import test from 'node:test';
import assert from 'node:assert/strict';
import {gsaRoute,GsaReviews} from '../../../sites/samuelbaird.com/worker/gsa.mjs';

const url='https://samuelbaird.com/gsa';
function session(email){
  return {configured:()=>true,readSession:()=>email && {access_token:'test'},
    asUser:async()=>({status:200,json:{email,email_confirmed_at:'today'}})};
}
test('authentication precedes all private reads and rejects forged reviewer headers',async()=>{
  assert.equal((await gsaRoute(new Request(url),{},session(null))).status,303);
  assert.equal((await gsaRoute(new Request(url,{headers:{'X-GSA-Actor':'David'}}),{},session('stranger@example.org'))).status,403);
  assert.equal((await gsaRoute(new Request(url+'/operator',{method:'POST'}),{},session(null))).status,403);
  assert.equal((await gsaRoute(new Request(url+'/work/test',{method:'POST',headers:{Origin:'https://other.example'}}),{},session('b13llama@gmail.com'))).status,403);
});
test('each assigned account can approve once per exact review version',async()=>{
  const data=new Map();
  const storage={get:k=>structuredClone(data.get(k)),put:(k,v)=>data.set(k,structuredClone(v)),list:()=>data,transaction:fn=>fn(storage)};
  const queue=new GsaReviews({storage});
  const env={GSA_REVIEWS:{idFromName:()=>1,get:()=>queue}};
  const packet={sha256:'a'.repeat(64),title:'Fixture',source:'https://example.org',pdf:'https://drive.google.com/example'};
  const put=()=>queue.fetch(new Request(url+'/operator',{method:'POST',headers:{'X-GSA-Actor':'operator'},body:JSON.stringify({id:'test',action:'put',packet})}));
  const {revision}=await (await put()).json();
  const form=new URLSearchParams({revision,decision:'Approved'});
  const post=email=>gsaRoute(new Request(url+'/work/test',{method:'POST',headers:{Origin:new URL(url).origin},body:form}),env,session(email));
  assert.equal((await post('b13llama@gmail.com')).status,422);
  for(const key of ['bibliographic_match','first_and_last_pages','body_spot_check','completeness','rights','filename_and_destination','format_preference'])form.set(key,'on');
  assert.equal((await post('b13llama@gmail.com')).status,303);
  assert.equal((await post('b13llama@gmail.com')).status,409);
  assert.equal((await post('davidjasonharper@gmail.com')).status,303);
  assert.deepEqual(Object.keys(data.get('test').decisions),['Samuel','David']);
  await put();assert.equal(Object.keys(data.get('test').decisions).length,2);
  packet.title='New edition';await put();
  assert.equal((await post('b13llama@gmail.com')).status,409);
  assert.deepEqual(data.get('test').decisions,{});
});

test('private Drive reviewer copies render inline with the checklist and a separate-tab fallback', async () => {
  const packet = {title:'Sample', pdf:'https://drive.google.com/file/d/test_id-1/view?usp=sharing&resourcekey=test-key'};
  const queue = new GsaReviews({storage:{get:async()=>({packet,decisions:{},revision:'1'})}});
  const env = {GSA_REVIEWS:{idFromName:()=>1,get:()=>queue}};
  const open = () => gsaRoute(new Request(url+'/work/test'),env,session('b13llama@gmail.com'));
  const result = await open();
  assert.match(result.headers.get('Content-Security-Policy'), /frame-src https:\/\/drive\.google\.com;/);
  const html = await result.text();
  assert.match(html, /<iframe src="https:\/\/drive.google.com\/file\/d\/test_id-1\/preview\?resourcekey=test-key"/);
  assert.match(html, /Open PDF in a new tab/);
  assert.match(html, /Approve publication/);
  packet.pdf = 'https://example.org/file/d/test/view';
  assert.doesNotMatch(await (await open()).text(), /<iframe/);
});

function memory() {
  const data = new Map();
  const storage = {
    get: k => structuredClone(data.get(k)),
    put: (k, v) => { if (typeof k === 'object') for (const [a, b] of Object.entries(k)) data.set(a, structuredClone(b)); else data.set(k, structuredClone(v)); },
    delete: keys => { for (const k of [].concat(keys)) data.delete(k); },
    list: (opts = {}) => new Map([...data].filter(([k]) => !opts.prefix || k.startsWith(opts.prefix))),
    transaction: fn => fn(storage),
  };
  const queue = new GsaReviews({storage});
  return {data, queue, env: {GSA_REVIEWS: {idFromName: () => 1, get: () => queue}}};
}
const operator = (queue, body) => queue.fetch(new Request(url + '/operator', {method: 'POST', headers: {'X-GSA-Actor': 'operator'}, body: JSON.stringify(body)}));
const basePacket = () => ({sha256: 'b'.repeat(64), title: 'Fixture', citation: 'Smith, Fixture (1999)', filename: 'Smith, Fixture.pdf',
  folder: 'Archive / Read', destination: 'read1', rights: 'CC BY', entry: 'Nov 19: Fixture', validation: 'Passed',
  source: 'https://example.org', pdf: 'https://drive.google.com/file/d/x/view'});
const edit = (env, email, field, value, origin = new URL(url).origin) => gsaRoute(new Request(url + '/work/test/edit', {method: 'POST',
  headers: {Origin: origin, 'Content-Type': 'application/json'}, body: JSON.stringify({field, value})}), env, session(email));
const approveAll = async (env, revision) => {
  const form = new URLSearchParams({revision, decision: 'Approved'});
  for (const key of ['bibliographic_match','first_and_last_pages','body_spot_check','completeness','rights','filename_and_destination','format_preference']) form.set(key, 'on');
  return gsaRoute(new Request(url + '/work/test', {method: 'POST', headers: {Origin: new URL(url).origin}, body: form}), env, session('b13llama@gmail.com'));
};

test('reviewers edit fields with autosave; edits change the version and reset decisions', async () => {
  const {data, queue, env} = memory();
  const {revision} = await (await operator(queue, {id: 'test', action: 'put', packet: basePacket()})).json();
  assert.equal((await approveAll(env, revision)).status, 303);
  let res = await edit(env, 'davidjasonharper@gmail.com', 'title', '  Fixture, Revised Edition ');
  assert.equal(res.status, 200);
  const saved = await res.json();
  assert.equal(saved.value, 'Fixture, Revised Edition');
  assert.equal(saved.decisionsCleared, true);
  assert.notEqual(saved.revision, revision);
  assert.deepEqual(data.get('test').decisions, {});
  assert.equal(data.get('test').edits.title.by, 'David');
  assert.equal(data.get('test').history.at(-1).from, 'Fixture');
  const html = await (await gsaRoute(new Request(url + '/work/test'), env, session('b13llama@gmail.com'))).text();
  assert.match(html, /<h1 id="page-title">Fixture, Revised Edition<\/h1>/);
  assert.match(html, /value="Fixture, Revised Edition"/);
  assert.match(html, /Edited by David/);
  assert.match(html, new RegExp(`name="revision" value="${saved.revision}"`));
  assert.match(html, /<script src="\/gsa\/review.js" defer><\/script>/);
  // Typing the original back removes the edit and restores the original version.
  const back = await (await edit(env, 'b13llama@gmail.com', 'title', 'Fixture')).json();
  assert.equal(back.revision, revision);
  assert.equal(data.get('test').edits.title, undefined);
});

test('edits are validated, need an assigned reviewer and a same-origin request', async () => {
  const {queue, env} = memory();
  await operator(queue, {id: 'test', action: 'put', packet: basePacket()});
  for (const [field, value, message] of [['title', '   ', /can't be empty/], ['filename', 'Smith/Fixture.pdf', /cannot contain/],
    ['filename', 'Smith, Fixture.epub', /Keep the \.pdf extension/], ['title', 'two\nlines', /not allowed/], ['sha256', 'c'.repeat(64), /cannot be edited/]]) {
    const res = await edit(env, 'b13llama@gmail.com', field, value);
    assert.ok(res.status >= 400, field);
    assert.match((await res.json()).error, message);
  }
  assert.equal((await edit(env, 'b13llama@gmail.com', 'filename', 'Smith, Fixture (2nd ed.).pdf')).status, 200);
  assert.equal((await edit(env, 'stranger@example.org', 'title', 'x')).status, 403);
  assert.equal((await edit(env, 'b13llama@gmail.com', 'title', 'x', 'https://other.example')).status, 403);
});

test('operator folder snapshot feeds the explorer and destination edits', async () => {
  const {data, queue, env} = memory();
  await operator(queue, {id: 'test', action: 'put', packet: basePacket()});
  const open = id => gsaRoute(new Request(url + '/folders/' + id), env, session('b13llama@gmail.com'));
  assert.equal((await open('root')).status, 404);
  const snap = await operator(queue, {action: 'folders', at: '2026-11-19T20:00:00Z', root: {id: 'root1', name: 'Archive'}, folders: [
    {id: 'read1', name: 'Read', parent: 'root1'}, {id: 'bible', name: 'Bible', parent: 'read1'}, {id: 'art', name: 'Articles', parent: 'read1'},
    {id: 'stray', name: 'Elsewhere', parent: 'unrelated'}]});
  assert.deepEqual(await snap.json(), {folders: 4});
  const root = await (await open('root')).json();
  assert.equal(root.id, 'root1');
  assert.deepEqual(root.children, [{id: 'read1', name: 'Read', count: 2}]);
  const read = await (await open('read1')).json();
  assert.deepEqual(read.children.map(c => c.name), ['Articles', 'Bible']);
  assert.deepEqual(read.trail.map(t => t.name), ['Archive', 'Read']);
  assert.equal((await open('stray')).status, 404);
  assert.match((await (await edit(env, 'b13llama@gmail.com', 'destination', 'root1')).json()).error, /not the archive root/);
  assert.match((await (await edit(env, 'b13llama@gmail.com', 'destination', 'stray')).json()).error, /not in the archive folder list/);
  const moved = await (await edit(env, 'b13llama@gmail.com', 'destination', 'bible')).json();
  assert.equal(moved.value, 'Archive / Read / Bible');
  // The operator sees base packet plus edits; a re-queue with the edited values absorbs them.
  const got = await (await operator(queue, {id: 'test', action: 'get'})).json();
  assert.equal(got.edits.destination.value, 'bible');
  assert.equal(got.packet.destination, 'read1');
  await operator(queue, {id: 'test', action: 'put', packet: {...basePacket(), destination: 'bible', folder: 'Archive / Read / Bible'}});
  assert.deepEqual(data.get('test').edits, {});
  assert.equal(data.get('test').revision, moved.revision);
  // The queue page lists works only, not folder records.
  const list = await (await gsaRoute(new Request(url), env, session('b13llama@gmail.com'))).text();
  assert.equal((list.match(/<section>/g) || []).length, 1);
});

test('the page script is served after sign-in and allowed by the CSP', async () => {
  const {env} = memory();
  assert.equal((await gsaRoute(new Request(url + '/review.js'), env, session(null))).status, 303);
  const res = await gsaRoute(new Request(url + '/review.js'), env, session('b13llama@gmail.com'));
  assert.match(res.headers.get('Content-Type'), /javascript/);
  assert.match(res.headers.get('Content-Security-Policy'), /script-src 'self'; connect-src 'self'/);
  const code = await res.text();
  assert.match(code, /Changes saved/);
  new Function(code); // parses
});

test('folders known only by path can be browsed but not chosen', async () => {
  const {queue, env} = memory();
  await operator(queue, {id: 'test', action: 'put', packet: basePacket()});
  await operator(queue, {action: 'folders', source: 'Table of Contents', root: {id: 'root1', name: 'Archive'}, folders: [
    {id: 'toc-0123456789abcdef01234567', name: '2025', parent: 'root1'}, {id: 'month11real', name: '11', parent: 'toc-0123456789abcdef01234567'}]});
  assert.match((await (await edit(env, 'b13llama@gmail.com', 'destination', 'toc-0123456789abcdef01234567')).json()).error, /only holds other folders/);
  assert.equal((await (await edit(env, 'b13llama@gmail.com', 'destination', 'month11real')).json()).value, 'Archive / 2025 / 11');
  const root = await (await gsaRoute(new Request(url + '/folders/root'), env, session('b13llama@gmail.com'))).json();
  assert.equal(root.source, 'Table of Contents');
});
