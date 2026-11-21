// Pure analytical functions shared by the browser and Node tests.
export const normalize = value => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR');
export function filterRows(rows, f) {
  const query = normalize(f.query).trim();
  return rows.filter(r => r.date.slice(0, 7) >= f.from && r.date.slice(0, 7) <= f.to &&
    (!f.kind || r.kind === f.kind) && (!f.party || r.party === f.party) &&
    (!f.uf || r.uf === f.uf) && (!f.author || r.authorId === f.author) &&
    (!f.theme || (f.theme === '__none__' ? !r.themes.length : r.themes.includes(f.theme))) &&
    (!query || (r.searchText ?? normalize((r.summary ?? '') + ' ' + (r.index ?? ''))).includes(query)));
}
export function monthRange(from, to) {
  if (!/^\d{4}-\d{2}$/.test(from) || !/^\d{4}-\d{2}$/.test(to) || from > to) return [];
  const months = []; let [y, m] = from.split('-').map(Number);
  if (m < 1 || m > 12) return [];
  while (months.length < 1200) {
    const month = `${y}-${String(m).padStart(2, '0')}`;
    if (month > to) break;
    months.push(month); m++; if (m === 13) { m = 1; y++; }
  }
  return months;
}
export function aggregate(rows, from, to, themeNames) {
  const monthly = new Map(monthRange(from,to).map(m=>[m,0]));
  const authors = new Map(), themes = new Map(themeNames.map(t=>[t,0]));
  let fullText=0, noTheme=0;
  for (const r of rows) {
    const month=r.date.slice(0,7); monthly.set(month,(monthly.get(month)||0)+1);
    const author=authors.get(r.authorId) ?? {id:r.authorId,name:r.author,count:0};
    author.count++; authors.set(r.authorId,author);
    fullText+=Number(r.fullText); noTheme+=Number(r.themes.length===0);
    for(const theme of r.themes) themes.set(theme,(themes.get(theme)||0)+1);
  }
  const ranking=[...authors.values()].sort((a,b)=>b.count-a.count || a.name.localeCompare(b.name,'pt-BR'));
  const top10=ranking.slice(0,10).reduce((sum,r)=>sum+r.count,0);
  return {total:rows.length,authors:ranking,monthly:[...monthly],themes:[...themes].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0],'pt-BR')),fullText,noTheme,top10};
}
export const sourceUrl = id => `https://www25.senado.leg.br/web/atividade/pronunciamentos/-/p/texto/${encodeURIComponent(id)}`;
export function csvCell(value) {
  let text=String(value ?? '');
  // Neutralize spreadsheet formula injection, including leading whitespace.
  if (/^\s*[=+@-]/u.test(text) || /^[\t\r\n]/u.test(text)) text="'"+text;
  return '"'+text.replaceAll('"','""')+'"';
}
export function toCSV(rows) {
  const header=['codigo','data','orador','codigo_parlamentar','partido_na_data','uf','tipo','temas_exploratorios','texto_integral_disponivel','resumo','indexacao','fonte'];
  const lines=rows.map(r=>[r.id,r.date,r.author,r.authorId,r.party,r.uf,r.kind,r.themes.join(' | '),r.fullText?'sim':'não',r.summary,r.index,sourceUrl(r.id)]);
  return '\uFEFF'+[header,...lines].map(row=>row.map(csvCell).join(';')).join('\r\n');
}

