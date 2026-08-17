from pathlib import Path

import pandas as pd
import pytest

from scripts.build_openwebui_knowledge_from_hf import (
    chunk_words,
    choose_text,
    normalize_text,
    relative_to_project,
)


def test_normalize_text_collapses_whitespace_and_nbsp():
    assert normalize_text("  um\u00a0texto\n\ncom\t espacos  ") == "um texto com espacos"


def test_normalize_text_handles_empty_values():
    assert normalize_text("") == ""
    assert normalize_text(None) == ""


def test_chunk_words_returns_empty_for_empty_text():
    assert chunk_words("", max_words=10, overlap_words=2) == []


def test_chunk_words_keeps_short_text_as_single_chunk():
    assert chunk_words("um dois tres", max_words=10, overlap_words=2) == [
        "um dois tres"
    ]


def test_chunk_words_splits_long_text_with_overlap():
    text = " ".join(f"w{i}" for i in range(1, 11))

    assert chunk_words(text, max_words=4, overlap_words=1) == [
        "w1 w2 w3 w4",
        "w4 w5 w6 w7",
        "w7 w8 w9 w10",
    ]


def test_chunk_words_rejects_overlap_greater_than_or_equal_to_max_words():
    with pytest.raises(ValueError, match="max_words must be greater than overlap_words"):
        chunk_words("um dois tres quatro cinco", max_words=3, overlap_words=3)


def test_choose_text_prefers_integral_text_and_reports_source():
    row = pd.Series(
        {
            "TextoDiscursoIntegral": " texto integral ",
            "Resumo": "resumo",
            "Indexacao": "indexacao",
        }
    )

    assert choose_text(row) == (" texto integral ", "texto_integral")


def test_choose_text_falls_back_to_resumo_then_indexacao():
    assert (
        choose_text(
            pd.Series(
                {
                    "TextoDiscursoIntegral": " ",
                    "Resumo": "resumo",
                    "Indexacao": "indexacao",
                }
            )
        )
        == ("resumo", "resumo")
    )
    assert (
        choose_text(
            pd.Series(
                {
                    "TextoDiscursoIntegral": "",
                    "Resumo": "",
                    "Indexacao": "indexacao",
                }
            )
        )
        == ("indexacao", "indexacao")
    )


def test_choose_text_returns_empty_when_no_text_field_is_available():
    assert choose_text(pd.Series({"TextoDiscursoIntegral": "", "Resumo": ""})) == (
        "",
        "",
    )


def test_relative_to_project_returns_relative_path_for_repo_files():
    assert relative_to_project(
        Path("knowledge_openwebui/build_metadata.json")
    ) == "knowledge_openwebui/build_metadata.json"
