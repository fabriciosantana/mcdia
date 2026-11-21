"""Generate small analytical index, monthly details and reproducible review sample."""
import hashlib
import json
from pathlib import Path
from collections import defaultdict
ROOT = Path(__file__).resolve().parents[1]
RULES_VERSION = 'dictionary-v1'

def write_json(path, value):
    payload=json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(payload)
    return {'path':str(path.relative_to(ROOT)), 'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()}

def build():
    data=json.loads((ROOT/'data/dashboard.json').read_text());rows=data['rows'];meta=data['meta']
    meta['rulesVersion']=RULES_VERSION;meta['appVersion']='2.0.0';meta['schemaVersion']=2
    fields=['party','uf','kind']; dictionaries={key:sorted({r[key] for r in rows}) for key in fields}
    themes=list(meta['themes']);authors=dict(sorted({r['authorId']:r['author'] for r in rows}.items()))
    indices={k:{v:i for i,v in enumerate(dictionaries[k])} for k in fields}
    compact=[];months=defaultdict(dict)
    for r in rows:
        flags=int(r['fullText'])+2*bool(r['summary'])+4*bool(r['index'])
        mask=sum(1<<themes.index(t) for t in r['themes'])
        compact.append([r['id'],r['date'],r['authorId'],*[indices[k][r[k]] for k in fields],flags,mask])
        months[r['date'][:7]][r['id']]={'summary':r['summary'],'index':r['index']}
    fragments={month:write_json(ROOT/f'data/details/{month}.json',records) for month,records in sorted(months.items())}
    manifest=json.loads((ROOT/'data/manifest.json').read_text())
    catalog={'meta':meta,'dictionaries':dictionaries,'authors':authors,'themes':themes,'columns':['id','date','authorId','party','uf','kind','flags','themesMask'],'rows':compact,'fragments':fragments}
    manifest['catalog']=write_json(ROOT/'data/catalog.json',catalog);manifest['fragments']=fragments
    # Stratified by theme and predicted presence; hash ordering is deterministic.
    sample=[];eligible=[r for r in rows if r['kind']=='Discurso']
    for theme in themes:
        for predicted in [True,False]:
            pool=[r for r in eligible if (theme in r['themes'])==predicted and r['summary']]
            pool.sort(key=lambda r:hashlib.sha256(f'vozes-v2|{theme}|{predicted}|{r["id"]}'.encode()).hexdigest())
            for r in pool[:5]:
                sample.append({'key':f'{r["id"]}|{theme}','id':r['id'],'date':r['date'],'author':r['author'],'theme':theme,'predicted':predicted,'summary':r['summary'],'index':r['index']})
    audit={'schemaVersion':1,'datasetRevision':meta['revision'],'rulesVersion':RULES_VERSION,'sampling':'5 positivos e 5 negativos preditos por tema; categoria Discurso com resumo; ordenação SHA-256 vozes-v2','items':sample}
    manifest['reviewSample']=write_json(ROOT/'data/review-sample.json',audit)
    manifest.update({k:meta[k] for k in ['rulesVersion','appVersion','schemaVersion']})
    (ROOT/'data/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'legacyBytes':(ROOT/'data/dashboard.json').stat().st_size,'catalogBytes':manifest['catalog']['bytes'],'monthlyFragments':len(fragments),'samplePairs':len(sample)},indent=2))
if __name__=='__main__': build()
