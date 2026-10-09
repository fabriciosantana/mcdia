import {aggregate,filterRows,comparePeriods,validPeriod,themeEvolution,cumulativeAuthors,qualityBy} from './analytics.mjs';
import {$,fmt,pct,monthName,esc,table,pairBars,lineChart} from './ui.mjs';
const signed=n=>(n>0?'+':'')+fmt(n);
export function comparison(rows,state,names){
 const a={from:state.aFrom,to:state.aTo},b={from:state.bFrom,to:state.bTo};
 if(!validPeriod(a.from,a.to)||!validPeriod(b.from,b.to)){
  $('compare-warning').textContent='Comparação indisponível: ajuste os dois intervalos para a janela fev/2019–jan/2023.';
  for(const id of ['compare-summary','compare-bars','compare-themes','compare-authors'])$(id).replaceChildren();return null;
 }
 const c=comparePeriods(rows,state,a,b,names);
 $('compare-warning').className=c.warnings.length?'notice':'';$('compare-warning').textContent=c.warnings.join(' ')||'Mesma duração e mesmos meses do ano. A equivalência de calendário não controla outras diferenças entre os períodos.';
 $('compare-summary').innerHTML=`<article><span>A · ${esc(monthName(a.from))}–${esc(monthName(a.to))}</span><strong>${fmt(c.A.total)}</strong><p>${c.monthsA} meses · ${fmt(c.A.total/c.monthsA)} registros/mês</p></article><article><span>B · ${esc(monthName(b.from))}–${esc(monthName(b.to))}</span><strong>${fmt(c.B.total)}</strong><p>${c.monthsB} meses · ${fmt(c.B.total/c.monthsB)} registros/mês</p></article><article><span>Mudança de A para B</span><strong>${signed(c.delta)}</strong><p>${c.relative===null?'Variação percentual indefinida: A tem zero registros.':`${signed(c.relative)}% sobre os ${fmt(c.A.total)} registros de A.`}</p></article>`;
 $('compare-bars').innerHTML=pairBars(c.A.total,c.B.total,['Período A','Período B']);
 $('compare-themes').innerHTML=table(['Tema','A: registros / total','A: %','B: registros / total','B: %','Mudança (p.p.)'],names.map(name=>{
  const n=c.A.themes.find(x=>x[0]===name)[1],m=c.B.themes.find(x=>x[0]===name)[1];
  return[name,`${fmt(n)} / ${fmt(c.A.total)}`,pct(n,c.A.total),`${fmt(m)} / ${fmt(c.B.total)}`,pct(m,c.B.total),c.A.total&&c.B.total?signed(100*m/c.B.total-100*n/c.A.total):'—'];
 }));
 const all=new Map();for(const r of c.A.authors)all.set(r.id,{name:r.name,a:r.count,b:0});for(const r of c.B.authors)all.set(r.id,{...(all.get(r.id)||{name:r.name,a:0}),b:r.count});
 $('compare-authors').innerHTML=table(['Orador','A','B','B − A'],[...all.values()].sort((x,y)=>(y.a+y.b)-(x.a+x.b)||x.name.localeCompare(y.name,'pt-BR')).map(r=>[r.name,fmt(r.a),fmt(r.b),signed(r.b-r.a)]));
 return c;
}
export function distribution(stats,allRows,state){
 const cumulative=cumulativeAuthors(stats.authors);const half=cumulative.find(x=>x.share>=50);
 $('concentration-title').textContent=half?`${half.rank} de ${stats.authors.length} oradores alcançam ao menos metade das falas.`:'Sem oradores para calcular a distribuição.';
 const points=[{value:0,label:'0',title:'0 oradores: 0%'},...cumulative.map(r=>({value:r.share,label:String(r.rank),title:`${r.rank} oradores: ${fmt(r.share)}% das falas`} ))];
 lineChart('cumulative-chart',stats.total?points:[],{label:'Participação acumulada nas falas (%)',xLabel:'Número acumulado de oradores · mais frequentes primeiro'});
 $('cumulative-table').innerHTML=table(['Ordem e orador','Registros','Acumulado','% acumulada'],cumulative.map(r=>[`${r.rank}. ${r.name}`,fmt(r.count),fmt(r.cumulative),fmt(r.share)+'%']));
 const pool=validPeriod(state.from,state.to)?filterRows(allRows,{...state,author:''}):[];
 const counts=[state.voice1,state.voice2].map(id=>pool.filter(r=>r.authorId===id).length);
 const labels=['voice1','voice2'].map(id=>$(id).selectedOptions[0]?.textContent||'Orador não selecionado');
 $('voice-comparison').innerHTML=pairBars(...counts,labels)+table(['Orador','Registros','% da base sem filtro de orador'],labels.map((name,i)=>[name,fmt(counts[i]),pct(counts[i],pool.length)]))+`<p class="footnote">Base comum: ${fmt(pool.length)} registros. ${state.voice1===state.voice2?'O mesmo orador está selecionado nos dois lados.':''} A frequência não mede produtividade.</p>`;
}
export function evolution(allRows,state,onMonth){
 const base=validPeriod(state.from,state.to)?filterRows(allRows,{...state,theme:''}):[];
 const series=validPeriod(state.from,state.to)?themeEvolution(base,state.from,state.to,state.trend):[];
 lineChart('trend-chart',series.map(r=>({value:r.share,month:r.month,label:r.month,title:`${monthName(r.month)}: ${r.count} de ${r.total}, ${r.share===null?'sem base':fmt(r.share)+'%'}. Explorar.`})),{label:'Registros com menção ao tema / total do mês (%)',onPoint:p=>onMonth(p.month,state.trend)});
 const peak=series.filter(r=>r.share!==null).sort((a,b)=>b.share-a.share)[0];
 const missing=series.filter(r=>r.total===0).length;
 $('trend-insight').textContent=peak?`${state.trend}: maior proporção em ${monthName(peak.month)}, ${pct(peak.count,peak.total)} (${fmt(peak.count)} de ${fmt(peak.total)} registros do mês). ${series.filter(r=>r.share===peak.share).length>1?'Há empate no máximo. ':''}${missing} meses sem base. Valores com poucos registros podem oscilar muito; o dicionário não identifica posição política.`:'Não há registros para calcular a evolução temática.';
 $('trend-table').innerHTML=table(['Mês','Registros com tema','Total do mês','% do mês'],series.map(r=>[monthName(r.month),fmt(r.count),fmt(r.total),pct(r.count,r.total)]));
}
export function quality(rows,state){
 const groups=qualityBy(rows,state.quality,validPeriod(state.from,state.to)?state.from:'',validPeriod(state.from,state.to)?state.to:'');
 const sums=['missingFull','missingSummary','missingIndex'].map(key=>groups.reduce((s,r)=>s+r[key],0));
 $('quality-chart').innerHTML=['Sem texto integral','Sem resumo','Sem indexação'].map((label,i)=>`<article class="quality-card"><p>${label}</p><strong>${fmt(sums[i])} · ${pct(sums[i],rows.length)}</strong><p>de ${fmt(rows.length)} registros</p></article>`).join('');
 const worst=groups.filter(g=>g.total).sort((a,b)=>b.missingFull/b.total-a.missingFull/a.total||b.total-a.total)[0];
 $('quality-insight').textContent=worst?`${state.quality==='month'?monthName(worst.key):worst.key} está entre os grupos com maior parcela de textos ausentes: ${fmt(worst.missingFull)} de ${fmt(worst.total)} (${pct(worst.missingFull,worst.total)}). Grupos pequenos exigem cuidado. ${state.kind?'Há um filtro de tipo ativo; use o botão abaixo para comparar categorias.':''}`:'Sem registros para auditar neste recorte.';
 $('quality-table').innerHTML=table([state.quality==='month'?'Mês':'Tipo','Total','Sem integral (n / %)','Sem resumo (n / %)','Sem indexação (n / %)'],groups.map(r=>[state.quality==='month'?monthName(r.key):r.key,fmt(r.total),...['missingFull','missingSummary','missingIndex'].map(k=>`${fmt(r[k])} / ${pct(r[k],r.total)}`)]));
}
export function historyContext(state){
 $('historical-context').innerHTML=validPeriod(state.from,state.to)&&state.from<='2020-03'&&state.to>='2020-03'?`<p><strong>Contexto histórico · 20/03/2020.</strong> O Senado realizou sua primeira votação remota. O evento está no período visualizado; este gráfico não estima seu efeito sobre o volume de falas. <a href="https://www12.senado.leg.br/noticias/materias/2020/03/20/secretario-geral-da-mesa-destaca-ineditismo-da-primeira-sessao-remota-do-senado" target="_blank" rel="noopener noreferrer">Fonte: Senado Notícias ↗</a></p>`:'';
}
