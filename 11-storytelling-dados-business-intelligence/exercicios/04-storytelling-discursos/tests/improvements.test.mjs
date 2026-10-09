import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {decodeCatalog,comparePeriods,themeEvolution,cumulativeAuthors,qualityBy,themeEvidence,reviewMetrics,validateReview,validPeriod,filterRows} from '../analytics.mjs';
import {defaults,parseState,serializeState} from '../state.mjs';
import {zipStore} from '../export.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url)));
const legacy=read('data/dashboard.json'),catalog=read('data/catalog.json'),manifest=read('data/manifest.json'),rows=decodeCatalog(catalog),names=catalog.themes;
const sample=read('data/review-sample.json');
test('compact index preserves every analytic field and all monthly texts/hashes',()=>{
 assert.equal(rows.length,legacy.rows.length);assert.ok(manifest.catalog.bytes<600000);
 const reconstituted=new Map();for(const descriptor of Object.values(catalog.fragments)){
  const bytes=readFileSync(new URL('../'+descriptor.path,import.meta.url));assert.equal(createHash('sha256').update(bytes).digest('hex'),descriptor.sha256);
  for(const [id,text]of Object.entries(JSON.parse(bytes)))reconstituted.set(id,text);
 }
 for(let i=0;i<rows.length;i++){
  const a=rows[i],b=legacy.rows[i];for(const key of ['id','date','author','authorId','party','uf','kind','fullText','themes'])assert.deepEqual(a[key],b[key]);
  assert.equal(a.hasSummary,!!b.summary);assert.equal(a.hasIndex,!!b.index);assert.deepEqual(reconstituted.get(a.id),{summary:b.summary,index:b.index});
 }
 assert.equal(reconstituted.size,rows.length);
});
test('A/B changes, explicit equal calendar, overlap and zero baseline',()=>{
 const a={from:'2019-02',to:'2019-12'},b={from:'2020-02',to:'2020-12'};
 const result=comparePeriods(rows,defaults,a,b,names);
 assert.equal(result.A.total,1788);const expected=legacy.rows.filter(r=>r.kind==='Discurso'&&r.date>='2020-02-01'&&r.date<='2020-12-31').length;
 assert.equal(result.B.total,expected);assert.equal(result.delta,expected-1788);assert.equal(result.warnings.length,0);
 assert.ok(comparePeriods(rows,defaults,a,a,names).warnings.some(x=>x.includes('sobrepõem')));
 const zero=comparePeriods(rows,{...defaults,author:'nonexistent'},a,b,names);assert.equal(zero.relative,null);assert.equal(zero.delta,0);
 const different=comparePeriods(rows,defaults,a,{from:'2021-01',to:'2021-06'},names);assert.equal(different.warnings.length,2);
 assert.equal(validPeriod('2022-13','2023-01'),false);assert.equal(validPeriod('2019-01','2020-01'),false);
});
test('theme proportions use monthly denominators and gaps, not filtered theme totals',()=>{
 const fixture=[{date:'2020-01-01',themes:['Educação']},{date:'2020-01-02',themes:[]},{date:'2020-03-01',themes:[]}];
 const s=themeEvolution(fixture,'2020-01','2020-03','Educação');assert.deepEqual(s.map(x=>x.share),[50,null,0]);assert.deepEqual(s.map(x=>x.total),[2,0,1]);
});
test('cumulative frequency has exact final 100% and a meaningful crossing',()=>{
 const out=cumulativeAuthors([{id:'a',count:6},{id:'b',count:3},{id:'c',count:1}]);assert.deepEqual(out.map(r=>r.share),[60,90,100]);assert.deepEqual(cumulativeAuthors([]),[]);
});
test('quality aggregates reconcile without conflating missing summary and full text',()=>{
 const groups=qualityBy(rows,'kind');assert.equal(groups.reduce((n,r)=>n+r.total,0),12414);assert.equal(groups.reduce((n,r)=>n+r.missingFull,0),623);assert.equal(groups.reduce((n,r)=>n+r.missingSummary,0),45);
 const months=qualityBy(rows,'month','2019-02','2023-01');assert.equal(months.length,48);assert.equal(months.reduce((n,r)=>n+r.total,0),12414);
});
test('explanations exactly reproduce Python theme labels across entire corpus',()=>{
 for(const row of legacy.rows){assert.deepEqual(themeEvidence(row,legacy.meta.themes).map(e=>e.theme),row.themes);}
 assert.equal(themeEvidence({summary:'sustentável',index:''},{Saúde:['sus']}).length,0);
 const found=themeEvidence({summary:'SAÚDE',index:'saude'},{Saúde:['saude']});assert.deepEqual(found[0].matches[0].fields,['summary','index']);
});
test('sample is balanced and AI-assisted labels never become human truth',()=>{
 assert.equal(sample.items.length,60);assert.equal(new Set(sample.items.map(i=>i.key)).size,60);
 for(const theme of names)for(const predicted of [true,false])assert.equal(sample.items.filter(i=>i.theme===theme&&i.predicted===predicted).length,5);
 const ai=read('data/assisted-review.json');assert.equal(ai.reviewerType,'ai-assisted');
 const m=reviewMetrics(sample.items,Object.fromEntries(ai.items.map(x=>[x.key,x])));assert.equal(m.resolved,60);assert.equal(m.fp,3);assert.equal(m.fn,2);
 assert.equal(reviewMetrics(sample.items,{}).pending,60);
 assert.throws(()=>validateReview(ai,sample.items,catalog.meta.revision,catalog.meta.rulesVersion));
 const human={schemaVersion:1,datasetRevision:catalog.meta.revision,rulesVersion:catalog.meta.rulesVersion,reviewerType:'human',reviewer:'Tester',annotations:{[sample.items[0].key]:{label:'yes',note:'tested'}}};
 assert.equal(Object.keys(validateReview(human,sample.items,catalog.meta.revision,catalog.meta.rulesVersion).annotations).length,1);
 assert.throws(()=>validateReview({...human,datasetRevision:'bad'},sample.items,catalog.meta.revision,catalog.meta.rulesVersion));
 assert.throws(()=>validateReview({...human,annotations:{fake:{label:'yes',note:''}}},sample.items,catalog.meta.revision,catalog.meta.rulesVersion));
});
test('URL round trip preserves empty All selection, accents, dates and comparative state',()=>{
 const state={...defaults,kind:'',theme:'Educação',query:'a & b = c',mode:'share',aFrom:'2021-02',aTo:'2021-12',voice2:'825'};
 assert.deepEqual(parseState('?'+serializeState(state)).state,state);
 const bad=parseState('?from=2020-13&mode=evil&theme=bad',{theme:['','Educação']});assert.equal(bad.warnings.length,3);assert.equal(bad.state.from,defaults.from);
});
test('ZIP contains UTF-8 text and central directory for a single reproducible download',async()=>{
 const bytes=new Uint8Array(await zipStore({'recorte.csv':'a;b\r\n1;ação','analise.json':'{"ok":true}'}).arrayBuffer()),v=new DataView(bytes.buffer);
 assert.equal(v.getUint32(0,true),0x04034b50);assert.equal(v.getUint32(bytes.length-22,true),0x06054b50);assert.equal(v.getUint16(bytes.length-14,true),2);
 const nameLen=v.getUint16(26,true),size=v.getUint32(18,true);assert.equal(new TextDecoder().decode(bytes.slice(30+nameLen,30+nameLen+size)),'a;b\r\n1;ação');
});
