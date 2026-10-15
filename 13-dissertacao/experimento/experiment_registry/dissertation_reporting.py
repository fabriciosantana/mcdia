"""Relatórios H1–H3 com denominadores, cobertura e artefatos de auditoria."""
from __future__ import annotations
import csv,hashlib,json,random,sqlite3,zipfile,subprocess
from pathlib import Path
from .evaluation_analysis import agreement_report

FIELDS=("factual_correctness","context_adherence","citation_support","proportional_completeness","insufficiency_recognition")
def _bootstrap(values,seed=20261014,reps=2000):
    if not values:return {"n":0,"mean":None,"ci95":None,"unit":"pergunta"}
    rng=random.Random(seed); means=[]; n=len(values)
    for _ in range(reps): means.append(sum(values[rng.randrange(n)] for _ in range(n))/n)
    means.sort(); return {"n":n,"mean":sum(values)/n,"ci95":[means[int(.025*reps)],means[min(reps-1,int(.975*reps))]],"unit":"pergunta","replicates":reps}

def _difference_bootstrap(left,right,seed=20261014,reps=2000):
    if not left or not right:return {"difference":None,"ci95":None,"left_n":len(left),"right_n":len(right),"unit":"pergunta"}
    rng=random.Random(seed); values=[]
    for _ in range(reps): values.append(sum(right[rng.randrange(len(right))] for _ in right)/len(right)-sum(left[rng.randrange(len(left))] for _ in left)/len(left))
    values.sort(); return {"difference_complex_minus_simple":sum(right)/len(right)-sum(left)/len(left),"ci95":[values[int(.025*reps)],values[min(reps-1,int(.975*reps))]],"left_n":len(left),"right_n":len(right),"unit":"pergunta","replicates":reps}

