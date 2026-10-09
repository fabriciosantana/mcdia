import {filterRows,aggregate,sourceUrl,toCSV,themeEvidence,validPeriod} from './analytics.mjs';
import {DataStore} from './data-store.mjs';
import {defaults,parseState,serializeState} from './state.mjs';
import {$,fmt,pct,monthName,dayName,esc,options,table,evidenceHTML,barChart} from './ui.mjs';
import {comparison,distribution,evolution,quality,historyContext} from './views.mjs';
import {setupReview} from './review.mjs';
import {download,zipStore} from './export.mjs';
const mainKeys=['from','to','kind','party','uf','author','theme','query'];
let store,allRows=[],meta,state={...defaults},filtered=[],stats,comparisonResult,page=0,renderId=0,recordsId=0,choices={};
const pageSize=8;
const fromControls=()=>{const value={...state};for(const k of Object.keys(defaults))if($(k))value[k]=$(k).value;return value;};
function applyControls(){for(const k of Object.keys(defaults))if($(k))$(k).value=state[k];document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===state.mode)));}
function writeURL(push=true){const next='?'+serializeState(state)+location.hash;if(location.search+location.hash!==next)history[push?'pushState':'replaceState'](null,'',next);}
function commit(changes={},push=true){state={...fromControls(),...changes};applyControls();writeURL(push);render();}
function reset(){state={...defaults};applyControls();writeURL();render();}
function fail(message,retry){$('operation-error').hidden=false;$('operation-error').replaceChildren(document.createTextNode(message+' '));if(retry){const b=document.createElement('button');b.textContent='Tentar novamente';b.type='button';b.addEventListener('click',retry);$('operation-error').append(b);}}
function selectMonth(month,theme){commit({from:month,to:month,...(theme?{theme}:{})});$('from').focus();}
function renderTimeline(){
 const {monthly,total}=stats;
 if(!total){$('timeline').innerHTML='<p class="empty">Sem registros para desenhar a série.</p>';$('timeline-mobile').replaceChildren();return;}
 const values=monthly.map(([m,n])=>[m,state.mode==='share'?100*n/total:n,n]);const max=Math.max(...values.map(r=>r[1]));const step=max<=5?1:10**Math.floor(Math.log10(max/4));const ceiling=Math.ceil(max/step)*step;
 const width=1040,height=305,left=60,right=18,top=36,bottom=43,w=width-left-right,h=height-top-bottom,band=w/values.length,peak=Math.max(...monthly.map(r=>r[1]));const y=v=>top+h-h*v/ceiling;
 let svg=`<svg viewBox="0 0 ${width} ${height}" role="group" aria-label="Pronunciamentos por mês; escala de zero a ${fmt(ceiling)} ${state.mode==='share'?'por cento do recorte':'registros'}"><text x="${left}" y="17" font-size="13">${state.mode==='share'?'% dos registros do recorte':'Registros por mês'} · eixo a partir de zero</text>`;
 for(let i=0;i<=4;i++){let v=ceiling*i/4;svg+=`<line x1="${left}" x2="${width-right}" y1="${y(v)}" y2="${y(v)}" stroke="#e5eae6"/><text x="${left-9}" y="${y(v)+4}" text-anchor="end" font-size="13">${fmt(v)}${state.mode==='share'?'%':''}</text>`;}
 values.forEach(([m,v,n],i)=>{const x=left+i*band+band*.12,bw=band*.76;svg+=`<rect class="month-bar${n===peak?' peak':''}" x="${x}" y="${y(v)}" width="${bw}" height="${Math.max(0,top+h-y(v))}" tabindex="0" role="button" data-month="${m}" aria-label="${esc(monthName(m))}: ${fmt(n)} registros, ${pct(n,total)}. Filtrar mês."><title>${esc(monthName(m))}: ${fmt(n)} · ${pct(n,total)}</title></rect>`;if(values.length<=12||m.endsWith('-01')||i===0)svg+=`<text x="${x+bw/2}" y="${height-15}" text-anchor="middle" font-size="12">${values.length<=12?esc(monthName(m)):m.slice(0,4)}</text>`;});
 $('timeline').innerHTML=svg+'</svg>';
 const years=[...new Set(monthly.map(r=>r[0].slice(0,4)))];
 $('timeline-mobile').innerHTML=years.map((year,i)=>`<details class="mobile-year" ${i===0?'open':''}><summary>${year} · meses do recorte</summary>${values.filter(r=>r[0].startsWith(year)).map(([m,v,n])=>`<button class="month-mobile-row" type="button" data-month="${m}" aria-label="${esc(monthName(m))}: ${fmt(n)} registros, ${pct(n,total)}. Filtrar mês."><span>${esc(monthName(m))}</span><span class="bar-track"><span class="bar-fill" style="width:${v/ceiling*100}%"></span></span><b>${state.mode==='share'?pct(n,total):fmt(n)}</b></button>`).join('')}</details>`).join('')+`<p class="footnote">Escala comum a todos os anos: 0–${fmt(ceiling)} ${state.mode==='share'?'% do recorte':'registros'}.</p>`;
 for(const el of document.querySelectorAll('[data-month]')){el.addEventListener('click',()=>selectMonth(el.dataset.month));if(el.tagName.toLowerCase()==='rect')el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selectMonth(el.dataset.month);}});}
}
async function renderRecords(){
 const token=++recordsId;const ordered=state.sort==='oldest'?[...filtered].reverse():filtered,totalPages=Math.max(1,Math.ceil(ordered.length/pageSize));page=Math.min(page,totalPages-1);const start=page*pageSize,visible=ordered.slice(start,start+pageSize);
 $('results-count').textContent=ordered.length?`${fmt(start+1)}–${fmt(start+visible.length)} de ${fmt(ordered.length)} registros neste recorte`:'Nenhum registro encontrado.';
 $('page-info').textContent=`Página ${ordered.length?page+1:0} de ${ordered.length?totalPages:0}`;$('prev').disabled=page===0;$('next').disabled=page>=totalPages-1;
 if(!visible.length){$('records').innerHTML='<div class="empty"><strong>Não há registros com esta combinação.</strong><br>Remova um filtro ou restaure a visão inicial.</div>';return;}
 $('records').setAttribute('aria-busy','true');$('records').innerHTML='<p role="status">Carregando apenas os textos desta página…</p>';
 try{
  const detailed=await store.hydrate(visible);if(token!==recordsId)return;
  $('records').innerHTML=detailed.map(r=>`<article class="record"><div><time class="record-date" datetime="${esc(r.date)}">${dayName(r.date)}</time><span class="record-kind">${esc(r.kind)}</span></div><div><h3>${esc(r.author)}<small>${esc(r.party)} · ${esc(r.uf)}</small></h3><p>${esc(r.summary||'Resumo não disponível neste registro.')}</p><a href="${sourceUrl(r.id)}" target="_blank" rel="noopener noreferrer">Consultar registro no Senado ↗ #${esc(r.id)}</a><div class="tags">${r.themes.map(t=>`<span class="tag">${esc(t)}</span>`).join('')}${!r.fullText?'<span class="tag warning">Texto integral ausente no dataset</span>':''}</div><details><summary>Por que estes temas? Ver palavras e campos</summary>${evidenceHTML(themeEvidence(r,meta.themes))}<p><strong>Indexação original:</strong> ${esc(r.index||'Não disponível')}</p></details></div></article>`).join('');
 }catch(e){if(token!==recordsId)return;$('records').innerHTML='<p class="empty">Os indicadores estão disponíveis, mas os textos desta página não carregaram.</p>';fail(e.message,()=>{$('operation-error').hidden=true;renderRecords();});}finally{if(token===recordsId)$('records').setAttribute('aria-busy','false');}
}
function resultsVisible(visible){document.querySelectorAll('.metrics,#ritmo,#comparar,#vozes,#concentracao,#evolucao,#qualidade,#evidencias').forEach(el=>el.hidden=!visible);}
async function render(){
 const token=++renderId;recordsId++;page=0;$('dashboard').setAttribute('aria-busy','true');$('operation-error').hidden=true;$('operation-status').textContent='';$('export').disabled=true;$('export-package').disabled=true;
 try{
  if(state.query.trim()){
   resultsVisible(false);
   $('operation-status').textContent='Buscando nos textos dos períodos selecionados…';
   const periods=[[state.from,state.to],[state.aFrom,state.aTo],[state.bFrom,state.bTo]].filter(p=>validPeriod(...p));
   const candidates=allRows.filter(r=>periods.some(([a,b])=>r.date.slice(0,7)>=a&&r.date.slice(0,7)<=b)&&(!state.kind||r.kind===state.kind)&&(!state.party||r.party===state.party)&&(!state.uf||r.uf===state.uf));
   const detailed=await store.hydrate(candidates);if(token!==renderId)return;const details=new Map(detailed.map(r=>[r.id,r]));for(const row of candidates)Object.assign(row,details.get(row.id));
   $('operation-status').textContent='Busca concluída nos textos dos períodos selecionados.';
  }
  if(token!==renderId)return;
  resultsVisible(true);
  const invalid=!validPeriod(state.from,state.to);$('filter-error').hidden=!invalid;$('filter-error').textContent='Escolha um intervalo válido entre fevereiro de 2019 e janeiro de 2023.';
  filtered=invalid?[]:filterRows(allRows,state);stats=aggregate(filtered,invalid?'':state.from,invalid?'':state.to,Object.keys(meta.themes));const n=stats.total;
  const active=[state.kind||'Todos os usos',state.party,state.uf,state.author?$('author').selectedOptions[0]?.textContent:'',state.theme?$('theme').selectedOptions[0]?.textContent:'',state.query?`Busca: “${state.query}”`:''].filter(Boolean);
  $('scope').textContent=invalid?'Intervalo principal inválido. Ajuste as datas.':`${monthName(state.from)} → ${monthName(state.to)} · ${active.join(' · ')} · ${fmt(n)} de ${fmt(allRows.length)} registros elegíveis`;
  $('kpi-count').textContent=fmt(n);$('kpi-count-note').textContent=`${pct(n,allRows.length)} dos ${fmt(allRows.length)} registros elegíveis`;$('kpi-authors').textContent=fmt(stats.authors.length);$('kpi-share').textContent=pct(stats.top10,n);$('kpi-share-note').textContent=`${fmt(stats.top10)} registros · ${Math.min(10,stats.authors.length)} oradores no grupo`;$('kpi-full').textContent=pct(stats.fullText,n);$('kpi-full-note').textContent=`${fmt(n-stats.fullText)} sem texto integral no recorte`;
  const peak=[...stats.monthly].sort((a,b)=>b[1]-a[1])[0],ties=peak?stats.monthly.filter(r=>r[1]===peak[1]).length:0;
  $('time-title').textContent=n?`${monthName(peak[0])} ${ties>1?'está entre os meses com mais registros':'concentra o maior volume do recorte'}.`:'Nenhum registro para este recorte.';
  $('time-caption').textContent=n?`${fmt(peak[1])} registros no mês de maior volume (${pct(peak[1],n)} do recorte). ${state.mode==='share'?'Barras divididas pelo total do recorte inteiro.':'Uma ocorrência por código de pronunciamento.'} ${ties>1?`Há ${ties} meses empatados.`:''}`:'Altere os filtros para explorar.';
  $('time-insight').textContent=n?`${stats.monthly.filter(r=>r[1]===0).length} meses sem registros neste recorte. Zero não comprova ausência de atividade. ${fmt(n-stats.fullText)} registros sem texto integral permanecem nas contagens; excluí-los mudaria a história.`:'Não há base para um achado neste recorte.';
  renderTimeline();$('time-table').innerHTML=table(['Mês','Registros','% do recorte'],stats.monthly.map(([m,n])=>[monthName(m),fmt(n),pct(n,stats.total)]));
  $('voices-title').textContent=n?`Os ${Math.min(10,stats.authors.length)} mais frequentes reúnem ${pct(stats.top10,n)} das falas.`:'Nenhum orador neste recorte.';
  $('voices-caption').textContent=`Participação em ${fmt(n)} registros, incluindo oradores fora do top 10 no denominador.`;
  barChart('authors-chart',stats.authors.slice(0,10),n,author=>commit({author}));$('authors-table').innerHTML=table(['Orador','Registros','% do recorte'],stats.authors.map(r=>[r.name,fmt(r.count),pct(r.count,n)]));
  barChart('themes-chart',stats.themes.map(([name,count])=>({id:name,name,count})),n,theme=>commit({theme}));$('themes-note').textContent=`${fmt(n-stats.noTheme)} de ${fmt(n)} registros têm tema detectado (${pct(n-stats.noTheme,n)}). Sem correspondência: ${fmt(stats.noTheme)}. Consulte as palavras acionadoras nos registros e a auditoria da amostra.`;
  comparisonResult=comparison(allRows,state,Object.keys(meta.themes));distribution(stats,allRows,state);evolution(allRows,state,selectMonth);quality(filtered,state);historyContext(state);
  $('export').disabled=!n;$('export-package').disabled=!n||!comparisonResult;
  await renderRecords();
 }catch(e){if(token===renderId){$('operation-status').textContent='Consulta não concluída; os resultados anteriores foram ocultados.';filtered=[];comparisonResult=null;resultsVisible(false);$('records').replaceChildren();for(const id of ['kpi-count','kpi-authors','kpi-share','kpi-full'])$(id).textContent='—';fail(e.message,render);}}
 finally{if(token===renderId)$('dashboard').setAttribute('aria-busy','false');}
}
async function exportData(bundle=false){
 const exportState={...state},rows=[...filtered],comparisonSnapshot=comparisonResult;const button=$(bundle?'export-package':'export');button.disabled=true;$('operation-status').textContent='Preparando exportação completa…';
 try{
  const detailed=await store.hydrate(rows),csv=toCSV(exportState.sort==='oldest'?[...detailed].reverse():detailed);
  if(!bundle){download(new Blob([csv],{type:'text/csv;charset=utf-8'}),`vozes-senado-${exportState.from}-${exportState.to}.csv`);}
  else{
   if(!comparisonSnapshot)throw new Error('Ajuste os períodos A e B antes de exportar o pacote.');
   const [a,b,response]=await Promise.all([store.hydrate(comparisonSnapshot.aRows),store.hydrate(comparisonSnapshot.bRows),fetch('data/manifest.json')]);if(!response.ok)throw new Error('Manifesto não disponível');const manifest=await response.json();
   const details={schemaVersion:2,appVersion:meta.appVersion,exportedAt:new Date().toISOString(),state:exportState,relativeURL:'?'+serializeState(exportState),source:{dataset:meta.dataset,revision:meta.revision,sourceSha256:meta.sourceSha256,catalog:manifest.catalog},rules:{version:meta.rulesVersion,dictionary:meta.themes,matching:'Palavras completas em resumo + indexação, ignorando caixa e acentos; multirrótulo.'},denominators:{main:rows.length,periodA:a.length,periodB:b.length,trend:'Total de cada mês sob filtros, exceto tema global.',voices:'Base sob filtros, exceto autor global.'},limitations:['Não mede produtividade, duração de fala ou influência.','Sem ajuste por dias efetivos de exercício.','Temas exploratórios, sem validação humana prévia.'],fragments:manifest.fragments};
   download(zipStore({'recorte.csv':csv,'periodo-a.csv':toCSV(a),'periodo-b.csv':toCSV(b),'analise.json':JSON.stringify(details,null,2),'LEIA-ME.txt':'CSV UTF-8 com BOM; separador ponto e vírgula. Filtros, regras e hashes em analise.json. Os três CSVs são completos. Períodos podem se sobrepor. Compartilhar a URL requer acesso à mesma hospedagem do dashboard.'}),`analise-vozes-${exportState.from}-${exportState.to}.zip`);
  }
  $('operation-status').textContent='Exportação concluída; confira o download do navegador.';
 }catch(e){fail(`Não foi possível exportar: ${e.message}`,()=>exportData(bundle));$('operation-status').textContent='Exportação interrompida, sem arquivo parcial.';}
 finally{button.disabled=!filtered.length||(bundle&&!comparisonResult);}
}
async function init(){try{
 store=await new DataStore().init();allRows=store.rows;meta=store.catalog.meta;
 const unique=key=>[...new Set(allRows.map(r=>r[key]))].sort((a,b)=>a.localeCompare(b,'pt-BR'));
 for(const [id,label]of [['kind','Todos os usos'],['party','Todos os partidos'],['uf','Todas as UFs']])options(id,unique(id),label);
 const authors=Object.entries(store.catalog.authors).sort((a,b)=>a[1].localeCompare(b[1],'pt-BR'));options('author',authors,'Todos os oradores');options('voice1',authors,null);options('voice2',authors,null);options('theme',[...Object.keys(meta.themes),['__none__','Sem tema detectado']],'Todos os temas');options('trend',Object.keys(meta.themes),null);
 for(const id of ['kind','party','uf','author','theme','voice1','voice2','trend'])choices[id]=[...$(id).options].map(o=>o.value);
 const parsed=parseState(location.search,choices);state=parsed.state;applyControls();writeURL(false);if(parsed.warnings.length){$('url-notice').hidden=false;$('url-notice').textContent=`Parâmetros inválidos ignorados: ${parsed.warnings.join(', ')}.`;}
 $('dictionary').innerHTML=Object.entries(meta.themes).map(([k,v])=>`<div class="dictionary-item"><strong>${esc(k)}</strong><p>${esc(v.join(', '))}</p></div>`).join('');
 const a=meta.audit;$('audit-summary').textContent=`Corpus de ${fmt(a.sourceRows)} códigos únicos; ${fmt(a.excludedRows)} excluídos por tipo de autor ou Casa. ${fmt(a.scopeRows)} elegíveis, ${fmt(a.defaultRows)} da categoria Discurso. Corpus completo: ${fmt(a.sourceMissingFullText)} textos integrais ausentes; recorte elegível: ${fmt(a.scopeMissingFullText)}. Não houve segunda coleta independente.`;
 $('provenance').textContent=`Dashboard ${meta.appVersion} · dataset ${meta.version} · revisão ${meta.revision.slice(0,12)}. Janela solicitada: 01/02/2019–31/01/2023. Datas observadas: ${dayName(a.observedStart)}–${dayName(a.observedEnd)}. Textos carregados sob demanda.`;
 $('filters').addEventListener('submit',e=>e.preventDefault());for(const id of Object.keys(defaults).filter(k=>k!=='query'&&k!=='mode'))$(id)?.addEventListener('change',()=>commit());let timer;$('query').addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>commit(),250);});$('reset').addEventListener('click',()=>{clearTimeout(timer);reset();});
 document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>commit({mode:b.dataset.mode})));
 $('prev').addEventListener('click',()=>{page--;renderRecords();});$('next').addEventListener('click',()=>{page++;renderRecords();});
 $('compare-main').addEventListener('click',()=>commit({aFrom:state.from,aTo:state.to}));$('compare-next-year').addEventListener('click',()=>{const add=s=>`${Number(s.slice(0,4))+1}${s.slice(4)}`;const bFrom=add(state.aFrom),bTo=add(state.aTo);if(!validPeriod(bFrom,bTo)){fail('O ano seguinte fica fora da janela disponível. Escolha outro período A.');return;}commit({bFrom,bTo});});
 $('quality-all-types').addEventListener('click',()=>commit({kind:'',quality:'kind'}));
 $('share').addEventListener('click',async()=>{writeURL(false);try{await navigator.clipboard.writeText(location.href);$('share-status').textContent='Link copiado. Quem abrir verá os mesmos filtros e comparações.';}catch{$('share-status').replaceChildren(document.createTextNode('Copie este endereço: '));const input=document.createElement('input');input.readOnly=true;input.value=location.href;input.setAttribute('aria-label','Link para copiar');$('share-status').append(input);input.select();}});
 window.addEventListener('popstate',()=>{clearTimeout(timer);state=parseState(location.search,choices).state;applyControls();render();});
 $('export').addEventListener('click',()=>exportData());$('export-package').addEventListener('click',()=>exportData(true));setupReview(meta);
 $('dashboard').hidden=false;$('load-status').hidden=true;await render();
 document.querySelectorAll('.table-scroll,.line-chart').forEach(el=>{el.tabIndex=0;el.setAttribute('role','region');el.setAttribute('aria-label',el.closest('section')?.querySelector('h2')?.textContent||'Tabela de dados rolável');});
 }catch(error){$('load-status').hidden=false;$('load-status').className='error';$('load-status').setAttribute('role','alert');$('load-status').textContent=`Não foi possível carregar os dados (${error.message}). Inicie o servidor conforme o README e confira data/catalog.json. Recarregue após corrigir.`;}}
init();
