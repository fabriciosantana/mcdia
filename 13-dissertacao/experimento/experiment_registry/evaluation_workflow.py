"""Rodadas de avaliação cegas e vínculos de evidência por afirmação."""
from __future__ import annotations
import json,uuid,hashlib,secrets,hmac
from .response_evaluation import record_human_evaluation

RUBRIC={"version":1,"scale":[0,1,2],"dimensions":{
 "factual_correctness":{"0":{"anchor":"afirmação falsa ou sem base factual identificável","example":"atribui ao discurso um dado que não aparece nas fontes"},"1":{"anchor":"núcleo correto, mas com erro ou imprecisão relevante","example":"acerta a tendência e erra o valor ou período"},"2":{"anchor":"afirmações centrais corretas e compatíveis com as fontes","example":"reproduz dado, autoria e período com exatidão"}},
 "context_adherence":{"0":{"anchor":"contradiz ou extrapola substancialmente o contexto recuperado","example":"generaliza além do que os trechos permitem"},"1":{"anchor":"usa o contexto em parte, com inferência não sinalizada","example":"combina trechos sem explicitar a lacuna"},"2":{"anchor":"resposta permanece dentro do contexto e distingue inferência","example":"limita a conclusão ao que os trechos sustentam"}},
 "citation_support":{"0":{"anchor":"afirmações centrais sem suporte identificável ou citação inválida","example":"citação não corresponde ao trecho"},"1":{"anchor":"suporte parcial ou citação não liga claramente a afirmação à fonte","example":"fonte pertinente, mas só sustenta parte da frase"},"2":{"anchor":"afirmações centrais ligadas a evidência pertinente e identificável","example":"cada alegação central aponta para trecho que a sustenta"}},
 "proportional_completeness":{"0":{"anchor":"omite elemento essencial ou acrescenta conteúdo desproporcional","example":"ignora ressalva necessária à resposta"},"1":{"anchor":"responde parcialmente, com omissão ou excesso moderado","example":"inclui o dado principal sem a comparação solicitada"},"2":{"anchor":"cobre o pedido na medida adequada, sem detalhe irrelevante","example":"inclui os elementos necessários e suas ressalvas"}},
 "insufficiency_recognition":{"0":{"anchor":"inventa resposta diante de evidência insuficiente","example":"afirma algo que o corpus não permite concluir"},"1":{"anchor":"sinaliza incerteza, mas ainda apresenta conclusão não sustentada","example":"ressalva a lacuna e depois especula"},"2":{"anchor":"declara a insuficiência e delimita o que falta","example":"diz que não há evidência no material e identifica o limite"}}
}}
def ensure_protocol(connection):
    row=connection.execute("SELECT protocol_id FROM evaluation_protocols WHERE name='Protocolo da dissertação' ORDER BY version DESC LIMIT 1").fetchone()
    if not row:
        pid=str(uuid.uuid4()); connection.execute("INSERT INTO evaluation_protocols(protocol_id,version,name,hypotheses_json,analysis_rules_json) VALUES (?,1,?,?,?)",(pid,"Protocolo da dissertação",json.dumps({"H1":"A pertinência das evidências recuperadas é condição necessária, mas não suficiente, para a verificabilidade das respostas.","H2":"O desempenho tende a ser inferior em perguntas complexas do que em perguntas factuais simples, delimitadas por autor e apoiadas em evidência direta.","H3":"LLM-as-a-judge terá concordância parcial com avaliação humana, mas será insuficiente como critério único."},ensure_ascii=False),json.dumps({"partial_answerability":"report separately","bootstrap_unit":"question","kappa_weights":"linear","complexity_groups":{},"document_length_bins_chars":[1000,5000]})))
        row=(pid,)
    rubric=connection.execute("SELECT rubric_id FROM rubric_versions WHERE version=1").fetchone()
    if not rubric:
        rid=str(uuid.uuid4()); connection.execute("INSERT INTO rubric_versions(rubric_id,version,rubric_json,state) VALUES (?,1,?,'frozen')",(rid,json.dumps(RUBRIC,ensure_ascii=False))); rubric=(rid,)
    return row[0],rubric[0]

def create_rubric_version(connection,rubric_json:dict)->str:
    required={"factual_correctness","context_adherence","citation_support","proportional_completeness","insufficiency_recognition"}
    dimensions=rubric_json.get('dimensions',{})
    if set(dimensions)!=required: raise ValueError("rubrica deve conter exatamente as cinco dimensões do protocolo")
    for field,anchors in dimensions.items():
        if set(str(k) for k in anchors)!={'0','1','2'} or any(not anchors[str(k)].get('anchor') for k in (0,1,2)):
            raise ValueError(f"dimensão {field} precisa de âncoras para 0, 1 e 2")
    version=connection.execute("SELECT COALESCE(MAX(version),0)+1 FROM rubric_versions").fetchone()[0];rid=str(uuid.uuid4())
    connection.execute("INSERT INTO rubric_versions(rubric_id,version,rubric_json,state) VALUES (?,?,?,'frozen')",(rid,version,json.dumps(rubric_json,ensure_ascii=False)))
    connection.execute("INSERT INTO audit_events(entity_type,entity_id,action,detail_json) VALUES ('rubric',?,'freeze',?)",(rid,json.dumps({'version':version})))
    return rid

