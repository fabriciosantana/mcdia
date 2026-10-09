import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {aggregate,filterRows,monthRange,normalize,toCSV,csvCell,sourceUrl} from '../analytics.mjs';
const raw=readFileSync(new URL('../data/dashboard.json',import.meta.url));
const {rows,meta}=JSON.parse(raw);
const manifest=JSON.parse(readFileSync(new URL('../data/manifest.json',import.meta.url)));
const base={from:'2019-02',to:'2023-01',kind:'Discurso',party:'',uf:'',author:'',theme:'',query:''};
const names=Object.keys(meta.themes);
test('snapshot checksum, unique IDs and scope reconcile',()=>{
 assert.equal(createHash('sha256').update(raw).digest('hex'),manifest.dashboardSha256);
 assert.equal(rows.length,12414);assert.equal(new Set(rows.map(r=>r.id)).size,rows.length);
 assert.equal(meta.audit.sourceRows,meta.audit.scopeRows+meta.audit.excludedRows);
 assert.ok(rows.every(r=>/^\d+$/.test(r.id)&&r.date>='2019-02-01'&&r.date<='2023-01-31'));
});
test('default totals independently reconciled with raw Parquet audit',()=>{
 const chosen=filterRows(rows,base),s=aggregate(chosen,base.from,base.to,names);
 assert.equal(s.total,4045);assert.equal(s.authors.length,106);assert.equal(s.fullText,3425);
 assert.equal(s.top10,1955);assert.equal(s.monthly.reduce((n,r)=>n+r[1],0),s.total);
 assert.deepEqual(Object.fromEntries(['2019','2020','2021','2022','2023'].map(y=>[y,chosen.filter(r=>r.date.startsWith(y)).length])),{2019:1788,2020:751,2021:721,2022:784,2023:1});
});
test('combined filters preserve predicates and partition totals',()=>{
 const f={...base,party:'PT',uf:'RS',author:'825',from:'2019-02',to:'2019-12'};
 const chosen=filterRows(rows,f);assert.ok(chosen.length>0);
 assert.ok(chosen.every(r=>r.authorId==='825'&&r.party==='PT'&&r.uf==='RS'&&r.kind==='Discurso'&&r.date.startsWith('2019')));
 const total=[...new Set(rows.map(r=>r.uf))].reduce((n,uf)=>n+filterRows(rows,{...base,uf}).length,0);assert.equal(total,4045);
});
test('search ignores accents; themes remain multi-label and selectable',()=>{
 assert.equal(normalize('EDUCAÇÃO'),'educacao');
 assert.deepEqual(filterRows(rows,{...base,query:'educação'}),filterRows(rows,{...base,query:'EDUCACAO'}));
 const chosen=filterRows(rows,base),s=aggregate(chosen,base.from,base.to,names);
 for(const [theme,count]of s.themes)assert.equal(filterRows(rows,{...base,theme}).length,count);
 assert.equal(filterRows(rows,{...base,theme:'__none__'}).length,s.noTheme);
});
test('empty results and monthly zero bins are well-defined',()=>{
 const chosen=filterRows(rows,{...base,query:'zzzz-no-match-2026'}),s=aggregate(chosen,base.from,base.to,names);
 assert.equal(chosen.length,0);assert.equal(s.top10,0);assert.equal(s.fullText,0);assert.equal(s.monthly.length,48);assert.ok(s.monthly.every(r=>r[1]===0));
 assert.deepEqual(monthRange('2022-12','2023-02'),['2022-12','2023-01','2023-02']);
 assert.deepEqual(monthRange('2023-01','2019-02'),[]);
});
test('CSV quotes content, neutralizes formulas and uses official sources',()=>{
 assert.equal(csvCell('a;"b"'),'"a;""b"""');assert.equal(csvCell('=1+1'),'"\'=1+1"');assert.equal(csvCell('  @SUM(A1)'),'"\'  @SUM(A1)"');
 assert.equal(sourceUrl('451286'),'https://www25.senado.leg.br/web/atividade/pronunciamentos/-/p/texto/451286');
 const csv=toCSV(rows.slice(0,2));assert.equal(csv.charCodeAt(0),0xFEFF);assert.equal(csv.split('\r\n').length,3);assert.ok(csv.includes('partido_na_data'));
});
