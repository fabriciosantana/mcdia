"""Registro persistente das execuções experimentais da dissertação."""

from .config import ExperimentPaths
from .db import connect, initialize_database

__all__ = ["ExperimentPaths", "connect", "initialize_database"]
