"""Dashboard local para consulta e gestão do registro experimental."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

# Permite executar `streamlit run dashboard/app.py` a partir de experimento/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from experiment_registry.config import ExperimentPaths
from experiment_registry.db import connect, initialize_database
from experiment_registry.registry import create_run, get_run, list_runs, validate_run


def parse_configuration(text: str) -> dict[str, Any]:
    """Converte a configuração da interface em um objeto JSON válido."""
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON inválido: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError("a configuração deve ser um objeto JSON")
    return value


def render_run_details(connection, run_id: str) -> None:
    run = get_run(connection, run_id)
    if run is None:
        st.error("A execução selecionada não existe mais no banco.")
        return
    st.subheader(run["name"])
    st.json({key: value for key, value in run.items() if key != "artifacts"})
    st.write("Artefatos")
    st.dataframe(run["artifacts"], use_container_width=True, hide_index=True)
    if st.button("Validar integridade", key=f"validate-{run_id}"):
        report = validate_run(connection, run_id)
        if report["ok"]:
            st.success("Execução e artefatos íntegros.")
        else:
            st.error("Foram encontrados artefatos alterados ou ausentes.")
        st.json(report)


def main() -> None:
    st.set_page_config(page_title="Registro experimental", layout="wide")
    st.title("Registro experimental")
    st.caption("Interface local para o gerenciador de experimentos da dissertação.")

    root_default = os.environ.get("EXPERIMENTO_ROOT", str(Path.cwd()))
    root_text = st.sidebar.text_input("Raiz do experimento", root_default)
    paths = ExperimentPaths.from_environment(root_text)
    initialize_database(paths)

    with st.sidebar.form("create-run"):
        st.subheader("Nova execução")
        name = st.text_input("Nome", placeholder="baseline-bm25")
        configuration_text = st.text_area(
            "Configuração JSON",
            value='{"retrieval": {"method": "bm25", "k": 5}}',
            height=160,
        )
        submitted = st.form_submit_button("Criar execução")
    if submitted:
        try:
            configuration = parse_configuration(configuration_text)
            if not name.strip():
                raise ValueError("o nome é obrigatório")
            with connect(paths.database) as connection:
                run_id = create_run(connection, name, configuration)
            st.sidebar.success(f"Execução criada: {run_id}")
        except (ValueError, json.JSONDecodeError) as exc:
            st.sidebar.error(str(exc))

    with connect(paths.database) as connection:
        runs = list_runs(connection)
        st.subheader("Execuções")
        st.dataframe(runs, use_container_width=True, hide_index=True)
        metrics = [dict(row) for row in connection.execute(
            "SELECT run_id, method, recall_at_1, recall_at_5, recall_at_10, mrr, respondible_questions "
            "FROM retrieval_metrics ORDER BY run_id"
        )]
        if metrics:
            st.subheader("Métricas de recuperação")
            st.dataframe(metrics, use_container_width=True, hide_index=True)
        if runs:
            options = {f'{run["name"]} — {run["run_id"]}': run["run_id"] for run in runs}
            selected_label = st.selectbox("Execução selecionada", list(options))
            render_run_details(connection, options[selected_label])
        else:
            st.info("Nenhuma execução registrada.")


if __name__ == "__main__":
    main()