export const validPeriod = (from,to) => /^20\d{2}-(0[1-9]|1[0-2])$/.test(from) && /^20\d{2}-(0[1-9]|1[0-2])$/.test(to) && from >= '2019-02' && to <= '2023-01' && from <= to;
export function decodeCatalog(catalog){
 return catalog.rows.map(([id,date,authorId,p,u,k,flags,mask])=>({id,date,authorId,author:catalog.authors[authorId],party:catalog.dictionaries.party[p],uf:catalog.dictionaries.uf[u],kind:catalog.dictionaries.kind[k],fullText:!!(flags&1),hasSummary:!!(flags&2),hasIndex:!!(flags&4),themes:catalog.themes.filter((_,i)=>mask&(1<<i))}));
}
export function comparePeriods(rows, filters, a, b, names){
 const aRows=filterRows(rows,{...filters,...a}),bRows=filterRows(rows,{...filters,...b});
 const A=aggregate(aRows,a.from,a.to,names),B=aggregate(bRows,b.from,b.to,names);
 const monthsA=monthRange(a.from,a.to),monthsB=monthRange(b.from,b.to);
 const warnings=[];
 if(monthsA.length!==monthsB.length)warnings.push('Duração diferente: compare também a média por mês.');
 if(monthsA.map(m=>m.slice(5)).join(',')!==monthsB.map(m=>m.slice(5)).join(','))warnings.push('Os meses do ano diferem; sazonalidade pode afetar a comparação.');
 if(a.from<=b.to&&b.from<=a.to)warnings.push('Os períodos se sobrepõem e compartilham registros.');
 if(a.to==='2023-01'||b.to==='2023-01')warnings.push('Janeiro de 2023 tem registros observados somente até 10/01.');
 const delta=B.total-A.total,relative=A.total?delta/A.total*100:null;
 return {A,B,aRows,bRows,delta,relative,monthsA:monthsA.length,monthsB:monthsB.length,warnings};
}
export function themeEvolution(rows,from,to,theme){
 const buckets=new Map(monthRange(from,to).map(month=>[month,{month,total:0,count:0,share:null}]));
 for(const row of rows){const b=buckets.get(row.date.slice(0,7));if(b){b.total++;b.count+=Number(row.themes.includes(theme));}}
 return [...buckets.values()].map(b=>({...b,share:b.total?100*b.count/b.total:null}));
}
export function cumulativeAuthors(authors){
 const total=authors.reduce((s,r)=>s+r.count,0);let cumulative=0;
 return authors.map((r,i)=>{cumulative+=r.count;return {...r,rank:i+1,cumulative,share:total?100*cumulative/total:null};});
}
export function qualityBy(rows,key='month',from='',to=''){
 const buckets=new Map(key==='month'?monthRange(from,to).map(m=>[m,{key:m,total:0,missingFull:0,missingSummary:0,missingIndex:0}]):[]);
 for(const r of rows){const id=key==='month'?r.date.slice(0,7):r.kind;const b=buckets.get(id)||{key:id,total:0,missingFull:0,missingSummary:0,missingIndex:0};b.total++;b.missingFull+=Number(!r.fullText);b.missingSummary+=Number(!(r.hasSummary??!!r.summary));b.missingIndex+=Number(!(r.hasIndex??!!r.index));buckets.set(id,b);}
 return [...buckets.values()].sort((a,b)=>a.key.localeCompare(b.key,'pt-BR'));
}
export function themeEvidence(row,dictionary){
 const evidence=[];
 for(const [theme,terms]of Object.entries(dictionary)){
  const matches=terms.map(term=>{const re=new RegExp(`(^|[^\\p{L}\\p{N}_])${term.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}(?=$|[^\\p{L}\\p{N}_])`,'u');
   const fields=['summary','index'].filter(k=>re.test(normalize(row[k])));return {term,fields};}).filter(m=>m.fields.length);
  if(matches.length)evidence.push({theme,matches});
 }
 return evidence;
}
export function reviewMetrics(sample,annotations){
 const result={tp:0,fp:0,tn:0,fn:0,uncertain:0,pending:0,total:sample.length};
 for(const item of sample){const label=annotations[item.key]?.label;
  if(!label){result.pending++;continue;}if(label==='uncertain'){result.uncertain++;continue;}
  result[item.predicted?(label==='yes'?'tp':'fp'):(label==='yes'?'fn':'tn')]++;
 }
 const resolved=result.tp+result.fp+result.tn+result.fn;
 return {...result,resolved,precision:result.tp+result.fp?result.tp/(result.tp+result.fp):null,recall:result.tp+result.fn?result.tp/(result.tp+result.fn):null};
}
export function validateReview(value,sample,revision,rulesVersion){
 if(value?.schemaVersion!==1||value.datasetRevision!==revision||value.rulesVersion!==rulesVersion||value.reviewerType!=='human'||typeof value.reviewer!=='string'||!value.reviewer.trim())throw new Error('Revisão incompatível: confira revisão, regras e identificação humana.');
 const keys=new Set(sample.map(x=>x.key));if(!value.annotations||typeof value.annotations!=='object'||Array.isArray(value.annotations))throw new Error('Anotações inválidas.');
 const clean={};for(const [key,a]of Object.entries(value.annotations)){
  if(!keys.has(key)||!['yes','no','uncertain'].includes(a?.label)||typeof a.note!=='string'||a.note.length>4000)throw new Error('Item, rótulo ou nota inválidos.');
  clean[key]={label:a.label,note:a.note,reviewer:typeof a.reviewer==='string'?a.reviewer.slice(0,120):value.reviewer.slice(0,120)};
 }
 return {...value,annotations:clean};
}
