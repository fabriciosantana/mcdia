"""Planos de execução congelados e reproduzíveis."""
from __future__ import annotations
import json,uuid

def create_plan(connection,name:str,battery_id:str,chunk_set_id:str,configuration:dict,index_id:str|None=None,prompt_version:str|None=None)->str:
    if not name.strip(): raise ValueError("nome de plano obrigatório")
    battery=connection.execute("SELECT state,chunk_set_id FROM question_batteries WHERE battery_id=?",(battery_id,)).fetchone()
    if not battery or battery['state']!='frozen' or battery['chunk_set_id']!=chunk_set_id: raise ValueError("bateria deve estar congelada para a segmentação escolhida")
    method=configuration.get('retrieval',{}).get('method')
    if method in {'dense','hybrid'}:
        index=connection.execute("SELECT state,chunk_set_id,model FROM vector_indexes WHERE index_id=?",(index_id,)).fetchone()
        if not index or index['state']!='completed' or index['chunk_set_id']!=chunk_set_id or index['model']!=configuration.get('retrieval',{}).get('embedding_model'): raise ValueError("índice Chroma incompleto ou incompatível")
    plan_id=str(uuid.uuid4())
    connection.execute("INSERT INTO experiment_plans(plan_id,name,battery_id,chunk_set_id,index_id,configuration_json,prompt_version,state,frozen_at) VALUES (?,?,?,?,?,?,?,'frozen',CURRENT_TIMESTAMP)",(plan_id,name.strip(),battery_id,chunk_set_id,index_id,json.dumps(configuration,ensure_ascii=False,sort_keys=True),prompt_version))
    connection.execute("INSERT INTO audit_events(entity_type,entity_id,action,detail_json) VALUES ('experiment_plan',?,'freeze',?)",(plan_id,json.dumps(configuration,ensure_ascii=False)))
    return plan_id
