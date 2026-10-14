"""Centro de controle local para executar e avaliar experimentos."""
from __future__ import annotations
import json, os, sys
from pathlib import Path
from typing import Any
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))
import streamlit as st
from experiment_registry.config import ExperimentPaths
from experiment_registry.config_profiles import list_profiles, save_profile
from experiment_registry.corpus import prepare_documents, search_chunks
from experiment_registry.db import connect, initialize_database
from experiment_registry.evaluation_analysis import agreement_report, judge_response
from experiment_registry.exports import export_run
from experiment_registry.analysis import record_error_case
from experiment_registry.openai_adapter import generate_responses
from experiment_registry.question_curation import get_question_metadata, save_question_metadata
from experiment_registry.question_bank import list_catalog, save_catalog_question, seed_question_catalog, get_catalog_question
from experiment_registry.registry import get_run, list_runs, validate_run
from experiment_registry.response_evaluation import list_responses, record_human_evaluation
from experiment_registry.retrieval import run_retrieval
EVALUATION_FIELDS = (("factual_correctness","Correção factual"),("context_adherence","Aderência ao contexto"),("citation_support","Suporte das citações"),("proportional_completeness","Completude proporcional"),("insufficiency_recognition","Reconhecimento de insuficiência"))

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
            prepare=st.form_submit_button("Preparar corpus")
        if prepare:
            try: st.success("Corpus preparado."); st.json(prepare_documents(paths, source_path, int(window), int(overlap)))
            except (OSError, RuntimeError, ValueError) as exc: st.error(str(exc))
    with st.form("retrieval-form"):
        name=st.text_input("Nome da execução",placeholder="piloto-hibrido")
        profile_label=st.selectbox("Perfil",list(profile_map) or ["(sem perfil — use os campos abaixo)"])
        documents_path=st.text_input("Arquivo de documentos JSONL",placeholder="dados/documentos.jsonl")
        catalog = list_catalog(connection, "validada")
        question_options = {f'{item["question_id"]} — {item["query"][:90]}': item["question_id"] for item in catalog}
        selected_question_ids = st.multiselect("Perguntas validadas do catálogo", list(question_options), disabled=not question_options)
        method=st.selectbox("Método de recuperação",["bm25","tfidf","hybrid","dense"])
        embedding_model=st.text_input("Modelo de embeddings (apenas dense)", value=os.environ.get("OPENAI_EMBEDDING_MODEL", ""))
        submitted=st.form_submit_button("Executar recuperação")
    if submitted:
        try:
            selected_profile=profile_map.get(profile_label)
            if selected_profile:
                configured_method=json.loads(selected_profile["configuration_json"]).get("retrieval", {}).get("method")
                if configured_method in {"bm25", "tfidf", "hybrid", "dense"}:
                    method=configured_method
            result=run_retrieval(paths,documents_path,None,method,name.strip() or f"run-{method}",embedding_model=embedding_model or None, question_ids=[question_options[label] for label in selected_question_ids]); st.success(f"Recuperação concluída: {result['run_id']}"); st.json(result); st.rerun()
        except (OSError,ValueError) as exc: st.error(str(exc))
    if not runs: st.info("Crie uma execução para habilitar a geração de respostas."); return
    options=_run_options(runs); selected_label=st.selectbox("Execução para administrar",list(options),key="experiment-run"); run_id=options[selected_label]; run=get_run(connection,run_id)
    if run:
        st.subheader(run["name"]); st.write(f"Estado: **{run['state']}** · ID: {run_id}"); st.dataframe(run["artifacts"],use_container_width=True,hide_index=True)
    with st.form(f"generation-form-{run_id}"):
        response_documents=st.text_input("Documentos para geração JSONL",placeholder="dados/documentos.jsonl")
        model=st.text_input("Modelo",value=os.environ.get("OPENAI_MODEL",""),placeholder="modelo configurado no .env")
        generate=st.form_submit_button("Gerar respostas com LLM")
    if generate:
        try: generated=generate_responses(paths,run_id,response_documents,model=model or None); st.success(f"{len(generated)} respostas geradas."); st.rerun()
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
    if st.button("Executar LLM-as-a-judge", key=f"judge-{item['response_id']}"):
        try:
            model=os.environ.get("OPENAI_MODEL")
            if not model: raise ValueError("OPENAI_MODEL não está configurado")
            judge_response(connection,item["response_id"],model); st.success("Julgamento automatizado registrado."); st.rerun()
        except (OSError,RuntimeError,ValueError) as exc: st.error(str(exc))
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
    with st.form(f"evaluation-form-{item['response_id']}"):
        evaluator=st.text_input("Avaliador",placeholder="nome ou identificador")
        scores={field:st.selectbox(label,[0,1,2],key=f"{item['response_id']}-{field}") for field,label in EVALUATION_FIELDS}
        notes=st.text_area("Notas",height=100); submit=st.form_submit_button("Registrar avaliação")
    if submit:
        try:
            if not evaluator.strip(): raise ValueError("o avaliador é obrigatório")
            record_human_evaluation(connection,item["response_id"],evaluator,scores,notes); st.success("Avaliação registrada."); st.rerun()
        except ValueError as exc: st.error(str(exc))


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
    catalog = list_catalog(connection)
    if catalog:
        summary = [{"ID": q["question_id"], "Pergunta": q["query"], "Categoria": q["category"], "Dificuldade": q["difficulty"], "Status": q["status"], "Respondível": q["respondible"]} for q in catalog]
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
    with st.form("catalog-question-form"):
        c1, c2, c3 = st.columns(3)
        question_id = c1.text_input("ID", value=text_value("question_id", "Q001"), disabled=selected != "(nova pergunta)")
        category = c2.text_input("Categoria", value=text_value("category"))
        status = c3.selectbox("Status", ["rascunho", "revisar", "validada", "arquivada"], index=["rascunho", "revisar", "validada", "arquivada"].index(text_value("status") or "rascunho"))
        query = st.text_area("Pergunta", value=text_value("query"), height=90)
        c1, c2, c3 = st.columns(3)
        difficulty = c1.selectbox("Dificuldade", ["easy", "medium", "hard"], index=["easy", "medium", "hard"].index(text_value("difficulty") or "medium"))
        answerability = c2.selectbox("Respondibilidade", ["sim", "parcial", "nao"], index=["sim", "parcial", "nao"].index(text_value("answerability") or "sim"))
        respondible = c3.checkbox("Utilizável no experimento", value=bool(current.get("respondible", True)))
        expected_authors = st.text_input("Autores esperados (separados por ;)", value=text_value("expected_authors"))
        reference_docs = st.text_input("Documentos de referência (separados por ;)", value=text_value("reference_doc_ids"))
        reference_chunks = st.text_input("Trechos de referência (separados por ;)", value=text_value("reference_chunk_ids"))
        criteria = st.text_area("Critérios da resposta", value=text_value("expected_answer_criteria"))
        risks = st.text_area("Riscos de avaliação", value=text_value("evaluation_risks"))
        notes = st.text_area("Notas de curadoria", value=text_value("curation_notes"))
        save = st.form_submit_button("Salvar pergunta")
    if save:
        try:
            save_catalog_question(connection, {"question_id": question_id, "query": query, "category": category, "status": status, "difficulty": difficulty, "answerability": answerability, "respondible": respondible, "expected_authors": expected_authors, "reference_doc_ids": reference_docs, "reference_chunk_ids": reference_chunks, "expected_answer_criteria": criteria, "evaluation_risks": risks, "curation_notes": notes, "source_category": current.get("source_category"), "source_question_id": current.get("source_question_id"), "source_file": current.get("source_file")})
            st.success("Pergunta salva no SQLite.")
            st.rerun()
        except ValueError as exc: st.error(str(exc))


