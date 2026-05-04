import os
from pathlib import Path

import pytest

from scripts import import_batches_to_openwebui as importer


def test_load_dotenv_sets_missing_values_and_preserves_existing(monkeypatch, tmp_path):
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text(
        "\n".join(
            [
                "EXISTING=from_file",
                "NEW_VALUE='quoted value'",
                "EMPTY=",
                "# comment",
                "INVALID_LINE",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("EXISTING", "from_env")

    importer.load_dotenv(dotenv_path)

    assert os.environ["EXISTING"] == "from_env"
    assert os.environ["NEW_VALUE"] == "quoted value"
    assert os.environ["EMPTY"] == ""


def test_require_env_returns_value_or_exits(monkeypatch):
    monkeypatch.setenv("REQUIRED_VALUE", " ok ")
    monkeypatch.delenv("MISSING_VALUE", raising=False)

    assert importer.require_env("REQUIRED_VALUE") == "ok"
    with pytest.raises(SystemExit, match="Variavel obrigatoria ausente"):
        importer.require_env("MISSING_VALUE")


def test_is_openai_rate_limit_error_requires_429_and_embeddings_url():
    assert importer.is_openai_rate_limit_error(
        RuntimeError("429 from https://api.openai.com/v1/embeddings")
    )
    assert not importer.is_openai_rate_limit_error(RuntimeError("429 other endpoint"))
    assert not importer.is_openai_rate_limit_error(
        RuntimeError("https://api.openai.com/v1/embeddings failed")
    )


def test_add_file_to_knowledge_with_retry_retries_only_rate_limits(monkeypatch):
    calls = []

    def fake_add_file_to_knowledge(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            raise RuntimeError("429 from https://api.openai.com/v1/embeddings")
        return {"ok": True}

    monkeypatch.setattr(importer, "add_file_to_knowledge", fake_add_file_to_knowledge)
    monkeypatch.setattr(importer.random, "uniform", lambda _start, _end: 0)
    monkeypatch.setattr(importer.time, "sleep", lambda _seconds: None)

    result = importer.add_file_to_knowledge_with_retry(
        base_url="http://webui",
        token="token",
        knowledge_id="kid",
        file_id="fid",
        max_retries=2,
        initial_backoff=1,
        max_backoff=10,
    )

    assert result == {"ok": True}
    assert len(calls) == 2


def test_add_file_to_knowledge_with_retry_does_not_retry_non_rate_limit(monkeypatch):
    calls = []

    def fake_add_file_to_knowledge(**kwargs):
        calls.append(kwargs)
        raise RuntimeError("500 from openwebui")

    monkeypatch.setattr(importer, "add_file_to_knowledge", fake_add_file_to_knowledge)

    with pytest.raises(RuntimeError, match="500 from openwebui"):
        importer.add_file_to_knowledge_with_retry(
            base_url="http://webui",
            token="token",
            knowledge_id="kid",
            file_id="fid",
            max_retries=2,
            initial_backoff=1,
            max_backoff=10,
        )

    assert len(calls) == 1


def test_start_from_filter_semantics_match_main_sorting():
    file_paths = sorted(Path(name) for name in ["batch_00003.md", "batch_00001.md"])

    assert [p.name for p in file_paths if p.name >= "batch_00002.md"] == [
        "batch_00003.md"
    ]


def test_build_import_summary_aggregates_counts_selection_and_timings(tmp_path):
    selected_files = [
        tmp_path / "batch_00002.md",
        tmp_path / "batch_00003.md",
    ]
    rows = [
        {
            "file_name": "batch_00002.md",
            "status": "imported",
            "file_id": "file-1",
            "duration_seconds": 2.0,
            "error": "",
        },
        {
            "file_name": "batch_00003.md",
            "status": "failed",
            "file_id": "file-2",
            "duration_seconds": 4.5,
            "error": "timeout",
        },
    ]

    summary = importer.build_import_summary(
        executed_at_utc="20260504T000000Z",
        finished_at_utc="20260504T000010Z",
        duration_seconds=10.1234,
        base_url="http://webui",
        knowledge_id="kid",
        pattern="knowledge_openwebui/md_batches/batch_*.md",
        start_from="batch_00002.md",
        limit=2,
        total_matched_files=3,
        skipped_by_start_from=1,
        selected_files=selected_files,
        rows=rows,
        summary_path=tmp_path / "import_summary.json",
    )

    assert summary["duration_seconds"] == 10.123
    assert summary["selection"] == {
        "pattern": "knowledge_openwebui/md_batches/batch_*.md",
        "start_from": "batch_00002.md",
        "limit": 2,
        "total_matched_files": 3,
        "selected_files": 2,
        "skipped_by_start_from": 1,
    }
    assert summary["files"] == {"imported": 1, "failed": 1, "attempted": 2}
    assert summary["timing"]["file_duration_seconds"] == {
        "min": 2.0,
        "avg": 3.25,
        "max": 4.5,
    }
    assert summary["file_results"][1]["error"] == "timeout"
    assert summary["artifacts"]["import_summary"].endswith("import_summary.json")
