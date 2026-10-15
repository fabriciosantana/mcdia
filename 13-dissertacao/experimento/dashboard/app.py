"""Centro de controle local para executar e avaliar experimentos."""
from __future__ import annotations
import json, os, sys
import threading
from pathlib import Path
from typing import Any
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))
import streamlit as st
from experiment_registry.config import ExperimentPaths
from experiment_registry.config_profiles import list_profiles, save_profile
from experiment_registry.corpus import prepare_documents, search_chunks, chunk_context
from experiment_registry.db import connect, initialize_database
from experiment_registry.evaluation_analysis import agreement_report, judge_response
from experiment_registry.exports import export_run
from experiment_registry.analysis import record_error_case
from experiment_registry.openai_adapter import generate_responses
from experiment_registry.question_curation import get_question_metadata, save_question_metadata
from experiment_registry.question_bank import list_catalog, save_catalog_question, seed_question_catalog, get_catalog_question, create_battery, add_battery_member, freeze_battery, import_pilot_battery, add_reference_chunk, validate_catalog_question, clone_battery
from experiment_registry.vector_index import create_index, set_index_state
from experiment_registry.evaluation_workflow import register_evaluator, authenticate_evaluator, create_round, assign_responses, sample_stratified_responses, blind_assignments, submit_assignment, add_claim, annotate_claim_evidence, ensure_protocol, save_analysis_protocol, create_rubric_version, RUBRIC
from experiment_registry.dissertation_reporting import build_report, export_report, create_audit_bundle, restore_audit_bundle
from experiment_registry.plans import create_plan
from experiment_registry.registry import get_run, list_runs, validate_run
from experiment_registry.response_evaluation import list_responses, record_human_evaluation
from experiment_registry.retrieval import run_retrieval
EVALUATION_FIELDS = (("factual_correctness","Correção factual"),("context_adherence","Aderência ao contexto"),("citation_support","Suporte das citações"),("proportional_completeness","Completude proporcional"),("insufficiency_recognition","Reconhecimento de insuficiência"))

def _launch_local_worker(target,**kwargs):
    thread=threading.Thread(target=target,kwargs=kwargs,daemon=True);thread.start();return thread

def _worker_with_error_record(target,experiment_paths,kind,job_run_id=None,**kwargs):
    try:target(**kwargs)
    except Exception as exc:
        with connect(experiment_paths.database) as connection:
            last=connection.execute("SELECT state FROM experiment_jobs WHERE run_id IS ? AND kind=? ORDER BY requested_at DESC LIMIT 1",(job_run_id,kind)).fetchone()
            if not last or last['state']!='failed':
                connection.execute("INSERT INTO experiment_jobs(job_id,run_id,kind,state,error,finished_at) VALUES (?,?,?,'failed',?,CURRENT_TIMESTAMP)",(os.urandom(16).hex(),job_run_id,kind+"-preflight",str(exc)))

def parse_configuration(text: str) -> dict[str, Any]:
    try: value = json.loads(text)
    except json.JSONDecodeError as exc: raise ValueError(f"JSON inválido: {exc.msg}") from exc
    if not isinstance(value, dict): raise ValueError("a configuração deve ser um objeto JSON")
    return value

def _run_options(runs): return {f'{run["name"]} — {run["run_id"]}': run["run_id"] for run in runs}

def render_overview(connection, runs):
    st.header("Visão geral")
    metric_rows = [dict(row) for row in connection.execute("SELECT run_id, method, recall_at_1, recall_at_5, recall_at_10, precision_at_5, hit_at_5, mrr, ndcg_at_5, respondible_questions FROM retrieval_metrics ORDER BY rowid DESC")]
    c1,c2,c3 = st.columns(3); c1.metric("Execuções",len(runs)); c2.metric("Respostas geradas",connection.execute("SELECT COUNT(*) FROM responses").fetchone()[0]); c3.metric("Avaliações humanas",connection.execute("SELECT COUNT(*) FROM human_evaluations").fetchone()[0])
    if metric_rows: st.subheader("Métricas de recuperação"); st.dataframe(metric_rows,use_container_width=True,hide_index=True)
    else: st.info("Ainda não há resultados de recuperação.")
    if runs: st.subheader("Execuções recentes"); st.dataframe(runs,use_container_width=True,hide_index=True)

def render_configuration_tab(connection):
    st.header("Configurações"); st.caption("Salve perfis reutilizáveis para manter parâmetros e entradas documentados.")
    with st.form("profile-form"):
        name=st.text_input("Nome do perfil",placeholder="baseline-hibrido")
        configuration_text=st.text_area("Configuração JSON",value='{"retrieval": {"method": "hybrid", "k": 10}}',height=180)
        submitted=st.form_submit_button("Salvar perfil")
    if submitted:
        try: profile_id=save_profile(connection,name,parse_configuration(configuration_text)); st.success(f"Perfil salvo: {profile_id}"); st.rerun()
        except (ValueError,json.JSONDecodeError) as exc: st.error(str(exc))
    profiles=list_profiles(connection)
    if profiles:
        st.subheader("Perfis salvos"); st.dataframe(profiles,use_container_width=True,hide_index=True)
        labels={f'{p["name"]} — {p["profile_id"]}':p for p in profiles}; selected=st.selectbox("Visualizar perfil",list(labels)); st.json(json.loads(labels[selected]["configuration_json"]))
    else: st.info("Nenhum perfil configurado.")

