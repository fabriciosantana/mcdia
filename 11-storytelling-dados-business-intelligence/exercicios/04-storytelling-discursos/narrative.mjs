import {$,fmt,pct} from './ui.mjs';

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
 $('evidencias').after(conclusion);
 const colors=document.createElement('p');colors.className='reading-note';colors.id='color-key';
 colors.textContent='Como ler as cores: verde escuro destaca o pico ou a primeira série; verde suave mantém o contexto. Terracota destaca o primeiro tema e a segunda série nas comparações A/B. Cores não representam partidos, mérito ou apoio político; rótulos e valores identificam cada marca.';
 $('ritmo').before(colors);
 const link=document.createElement('a');link.href='#conclusao';link.textContent='Conclusão';document.querySelector('.masthead nav').append(link);
}

export function updateNarrative(stats,comparison){
 $('conclusion-answer').textContent=narrativeSummary(stats);
 const top=stats.themes[0],ties=top?stats.themes.filter(t=>t[1]===top[1]).length:0;
 $('themes-title').textContent=top?.[1]?`${top[0]} ${ties>1?'está entre os temas mais detectados':'é o tema mais detectado'}: ${pct(top[1],stats.total)} dos registros.`:'Nenhum tema do dicionário foi detectado neste recorte.';
 document.querySelector('#comparar h2').textContent=!comparison?'Sem comparação: ajuste os períodos.':`B tem ${fmt(Math.abs(comparison.delta))} registros ${comparison.delta<0?'a menos':comparison.delta>0?'a mais':'de diferença'} em relação a A.`;
 document.querySelector('#qualidade h2').textContent=stats.total?`${pct(stats.total-stats.fullText,stats.total)} dos registros não têm texto integral no snapshot.`:'Sem registros para avaliar disponibilidade.';
}