def save_analysis_protocol(connection,protocol_id:str,hypotheses:dict,rules:dict,freeze:bool=False)->str:
    current=connection.execute("SELECT * FROM evaluation_protocols WHERE protocol_id=?",(protocol_id,)).fetchone()
    if not current: raise ValueError("protocolo não encontrado")
    if set(hypotheses)!={"H1","H2","H3"}:raise ValueError("protocolo deve definir H1, H2 e H3")
    groups=rules.get('complexity_groups',{})
    if freeze and (not groups.get('simple') or not groups.get('complex')): raise ValueError("defina os grupos simple e complex antes de congelar o protocolo")
    if groups.get('simple') and set(groups['simple'])&set(groups.get('complex',[])): raise ValueError("grupos simple e complex devem ser disjuntos")
    bins=rules.get('document_length_bins_chars',[1000,5000])
    if len(bins)!=2 or not (0<int(bins[0])<int(bins[1])):raise ValueError("limites de extensão devem ser dois inteiros crescentes")
    rules['document_length_bins_chars']=[int(bins[0]),int(bins[1])]
    if current['state']=='frozen':
        connection.execute("UPDATE evaluation_protocols SET state='superseded' WHERE protocol_id=?",(protocol_id,))
        protocol_id=str(uuid.uuid4()); version=current['version']+1
        connection.execute("INSERT INTO evaluation_protocols(protocol_id,version,name,hypotheses_json,analysis_rules_json,state) VALUES (?,?,?,?,?,'draft')",(protocol_id,version,current['name'],json.dumps(hypotheses,ensure_ascii=False),json.dumps(rules,ensure_ascii=False)))
    else:
        connection.execute("UPDATE evaluation_protocols SET hypotheses_json=?,analysis_rules_json=? WHERE protocol_id=?",(json.dumps(hypotheses,ensure_ascii=False),json.dumps(rules,ensure_ascii=False),protocol_id))
    if freeze: connection.execute("UPDATE evaluation_protocols SET state='frozen',frozen_at=CURRENT_TIMESTAMP WHERE protocol_id=?",(protocol_id,))
    connection.execute("INSERT INTO audit_events(entity_type,entity_id,action,detail_json) VALUES ('evaluation_protocol',?,?,?)",(protocol_id,'freeze' if freeze else 'save',json.dumps({'rules':rules},ensure_ascii=False)))
    return protocol_id

def register_evaluator(connection,pseudonym: str,informed: bool=True,access_code:str|None=None) -> str:
    if not pseudonym.strip(): raise ValueError("pseudônimo obrigatório")
    if not access_code or len(access_code)<12: raise ValueError("código de acesso deve ter ao menos 12 caracteres")
    salt=secrets.token_hex(16); digest=hashlib.pbkdf2_hmac('sha256',access_code.encode(),bytes.fromhex(salt),200000).hex()
    row=connection.execute("SELECT evaluator_id FROM evaluator_registry WHERE pseudonym=?",(pseudonym.strip(),)).fetchone()
    if row:
        connection.execute("UPDATE evaluator_registry SET informed=?,access_salt=?,access_hash=? WHERE evaluator_id=?",(int(informed),salt,digest,row[0])); return row[0]
    eid=str(uuid.uuid4()); connection.execute("INSERT INTO evaluator_registry(evaluator_id,pseudonym,informed,access_salt,access_hash) VALUES (?,?,?,?,?)",(eid,pseudonym.strip(),int(informed),salt,digest)); return eid

def authenticate_evaluator(connection,access_code:str):
    if not access_code:return None
    for row in connection.execute("SELECT evaluator_id,pseudonym,access_salt,access_hash FROM evaluator_registry WHERE active=1 AND informed=1 AND access_hash IS NOT NULL"):
        digest=hashlib.pbkdf2_hmac('sha256',access_code.encode(),bytes.fromhex(row['access_salt']),200000).hex()
        if hmac.compare_digest(digest,row['access_hash']):return {"evaluator_id":row['evaluator_id'],"pseudonym":row['pseudonym']}
    return None

def create_round(connection,run_id: str,label: str,kind: str="human",blind: bool=True,model: str|None=None) -> str:
    if kind not in {"human","judge","adjudication"}: raise ValueError("tipo de rodada inválido")
    protocol,rubric=ensure_protocol(connection); rid=str(uuid.uuid4())
    connection.execute("INSERT INTO evaluation_rounds(round_id,run_id,protocol_id,rubric_id,kind,label,model,blind,state) VALUES (?,?,?,?,?,?,?,?, 'active')",(rid,run_id,protocol,rubric,kind,label.strip() or kind,model,int(blind)))
    return rid