def render_experiments_tab(paths, connection, runs, profiles):
    st.header("Experimentos"); st.caption("Execute recuperação e geração de respostas sem editar arquivos do registro manualmente.")
    profile_map={f'{p["name"]} — {p["profile_id"]}':p for p in profiles}
    with st.expander("Preparar corpus e chunks"):
        with st.form("prepare-corpus-form"):
            source_path=st.text_input("Corpus JSONL ou Parquet", placeholder="../dados/data/full/discursos.parquet")
            window=st.number_input("Tokens por chunk", min_value=20, value=160, step=16)
            overlap=st.number_input("Sobreposição", min_value=0, value=32, step=8)
            tokenizer=st.text_input("Tokenizador (whitespace-regex legado ou modelo tiktoken)",value="whitespace-regex")
            prepare=st.form_submit_button("Preparar corpus")
        if prepare:
            try: st.success("Corpus preparado."); st.json(prepare_documents(paths, source_path, int(window), int(overlap),tokenizer))
            except (OSError, RuntimeError, ValueError) as exc: st.error(str(exc))
    chunk_sets=[dict(r) for r in connection.execute("SELECT cs.chunk_set_id,cs.corpus_version_id,cs.window_size,cs.overlap_size,cs.tokenizer,cs.chunk_count,cv.name FROM chunk_sets cs JOIN corpus_versions cv USING(corpus_version_id) WHERE cs.state='completed' ORDER BY cs.created_at DESC")]
    indexes=[dict(r) for r in connection.execute("SELECT * FROM vector_indexes ORDER BY created_at DESC")]
    if chunk_sets:
        with st.expander("Índices vetoriais Chroma",expanded=False):
            chosen=st.selectbox("Segmentação para índice",chunk_sets,format_func=lambda x:f"{x['name']} — {x['chunk_set_id']} ({x['chunk_count']} chunks)",key="index-chunk-set")
            index_model=st.text_input("Modelo do índice",value=os.environ.get("OPENAI_EMBEDDING_MODEL",""),key="index-model")
            if st.button("Criar ou retomar índice",key="create-index"):
                try: _launch_local_worker(_worker_with_error_record,target=create_index,experiment_paths=paths,kind="index-build",paths=paths,chunk_set_id=chosen["chunk_set_id"],model=index_model);st.success("Construção local enfileirada. O progresso ficará registrado nos jobs.");st.rerun()
                except (ValueError,RuntimeError,OSError) as exc: st.error(str(exc))
            if indexes: st.dataframe(indexes,use_container_width=True,hide_index=True)
            manageable=[i for i in indexes if i['state'] in {'completed','archived','failed'}]
            if manageable:
                target_index=st.selectbox("Índice para administrar",manageable,format_func=lambda i:f"{i['index_id']} — {i['state']}",key="managed-index")
                state_button="Arquivar índice" if target_index['state']=='completed' else "Validar e reativar índice"
                if st.button(state_button,key="toggle-index-state"):
                    try:set_index_state(paths,target_index['index_id'],'archived' if target_index['state']=='completed' else 'completed');st.success("Estado do índice atualizado.");st.rerun()
                    except (ValueError,RuntimeError,OSError) as exc:st.error(str(exc))
    batteries=[dict(r) for r in connection.execute("SELECT b.*,COUNT(m.question_id) AS members FROM question_batteries b LEFT JOIN battery_members m USING(battery_id) GROUP BY b.battery_id ORDER BY b.created_at DESC")]
    frozen_plans=[dict(r) for r in connection.execute("SELECT * FROM experiment_plans WHERE state='frozen' ORDER BY created_at DESC")]
    if frozen_plans:
        with st.expander("Executar plano congelado"):
            plan=st.selectbox("Plano salvo",frozen_plans,format_func=lambda p:f"{p['name']} — {p['plan_id']}",key="saved-plan")
            if st.button("Executar novamente",key="execute-saved-plan"):
                try:
                    _launch_local_worker(_worker_with_error_record,target=run_retrieval,experiment_paths=paths,kind="retrieval",paths=paths,name=plan['name'],plan_id=plan['plan_id']);st.success("Execução enfileirada localmente.");st.rerun()
                except (OSError,ValueError,RuntimeError) as exc: st.error(str(exc))
    with st.form("retrieval-form"):
        name=st.text_input("Nome da execução",placeholder="piloto-hibrido")
        profile_label=st.selectbox("Perfil",list(profile_map) or ["(sem perfil — use os campos abaixo)"])
        use_profile=st.checkbox("Aplicar parâmetros deste perfil explicitamente",value=False,disabled=profile_label.startswith("("))
        chunk_set=st.selectbox("Segmentação congelada",chunk_sets,format_func=lambda x:f"{x['name']} — {x['chunk_set_id']}",disabled=not chunk_sets)
        battery=st.selectbox("Bateria de perguntas",batteries,format_func=lambda x:f"{x['name']} ({x['members']} itens; {x['state']})",disabled=not batteries)
        method=st.selectbox("Método de recuperação",["bm25","dense","hybrid","tfidf","hybrid_legacy"])
        embedding_model=st.text_input("Modelo de embeddings (apenas dense)", value=os.environ.get("OPENAI_EMBEDDING_MODEL", ""))
        index_options=[i for i in indexes if i["state"]=="completed" and chunk_sets and i["chunk_set_id"]==chunk_set["chunk_set_id"]]
        vector_index=st.selectbox("Índice Chroma",index_options,format_func=lambda x:f"{x['index_id']} — {x['model']}",disabled=method not in {"dense","hybrid"} or not index_options)
        top_k=st.number_input("Top-k",min_value=1,max_value=100,value=10)
        k1=st.number_input("BM25 k1",min_value=0.1,max_value=5.0,value=1.5,step=0.1)
        bm25_b=st.number_input("BM25 b",min_value=0.0,max_value=1.0,value=0.75,step=0.05)
        rrf_k=st.number_input("RRF k",min_value=1,max_value=200,value=60,step=1)
        dense_candidate_k=st.number_input("Candidatos da busca vetorial",min_value=10,max_value=10000,value=1000,step=100)
        active_execution=connection.execute("SELECT 1 FROM experiment_jobs WHERE state='running' AND kind IN ('retrieval','generation','index-build','lexical-build') LIMIT 1").fetchone() is not None
        submitted=st.form_submit_button("Salvar plano e executar recuperação",disabled=active_execution)
    selected_profile=profile_map.get(profile_label)
    if selected_profile and use_profile:
        try: st.json(parse_configuration(selected_profile["configuration_json"]))
        except ValueError as exc: st.error(f"Perfil inválido: {exc}")
    if submitted:
        try:
            effective_parameters={"k1":float(k1),"b":float(bm25_b),"rrf_k":int(rrf_k),"dense_candidate_k":int(dense_candidate_k)}; effective_top_k=int(top_k)
            if selected_profile and use_profile:
                configured=parse_configuration(selected_profile["configuration_json"]).get("retrieval",{})
                method=configured.get("method",method); effective_top_k=int(configured.get("k",effective_top_k)); effective_parameters={**effective_parameters,**configured.get("parameters",{})}
                embedding_model=configured.get("embedding_model",embedding_model)
            st.write("Parâmetros efetivos da execução"); st.json({"method":method,"k":effective_top_k,"embedding_model":embedding_model,"parameters":effective_parameters,"battery_id":battery["battery_id"] if batteries else None,"chunk_set_id":chunk_set["chunk_set_id"] if chunk_sets else None})
            if not chunk_sets or not batteries: raise ValueError("prepare uma segmentação e crie/importa uma bateria")
            if method in {"dense","hybrid"} and not index_options: raise ValueError("crie um índice Chroma concluído para esta segmentação e modelo")
            effective_index=vector_index["index_id"] if method in {"dense","hybrid"} else None
            plan_config={"retrieval":{"method":method,"k":effective_top_k,"embedding_model":embedding_model or None,"parameters":effective_parameters},"generation":{"prompt_version":"response-prompt-v1"}}
            plan_id=create_plan(connection,name.strip() or f"Plano {method}",battery["battery_id"],chunk_set["chunk_set_id"],plan_config,effective_index,"response-prompt-v1")
            _launch_local_worker(_worker_with_error_record,target=run_retrieval,experiment_paths=paths,kind="retrieval",paths=paths,name=name.strip() or f"run-{method}",plan_id=plan_id);st.success("Plano congelado e execução enfileirada localmente.");st.rerun()
        except (OSError,ValueError) as exc: st.error(str(exc))
    jobs=[dict(r) for r in connection.execute("SELECT * FROM experiment_jobs ORDER BY requested_at DESC LIMIT 20")]
    running_jobs=[j for j in jobs if j['state']=='running']
    if jobs:st.subheader("Histórico de tarefas locais");st.dataframe(jobs,use_container_width=True,hide_index=True)
    if running_jobs:
        st.subheader("Tarefas locais em andamento"); st.dataframe(running_jobs,use_container_width=True,hide_index=True)
        cancel_id=st.selectbox("Solicitar cancelamento antes do próximo item",running_jobs,format_func=lambda j:f"{j['kind']} — {j['job_id']} ({j['progress_done']}/{j['progress_total']})",key="cancel-job-select")
        if st.button("Solicitar cancelamento",key="cancel-job"):
            connection.execute("UPDATE experiment_jobs SET state='cancelled',error='cancelamento solicitado pelo operador',finished_at=CURRENT_TIMESTAMP WHERE job_id=? AND state='running'",(cancel_id['job_id'],)); st.rerun()
    if not runs: st.info("Crie uma execução para habilitar a geração de respostas."); return
    options=_run_options(runs); selected_label=st.selectbox("Execução para administrar",list(options),key="experiment-run"); run_id=options[selected_label]; run=get_run(connection,run_id)
    if run:
        st.subheader(run["name"]); st.write(f"Estado: **{run['state']}** · ID: {run_id}"); st.dataframe(run["artifacts"],use_container_width=True,hide_index=True)
    with st.form(f"generation-form-{run_id}"):
        model=st.text_input("Modelo",value=os.environ.get("OPENAI_MODEL",""),placeholder="modelo configurado no .env")
        temperature=st.number_input("Temperatura",min_value=0.0,max_value=2.0,value=0.0,step=0.1)
        generation_attempt=st.number_input("Repetição da geração",min_value=1,value=1,step=1)
        max_responses=st.number_input("Máximo de chamadas nesta operação",min_value=1,value=100,step=10)
        max_prompt_tokens=st.number_input("Teto estimado de tokens de entrada",min_value=100,max_value=1000000,value=50000,step=1000)
        max_duration=st.number_input("Limite de duração (segundos)",min_value=10,value=1800,step=60)
        retry_uncertain=st.checkbox("Confirmo reenviar itens cujo resultado anterior ficou incerto",value=False)
        generate=st.form_submit_button("Enfileirar geração com LLM",disabled=bool(running_jobs))
    if generate:
        try:
            _launch_local_worker(_worker_with_error_record,target=generate_responses,experiment_paths=paths,kind="generation",job_run_id=run_id,paths=paths,run_id=run_id,model=model or None,parameters={"temperature":temperature},attempt=int(generation_attempt),max_items=int(max_responses),max_total_prompt_tokens=int(max_prompt_tokens),max_duration_seconds=int(max_duration),retry_uncertain=retry_uncertain);st.success("Geração enfileirada localmente; respostas concluídas permanecem salvas por item.");st.rerun()
        except (OSError,ValueError,RuntimeError) as exc: st.error(str(exc))
    if st.button("Validar integridade",key=f"validate-{run_id}"):
        report=validate_run(connection,run_id)
        if report["ok"]: st.success("Execução íntegra.")
        else: st.error("Há artefatos ausentes ou alterados.")
        st.json(report)
    if st.button("Exportar resultados CSV/LaTeX", key=f"export-{run_id}"):
        try:
            result=export_run(connection, paths.outputs, run_id); st.success("Artefatos de redação exportados."); st.json(result)
        except ValueError as exc: st.error(str(exc))
    if st.button("Ver concordância humano–juiz", key=f"agreement-{run_id}"):
        st.json(agreement_report(connection, run_id))
    with st.expander("Protocolo analítico H1–H3 e pacote de evidências"):
        protocol_id,rubric_id=ensure_protocol(connection)
        protocol=dict(connection.execute("SELECT * FROM evaluation_protocols WHERE protocol_id=?",(protocol_id,)).fetchone())
        hypotheses=json.loads(protocol['hypotheses_json']); rules=json.loads(protocol['analysis_rules_json'])
        latest_rubric=connection.execute("SELECT * FROM rubric_versions ORDER BY version DESC LIMIT 1").fetchone()
        with st.form("rubric-version-form"):
            rubric_text=st.text_area("Rubrica (âncoras e exemplos por dimensão)",latest_rubric['rubric_json'] if latest_rubric else json.dumps(RUBRIC,ensure_ascii=False,indent=2),height=300)
            save_rubric=st.form_submit_button("Congelar nova versão da rubrica")
        if save_rubric:
            try: create_rubric_version(connection,parse_configuration(rubric_text));st.success("Nova versão congelada; novas rodadas passam a usá-la.");st.rerun()
            except ValueError as exc: st.error(str(exc))
        categories=[r[0] for r in connection.execute("SELECT DISTINCT COALESCE(source_category,category) FROM run_question_snapshots WHERE source_category IS NOT NULL OR category IS NOT NULL ORDER BY 1")]
        st.caption(f"Protocolo v{protocol['version']} · {protocol['state']} · rubrica v1")
        with st.form("analysis-protocol-form"):
            hypothesis_text=st.text_area("Hipóteses H1–H3 (JSON)",json.dumps(hypotheses,ensure_ascii=False,indent=2),height=180)
            simple=st.multiselect("Categorias do grupo simples",categories,default=[c for c in rules.get('complexity_groups',{}).get('simple',[]) if c in categories])
            complex_group=st.multiselect("Categorias do grupo complexo",categories,default=[c for c in rules.get('complexity_groups',{}).get('complex',[]) if c in categories])
            length_bins=rules.get("document_length_bins_chars",[1000,5000]);len1=st.number_input("Limite inferior de extensão do documento (caracteres)",min_value=1,value=int(length_bins[0]));len2=st.number_input("Limite superior de extensão do documento (caracteres)",min_value=2,value=int(length_bins[1]))
            human_rounds=[dict(r) for r in connection.execute("SELECT round_id,label FROM evaluation_rounds WHERE run_id=? AND kind='human' ORDER BY created_at DESC",(run_id,))]
            judge_rounds=[dict(r) for r in connection.execute("SELECT round_id,label FROM evaluation_rounds WHERE run_id=? AND kind='judge' ORDER BY created_at DESC",(run_id,))]
            hr=st.selectbox("Rodada humana para H3",[None]+human_rounds,format_func=lambda x:"Mais recente por resposta" if x is None else x['label'])
            jr=st.selectbox("Rodada do juiz para H3",[None]+judge_rounds,format_func=lambda x:"Mais recente por resposta" if x is None else x['label'])
            freeze=st.checkbox("Congelar esta versão do protocolo",value=False)
            save_protocol=st.form_submit_button("Salvar protocolo")
        if save_protocol:
            try:
                new_hypotheses=parse_configuration(hypothesis_text)
                updated={**rules,"complexity_groups":{"simple":simple,"complex":complex_group},"document_length_bins_chars":[int(len1),int(len2)],"bootstrap_unit":"question","kappa_weights":"linear","human_round_id":hr['round_id'] if hr else None,"judge_round_id":jr['round_id'] if jr else None}
                save_analysis_protocol(connection,protocol_id,new_hypotheses,updated,freeze); st.success("Protocolo salvo."); st.rerun()
            except (ValueError,json.JSONDecodeError) as exc: st.error(str(exc))
        report_run_options={f"{candidate['name']} — {candidate['run_id']}":candidate for candidate in runs}
        selected_report_labels=st.multiselect("Execuções para analisar",list(report_run_options),default=[label for label,candidate in report_run_options.items() if run and candidate['run_id']==run_id],key="analysis-run-select")
        report_runs=[report_run_options[label] for label in selected_report_labels]
        if report_runs and st.button("Gerar relatório H1–H3",key="build-analysis"):
            try:
                current_protocol=connection.execute("SELECT protocol_id FROM evaluation_protocols WHERE name='Protocolo da dissertação' ORDER BY version DESC LIMIT 1").fetchone()[0]
                ids=[r['run_id'] for r in report_runs]; report=build_report(connection,ids,current_protocol)
                artifact_dir=paths.outputs/"analysis"/current_protocol; exports=export_report(report,artifact_dir)
                for rid in ids: connection.execute("INSERT INTO analysis_reports(report_id,run_id,protocol_id,report_json) VALUES (?,?,?,?)",(__import__('uuid').uuid4().hex,rid,current_protocol,json.dumps(report,ensure_ascii=False)))
                st.session_state['latest_analysis']={"report":report,"exports":{k:str(v) for k,v in exports.items()}}
            except (ValueError,OSError) as exc: st.error(str(exc))
        latest=st.session_state.get('latest_analysis')
        if latest:
            st.json(latest['report']); st.dataframe(latest['report'].get('H1',{}).get('cases',[]),use_container_width=True,hide_index=True)
            for label,path in latest['exports'].items():
                with open(path,'rb') as f: st.download_button(f"Baixar {label}",f.read(),file_name=Path(path).name,key=f"download-report-{label}")
            if st.button("Gerar pacote de auditoria SQLite + Chroma",key="audit-bundle"):
                bundle=paths.outputs/"audit"/("evidencias-"+"-".join(latest['report']['runs'])[:48]+".zip")
                try: create_audit_bundle(paths,latest['report']['runs'],bundle); st.session_state['audit_bundle']=str(bundle); st.success("Pacote criado.")
                except (ValueError,OSError) as exc: st.error(str(exc))
            if st.session_state.get('audit_bundle'):
                with open(st.session_state['audit_bundle'],'rb') as f: st.download_button("Baixar pacote de auditoria",f.read(),file_name=Path(st.session_state['audit_bundle']).name)
        upload=st.file_uploader("Restaurar pacote em novo diretório",type=["zip"],key="restore-audit-upload")
        target=st.text_input("Diretório novo de restauração",str(paths.root/"restored"/"audit-restore"))
        if upload and st.button("Restaurar em diretório novo",key="restore-audit"):
            temp=paths.outputs/"restore-upload.zip";temp.parent.mkdir(parents=True,exist_ok=True);temp.write_bytes(upload.getvalue())
            try: restore_audit_bundle(temp,Path(target).expanduser());st.success(f"Backup restaurado em {target}. O banco ativo não foi substituído.")
            except (OSError,ValueError) as exc: st.error(str(exc))

