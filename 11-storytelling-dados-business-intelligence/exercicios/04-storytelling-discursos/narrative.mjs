import {$,fmt,pct} from './ui.mjs';
import {setupPresentation} from './presentation.mjs';

export function narrativeHeadline(stats){
 if(!stats.total)return 'Não há registros neste recorte.';
 if(stats.authors.length<=10)return `${fmt(stats.authors.length)} ${stats.authors.length===1?'orador':'oradores'} no recorte; o grupo dos dez inclui todos eles.`;
 if(new Set(stats.authors.map(a=>a.count)).size===1)return 'Todos os oradores deste recorte têm a mesma contagem.';
 return `Dez de ${fmt(stats.authors.length)} oradores reúnem ${pct(stats.top10,stats.total)} dos ${fmt(stats.total)} registros.`;
}

export function narrativeSummary(stats){
 if(!stats.total)return 'Não há registros neste recorte. Ajuste os filtros antes de formular uma conclusão.';
 const group=Math.min(10,stats.authors.length);
 return `Neste recorte, ${group} de ${fmt(stats.authors.length)} oradores reúnem ${fmt(stats.top10)} dos ${fmt(stats.total)} registros (${pct(stats.top10,stats.total)}). `+
  (stats.authors.length<=10?'Como há no máximo dez oradores selecionados, a parcela do grupo é 100% por construção; não descreve a concentração no conjunto da legislatura. ':new Set(stats.authors.map(a=>a.count)).size>1?'A frequência registrada é distribuída de forma desigual; ela não mede duração, influência ou produtividade. ':'Os oradores deste recorte têm a mesma contagem; isso não significa igual duração, influência ou produtividade. ')+
  `${fmt(stats.total-stats.fullText)} registros não têm texto integral no snapshot, mas permanecem na contagem. A resposta vale somente para os filtros e datas acima.`;
}

export function setupNarrative(){
 const guide=document.createElement('details');guide.className='presentation-guide';guide.id='apresentacao';
 guide.innerHTML='<summary>Percurso de apresentação · exatamente 10 minutos</summary><p>Restaure a visão inicial antes de começar. Use um cronômetro externo e encerre em 10:00; o roteiro não substitui o ensaio.</p><ol><li>0:00–1:00 · Pergunta e relevância: quem ocupa a palavra registrada?</li><li>1:00–2:00 · <a href="#metodo">Fonte, unidade de contagem e recorte</a>.</li><li>2:00–3:30 · <a href="#ritmo">O ritmo e o pico mensal</a>.</li><li>3:30–5:30 · <a href="#vozes">Quem concentra as falas</a>; <a href="#concentracao">curva acumulada</a>.</li><li>5:30–7:00 · <a href="#vozes">Temas como pistas</a>, sem confundir menção com posição.</li><li>7:00–8:30 · <a href="#qualidade">Lacunas</a> e <a href="#evidencias">um registro verificável</a>.</li><li>8:30–10:00 · <a href="#conclusao">Resposta, limites e encerramento</a>.</li></ol><p>Comparações A/B, evolução temática e auditoria são exploração complementar; não tente apresentar todas as ferramentas.</p><a href="ROTEIRO-APRESENTACAO.md">Baixar roteiro de fala e checklist</a>';
 $('explorar').before(guide);
 const conclusion=document.createElement('section');conclusion.id='conclusao';conclusion.className='chapter conclusion';
 conclusion.innerHTML='<p class="eyebrow">05 / O QUE LEVAMOS DESTA HISTÓRIA</p><h2>A palavra registrada não é uma medida de desempenho.</h2><p id="conclusion-answer" class="insight" aria-live="polite"></p><p><strong>Por que importa?</strong> A distribuição das falas torna visível uma dimensão da participação parlamentar e ajuda a formular perguntas sobre representação. Não basta, sozinha, para avaliar a atuação de um senador.</p><p><strong>Próximo passo:</strong> ler os registros originais e investigar oportunidades de fala e dias efetivos de exercício antes de comparar desempenho. Temas são pistas de um dicionário, não posições políticas validadas.</p><a href="#metodo">Conferir fontes e limites →</a>';
 $('ritmo').after(conclusion);
 const colors=document.createElement('p');colors.className='reading-note';colors.id='color-key';
 colors.textContent='Como ler as cores: verde escuro destaca o pico ou a primeira série; verde suave mantém o contexto. Terracota destaca o primeiro tema e a segunda série nas comparações A/B. Cores não representam partidos, mérito ou apoio político; rótulos e valores identificam cada marca.';
 $('ritmo').before(colors);
 const link=document.createElement('a');link.href='#conclusao';link.textContent='Conclusão';document.querySelector('.masthead nav').append(link);
 setupReadingPath();
 setupPresentation();
}

