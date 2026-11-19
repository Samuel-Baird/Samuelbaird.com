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