def render_questions_tab(connection,runs):
    st.header("Questões e respostas")
    if not runs: st.info("Nenhuma execução disponível."); return
    options=_run_options(runs); selected_label=st.selectbox("Execução",list(options),key="questions-run"); run_id=options[selected_label]
    questions=[dict(row) for row in connection.execute("SELECT q.question_id, q.query, q.reference_doc_ids_json, q.respondible, m.category, m.validation_status, m.reference_chunks_json FROM questions q LEFT JOIN question_metadata m ON m.run_id=q.run_id AND m.question_id=q.question_id WHERE q.run_id=? ORDER BY q.question_id",(run_id,))]
    if questions: st.subheader("Perguntas"); st.dataframe(questions,use_container_width=True,hide_index=True)
    if questions:
        question_map={q["question_id"]: q for q in questions}; selected_question=st.selectbox("Pergunta para curadoria", list(question_map), key=f"curation-question-{run_id}"); metadata=get_question_metadata(connection, run_id, selected_question)
        with st.form(f"curation-form-{run_id}-{selected_question}"):
            category=st.text_input("Categoria", value=metadata["category"] or "")
            status=st.selectbox("Status", ["rascunho","revisar","validada"], index=["rascunho","revisar","validada"].index(metadata["validation_status"]) if metadata["validation_status"] in {"rascunho","revisar","validada"} else 0)
            chunks=st.text_input("IDs dos trechos relevantes (separados por ;)", value=";".join(metadata["reference_chunks"]))
            notes=st.text_area("Justificativa/observações", value=metadata["curation_notes"])
            save=st.form_submit_button("Salvar curadoria")
        if save:
            try: save_question_metadata(connection,run_id,selected_question,category,status,[x.strip() for x in chunks.split(";") if x.strip()],{},notes); st.success("Curadoria salva."); st.rerun()
            except ValueError as exc: st.error(str(exc))
    responses=list_responses(connection,run_id)
    if not responses: st.info("Nenhuma resposta gerada para esta execução."); return
    st.subheader("Respostas"); response_map={f'{item["question_id"]} — {item["response_id"]}':item for item in responses}; selected_response=st.selectbox("Resposta para visualizar e avaliar",list(response_map)); item=response_map[selected_response]
    st.markdown(item["answer"])
    with st.expander("Citações e metadados",expanded=True): st.json({"model":item["model"],"prompt_hash":item["prompt_hash"],"citations":item["citations"]})
    judge_rounds=[dict(r) for r in connection.execute("SELECT * FROM evaluation_rounds WHERE run_id=? AND kind='judge' AND state IN ('active','completed') ORDER BY created_at DESC",(run_id,))]
    judge_model=st.text_input("Modelo do juiz",value=os.environ.get("OPENAI_MODEL",""),key=f"judge-model-{run_id}")
    if st.button("Criar rodada do juiz",key=f"create-judge-round-{run_id}"):
        try: create_round(connection,run_id,"Juiz — "+judge_model,"judge",True,judge_model);st.success("Rodada do juiz criada.");st.rerun()
        except ValueError as exc: st.error(str(exc))
    if judge_rounds:
        judge_round=st.selectbox("Rodada de julgamento",judge_rounds,format_func=lambda r:f"{r['label']} — {r['model']}",key=f"judge-round-{run_id}")
        judge_attempt=st.number_input("Repetição do juiz",min_value=1,value=1,step=1,key=f"judge-attempt-{run_id}")
        if st.button("Executar LLM-as-a-judge", key=f"judge-{item['response_id']}"):
            try:
                if not judge_model: raise ValueError("informe o modelo do juiz")
                judge_response(connection,item["response_id"],judge_model,round_id=judge_round['round_id'],attempt=int(judge_attempt)); st.success("Julgamento automatizado registrado."); st.rerun()
            except (OSError,RuntimeError,ValueError) as exc: st.error(str(exc))
    else: st.info("Crie uma rodada do juiz para rastrear modelo, prompts e repetições.")
    if item["evaluations"]: st.write("Avaliações registradas"); st.dataframe(item["evaluations"],use_container_width=True,hide_index=True)
    if item["automated_evaluations"]: st.write("Julgamentos automatizados"); st.dataframe(item["automated_evaluations"],use_container_width=True,hide_index=True)
    if item["error_cases"]: st.write("Casos críticos"); st.dataframe(item["error_cases"],use_container_width=True,hide_index=True)
    with st.form(f"error-form-{item['response_id']}"):
        error_type=st.selectbox("Tipo de erro", ["falha_recuperacao","extrapolacao_contexto","atribuicao_incorreta","citacao_insuficiente","insuficiencia_nao_reconhecida","outro"])
        severity=st.selectbox("Severidade", ["low","moderate","high","critical"])
        error_notes=st.text_area("Descrição do caso crítico", height=80)
        save_error=st.form_submit_button("Registrar caso crítico")
    if save_error:
        try: record_error_case(connection,item["response_id"],error_type,severity,error_notes); st.success("Caso crítico registrado."); st.rerun()
        except ValueError as exc: st.error(str(exc))
    st.info("Para avaliar respostas com cegamento e registro de rodadas, use a aba Avaliação humana.")