def build_report(connection,run_ids:list[str],protocol_id:str):
    protocol=connection.execute("SELECT * FROM evaluation_protocols WHERE protocol_id=?",(protocol_id,)).fetchone()
    if not protocol: raise ValueError("protocolo analítico inexistente")
    rules=json.loads(protocol['analysis_rules_json'] or '{}'); report={"protocol_id":protocol_id,"protocol_version":protocol['version'],"protocol_state":protocol['state'],"runs":run_ids,"pending":[],"H1":{},"H2":{},"H3":{}}
    if protocol['state']!='frozen': report['pending'].append("protocolo não congelado")
    if not rules.get('complexity_groups'): report['pending'].append("grupos de complexidade H2 ainda não definidos")
    report['stratification']={}
    for run_id in run_ids:
        categories={}
        qrows=connection.execute("SELECT q.question_id,m.category,m.validation_status,s.source_category,s.secondary_categories_json,s.sufficient_chunks_json FROM questions q LEFT JOIN question_metadata m USING(run_id,question_id) LEFT JOIN run_question_snapshots s USING(run_id,question_id) WHERE q.run_id=?",(run_id,)).fetchall()
        for q in qrows: categories[q['question_id']]={"category":q['category'],"source_category":q['source_category'] or q['category'],"secondary":json.loads(q['secondary_categories_json'] or '[]') if q['secondary_categories_json'] else [],"sufficient":json.loads(q['sufficient_chunks_json'] or '[]') if q['sufficient_chunks_json'] else [],"validation_status":q['validation_status']}
        for question_id,meta in categories.items():
            retrieved=connection.execute("SELECT chunk_id FROM run_contexts WHERE run_id=? AND question_id=? AND rank<=5 ORDER BY rank",(run_id,question_id)).fetchall()
            snapshot=connection.execute("SELECT reference_chunks_json,sufficient_chunks_json FROM run_question_snapshots WHERE run_id=? AND question_id=?",(run_id,question_id)).fetchone()
            gold=set(json.loads(snapshot[0] or '[]')) if snapshot else set()
            sufficient=set(json.loads(snapshot['sufficient_chunks_json'] or '[]')) if snapshot else set()
            response=connection.execute("SELECT response_id FROM responses r WHERE run_id=? AND question_id=? AND generation_attempt=(SELECT MIN(r2.generation_attempt) FROM responses r2 WHERE r2.run_id=r.run_id AND r2.question_id=r.question_id) ORDER BY created_at,response_id LIMIT 1",(run_id,question_id)).fetchone()
            claims=connection.execute("SELECT claim_id FROM response_claims WHERE response_id=? ORDER BY ordinal",(response['response_id'],)).fetchall() if response else []
            supported=None
            if claims and response:
                vals=[]
                for claim in claims:
                    if rules.get('human_round_id'):
                        counts=connection.execute("SELECT COUNT(*),SUM(CASE WHEN support='complete' AND citation_id IS NOT NULL THEN 1 ELSE 0 END) FROM claim_evidence WHERE claim_id=? AND round_id=?",(claim[0],rules['human_round_id'])).fetchone()
                    else:
                        counts=connection.execute("SELECT COUNT(*),SUM(CASE WHEN e.support='complete' AND e.citation_id IS NOT NULL THEN 1 ELSE 0 END) FROM claim_evidence e JOIN evaluation_rounds er USING(round_id) WHERE e.claim_id=? AND er.kind='human'",(claim[0],)).fetchone()
                    vals.append(bool(counts[0]) and counts[0]==(counts[1] or 0))
                supported=all(vals)
            pertinent=(any(r[0] in sufficient for r in retrieved) if sufficient else None)
            source_row=connection.execute("SELECT d.document_date,d.metadata_json,d.indexed_text,d.text_source,d.source_url FROM run_contexts rc JOIN documents d ON d.document_id=rc.document_id JOIN chunk_sets cs ON cs.chunk_set_id=rc.chunk_set_id AND cs.corpus_version_id=d.corpus_version_id WHERE rc.run_id=? AND rc.question_id=? AND rc.rank=1",(run_id,question_id)).fetchone()
            metadata=json.loads(source_row['metadata_json'] or '{}') if source_row else {}
            date_value=(source_row['document_date'] if source_row else None) or metadata.get('Data')
            year=str(date_value)[:4] if date_value else 'desconhecido'
            source=(metadata.get('Casa') or metadata.get('source') or metadata.get('Fonte') or (source_row['source_url'] if source_row else None) or 'desconhecida')
            length=len(source_row['indexed_text'] or '') if source_row else 0;lower,upper=rules.get('document_length_bins_chars',[1000,5000])
            length_bucket='curto' if length and length<=lower else 'médio' if length<=upper and length else 'longo' if length else 'ausente'
            report['H1'].setdefault('cases',[]).append({"run_id":run_id,"question_id":question_id,"category":meta['category'],"source_category":meta['source_category'],"year":year,"source":source,"indexed_text_chars":length,"length_bucket":length_bucket,"text_source":source_row['text_source'] if source_row else 'ausente',"relevant_gold_count":len(gold),"sufficient_gold_count":len(sufficient),"hit5":int(pertinent) if pertinent is not None else None,"verifiable":int(supported) if supported is not None else None,"cell":(f"pertinente/{'verificável' if supported else 'não verificável'}" if pertinent and supported is not None else f"não pertinente/{'verificável' if supported else 'não verificável'}" if pertinent is False and supported is not None else "não aplicável")})
        report['H2'][run_id]={"by_category":{},"groups":{},"contrasts":{}}
        for category in sorted({m['category'] for m in categories.values() if m['category']}):
            ids=[qid for qid,m in categories.items() if m['category']==category]
            vals=[]
            for qid in ids:
                score=connection.execute("SELECT AVG((factual_correctness+context_adherence+citation_support+proportional_completeness+insufficiency_recognition)/10.0) FROM human_evaluations h JOIN responses r USING(response_id) WHERE r.run_id=? AND r.question_id=?",(run_id,qid)).fetchone()[0]
                if score is not None: vals.append(float(score))
            report['H2'][run_id]['by_category'][category]={**_bootstrap(vals),"questions_in_category":len(ids),"missing_evaluations":len(ids)-len(vals)}
        groups=rules.get('complexity_groups',{})
        group_samples={}
        for group,cats in groups.items():
            ids=[qid for qid,m in categories.items() if m['source_category'] in cats or m['category'] in cats or any(c in cats for c in m['secondary'])]
            scorevals=[]; hits=[]; dimensions={field:[] for field in FIELDS}
            for qid in ids:
                score=connection.execute("SELECT AVG((factual_correctness+context_adherence+citation_support+proportional_completeness+insufficiency_recognition)/10.0) FROM human_evaluations h JOIN responses r USING(response_id) WHERE r.run_id=? AND r.question_id=?",(run_id,qid)).fetchone()[0]
                if score is not None: scorevals.append(float(score))
                for field in FIELDS:
                    dim=connection.execute(f"SELECT AVG({field}/2.0) FROM human_evaluations h JOIN responses r USING(response_id) WHERE r.run_id=? AND r.question_id=?",(run_id,qid)).fetchone()[0]
                    if dim is not None: dimensions[field].append(float(dim))
                metricrow=connection.execute("SELECT metrics_json FROM retrieval_question_metrics WHERE run_id=? AND question_id=?",(run_id,qid)).fetchone()
                if metricrow:
                    m=json.loads(metricrow[0]);
                    if m.get('coverage',{}).get('eligible',0): hits.append(float(m.get('hit_at_5') or 0))
            report['H2'][run_id]['groups'][group]={"categories":cats,"question_count":len(ids),"score":_bootstrap(scorevals),"hit_at_5":_bootstrap(hits),"dimensions":{field:_bootstrap(values) for field,values in dimensions.items()},"missing_score_count":len(ids)-len(scorevals)}
            group_samples[group]={"score":scorevals,"hit_at_5":hits,"dimensions":dimensions}
        if 'simple' in report['H2'][run_id]['groups'] and 'complex' in report['H2'][run_id]['groups']:
            for metric in ('score','hit_at_5'):
                report['H2'][run_id]['contrasts'][metric]=_difference_bootstrap(group_samples['simple'][metric],group_samples['complex'][metric])
            report['H2'][run_id]['contrasts']['dimensions']={field:_difference_bootstrap(group_samples['simple']['dimensions'][field],group_samples['complex']['dimensions'][field]) for field in FIELDS}
        report['H3'][run_id]=agreement_report(connection,run_id,rules.get('human_round_id'),rules.get('judge_round_id'))
        false_positive=[];false_negative=[]
        human_filter=" AND h.round_id=?" if rules.get('human_round_id') else "";judge_filter=" AND a.round_id=?" if rules.get('judge_round_id') else ""
        pair_params=([rules['human_round_id']] if rules.get('human_round_id') else [])+([rules['judge_round_id']] if rules.get('judge_round_id') else [])+[run_id]
        pair_sql="WITH h AS (SELECT h.*,ROW_NUMBER() OVER(PARTITION BY response_id ORDER BY submitted_at DESC,rowid DESC) rn FROM human_evaluations h WHERE 1=1"+human_filter+"),a AS (SELECT a.*,ROW_NUMBER() OVER(PARTITION BY response_id ORDER BY rowid DESC) rn FROM automated_evaluations a WHERE 1=1"+judge_filter+") SELECT * FROM (SELECT h.citation_support hs,a.citation_support js,r.question_id,ROW_NUMBER() OVER(PARTITION BY r.question_id ORDER BY r.generation_attempt,r.response_id) qn FROM h JOIN a USING(response_id) JOIN responses r USING(response_id) WHERE r.run_id=? AND r.generation_attempt=(SELECT MIN(r2.generation_attempt) FROM responses r2 WHERE r2.run_id=r.run_id AND r2.question_id=r.question_id) AND h.rn=1 AND a.rn=1) WHERE qn=1"
        for pair in connection.execute(pair_sql,pair_params):
            if pair['hs'] is None or pair['js'] is None: continue
            if pair['hs']==0 and pair['js']>0:false_positive.append(pair['question_id'])
            if pair['hs']>0 and pair['js']==0:false_negative.append(pair['question_id'])
        pair_count=report['H3'][run_id]['paired_responses']
        report['H3'][run_id]['citation_support_false_positives']={"count":len(set(false_positive)),"rate":len(set(false_positive))/pair_count if pair_count else None,"question_ids":sorted(set(false_positive))}
        report['H3'][run_id]['citation_support_false_negatives']={"count":len(set(false_negative)),"rate":len(set(false_negative))/pair_count if pair_count else None,"question_ids":sorted(set(false_negative))}
        report['stratification'][run_id]={}
        run_cases=[c for c in report['H1']['cases'] if c['run_id']==run_id]
        for dimension in ('year','source','length_bucket','text_source'):
            report['stratification'][run_id][dimension]={}
            for value in sorted({c[dimension] for c in run_cases}):
                cases=[c for c in run_cases if c[dimension]==value];scores=[]
                for case in cases:
                    score=connection.execute("SELECT AVG((factual_correctness+context_adherence+citation_support+proportional_completeness+insufficiency_recognition)/10.0) FROM human_evaluations h JOIN responses r USING(response_id) WHERE r.run_id=? AND r.question_id=? AND r.generation_attempt=(SELECT MIN(r2.generation_attempt) FROM responses r2 WHERE r2.run_id=r.run_id AND r2.question_id=r.question_id)",(run_id,case['question_id'])).fetchone()[0]
                    if score is not None:scores.append(float(score))
                hits=[float(c['hit5']) for c in cases if c['hit5'] is not None]
                report['stratification'][run_id][dimension][value]={"question_count":len(cases),"score":_bootstrap(scores),"hit_at_5":_bootstrap(hits),"missing_score_count":len(cases)-len(scores),"missing_hit_count":len(cases)-len(hits)}
    cells={}
    for case in report['H1'].get('cases',[]): cells[case['cell']]=cells.get(case['cell'],0)+1
    report['H1']['matrix_counts']=cells
    report['H1']['coverage']={"annotated_cases":sum(c['verifiable'] is not None for c in report['H1'].get('cases',[])),"total_cases":len(report['H1'].get('cases',[])),"without_reference_gold":sum(c['relevant_gold_count']==0 for c in report['H1'].get('cases',[])),"without_sufficient_gold":sum(c['sufficient_gold_count']==0 for c in report['H1'].get('cases',[]))}
    return report

