#!/usr/bin/env python3
"""Build an auditable, offline snapshot from a pinned public Parquet."""
import argparse
from collections import Counter
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import urllib.request
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
REPO = 'fabriciosantana/discursos-senado-legislatura-56'
REVISION = 'c20b4e1ea45bbbfb408167cc07c6f79789c7c345'
EXPECTED_HASH = 'e09cfc4793e5394be440906320c7d3008cda5a52b90bbc85bf47446362406af1'
FILES = {'discursos.parquet': 'data/full/discursos_2019-02-01_2023-01-31.parquet', 'dataset-card.md': 'README.md', 'collection.json': 'metadata/collection.json'}
THEMES = {
    'Saúde e pandemia': ['saude', 'sus', 'hospital', 'hospitais', 'pandemia', 'covid', 'coronavirus', 'vacina', 'vacinas', 'vacinacao'],
    'Economia e trabalho': ['economia', 'economico', 'economica', 'emprego', 'desemprego', 'trabalho', 'inflacao', 'juros', 'tributaria', 'tributario', 'imposto', 'impostos', 'orcamento', 'fiscal'],
    'Educação': ['educacao', 'ensino', 'escola', 'escolas', 'universidade', 'universidades', 'professor', 'professores', 'fundeb'],
    'Previdência e proteção social': ['previdencia', 'previdenciaria', 'previdenciario', 'aposentadoria', 'aposentados', 'pensao', 'bolsa familia', 'auxilio emergencial', 'assistencia social'],
    'Meio ambiente': ['meio ambiente', 'ambiental', 'amazonia', 'desmatamento', 'clima', 'climatico', 'barragem', 'barragens', 'brumadinho', 'queimadas'],
    'Direitos e segurança': ['direitos humanos', 'violencia', 'seguranca publica', 'racismo', 'feminicidio', 'policia', 'policial', 'mulheres', 'indigenas']
}
def normalize(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.lower()) if not unicodedata.combining(c))
def detect_themes(text):
    value = normalize(text)
    return [name for name, words in THEMES.items() if any(re.search(r'\b' + re.escape(w) + r'\b', value) for w in words)]
def text(value):
    return re.sub(r'\s+', ' ', str(value or '')).strip()
def build(download=False):
    raw = ROOT / 'data/raw'; raw.mkdir(parents=True, exist_ok=True)
    for local, remote in FILES.items():
        destination = raw / local
        if download or not destination.exists():
            temporary = destination.with_suffix(destination.suffix + '.part')
            urllib.request.urlretrieve(f'https://huggingface.co/datasets/{REPO}/resolve/{REVISION}/{remote}', temporary)
            temporary.replace(destination)
    digest = hashlib.sha256((raw/'discursos.parquet').read_bytes()).hexdigest()
    if digest != EXPECTED_HASH:
        raise ValueError('SHA-256 do Parquet diverge da revisão fixada. Saída não alterada.')
    source = pq.read_table(raw/'discursos.parquet').to_pylist()
    ids = [r['CodigoPronunciamento'] for r in source]
    if len(ids) != len(set(ids)):
        raise ValueError('Códigos duplicados; revisão manual necessária.')
    rows = []
    for r in source:
        date.fromisoformat(r['Data'])
        if not '2019-02-01' <= r['Data'] <= '2023-01-31':
            raise ValueError('Data fora da janela de coleta.')
        if r['TipoAutor'] != 'Senador(a)' or r['Casa'] != 'Senado Federal':
            continue
        name = text(r['NomeAutor']) or 'Autoria não informada'
        summary, index = text(r['Resumo']), text(r['Indexacao'])
        integral = bool(r['ok'] and text(r['TextoDiscursoIntegral']))
        rows.append(dict(id=str(r['CodigoPronunciamento']), date=r['Data'], author=name,
                         authorId=str(r['CodigoParlamentar'] or f'nome:{name}'),
                         party=text(r['Partido']) or 'Não informado', uf=text(r['UF']) or 'Não informada',
                         kind=text(r['TipoUsoPalavra.Descricao']) or 'Não informado',
                         summary=summary, index=index, fullText=integral,
                         themes=detect_themes(summary+' '+index)))
    rows.sort(key=lambda r: (r['date'],r['id']), reverse=True)
    default = [r for r in rows if r['kind']=='Discurso']
    audit = dict(sourceRows=len(source), scopeRows=len(rows), excludedRows=len(source)-len(rows),
        uniqueIds=len(set(ids)), duplicateIds=len(ids)-len(set(ids)),
        observedStart=min(r['Data'] for r in source), observedEnd=max(r['Data'] for r in source),
        sourceMissingFullText=sum(not (r['ok'] and text(r['TextoDiscursoIntegral'])) for r in source),
        scopeMissingFullText=sum(not r['fullText'] for r in rows),
        scopeMissingSummary=sum(not r['summary'] for r in rows),
        scopeMissingAuthorId=sum(not r['CodigoParlamentar'] for r in source if r['TipoAutor']=='Senador(a)' and r['Casa']=='Senado Federal'),
        defaultRows=len(default), defaultAuthors=len({r['authorId'] for r in default}),
        defaultMissingFullText=sum(not r['fullText'] for r in default),
        defaultYears=dict(sorted(Counter(r['date'][:4] for r in default).items())),
        sourceAuthorTypes=dict(Counter(r['TipoAutor'] for r in source)),
        sourceHouses=dict(Counter(r['Casa'] for r in source)))
    meta = dict(dataset=REPO, revision=REVISION, version='v1.1.1', sourceSha256=digest,
        builtAt=datetime.now(timezone.utc).isoformat(), license='MIT (consolidação)',
        windowStart='2019-02-01', windowEnd='2023-01-31', scope='TipoAutor = Senador(a); Casa = Senado Federal',
        themes=THEMES, audit=audit)
    payload = json.dumps(dict(meta=meta,rows=rows),ensure_ascii=False,separators=(',',':'))
    (ROOT/'data/dashboard.json').write_text(payload,encoding='utf-8')
    meta['dashboardSha256']=hashlib.sha256(payload.encode()).hexdigest()
    (ROOT/'data/manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(audit,ensure_ascii=False,indent=2))
    print(f'JSON: {len(payload.encode()):,} bytes')
if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--download',action='store_true',help='Baixar novamente a revisão fixada')
    build(parser.parse_args().download)