def render_question_catalog_tab(connection):
    st.header("Banco de perguntas")
    st.caption("O catálogo operacional fica no SQLite. CSV e JSON servem apenas para importação inicial ou exportação.")
    default_source = PROJECT_ROOT.parent / "dados" / "piloto" / "banco_perguntas_dissertacao_v1.json"
    if connection.execute("SELECT COUNT(*) FROM question_catalog").fetchone()[0] == 0 and default_source.is_file():
        if st.button("Importar banco inicial para o SQLite"):
            inserted = seed_question_catalog(connection, default_source)
            st.success(f"{inserted} perguntas importadas.")
            st.rerun()
        st.info("O banco inicial está disponível para importação. Depois disso, administre as perguntas nesta tela.")
    show_archived=st.checkbox("Mostrar perguntas arquivadas",value=False)
    catalog = list_catalog(connection,"arquivada") if show_archived else list_catalog(connection)
    if catalog:
        summary = [{"ID": q["question_id"], "Pergunta": q["query"], "Categoria": q["category"], "Dificuldade": q["difficulty"], "Status": q["status"], "Elegível":q["eligible"],"Respondível": q["respondible"],"Pendência":q.get("pending_review")} for q in catalog]
        st.dataframe(summary, use_container_width=True, hide_index=True)
    st.subheader("Cadastrar ou editar pergunta")
    ids = [q["question_id"] for q in catalog]
    selected = st.selectbox("Pergunta", ["(nova pergunta)"] + ids, key="catalog-selected")
    current = get_catalog_question(connection, selected) if selected != "(nova pergunta)" else {}
    def text_value(name, default=""):
        value = current.get(name, default)
        if isinstance(value, list): return ";".join(value)
        if isinstance(value, dict): return json.dumps(value, ensure_ascii=False)
        return value or ""
    with st.form(f"catalog-question-form-{selected}"):
        c1, c2, c3 = st.columns(3)
        question_id = c1.text_input("ID", value=text_value("question_id", "Q001"), disabled=selected != "(nova pergunta)",key=f"catalog-id-{selected}")
        category = c2.text_input("Categoria", value=text_value("category"),key=f"catalog-category-{selected}")
        status_value=text_value("status") or "rascunho"; status = c3.selectbox("Status", ["rascunho", "revisar", "validada", "arquivada"], index=["rascunho", "revisar", "validada", "arquivada"].index(status_value),key=f"catalog-status-{selected}")
        query = st.text_area("Pergunta", value=text_value("query"), height=90,key=f"catalog-query-{selected}")
        c1, c2, c3 = st.columns(3)
        difficulty_value=text_value("difficulty") or "medium"; difficulty = c1.selectbox("Dificuldade", ["easy", "medium", "hard"], index=["easy", "medium", "hard"].index(difficulty_value),key=f"catalog-difficulty-{selected}")
        answerability_value=text_value("answerability") or "sim"; answerability = c2.selectbox("Respondibilidade", ["sim", "parcial", "nao"], index=["sim", "parcial", "nao"].index(answerability_value),key=f"catalog-answerability-{selected}")
        respondible = c3.checkbox("Projeção binária respondível (revisar se parcial)",value=bool(current.get("respondible",True)),key=f"catalog-respondible-{selected}")
        eligible = c3.checkbox("Elegível para uso experimental", value=bool(current.get("eligible", True)),key=f"catalog-eligible-{selected}")
        expected_authors = st.text_input("Autores esperados (separados por ;)", value=text_value("expected_authors"),key=f"catalog-authors-{selected}")
        secondary_categories=st.text_input("Categorias secundárias (separadas por ;)",value=text_value("secondary_categories"),key=f"catalog-secondary-{selected}")
        reference_docs = st.text_input("Documentos de referência (separados por ;)", value=text_value("reference_doc_ids"),key=f"catalog-refdocs-{selected}")
        reference_chunks = st.text_input("Trechos de referência (separados por ;)", value=text_value("reference_chunk_ids"),key=f"catalog-refchunks-{selected}")
        criteria = st.text_area("Critérios da resposta", value=text_value("expected_answer_criteria"),key=f"catalog-criteria-{selected}")
        risks = st.text_area("Riscos de avaliação", value=text_value("evaluation_risks"),key=f"catalog-risks-{selected}")
        notes = st.text_area("Notas de curadoria", value=text_value("curation_notes"),key=f"catalog-notes-{selected}")
        save = st.form_submit_button("Salvar pergunta")
    if save:
        try:
            save_catalog_question(connection, {"question_id": question_id, "query": query, "category": category, "status": status, "difficulty": difficulty, "answerability": answerability, "respondible": respondible, "eligible": eligible, "expected_authors": expected_authors,"secondary_categories":secondary_categories, "reference_doc_ids": reference_docs, "reference_chunk_ids": reference_chunks, "relevance_judgments":current.get("relevance_judgments",{}), "expected_answer_criteria": criteria, "evaluation_risks": risks, "curation_notes": notes, "source_category": current.get("source_category"), "source_question_id": current.get("source_question_id"), "source_file": current.get("source_file")})
            st.success("Pergunta salva no SQLite.")
            st.rerun()
        except ValueError as exc: st.error(str(exc))
    if current and current.get('status')=='arquivada' and st.button("Restaurar pergunta para revisão",key=f"restore-question-{selected}"):
        connection.execute("UPDATE question_catalog SET status='revisar',updated_at=CURRENT_TIMESTAMP WHERE question_id=?",(selected,))
        connection.execute("INSERT INTO audit_events(entity_type,entity_id,action) VALUES ('question',?,'restore')",(selected,));st.rerun()


