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


def test_wait_for_processing_raises_specific_error_on_failed_status(monkeypatch):
    class FakeResponse:
        status_code = 200

        def json(self):
            return {"status": "failed", "detail": "429 embeddings"}

    monkeypatch.setattr(importer.requests, "get", lambda *args, **kwargs: FakeResponse())

    with pytest.raises(importer.ProcessingFailedError, match="Processamento falhou"):
        importer.wait_for_processing(
            base_url="http://webui",
            token="token",
            file_id="file-1",
            timeout_seconds=30,
            poll_interval=0,
        )


def test_retry_sleep_seconds_caps_backoff_and_adds_jitter(monkeypatch):
    monkeypatch.setattr(importer.random, "uniform", lambda _start, _end: 0.5)

    assert importer.retry_sleep_seconds(1, initial_backoff=10, max_backoff=60) == 10.5
    assert importer.retry_sleep_seconds(4, initial_backoff=10, max_backoff=60) == 60.5


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
        state_path=tmp_path / "import_state.json",
        resume=True,
        dry_run=False,
        process_failed_retries=3,
        process_failed_initial_backoff=60,
        process_failed_max_backoff=600,
        sleep_between_files=5,
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
    assert summary["resume_enabled"] is True
    assert summary["dry_run"] is False
    assert summary["retry_policy"] == {
        "process_failed_retries": 3,
        "process_failed_initial_backoff": 60,
        "process_failed_max_backoff": 600,
        "sleep_between_files": 5,
    }
    assert summary["files"] == {
        "imported": 1,
        "failed": 1,
        "skipped_already_imported": 0,
        "dry_run": 0,
        "processing_retries": 0,
        "attempted": 2,
    }
    assert summary["timing"]["file_duration_seconds"] == {
        "min": 2.0,
        "avg": 3.25,
        "max": 4.5,
    }
    assert summary["file_results"][1]["error"] == "timeout"
    assert summary["artifacts"]["import_summary"].endswith("import_summary.json")
    assert summary["artifacts"]["import_state"].endswith("import_state.json")


def test_import_state_updates_status_and_preserves_attempt_for_pipeline_steps(tmp_path):
    state = importer.load_import_state(tmp_path / "missing_state.json")
    state_path = tmp_path / "import_state.json"
    batch_path = tmp_path / "batch_00001.md"
    batch_path.write_text("conteudo", encoding="utf-8")

    uploaded = importer.update_import_state_entry(
        state=state,
        state_path=state_path,
        knowledge_id="kid",
        file_path=batch_path,
        status="uploaded",
        file_id="file-1",
    )
    processed = importer.update_import_state_entry(
        state=state,
        state_path=state_path,
        knowledge_id="kid",
        file_path=batch_path,
        status="processed",
        file_id="file-1",
    )
    added = importer.update_import_state_entry(
        state=state,
        state_path=state_path,
        knowledge_id="kid",
        file_path=batch_path,
        status="added",
        file_id="file-1",
    )

    assert uploaded["attempts"] == 1
    assert processed["attempts"] == 1
    assert added["attempts"] == 1
    assert importer.should_skip_imported_file(
        state=state,
        knowledge_id="kid",
        file_path=batch_path,
    )

    persisted = importer.load_import_state(state_path)
    assert persisted["imports"]["kid"]["files"]["batch_00001.md"]["status"] == "added"


def test_should_skip_imported_file_requires_matching_hash(tmp_path):
    state = {"version": 1, "imports": {"kid": {"files": {}}}}
    state_path = tmp_path / "import_state.json"
    batch_path = tmp_path / "batch_00001.md"
    batch_path.write_text("versao 1", encoding="utf-8")

    importer.update_import_state_entry(
        state=state,
        state_path=state_path,
        knowledge_id="kid",
        file_path=batch_path,
        status="added",
        file_id="file-1",
    )
    batch_path.write_text("versao 2", encoding="utf-8")

    assert not importer.should_skip_imported_file(
        state=state,
        knowledge_id="kid",
        file_path=batch_path,
    )
