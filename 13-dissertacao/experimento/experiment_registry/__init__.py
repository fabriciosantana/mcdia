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