def render_batteries_tab(connection):
    st.header("Baterias e validação")
    pilot=PROJECT_ROOT.parent/"dados"/"piloto"/"bateria_piloto_dissertacao_24_v1.json"
    if pilot.is_file() and not connection.execute("SELECT 1 FROM question_batteries WHERE name='Piloto da dissertação — 24 perguntas'").fetchone():
        if st.button("Importar piloto de 24 itens por proveniência"):
            result=import_pilot_battery(connection,pilot); st.json(result); st.rerun()
    batteries=[dict(r) for r in connection.execute("SELECT b.*,COUNT(m.question_id) members FROM question_batteries b LEFT JOIN battery_members m USING(battery_id) GROUP BY b.battery_id ORDER BY b.created_at DESC")]
    with st.form("new-battery-form"):
        name=st.text_input("Nome da nova bateria"); purpose=st.text_input("Finalidade / protocolo")
        if st.form_submit_button("Criar bateria"):
            try: create_battery(connection,name,purpose); st.success("Bateria criada."); st.rerun()
            except ValueError as exc: st.error(str(exc))
    if not batteries: st.info("Nenhuma bateria cadastrada."); return
    selected=st.selectbox("Bateria",batteries,format_func=lambda b:f"{b['name']} — {b['state']} — {b['members']} perguntas")
    members=[dict(r) for r in connection.execute("SELECT bm.*,q.query,q.category,q.status,q.eligible FROM battery_members bm JOIN question_catalog q USING(question_id) WHERE bm.battery_id=? ORDER BY bm.position",(selected['battery_id'],))]
    if members: st.dataframe(members,use_container_width=True,hide_index=True)
    if selected['state'] in {'frozen','archived'}:
        new_name=st.text_input("Nome da próxima versão da bateria",value=selected['name']+" — revisão",key=f"clone-name-{selected['battery_id']}")
        if st.button("Criar nova versão editável",key=f"clone-battery-{selected['battery_id']}"):
            try: clone_battery(connection,selected['battery_id'],new_name); st.success("Nova bateria criada com snapshots existentes."); st.rerun()
            except ValueError as exc: st.error(str(exc))
    if selected['state']=='frozen' and st.button("Arquivar bateria",key=f"archive-battery-{selected['battery_id']}"):
        connection.execute("UPDATE question_batteries SET state='archived' WHERE battery_id=?",(selected['battery_id'],));st.rerun()
    if selected['state']=='archived' and st.button("Restaurar bateria congelada",key=f"restore-battery-{selected['battery_id']}"):
        connection.execute("UPDATE question_batteries SET state='frozen' WHERE battery_id=?",(selected['battery_id'],));st.rerun()
    if selected['state']=='draft':
        if members:
            member_to_remove=st.selectbox("Remover membro da bateria em edição",members,format_func=lambda m:f"{m['question_id']} — {m['query'][:80]}",key=f"remove-member-{selected['battery_id']}")
            if st.button("Remover da bateria",key=f"remove-member-button-{selected['battery_id']}"):
                connection.execute("DELETE FROM battery_members WHERE battery_id=? AND question_id=?",(selected['battery_id'],member_to_remove['question_id']));st.rerun()
        available=[q for q in list_catalog(connection) if q['status']!='arquivada' and q['question_id'] not in {m['question_id'] for m in members}]
        if available:
            with st.form("battery-member-form"):
                q=st.selectbox("Adicionar pergunta",available,format_func=lambda x:f"{x['question_id']} — {x['category']} — {x['query'][:80]}")
                split=st.selectbox("Divisão",["pilot","evaluation","development"]); position=st.number_input("Posição",min_value=0,value=len(members)+1)
                if st.form_submit_button("Adicionar à bateria"):
                    try: add_battery_member(connection,selected['battery_id'],q['question_id'],split=split,position=int(position)); st.rerun()
                    except ValueError as exc: st.error(str(exc))
        chunk_sets=[dict(r) for r in connection.execute("SELECT chunk_set_id FROM chunk_sets WHERE state='completed' ORDER BY created_at DESC")]
        if members and chunk_sets:
            freeze_set=st.selectbox("Segmentação para validar/congelar",chunk_sets,format_func=lambda x:x['chunk_set_id'],key=f"freeze-set-{selected['battery_id']}")
            if st.button("Congelar bateria",key=f"freeze-{selected['battery_id']}"):
                try: freeze_battery(connection,selected['battery_id'],freeze_set['chunk_set_id']); st.success("Bateria e segmentação congeladas."); st.rerun()
                except ValueError as exc: st.error(str(exc))
    else: st.caption("Bateria congelada: para revisões, crie uma nova versão a partir da composição atual.")
    if members:
        qmap={q['question_id']:q for q in list_catalog(connection)}
        q=st.selectbox("Validar pergunta",[m['question_id'] for m in members],format_func=lambda qid:f"{qid} — {qmap[qid]['query'][:90]}")
        sets=[dict(r) for r in connection.execute("SELECT chunk_set_id FROM chunk_sets WHERE state='completed' ORDER BY created_at DESC")]
        if sets:
            with st.form("validate-question-form"):
                cs=st.selectbox("Segmentação",sets,format_func=lambda x:x['chunk_set_id'])
                decision=st.selectbox("Decisão",["respondible","partially_respondible","not_respondible"])
                rationale=st.text_area("Justificativa")
                scope=st.text_area("Escopo de busca documentado")
                validator=st.text_input("Validador")
                if st.form_submit_button("Registrar validação"):
                    try: validate_catalog_question(connection,q,cs['chunk_set_id'],decision,rationale,scope,validator); st.success("Validação registrada na revisão atual."); st.rerun()
                    except ValueError as exc: st.error(str(exc))