def export_report(report:dict,path:Path):
    path.mkdir(parents=True,exist_ok=True); jp=path/'analise-H1-H3.json'; jp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    cp=path/'analise-H1-casos.csv'; rows=report.get('H1',{}).get('cases',[])
    with cp.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['run_id','question_id']);w.writeheader();w.writerows(rows)
    tp=path/'analise-H1-H3.tex'; lines=[r'\documentclass{article}',r'\usepackage[utf8]{inputenc}',r'\usepackage{booktabs}',r'\begin{document}',r'\begin{tabular}{llrr}',r'\toprule',r'Hipótese & Grupo/execução & $n$ & Média \\',r'\midrule']
    for run,details in report.get('H2',{}).items():
        for category,stat in details['by_category'].items():
            safe_category=category.replace('\\','\\textbackslash{}').replace('_',r'\_').replace('&',r'\&')
            lines.append(f"H2 & {safe_category} ({run}) & {stat['n']} & {stat['mean'] if stat['mean'] is not None else 'NA'} "+r"\\")
    lines += [r'\bottomrule',r'\end{tabular}',r'\end{document}',''];tp.write_text('\n'.join(lines),encoding='utf8')
    return {"json":jp,"cases_csv":cp,"latex":tp}

def create_audit_bundle(paths,run_ids:list[str],destination:Path):
    destination.parent.mkdir(parents=True,exist_ok=True); temp_db=destination.with_suffix('.sqlite')
    check=sqlite3.connect(str(paths.database))
    try:
        active=check.execute("SELECT COUNT(*) FROM experiment_jobs WHERE state='running'").fetchone()[0]
        if active: raise ValueError("aguarde a conclusão/cancelamento dos jobs antes do backup")
    finally:check.close()
    source=sqlite3.connect(str(paths.database)); target=sqlite3.connect(str(temp_db))
    try: source.backup(target)
    finally: target.close();source.close()
    # Keep evaluator-level analyses while removing access credentials and the live pseudonym mapping.
    anonymize=sqlite3.connect(str(temp_db));anonymize.row_factory=sqlite3.Row
    try:
        evaluators=anonymize.execute("SELECT evaluator_id FROM evaluator_registry ORDER BY evaluator_id").fetchall()
        for number,row in enumerate(evaluators,1):
            alias=f"avaliador-{number:03d}"
            anonymize.execute("UPDATE evaluator_registry SET pseudonym=?,access_salt=NULL,access_hash=NULL WHERE evaluator_id=?",(alias,row['evaluator_id']))
            anonymize.execute("UPDATE human_evaluations SET evaluator=? WHERE evaluator_id=?",(alias,row['evaluator_id']))
        anonymize.commit()
    finally:anonymize.close()
    digest=hashlib.sha256(temp_db.read_bytes()).hexdigest()
    manifest={"runs":run_ids,"sqlite_sha256":digest,"chromadb_directory":"chromadb/","secrets_included":False,"evaluator_identity_mapping_included":False,"run_configs":[]}
    con=sqlite3.connect(str(temp_db));con.row_factory=sqlite3.Row
    try:
        for rid in run_ids:
            row=con.execute("SELECT r.run_id,r.name,c.configuration_json,r.started_at FROM experiment_runs r JOIN configurations c USING(configuration_hash) WHERE r.run_id=?",(rid,)).fetchone()
            if row: manifest['run_configs'].append(dict(row))
        manifest['vector_indexes']=[dict(r) for r in con.execute("SELECT index_id,chunk_set_id,collection_name,provider,model,dimensions,state,total_items,completed_items FROM vector_indexes WHERE chunk_set_id IN (SELECT chunk_set_id FROM run_question_snapshots WHERE run_id IN ("+','.join('?' for _ in run_ids)+"))",run_ids)] if run_ids else []
    finally:con.close()
    try: manifest['git_revision']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=Path(__file__).resolve().parents[1],text=True,stderr=subprocess.DEVNULL).strip()
    except Exception: manifest['git_revision']=None
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as z:
        z.write(temp_db,'registry.sqlite')
        chroma=paths.embeddings/'chroma'
        if chroma.exists():
            for file in chroma.rglob('*'):
                if file.is_file(): z.write(file,'chromadb/'+str(file.relative_to(chroma)))
        z.writestr('manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
    temp_db.unlink(missing_ok=True);return destination

def restore_audit_bundle(bundle:Path,target_dir:Path):
    target_dir.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(bundle) as z:
        for member in z.infolist():
            dest=(target_dir/member.filename).resolve()
            if target_dir.resolve() not in dest.parents: raise ValueError("arquivo de backup contém caminho inválido")
        z.extractall(target_dir)
    return target_dir