def render_chunks_tab(connection):
    st.header("Documentos e chunks")
    st.caption("Consulte os chunks persistidos no SQLite para localizar evidências e preencher a curadoria das perguntas.")
    total = connection.execute("SELECT COUNT(*) FROM document_chunks").fetchone()[0]
    st.metric("Chunks persistidos", total)
    with st.form("chunk-search-form"):
        c1, c2, c3 = st.columns([2, 2, 1])
        text = c1.text_input("Texto contém", placeholder="ex.: segurança bancária")
        document_id = c2.text_input("Document ID", placeholder="ex.: 451286")
        limit = c3.number_input("Limite", min_value=10, max_value=500, value=100, step=10)
        search = st.form_submit_button("Pesquisar chunks")
    if search or total:
        rows = search_chunks(connection, text, document_id, int(limit))
        if rows:
            st.dataframe([{"chunk_id": row["chunk_id"], "document_id": row["document_id"], "texto": row["text"], "fonte_sha256": row["source_sha256"]} for row in rows], use_container_width=True, hide_index=True)
            selected = st.selectbox("Visualizar chunk", [row["chunk_id"] for row in rows], key="selected-chunk")
            item = next(row for row in rows if row["chunk_id"] == selected)
            st.code(item["chunk_id"], language="text")
            st.text_area("Conteúdo do chunk", item["text"], height=240, key=f"chunk-content-{selected}")
            st.json(json.loads(item["metadata_json"]))
        else:
            st.info("Nenhum chunk corresponde aos filtros informados. Prepare o corpus na aba Experimentos se o catálogo estiver vazio.")
def main():
    st.set_page_config(page_title="Centro de controle experimental",layout="wide"); st.title("Centro de controle experimental"); st.caption("Execute, acompanhe e avalie os experimentos da dissertação em um único lugar.")
    root_default=os.environ.get("EXPERIMENTO_ROOT",str(PROJECT_ROOT)); root_text=st.sidebar.text_input("Raiz do experimento",root_default); paths=ExperimentPaths.from_environment(root_text); initialize_database(paths)
    with connect(paths.database) as connection:
        runs=list_runs(connection); profiles=list_profiles(connection); tabs=st.tabs(["Visão geral","Configurações","Banco de perguntas","Documentos e chunks","Experimentos","Questões e respostas"])
        with tabs[0]: render_overview(connection,runs)
        with tabs[1]: render_configuration_tab(connection)
        with tabs[2]: render_question_catalog_tab(connection)
        with tabs[3]: render_chunks_tab(connection)
        with tabs[4]: render_experiments_tab(paths,connection,runs,profiles)
        with tabs[5]: render_questions_tab(connection,runs)

if __name__ == "__main__": main()