function setupReadingPath(){
 const hero=document.querySelector('.hero');hero.id='abertura';
 const finding=document.createElement('div');finding.className='opening-finding';
 finding.innerHTML='<p id="opening-answer" aria-live="polite">Calculando a distribuição das falas…</p><p id="opening-scope" class="footnote"></p><p class="footnote">Uma ocorrência por código de pronunciamento; frequência não mede produtividade. Fonte: dados abertos do Senado Federal, consolidação de Fabricio Fernandes Santana, v1.1.1. <a href="https://huggingface.co/datasets/fabriciosantana/discursos-senado-legislatura-56" target="_blank" rel="noopener noreferrer">Consultar base ↗</a></p>';
 hero.querySelector('.intro').after(finding);
 const start=hero.querySelector('.primary-link');start.href='#vozes';start.innerHTML='Veja a distribuição <span aria-hidden="true">↓</span>';
 const extra=document.createElement('details');extra.id='exploracao';extra.className='exploration';
 extra.innerHTML='<summary>Explore outros recortes, temas, qualidade e registros</summary><p>As ferramentas abaixo complementam a história principal. Os filtros atualizam os indicadores e a conclusão; o exemplo editorial permanece identificado como fixo.</p>';
 $('conclusao').after(extra);
 const themes=document.createElement('section');themes.id='temas';themes.className='chapter';
 themes.append(document.querySelector('.theme-panel'));
 $('vozes').classList.remove('two-columns');
 $('vozes').querySelector('.eyebrow').textContent='01 / A DISTRIBUIÇÃO DA PALAVRA';
 $('ritmo').querySelector('.eyebrow').textContent='03 / O CONTEXTO NO TEMPO';
 const pair=document.createElement('details');pair.className='pair-exploration';pair.innerHTML='<summary>Comparar dois oradores</summary>';
 const heading=document.querySelector('#concentracao h3');
 while(heading.nextSibling)pair.append(heading.nextSibling);
 pair.prepend(heading);$('concentracao').append(pair);
 $('vozes').after($('concentracao'));$('concentracao').after($('ritmo'));
 for(const id of ['explorar','comparar'])extra.append($(id));
 extra.append(themes);
 for(const id of ['evolucao','qualidade','auditoria','evidencias'])extra.append($(id));
 extra.append($('apresentacao'));
 $('ritmo').after($('conclusao'));$('conclusao').after(extra);
 $('vozes').before(document.querySelector('.metrics'),$('color-key'));
 const evidence=document.createElement('section');evidence.id='exemplo';evidence.className='chapter featured-evidence';
 evidence.innerHTML=`<p class="eyebrow">04 / UM REGISTRO, UMA OCORRÊNCIA</p><h2>Uma fala pode tratar de educação e previdência ao mesmo tempo.</h2>
 <p><strong>Paulo Paim · PT–RS · 29/05/2019 · Discurso #453869</strong></p>
 <blockquote>Comentários sobre a manifestação popular programada para o dia 30 de maio, a se realizar no Brasil e em outros países, em defesa de diversas pautas importantes para o País, como a educação e a previdência.</blockquote>
 <p class="footnote">Resumo do registro no corpus; não é transcrição literal da fala. <a href="https://www25.senado.leg.br/web/atividade/pronunciamentos/-/p/texto/453869" target="_blank" rel="noopener noreferrer">Consultar registro no Senado ↗</a></p>
 <p><strong>Como isso entra no gráfico?</strong> É uma ocorrência na contagem de falas e pode aparecer em dois temas. O total de menções temáticas não é o total de discursos.</p>
 <p><strong>Por que este exemplo?</strong> Ele liga o orador mais frequente do recorte inicial ao mês de maior volume e mostra como pautas de interesse público aparecem em um registro concreto. Não explica a concentração das falas nem representa todo o corpus.</p>
 <p class="footnote">Exemplo editorial fixo, selecionado na categoria Discurso, fev/2019–jan/2023; não muda com os filtros. <span id="example-scope"></span></p>`;
 $('conclusao').before(evidence);
 document.querySelector('.masthead nav').innerHTML='<a href="#vozes">As vozes</a><a href="#ritmo">O ritmo</a><a href="#exemplo">Um registro</a><a href="#conclusao">Conclusão</a><a href="#exploracao">Explorar</a><a href="#metodo">Fontes</a>';
 // Anchors into a collapsed exploration must reveal their target.
 const reveal=hash=>{const target=document.getElementById(hash.slice(1));if(target&&extra.contains(target)){extra.open=true;target.scrollIntoView();}};
 document.addEventListener('click',event=>{const a=event.target.closest('a[href^="#"]');if(a)reveal(a.getAttribute('href'));});
 window.addEventListener('hashchange',()=>reveal(location.hash));reveal(location.hash);
 $('apresentacao').querySelector('ol').innerHTML='<li>0:00–2:00 · Pergunta, achado, fonte e recorte.</li><li>2:00–4:00 · Distribuição entre oradores.</li><li>4:00–5:00 · Participação acumulada.</li><li>5:00–6:30 · Ritmo mensal.</li><li>6:30–8:30 · Registro #453869 e limites.</li><li>8:30–10:00 · Conclusão e encerramento.</li>';
}

export function updateNarrative(stats,comparison){
 $('opening-answer').textContent=narrativeHeadline(stats);
 $('opening-scope').textContent=$('scope').textContent;
 document.querySelector('#conclusao h2').textContent=narrativeHeadline(stats);
 $('conclusion-answer').textContent=narrativeSummary(stats);
 const top=stats.themes[0],ties=top?stats.themes.filter(t=>t[1]===top[1]).length:0;
 $('themes-title').textContent=top?.[1]?`${top[0]} ${ties>1?'está entre os temas mais detectados':'é o tema mais detectado'}: ${pct(top[1],stats.total)} dos registros.`:'Nenhum tema do dicionário foi detectado neste recorte.';
 document.querySelector('#comparar h2').textContent=!comparison?'Sem comparação: ajuste os períodos.':`B tem ${fmt(Math.abs(comparison.delta))} registros ${comparison.delta<0?'a menos':comparison.delta>0?'a mais':'de diferença'} em relação a A.`;
 document.querySelector('#qualidade h2').textContent=stats.total?`${pct(stats.total-stats.fullText,stats.total)} dos registros não têm texto integral no snapshot.`:'Sem registros para avaliar disponibilidade.';
}
