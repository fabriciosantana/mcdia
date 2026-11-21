import {$} from './ui.mjs';

export function setupPresentation(){
 const slides=['abertura','vozes','concentracao','ritmo','exemplo','conclusao'].map($);
 const labels=['Pergunta e recorte','Distribuição das falas','Participação acumulada','Ritmo mensal','Um registro concreto','Conclusão'];
 let active=false,index=0;
 const charts=['authors-chart','timeline','timeline-mobile'].map($);
 const chartHelp=document.querySelector('#vozes .footnote'),originalHelp=chartHelp.textContent;
 const launch=document.createElement('button');launch.id='present';launch.type='button';launch.textContent='Apresentar em 6 telas';
 launch.setAttribute('aria-pressed','false');document.querySelector('.hero .primary-link').after(launch);
 const controls=document.createElement('nav');controls.className='presentation-controls';controls.hidden=true;controls.setAttribute('aria-label','Controle da apresentação');
 controls.innerHTML='<button id="slide-prev" type="button">← Anterior</button><span id="slide-position" role="status"></span><button id="slide-next" type="button">Próxima →</button><button id="slide-exit" type="button">Sair · Esc</button>';
 document.body.append(controls);
 for(const slide of slides){slide.classList.add('presentation-slide');slide.tabIndex=-1;}
 function show(next){
  index=Math.max(0,Math.min(slides.length-1,next));
  slides.forEach((slide,i)=>slide.classList.toggle('active-slide',i===index));
  $('slide-position').textContent=`${index+1} / ${slides.length} · ${labels[index]}`;
  $('slide-prev').disabled=index===0;$('slide-next').disabled=index===slides.length-1;
  slides[index].focus({preventScroll:true});window.scrollTo(0,0);
 }
 function exit(){active=false;document.body.classList.remove('presenting');charts.forEach(el=>el.inert=false);chartHelp.textContent=originalHelp;controls.hidden=true;launch.setAttribute('aria-pressed','false');launch.focus();}
 launch.addEventListener('click',()=>{
  if($('dashboard').getAttribute('aria-busy')==='true')return;
  active=true;document.body.classList.add('presenting');charts.forEach(el=>el.inert=true);controls.hidden=false;launch.setAttribute('aria-pressed','true');show(0);
  chartHelp.textContent='As barras partem de zero e exibem os 10 maiores totais. A frequência não mede desempenho; não há ajuste por dias de exercício.';
 });
 $('slide-prev').addEventListener('click',()=>show(index-1));$('slide-next').addEventListener('click',()=>show(index+1));$('slide-exit').addEventListener('click',exit);
 document.addEventListener('keydown',event=>{
  if(!active)return;
  if(event.key==='Escape'){event.preventDefault();exit();}
  if(event.target.closest('input,select,textarea,button,a,[role="button"],summary'))return;
  if(event.key==='ArrowRight'){event.preventDefault();show(index+1);}
  if(event.key==='ArrowLeft'){event.preventDefault();show(index-1);}
 });
 document.addEventListener('click',event=>{if(active&&event.target.closest('a[href^="#"]'))exit();});
}