def render_chunks_tab(connection):
    st.header("Documentos e chunks")
    st.caption("Consulte os chunks persistidos no SQLite para localizar evidências e preencher a curadoria das perguntas.")
    versions=[dict(r) for r in connection.execute("SELECT corpus_version_id,name,source_sha256,document_count,excluded_count,metadata_coverage_json,imported_at FROM corpus_versions ORDER BY imported_at DESC")]
    if versions:
        st.subheader("Versões do corpus")
        st.dataframe(versions,use_container_width=True,hide_index=True)
        if len(versions)>1:
            selected_versions=st.multiselect("Comparar versões",versions,default=versions[:2],format_func=lambda x:f"{x['name']} — {x['source_sha256'][:12]}")
            if len(selected_versions)==2:
                a,b=selected_versions
                st.json({"same_source":a['source_sha256']==b['source_sha256'],"document_count_delta":b['document_count']-a['document_count'],"excluded_count_delta":b['excluded_count']-a['excluded_count'],"metadata_coverage":{"left":json.loads(a['metadata_coverage_json']),"right":json.loads(b['metadata_coverage_json'])}})
    chunk_sets=[dict(r) for r in connection.execute("SELECT cs.*,cv.name FROM chunk_sets cs JOIN corpus_versions cv USING(corpus_version_id) WHERE cs.state='completed' ORDER BY cs.created_at DESC")]
    if not chunk_sets: st.info("Importe um corpus para consultar chunks."); return
    selected_set=st.selectbox("Versão da segmentação",chunk_sets,format_func=lambda x:f"{x['name']} — {x['chunk_set_id']} ({x['chunk_count']} chunks)")
    total = connection.execute("SELECT COUNT(*) FROM document_chunks WHERE chunk_set_id=?",(selected_set['chunk_set_id'],)).fetchone()[0]
    st.metric("Chunks persistidos", total)
    with st.form("chunk-search-form"):
        c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
        text = c1.text_input("Texto contém", placeholder="ex.: segurança bancária")
        document_id = c2.text_input("Document ID", placeholder="ex.: 451286")
        limit = c3.number_input("Limite", min_value=10, max_value=500, value=100, step=10)
        author=c4.text_input("Autor contém")
        date1,date2,date3=st.columns(3); date_from=date1.text_input("Data inicial (YYYY-MM-DD)"); date_to=date2.text_input("Data final (YYYY-MM-DD)"); page=date3.number_input("Página",min_value=1,value=1,step=1)
        search = st.form_submit_button("Pesquisar chunks")
    if search or total:
        offset=(int(page)-1)*int(limit)
        rows = search_chunks(connection, text, document_id, int(limit),offset,author,date_from,date_to,selected_set['chunk_set_id'])
        if rows:
            st.dataframe([{"chunk_id": row["chunk_id"], "document_id": row["document_id"], "texto": row["text"], "fonte_sha256": row["source_sha256"]} for row in rows], use_container_width=True, hide_index=True)
            selected = st.selectbox("Visualizar chunk", [row["chunk_id"] for row in rows], key="selected-chunk")
            item = next(row for row in rows if row["chunk_id"] == selected)
            st.code(item["chunk_id"], language="text")
            st.text_area("Conteúdo do chunk", item["text"], height=240, key=f"chunk-content-{selected}")
            st.json(json.loads(item["metadata_json"]))
            context_rows=chunk_context(connection,selected_set['chunk_set_id'],selected)
            st.caption("Contexto do documento próximo ao trecho selecionado")
            st.dataframe(context_rows,use_container_width=True,hide_index=True)
            catalog=list_catalog(connection)
            if catalog:
                question=st.selectbox("Vincular trecho a pergunta",catalog,format_func=lambda q:f"{q['question_id']} — {q['query'][:100]}")
                with st.form(f"reference-chunk-{question['question_id']}-{selected}"):
                    grade=st.selectbox("Grau de relevância",[0,1,2],index=2)
                    sufficient=st.checkbox("Evidência suficiente para responder")
                    annotator=st.text_input("Avaliador da evidência")
                    justification=st.text_area("Justificativa da relevância")
                    review=st.selectbox("Estado",["draft","review","validated"])
                    if st.form_submit_button("Salvar vínculo pergunta–chunk"):
                        try: add_reference_chunk(connection,question['question_id'],selected_set['chunk_set_id'],selected,grade,sufficient,annotator,justification,review); st.success("Evidência vinculada à revisão atual da pergunta."); st.rerun()
                        except ValueError as exc: st.error(str(exc))
        else:
            st.info("Nenhum chunk corresponde aos filtros informados. Prepare o corpus na aba Experimentos se o catálogo estiver vazio.")


