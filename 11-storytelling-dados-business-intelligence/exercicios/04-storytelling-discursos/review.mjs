import {reviewMetrics,validateReview,themeEvidence,sourceUrl} from './analytics.mjs';
import {$,esc,fmt,evidenceHTML} from './ui.mjs';
import {download} from './export.mjs';
export function setupReview(meta){
 let sample,assisted,index=0,annotations={},loaded=false;const key=`vozes-review:${meta.revision}:${meta.rulesVersion}`;
 const status=text=>{$('review-status').textContent=text;};
 function payload(){return {schemaVersion:1,datasetRevision:meta.revision,rulesVersion:meta.rulesVersion,reviewerType:'human',reviewer:$('reviewer').value.trim(),exportedAt:new Date().toISOString(),annotations};}
 function persist(){try{localStorage.setItem(key,JSON.stringify(payload()));status('Revisão salva somente neste navegador. Exporte para manter uma cópia.');}catch{status('Armazenamento local indisponível. Exporte a revisão antes de fechar.');}}
 function metrics(){const m=reviewMetrics(sample.items,annotations);$('review-metrics').textContent=`Revisão humana informada: ${m.resolved} pares decididos, ${m.uncertain} em dúvida, ${m.pending} pendentes. VP ${m.tp} · FP ${m.fp} · VN ${m.tn} · FN ${m.fn}. Precisão na amostra: ${m.precision===null?'—':fmt(100*m.precision)+'%'}; recall na amostra: ${m.recall===null?'—':fmt(100*m.recall)+'%'}. Amostra balanceada por previsão, sem pesos: não generalizar ao corpus.`;}
 function draw(){const item=sample.items[index],a=annotations[item.key];
  $('review-position').textContent=`Item ${index+1} de ${sample.items.length}`;$('review-prev').disabled=index===0;$('review-next').disabled=index===sample.items.length-1;
  $('review-item').innerHTML=`<article class="review-card"><h3>${esc(item.theme)} · registro #${esc(item.id)}</h3><p>${esc(item.author)} · ${esc(item.date)}</p><p><strong>Resumo:</strong> ${esc(item.summary)}</p><details open><summary>Indexação original</summary><p>${esc(item.index||'Não disponível')}</p></details><a href="${sourceUrl(item.id)}" target="_blank" rel="noopener noreferrer">Consultar no Senado ↗</a><fieldset class="review-labels"><legend>O tema é substantivamente abordado?</legend>${[['yes','Sim'],['no','Não'],['uncertain','Em dúvida']].map(([v,label])=>`<label><input type="radio" name="review-label" value="${v}" ${a?.label===v?'checked':''}>${label}</label>`).join('')}</fieldset><label>Justificativa<textarea id="review-note" maxlength="4000">${esc(a?.note||'')}</textarea></label><details><summary>Revelar previsão e palavras acionadoras</summary><p>Detecção do dicionário: ${item.predicted?'sim':'não'} para ${esc(item.theme)}.</p>${evidenceHTML(themeEvidence(item,meta.themes).filter(e=>e.theme===item.theme))}</details></article>`;
  const save=()=>{if(!$('reviewer').value.trim()){status('Informe a identificação do revisor antes de salvar uma avaliação.');$('reviewer').focus();draw();return;}
   const label=document.querySelector('[name="review-label"]:checked')?.value;if(!label)return;annotations[item.key]={label,note:$('review-note').value,reviewer:$('reviewer').value.trim()};persist();metrics();};
  document.querySelectorAll('[name="review-label"]').forEach(el=>el.addEventListener('change',save));$('review-note').addEventListener('input',save);metrics();
 }
 $('open-review').addEventListener('click',async()=>{
  $('open-review').disabled=true;
  try{
   if(!loaded){const responses=await Promise.all(['review-sample','assisted-review'].map(async name=>{const r=await fetch(`data/${name}.json`);if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json();}));[sample,assisted]=responses;
    if(sample.datasetRevision!==meta.revision||sample.rulesVersion!==meta.rulesVersion||assisted.datasetRevision!==meta.revision||assisted.rulesVersion!==meta.rulesVersion)throw new Error('Amostra ou leitura assistida incompatível com o dataset.');
    try{const raw=localStorage.getItem(key);if(raw){const valid=validateReview(JSON.parse(raw),sample.items,meta.revision,meta.rulesVersion);annotations=valid.annotations;$('reviewer').value=valid.reviewer;}}catch{status('Revisão local incompatível não foi carregada. Você pode importar uma cópia válida.');}
    const ai=Object.fromEntries(assisted.items.map(i=>[i.key,i])),m=reviewMetrics(sample.items,ai);
    $('assisted-summary').textContent=`Leitura assistida por IA: ${m.resolved} pares lidos; ${m.fp+m.fn} divergências em relação ao dicionário (${m.fp} possíveis falsos positivos e ${m.fn} possíveis falsos negativos). Não é validação humana ou independente. As regras não foram ajustadas a esta amostra.`;
    $('assisted-findings').innerHTML=`<p>${esc(assisted.limitations)}</p>`+sample.items.filter(i=>ai[i.key]?.label!==(i.predicted?'yes':'no')).map(i=>`<p><a href="${sourceUrl(i.id)}" target="_blank" rel="noopener noreferrer">#${esc(i.id)} · ${esc(i.theme)}</a>: ${esc(ai[i.key].note)}</p>`).join('')+'<p><a href="data/assisted-review.json">Baixar todas as justificativas assistidas</a></p>';
    loaded=true;
   }
   $('review-panel').hidden=false;$('review-export').disabled=false;$('review-import').disabled=false;draw();$('open-review').textContent='Amostra aberta · revisão disponível abaixo';
  }catch(e){$('review-panel').hidden=false;for(const id of ['review-prev','review-next','review-export','review-import'])$(id).disabled=true;status(`Falha ao abrir amostra: ${e.message}. Tente novamente.`);}finally{$('open-review').disabled=false;}
 });
 $('review-prev').addEventListener('click',()=>{if(index>0){index--;draw();}});$('review-next').addEventListener('click',()=>{if(index<sample.items.length-1){index++;draw();}});
 $('reviewer').addEventListener('change',()=>{if(loaded&&$('reviewer').value.trim())persist();});
 $('review-export').addEventListener('click',()=>{try{const value=validateReview(payload(),sample.items,meta.revision,meta.rulesVersion);download(new Blob([JSON.stringify(value,null,2)],{type:'application/json'}),'revisao-humana-vozes.json');status('Arquivo de revisão humana exportado.');}catch(e){status(e.message);}});
 $('review-import').addEventListener('change',async e=>{try{const file=e.target.files[0];if(!file)return;if(file.size>2_000_000)throw new Error('Arquivo maior que 2 MB.');const value=validateReview(JSON.parse(await file.text()),sample.items,meta.revision,meta.rulesVersion);annotations=value.annotations;$('reviewer').value=value.reviewer;persist();draw();status('Revisão importada e substituída neste navegador.');}catch(err){status(`Importação recusada: ${err.message}`);}finally{e.target.value='';}});
}
