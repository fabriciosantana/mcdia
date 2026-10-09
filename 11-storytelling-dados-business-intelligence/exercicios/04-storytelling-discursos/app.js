import {normalize,filterRows,aggregate,sourceUrl,toCSV} from './analytics.mjs';
const $ = id => document.getElementById(id);
const fmt = n => new Intl.NumberFormat('pt-BR').format(n);
const pct = (n,d) => d ? (100*n/d).toLocaleString('pt-BR',{maximumFractionDigits:1})+'%' : '—';
const monthName = m => new Date(m+'-01T12:00:00Z').toLocaleDateString('pt-BR',{month:'short',year:'numeric',timeZone:'UTC'});
const dayName = d => d.split('-').reverse().join('/');
const esc = value => String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const defaultFilters = {from:'2019-02',to:'2023-01',kind:'Discurso',party:'',uf:'',author:'',theme:'',query:''};
let allRows=[],meta,filtered=[],stats,mode='count',page=0;
const pageSize=8;
function options(id, values, allLabel) {
  $(id).replaceChildren(new Option(allLabel,''),...values.map(v=>Array.isArray(v)?new Option(v[1],v[0]):new Option(v,v)));
}
function readFilters(){return Object.fromEntries(Object.keys(defaultFilters).map(k=>[k,$(k).value]));}
function setFilter(id,value){$(id).value=value;render();}
function reset(){for(const[k,v]of Object.entries(defaultFilters))$(k).value=v;mode='count';$('sort').value='newest';document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===mode)));render();}
function table(headers,rows){return `<table><thead><tr>${headers.map(x=>`<th scope="col">${esc(x)}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map((v,i)=>`<td${i?' class="num"':''}>${esc(v)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;}
function barChart(target,items,total,onSelect,unit='registros') {
  const container=$(target);container.replaceChildren();
  const max=Math.max(0,...items.map(r=>r.count));
  if(!max){container.innerHTML='<p class="empty">Nenhuma ocorrência neste recorte.</p>';return;}
  const axis=document.createElement('div');axis.className='bar-axis';axis.innerHTML=`<span>0</span><span>${fmt(max)} ${esc(unit)} · escala deste gráfico</span>`;container.append(axis);
  for(const item of items){
    const button=document.createElement('button');button.type='button';button.className='bar-row';
    button.setAttribute('aria-label',`${item.name}: ${fmt(item.count)} registros, ${pct(item.count,total)} do recorte. Filtrar.`);
    button.innerHTML=`<span class="bar-label"><span>${esc(item.name)}</span><b>${fmt(item.count)} <span style="color:var(--muted)">· ${pct(item.count,total)}</span></b></span><span class="bar-track"><span class="bar-fill" style="width:${100*item.count/max}%"></span></span>`;
    button.addEventListener('click',()=>onSelect(item.id));container.append(button);
  }
}
function renderTimeline(){
  const {monthly,total}=stats;
  if(!total){$('timeline').innerHTML='<p class="empty">Sem registros para desenhar a série. Ajuste os filtros acima.</p>';return;}
  const values=monthly.map(([m,n])=>[m,mode==='share'?100*n/total:n,n]);
  const max=Math.max(...values.map(r=>r[1]));
  const step=max<=5?1:10**Math.floor(Math.log10(max/4));
  const ceiling=Math.ceil(max/step)*step;
  const width=1040,height=292,left=52,right=18,top=36,bottom=43;
  const w=width-left-right,h=height-top-bottom,band=w/values.length;
  const peak=Math.max(...monthly.map(r=>r[1]));
  const y=v=>top+h-h*v/ceiling;
  let svg=`<svg viewBox="0 0 ${width} ${height}" role="group" aria-label="Pronunciamentos por mês; escala de zero a ${fmt(ceiling)} ${mode==='share'?'por cento do recorte':'registros'}"><text x="${left}" y="15" font-size="11">${mode==='share'?'% de todos os registros do recorte':'Registros por mês'} · eixo a partir de zero</text>`;
  for(let i=0;i<=4;i++){let v=ceiling*i/4;svg+=`<line x1="${left}" x2="${width-right}" y1="${y(v)}" y2="${y(v)}" stroke="#e5eae6"/><text x="${left-9}" y="${y(v)+4}" text-anchor="end" font-size="10">${v.toLocaleString('pt-BR',{maximumFractionDigits:1})}${mode==='share'?'%':''}</text>`;}
  values.forEach(([m,v,n],i)=>{
    const x=left+i*band+band*.12,bw=band*.76;
    svg+=`<rect class="month-bar${n===peak?' peak':''}" x="${x}" y="${y(v)}" width="${bw}" height="${Math.max(0,top+h-y(v))}" tabindex="0" role="button" data-month="${m}" aria-label="${esc(monthName(m))}: ${fmt(n)} registros, ${pct(n,total)} do recorte. Filtrar mês."><title>${esc(monthName(m))}: ${fmt(n)} registros · ${pct(n,total)}</title></rect>`;
    if(values.length<=12 || m.endsWith('-01') || i===0){svg+=`<text x="${x+bw/2}" y="${height-16}" text-anchor="middle" font-size="10">${values.length<=12?esc(monthName(m)):m.slice(0,4)}</text>`;}
  });
  svg+='</svg>';$('timeline').innerHTML=svg;
  $('timeline').querySelectorAll('[data-month]').forEach(el=>{
    const select=()=>{$('from').value=el.dataset.month;$('to').value=el.dataset.month;render();$('from').focus();};
    el.addEventListener('click',select);el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select();}});
  });
}
function renderRecords(){
  const ordered=$('sort').value==='oldest'?[...filtered].reverse():filtered;
  const totalPages=Math.max(1,Math.ceil(ordered.length/pageSize));page=Math.min(page,totalPages-1);
  const start=page*pageSize,visible=ordered.slice(start,start+pageSize);
  $('results-count').textContent=ordered.length?`${fmt(start+1)}–${fmt(start+visible.length)} de ${fmt(ordered.length)} registros neste recorte`:'Nenhum registro encontrado.';
  $('records').innerHTML=visible.length?visible.map(r=>`<article class="record"><div><time class="record-date" datetime="${esc(r.date)}">${dayName(r.date)}</time><span class="record-kind">${esc(r.kind)}</span></div><div><h3>${esc(r.author)}<small>${esc(r.party)} · ${esc(r.uf)}</small></h3><p>${esc(r.summary||'Resumo não disponível neste registro.')}</p><a href="${sourceUrl(r.id)}" target="_blank" rel="noopener noreferrer">Consultar registro no Senado ↗ <span class="footnote">#${esc(r.id)}</span></a><div class="tags">${r.themes.map(t=>`<span class="tag">${esc(t)}</span>`).join('')}${!r.fullText?'<span class="tag warning">Texto integral ausente no dataset</span>':''}</div></div></article>`).join(''):'<div class="empty"><strong>Não há registros com esta combinação.</strong><br>Remova um filtro, amplie o período ou use “Restaurar visão inicial”.</div>';
  $('page-info').textContent=`Página ${ordered.length?page+1:0} de ${ordered.length?totalPages:0}`;
  $('prev').disabled=page===0;$('next').disabled=page>=totalPages-1;$('export').disabled=!ordered.length;
}
function render(){
  page=0;const f=readFilters();
  const invalid=!f.from||!f.to||f.from>f.to||f.from<'2019-02'||f.to>'2023-01';
  $('filter-error').hidden=!invalid;$('filter-error').textContent='Escolha um intervalo válido entre fevereiro de 2019 e janeiro de 2023, com início anterior ou igual ao fim.';
  filtered=invalid?[]:filterRows(allRows,f);
  stats=aggregate(filtered,invalid?'':f.from,invalid?'':f.to,Object.keys(meta.themes));
  const n=stats.total;
  const active=[f.kind||'Todos os usos da palavra',f.party,f.uf,f.author?$('author').selectedOptions[0].textContent:'',f.theme?$('theme').selectedOptions[0].textContent:'',f.query?`Busca: “${f.query}”`:''].filter(Boolean);
  $('scope').textContent=invalid?'Intervalo inválido: ajuste as datas para explorar.':`${monthName(f.from)} → ${monthName(f.to)} · ${active.join(' · ')} · ${fmt(n)} de ${fmt(allRows.length)} registros elegíveis`;
  $('kpi-count').textContent=fmt(n);$('kpi-count-note').textContent=`${pct(n,allRows.length)} dos ${fmt(allRows.length)} registros elegíveis`;
  $('kpi-authors').textContent=fmt(stats.authors.length);$('kpi-share').textContent=pct(stats.top10,n);
  $('kpi-share-note').textContent=`${fmt(stats.top10)} registros · ${Math.min(10,stats.authors.length)} oradores no grupo`;
  $('kpi-full').textContent=pct(stats.fullText,n);$('kpi-full-note').textContent=`${fmt(n-stats.fullText)} sem texto integral no recorte`;
  const peak=[...stats.monthly].sort((a,b)=>b[1]-a[1])[0];
  const ties=peak?stats.monthly.filter(r=>r[1]===peak[1]).length:0;
  $('time-title').textContent=n?`${monthName(peak[0])} ${ties>1?'está entre os meses com mais registros':'concentra o maior volume do recorte'}.`:'Nenhum registro para este recorte.';
  $('time-caption').textContent=n?`${fmt(peak[1])} registros no mês ${ties>1?`(empate entre ${ties} meses)`:'de maior volume'}: ${pct(peak[1],n)} dos ${fmt(n)} selecionados. ${mode==='share'?'Cada barra divide o total do mês pelo total de registros filtrados.':'Uma ocorrência por código de pronunciamento.'} Meses sem registros aparecem com zero; isso não comprova ausência de atividade.`:'Altere os filtros para voltar a explorar a distribuição mensal.';
  renderTimeline();
  $('time-table').innerHTML=table(['Mês','Registros','% do recorte'],stats.monthly.map(([m,n])=>[monthName(m),fmt(n),pct(n,stats.total)]));
  $('voices-title').textContent=n?`Os ${Math.min(10,stats.authors.length)} mais frequentes reúnem ${pct(stats.top10,n)} das falas.`:'Nenhum orador neste recorte.';
  $('voices-caption').textContent=`Participação em ${fmt(n)} registros filtrados. As porcentagens usam o total do recorte, incluindo os oradores fora do top 10.`;
  barChart('authors-chart',stats.authors.slice(0,10),n,id=>setFilter('author',id));
  $('authors-table').innerHTML=table(['Orador(a)','Registros','% do recorte'],stats.authors.map(r=>[r.name,fmt(r.count),pct(r.count,n)]));
  barChart('themes-chart',stats.themes.map(([name,count])=>({id:name,name,count})),n,id=>setFilter('theme',id));
  $('themes-note').textContent=`${fmt(n-stats.noTheme)} de ${fmt(n)} registros têm pelo menos um tema detectado (${pct(n-stats.noTheme,n)}). Sem correspondência: ${fmt(stats.noTheme)}. O dicionário não cobre todos os assuntos.`;
  renderRecords();
}
async function init(){
  try{
    const response=await fetch('./data/dashboard.json');if(!response.ok)throw new Error(`HTTP ${response.status}`);
    const data=await response.json();if(!Array.isArray(data.rows)||!data.meta?.audit)throw new Error('Formato de dados inválido');
    allRows=data.rows;meta=data.meta;
    for(const r of allRows)r.searchText=normalize(r.summary+' '+r.index);
    const unique=key=>[...new Set(allRows.map(r=>r[key]))].sort((a,b)=>a.localeCompare(b,'pt-BR'));
    options('kind',unique('kind'),'Todos os usos');options('party',unique('party'),'Todos os partidos');options('uf',unique('uf'),'Todas as UFs');
    const authors=[...new Map(allRows.map(r=>[r.authorId,r.author])).entries()].sort((a,b)=>a[1].localeCompare(b[1],'pt-BR'));
    options('author',authors,'Todos os oradores');options('theme',[...Object.keys(meta.themes),['__none__','Sem tema detectado']],'Todos os temas');
    $('dictionary').innerHTML=Object.entries(meta.themes).map(([k,v])=>`<div class="dictionary-item"><strong>${esc(k)}</strong><p>${esc(v.join(', '))}</p></div>`).join('');
    const a=meta.audit;
    $('audit-summary').textContent=`O corpus tem ${fmt(a.sourceRows)} registros únicos. Excluímos ${fmt(a.excludedRows)} de outros tipos de autor ou da Casa Congresso Nacional. Restam ${fmt(a.scopeRows)} pronunciamentos elegíveis; ${fmt(a.defaultRows)} são da categoria “Discurso”, exibida inicialmente. No corpus completo, ${fmt(a.sourceMissingFullText)} registros estão sem texto integral. No recorte elegível, são ${fmt(a.scopeMissingFullText)}. A completude da atividade parlamentar não foi verificada contra outra coleta.`;
    $('provenance').textContent=`Snapshot ${meta.version} · revisão ${meta.revision.slice(0,12)} · preparado em ${new Date(meta.builtAt).toLocaleDateString('pt-BR',{timeZone:'UTC'})}. Janela solicitada: 01/02/2019–31/01/2023. Datas observadas no corpus: ${dayName(a.observedStart)}–${dayName(a.observedEnd)}.`;
    $('filters').addEventListener('submit',e=>e.preventDefault());
    for(const id of Object.keys(defaultFilters).filter(k=>k!=='query'))$(id).addEventListener('change',render);
    let timer;$('query').addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(render,180);});
    $('reset').addEventListener('click',()=>{clearTimeout(timer);reset();});
    document.querySelectorAll('[data-mode]').forEach(button=>button.addEventListener('click',()=>{mode=button.dataset.mode;document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));render();}));
    $('sort').addEventListener('change',()=>{page=0;renderRecords();});
    $('prev').addEventListener('click',()=>{page--;renderRecords();});$('next').addEventListener('click',()=>{page++;renderRecords();});
    $('export').addEventListener('click',()=>{const blob=new Blob([toCSV(filtered)],{type:'text/csv;charset=utf-8'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=`vozes-senado-${$('from').value}-${$('to').value}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
    reset();$('dashboard').hidden=false;$('load-status').hidden=true;
  }catch(error){$('load-status').className='error';$('load-status').setAttribute('role','alert');$('load-status').textContent=`Não foi possível carregar os dados locais (${error.message}). Inicie o servidor conforme o README, abra http://localhost:8000 e confira se data/dashboard.json está presente. Recarregue a página após corrigir.`;}
}
init();