def render_evaluation_admin(connection,runs):
    st.subheader("Gestão de rodadas e atribuições")
    if not runs: st.info("Crie execuções com respostas antes de abrir uma rodada."); return
    run_labels=_run_options(runs); run_label=st.selectbox("Execução administrativa",list(run_labels),key="evaluation-admin-run");run_id=run_labels[run_label]
    with st.form("evaluator-registration"):
        pseudonym=st.text_input("Pseudônimo");access_code=st.text_input("Código de acesso (mínimo 12 caracteres)",type="password");informed=st.checkbox("Avaliador informou ciência da rubrica e finalidade",value=True)
        if st.form_submit_button("Registrar avaliador"):
            try: register_evaluator(connection,pseudonym,informed,access_code);st.success("Avaliador registrado. Entregue o código ao avaliador por canal separado.");st.rerun()
            except ValueError as exc:st.error(str(exc))
    evaluators=[dict(r) for r in connection.execute("SELECT evaluator_id,pseudonym,informed,active FROM evaluator_registry WHERE active=1 ORDER BY pseudonym")]
    with st.form("evaluation-round-create"):
        label=st.text_input("Rótulo da rodada (não inclua sistema ou modelo)");kind=st.selectbox("Tipo",["human","adjudication"])
        if st.form_submit_button("Criar rodada cega"):
            try:create_round(connection,run_id,label,kind,True);st.success("Rodada cega criada.");st.rerun()
            except ValueError as exc:st.error(str(exc))
    rounds=[dict(r) for r in connection.execute("SELECT * FROM evaluation_rounds WHERE run_id=? AND kind IN ('human','adjudication') ORDER BY created_at DESC",(run_id,))]
    if not evaluators or not rounds:st.info("Registre avaliadores e crie uma rodada para atribuir respostas.");return
    rid=st.selectbox("Rodada para atribuir",rounds,format_func=lambda r:f"{r['label']} — {r['kind']} — {r['state']}",key="assignment-round")
    evaluator=st.selectbox("Atribuir ao pseudônimo",evaluators,format_func=lambda e:e['pseudonym'],key="assignment-evaluator")
    response_rows=[dict(r) for r in connection.execute("SELECT r.response_id FROM responses r WHERE r.run_id=? AND r.generation_attempt=(SELECT MIN(r2.generation_attempt) FROM responses r2 WHERE r2.run_id=r.run_id AND r2.question_id=r.question_id) ORDER BY r.question_id",(run_id,))]
    sampling=st.selectbox("Seleção da amostra",["Todas as respostas","Amostra estratificada por categoria","Seleção manual"],key="assignment-sampling")
    if sampling=="Amostra estratificada por categoria":
        sample_size=st.number_input("Tamanho da amostra",min_value=1,max_value=max(1,len(response_rows)),value=min(24,max(1,len(response_rows))),key="stratified-size");seed=st.number_input("Semente reprodutível",min_value=0,value=20261014,step=1,key="stratified-seed")
        try:
            sample=sample_stratified_responses(connection,run_id,int(sample_size),int(seed));selected_ids=sample['response_ids'];st.json(sample['allocation'])
        except ValueError as exc:st.error(str(exc));selected_ids=[]
    elif sampling=="Seleção manual":
        selected=st.multiselect("Respostas da amostra",response_rows,default=[],format_func=lambda r:r['response_id'],key="assignment-responses");selected_ids=[r['response_id'] for r in selected]
    else:selected_ids=[r['response_id'] for r in response_rows]
    if st.button("Criar atribuições",key="assign-evaluation"):
        try:st.success(f"Novas atribuições: {assign_responses(connection,rid['round_id'],evaluator['evaluator_id'],selected_ids)}");st.rerun()
        except ValueError as exc:st.error(str(exc))

