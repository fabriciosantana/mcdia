export const $=id=>document.getElementById(id);
export const fmt=n=>new Intl.NumberFormat('pt-BR',{maximumFractionDigits:1}).format(n);
export const pct=(n,d)=>d?fmt(100*n/d)+'%':'—';
export const monthName=m=>new Date(m+'-01T12:00:00Z').toLocaleDateString('pt-BR',{month:'short',year:'numeric',timeZone:'UTC'});
export const dayName=d=>d.split('-').reverse().join('/');
export const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function options(id,values,allLabel){$(id).replaceChildren(...(allLabel!==null?[new Option(allLabel,'')]:[]),...values.map(v=>Array.isArray(v)?new Option(v[1],v[0]):new Option(v,v)));}
export function table(headers,rows){return `<table><thead><tr>${headers.map(x=>`<th scope="col">${esc(x)}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map((v,i)=>i?`<td>${esc(v)}</td>`:`<th scope="row">${esc(v)}</th>`).join('')}</tr>`).join('')}</tbody></table>`;}
export function evidenceHTML(evidence){return evidence.length?`<ul class="evidence">${evidence.map(e=>`<li><strong>${esc(e.theme)}</strong>: ${e.matches.map(m=>`${esc(m.term)} <small>(${m.fields.map(f=>f==='summary'?'resumo':'indexação').join(' e ')})</small>`).join('; ')}</li>`).join('')}</ul>`:'<p>Nenhuma palavra do dicionário foi encontrada nestes campos.</p>';}
export function barChart(target,items,total,onSelect){
 const container=$(target);container.replaceChildren();const max=Math.max(0,...items.map(r=>r.count));
 if(!max){container.innerHTML='<p class="empty">Nenhuma ocorrência neste recorte.</p>';return;}
 const axis=document.createElement('div');axis.className='bar-axis';axis.innerHTML=`<span>0</span><span>${fmt(max)} registros · escala deste gráfico</span>`;container.append(axis);
 for(const item of items){const b=document.createElement('button');b.type='button';b.className='bar-row';b.setAttribute('aria-label',`${item.name}: ${fmt(item.count)} registros, ${pct(item.count,total)} do recorte. Filtrar.`);b.innerHTML=`<span class="bar-label"><span>${esc(item.name)}</span><b>${fmt(item.count)} · ${pct(item.count,total)}</b></span><span class="bar-track"><span class="bar-fill" style="width:${100*item.count/max}%"></span></span>`;b.addEventListener('click',()=>onSelect(item.id));container.append(b);}
}
export function pairBars(a,b,labels){const max=Math.max(a,b,1);return `<div class="paired-row">${[a,b].map((n,i)=>`<div class="pair-bar"><span>${esc(labels[i])}</span><span class="pair-track"><i style="width:${100*n/max}%"></i></span><b>${fmt(n)}</b></div>`).join('')}<p class="footnote">Escala comum: 0–${fmt(max)} registros.</p></div>`;}
export function lineChart(target,points,{label,max=100,xLabel='Mês',onPoint}={}){
 if(!points.length||points.every(p=>p.value===null)){ $(target).innerHTML='<p class="empty">Sem registros para desenhar esta série.</p>';return;}
 const w=850,h=290,l=65,r=30,t=35,b=50,ih=h-t-b,iw=w-l-r;
 const x=i=>l+(points.length===1?iw/2:i*iw/(points.length-1)),y=v=>t+ih*(1-v/max);
 let svg=`<svg viewBox="0 0 ${w} ${h}" role="${onPoint?'group':'img'}" aria-label="${esc(label)}"><title>${esc(label)}</title>`;
 for(const v of [0,max*.25,max*.5,max*.75,max])svg+=`<line x1="${l}" y1="${y(v)}" x2="${w-r}" y2="${y(v)}" stroke="#dce3df"/><text x="${l-9}" y="${y(v)+4}" text-anchor="end">${fmt(v)}%</text>`;
 let path='',connected=false;
 points.forEach((p,i)=>{if(p.value===null){connected=false;return;}path+=`${connected?'L':'M'}${x(i)},${y(p.value)} `;connected=true;});
 svg+=`<path d="${path}" fill="none" stroke="#17695f" stroke-width="2.5"/>`;
 points.forEach((p,i)=>{
  if(p.value!==null)svg+=`<circle cx="${x(i)}" cy="${y(p.value)}" r="${onPoint?5:3}" fill="#17695f" ${onPoint?`tabindex="0" role="button" data-point="${i}"`:''} aria-label="${esc(p.title)}"><title>${esc(p.title)}</title></circle>`;
  if(i===0||i===points.length-1||i%Math.max(1,Math.ceil(points.length/5))===0)svg+=`<text x="${x(i)}" y="${h-b+23}" text-anchor="middle">${esc(p.label)}</text>`;
 });
 svg+=`<text x="${l}" y="18">${esc(label)}</text><text x="${w/2}" y="${h-4}" text-anchor="middle">${esc(xLabel)}</text></svg>`;
 $(target).innerHTML=svg;
 if(onPoint)$(target).querySelectorAll('[data-point]').forEach(el=>{const action=()=>onPoint(points[+el.dataset.point]);el.addEventListener('click',action);el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();action();}});});
}