def assign_responses(connection,round_id: str,evaluator_id: str,response_ids:list[str]) -> int:
    evaluator=connection.execute("SELECT informed FROM evaluator_registry WHERE evaluator_id=? AND active=1",(evaluator_id,)).fetchone()
    if not evaluator or not evaluator[0]: raise ValueError("avaliador inexistente, inativo ou sem ciência registrada")
    count=0
    for response_id in response_ids:
        aid=str(uuid.uuid4()); cursor=connection.execute("INSERT OR IGNORE INTO evaluation_assignments(assignment_id,round_id,response_id,evaluator_id) VALUES (?,?,?,?)",(aid,round_id,response_id,evaluator_id)); count+=max(cursor.rowcount,0)
    return count

def sample_stratified_responses(connection,run_id:str,sample_size:int,seed:int=20261014):
    import random,math
    if sample_size<1:raise ValueError("tamanho da amostra deve ser positivo")
    rows=[dict(r) for r in connection.execute("SELECT r.response_id,q.question_id,COALESCE(s.source_category,s.category,m.category,'sem categoria') category FROM responses r JOIN questions q ON q.run_id=r.run_id AND q.question_id=r.question_id LEFT JOIN run_question_snapshots s USING(run_id,question_id) LEFT JOIN question_metadata m USING(run_id,question_id) WHERE r.run_id=? AND r.generation_attempt=(SELECT MIN(r2.generation_attempt) FROM responses r2 WHERE r2.run_id=r.run_id AND r2.question_id=r.question_id) ORDER BY q.question_id",(run_id,))]
    if not rows:raise ValueError("execução sem respostas disponíveis para amostragem")
    if sample_size>len(rows):raise ValueError(f"amostra solicitada ({sample_size}) excede as {len(rows)} perguntas disponíveis")
    groups={}
    for row in rows:groups.setdefault(row['category'],[]).append(row)
    quotas={cat:sample_size*len(items)/len(rows) for cat,items in groups.items()};allocation={cat:math.floor(q) for cat,q in quotas.items()}
    for cat in sorted(groups,key=lambda key:(-(quotas[key]-allocation[key]),key))[:sample_size-sum(allocation.values())]:allocation[cat]+=1
    rng=random.Random(seed);selected=[]
    for cat,items in groups.items():
        selected.extend(rng.sample(items,allocation[cat]))
    return {"response_ids":[r['response_id'] for r in selected],"sample_size":len(selected),"seed":seed,"allocation":{cat:{"population":len(groups[cat]),"sampled":allocation[cat]} for cat in sorted(groups)}}

def blind_assignments(connection,round_id: str,evaluator_id: str):
    return [dict(r) for r in connection.execute("SELECT a.assignment_id,a.response_id,q.query,r.answer FROM evaluation_assignments a JOIN responses r USING(response_id) JOIN questions q ON q.run_id=r.run_id AND q.question_id=r.question_id WHERE a.round_id=? AND a.evaluator_id=? AND a.state='assigned' ORDER BY a.created_at",(round_id,evaluator_id))]

def submit_assignment(connection,assignment_id: str,evaluator_id: str,scores:dict,notes:str="") -> str:
    row=connection.execute("SELECT a.round_id,a.response_id,e.pseudonym,er.kind FROM evaluation_assignments a JOIN evaluator_registry e USING(evaluator_id) JOIN evaluation_rounds er USING(round_id) WHERE a.assignment_id=? AND a.evaluator_id=? AND a.state='assigned'",(assignment_id,evaluator_id)).fetchone()
    if not row: raise ValueError("atribuição não encontrada, já submetida ou não pertence ao avaliador")
    evaluation_id=record_human_evaluation(connection,row['response_id'],row['pseudonym'],scores,notes,row['round_id'],assignment_id,evaluator_id)
    if row['kind']=='adjudication':
        originals=connection.execute("SELECT h.evaluation_id FROM human_evaluations h JOIN evaluation_rounds er ON er.round_id=h.round_id WHERE h.response_id=? AND er.kind='human'",(row['response_id'],)).fetchall()
        with connection:
            for original in originals:connection.execute("INSERT OR IGNORE INTO evaluation_adjudication_links(adjudicated_evaluation_id,source_evaluation_id) VALUES (?,?)",(evaluation_id,original[0]))
    return evaluation_id

def add_claim(connection,response_id: str,ordinal:int,claim_text:str) -> str:
    if not claim_text.strip(): raise ValueError("afirmação obrigatória")
    cid=str(uuid.uuid4()); connection.execute("INSERT INTO response_claims(claim_id,response_id,ordinal,claim_text) VALUES (?,?,?,?)",(cid,response_id,ordinal,claim_text.strip())); return cid

def annotate_claim_evidence(connection,claim_id:str,citation_id:str|None,support:str,evaluator_id:str,note:str="",round_id:str|None=None):
    if support not in {"complete","partial","absent"}: raise ValueError("suporte deve ser completo, parcial ou ausente")
    connection.execute("INSERT OR REPLACE INTO claim_evidence(claim_id,citation_id,support,note,evaluator_id,round_id) VALUES (?,?,?,?,?,?)",(claim_id,citation_id,support,note,evaluator_id,round_id))
