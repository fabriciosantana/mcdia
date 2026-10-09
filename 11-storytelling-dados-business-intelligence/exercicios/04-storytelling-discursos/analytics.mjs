// Pure analytical functions shared by the browser and Node tests.
export const normalize = value => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR');
export function filterRows(rows, f) {
  const query = normalize(f.query).trim();
  return rows.filter(r => r.date.slice(0, 7) >= f.from && r.date.slice(0, 7) <= f.to &&
    (!f.kind || r.kind === f.kind) && (!f.party || r.party === f.party) &&
    (!f.uf || r.uf === f.uf) && (!f.author || r.authorId === f.author) &&
    (!f.theme || (f.theme === '__none__' ? !r.themes.length : r.themes.includes(f.theme))) &&
    (!query || (r.searchText ?? normalize(r.summary + ' ' + r.index)).includes(query)));
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
