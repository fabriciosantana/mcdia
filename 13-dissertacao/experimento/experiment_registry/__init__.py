"""Registro persistente das execuções experimentais da dissertação."""

from .config import ExperimentPaths
from .db import connect, initialize_database
from .registry import create_run, get_run, list_runs, register_artifact, validate_run

__all__ = [
    "ExperimentPaths", "connect", "initialize_database", "create_run", "get_run",
    "list_runs", "register_artifact", "validate_run",
]

from .response_evaluation import record_response, record_human_evaluation, list_responses, ingest_jsonl

from .openai_adapter import generate_responses
from .config_profiles import save_profile, list_profiles, get_profile
from .corpus import load_corpus, chunk_documents, prepare_documents, load_chunks
from .evaluation_analysis import record_automated_evaluation, agreement_report, parse_judge_json, judge_response
from .exports import export_run
from .question_curation import save_question_metadata, get_question_metadata
from .analysis import bootstrap_mean, record_error_case, list_error_cases