def render_blind_evaluation_tab(connection,runs):
    st.header("Sessão cega do avaliador")
    st.caption("Entre com o código individual. A sessão mostra apenas perguntas e evidências atribuídas, sem nome de execução, sistema, modelo ou avaliações de outras pessoas.")
    identity=st.session_state.get('evaluator_session')
    if not identity:
        with st.form("evaluator-login"):
            code=st.text_input("Código de acesso",type="password")
            if st.form_submit_button("Entrar na sessão cega"):
                identity=authenticate_evaluator(connection,code)
                if identity:st.session_state['evaluator_session']=identity;st.rerun()
                else:st.error("Código inválido ou avaliador sem ciência registrada.")
        return
    st.caption(f"Sessão autenticada: {identity['pseudonym']}")
    if st.button("Encerrar sessão",key="evaluator-logout"):st.session_state.pop('evaluator_session',None);st.rerun()
    rounds=[dict(r) for r in connection.execute("SELECT DISTINCT er.round_id,er.kind FROM evaluation_rounds er JOIN evaluation_assignments a USING(round_id) WHERE a.evaluator_id=? AND a.state='assigned' AND er.kind IN ('human','adjudication') ORDER BY er.created_at DESC",(identity['evaluator_id'],))]
    if not rounds:st.info("Não há avaliações pendentes para este avaliador.");return
    round_row=st.selectbox("Rodada",rounds,format_func=lambda r:"Rodada de avaliação" if r['kind']=='human' else "Rodada de adjudicação",key="evaluator-round")
    assignments=blind_assignments(connection,round_row['round_id'],identity['evaluator_id'])
    if not assignments:st.info("Não há itens pendentes nesta rodada.");return
    assignment=st.selectbox("Pergunta atribuída",assignments,format_func=lambda a:a['query'][:140],key="evaluator-assignment")
    st.markdown("**Pergunta**\n\n"+assignment['query']);st.markdown("**Resposta**\n\n"+assignment['answer'])
    response_id=assignment['response_id'];run=connection.execute("SELECT run_id,question_id FROM responses WHERE response_id=?",(response_id,)).fetchone()
    contexts=[dict(r) for r in connection.execute("SELECT rank,chunk_id,document_id,text,source_url FROM run_contexts WHERE run_id=? AND question_id=? ORDER BY rank",(run['run_id'],run['question_id']))]
    with st.expander("Contexto fornecido ao sistema",expanded=True):
        for ctx in contexts:st.markdown(f"**{ctx['rank']}. {ctx['chunk_id']}** · documento {ctx['document_id']} · {ctx['source_url'] or 'URL ausente'}\n\n{ctx['text']}")
    snapshot=connection.execute("SELECT chunk_set_id,reference_chunks_json FROM run_question_snapshots WHERE run_id=? AND question_id=?",(run['run_id'],run['question_id'])).fetchone()
    if snapshot:
        ref_ids=json.loads(snapshot['reference_chunks_json'] or '[]');refs=[]
        if ref_ids:
            placeholders=','.join('?' for _ in ref_ids);refs=[dict(r) for r in connection.execute(f"SELECT chunk_id,document_id,text FROM document_chunks WHERE chunk_set_id=? AND chunk_id IN ({placeholders})",[snapshot['chunk_set_id'],*ref_ids])]
        with st.expander("Evidência de referência do corpus"):st.dataframe(refs,use_container_width=True,hide_index=True)
    rubric_row=connection.execute("SELECT rv.rubric_json FROM evaluation_rounds er JOIN rubric_versions rv USING(rubric_id) WHERE er.round_id=?",(round_row['round_id'],)).fetchone()
    with st.expander("Rubrica versionada e âncoras"):st.json(json.loads(rubric_row['rubric_json']) if rubric_row else RUBRIC)
    with st.form(f"blind-score-form-{assignment['assignment_id']}"):
        scores={field:st.select_slider(label,options=[0,1,2],value=1,key=f"blind-{assignment['assignment_id']}-{field}") for field,label in EVALUATION_FIELDS};notes=st.text_area("Justificativa da avaliação")
        if st.form_submit_button("Submeter avaliação"):
            try:submit_assignment(connection,assignment['assignment_id'],identity['evaluator_id'],scores,notes);st.success("Avaliação submetida.");st.rerun()
            except ValueError as exc:st.error(str(exc))
    st.subheader("Afirmações e suporte das citações")
    claims=[dict(r) for r in connection.execute("SELECT * FROM response_claims WHERE response_id=? ORDER BY ordinal",(response_id,))]
    with st.form(f"claim-form-{response_id}"):
        claim_text=st.text_area("Afirmação central da resposta");ordinal=st.number_input("Ordem",min_value=1,value=len(claims)+1)
        if st.form_submit_button("Registrar afirmação"):
            if claim_text.strip():add_claim(connection,response_id,int(ordinal),claim_text);st.rerun()
            else:st.error("Informe a afirmação.")
    citations=[dict(r) for r in connection.execute("SELECT citation_id,chunk_id,document_id,cited_text FROM citations WHERE response_id=?",(response_id,))]
    for claim in claims:
        st.write(claim['ordinal'],claim['claim_text'])
        with st.form(f"claim-evidence-{claim['claim_id']}"):
            citation=st.selectbox("Citação associada",[None]+citations,format_func=lambda c:"Sem citação" if c is None else f"{c['chunk_id'] or c['document_id']} — {c['cited_text']}")
            support=st.selectbox("Suporte",["complete","partial","absent"],format_func=lambda x:{"complete":"Completo","partial":"Parcial","absent":"Ausente"}[x]);note=st.text_input("Nota");save=st.form_submit_button("Registrar suporte")
        if save:
            try:annotate_claim_evidence(connection,claim['claim_id'],citation['citation_id'] if citation else None,support,identity['evaluator_id'],note,round_row['round_id']);st.success("Suporte anotado.");st.rerun()
            except ValueError as exc:st.error(str(exc))

def render_evaluation_hub(connection,runs):
    admin,review=st.tabs(["Gestão","Sessão do avaliador"])
    with admin:render_evaluation_admin(connection,runs)
    with review:render_blind_evaluation_tab(connection,runs)
def main():
    st.set_page_config(page_title="Centro de controle experimental",layout="wide"); st.title("Centro de controle experimental"); st.caption("Execute, acompanhe e avalie os experimentos da dissertação em um único lugar.")
    root_default=os.environ.get("EXPERIMENTO_ROOT",str(PROJECT_ROOT)); root_text=st.sidebar.text_input("Raiz do experimento",root_default); paths=ExperimentPaths.from_environment(root_text); initialize_database(paths)
    with connect(paths.database) as connection:
        runs=list_runs(connection); profiles=list_profiles(connection); tabs=st.tabs(["Visão geral","Configurações","Banco de perguntas","Baterias","Documentos e chunks","Experimentos","Questões e respostas","Avaliação humana"])
        with tabs[0]: render_overview(connection,runs)
        with tabs[1]: render_configuration_tab(connection)
        with tabs[2]: render_question_catalog_tab(connection)
        with tabs[3]: render_batteries_tab(connection)
        with tabs[4]: render_chunks_tab(connection)
        with tabs[5]: render_experiments_tab(paths,connection,runs,profiles)
        with tabs[6]: render_questions_tab(connection,runs)
        with tabs[7]: render_evaluation_hub(connection,runs)

if __name__ == "__main__": main()

