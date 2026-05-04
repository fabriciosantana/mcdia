import json

import pytest

from scripts.run_rag_eval import (
    build_generation_messages,
    build_prompt_from_template,
    build_run_summary,
    coerce_score,
    extract_answer,
    parse_json_object,
)


def test_extract_answer_from_openai_style_payload():
    payload = {"choices": [{"message": {"content": "resposta"}}]}

    assert extract_answer(payload) == "resposta"


def test_extract_answer_from_message_payload():
    payload = {"message": {"content": "resposta direta"}}

    assert extract_answer(payload) == "resposta direta"


def test_extract_answer_rejects_null_payload_and_null_content():
    with pytest.raises(ValueError, match="Payload nulo"):
        extract_answer(None)

    with pytest.raises(ValueError, match="content veio nulo"):
        extract_answer({"choices": [{"message": {"content": None}}]})


def test_extract_answer_falls_back_to_json_for_unknown_dict_payload():
    assert json.loads(extract_answer({"ok": True})) == {"ok": True}


def test_parse_json_object_accepts_clean_json_and_json_with_surrounding_text():
    assert parse_json_object('{"score": 2}') == {"score": 2}
    assert parse_json_object('texto antes {"score": 1} texto depois') == {"score": 1}


def test_parse_json_object_rejects_empty_or_non_object_json():
    with pytest.raises(ValueError, match="Resposta vazia"):
        parse_json_object("")

    with pytest.raises(ValueError, match="nao e um objeto JSON"):
        parse_json_object("[1, 2, 3]")


def test_coerce_score_accepts_only_scale_0_to_2():
    assert coerce_score("0", "campo") == 0
    assert coerce_score(1, "campo") == 1
    assert coerce_score(2, "campo") == 2

    with pytest.raises(ValueError, match="fora da escala"):
        coerce_score(3, "campo")

    with pytest.raises(ValueError, match="invalido"):
        coerce_score("alto", "campo")


def test_build_prompt_from_template_replaces_known_placeholders_and_strips_values():
    template = "Pergunta: {question}\nResposta: {answer}\nFixo: {missing}"

    assert build_prompt_from_template(
        template,
        {
            "question": "  Qual?  ",
            "answer": "  Esta.  ",
        },
    ) == "Pergunta: Qual?\nResposta: Esta.\nFixo: {missing}"


def test_build_generation_messages_for_none_system_and_user_template_modes():
    assert build_generation_messages("pergunta", "prompt", "none") == [
        {"role": "user", "content": "pergunta"}
    ]
    assert build_generation_messages("pergunta", "prompt", "system") == [
        {"role": "system", "content": "prompt"},
        {"role": "user", "content": "pergunta"},
    ]
    assert build_generation_messages("{x}", "Pergunta: {question}", "user_template") == [
        {"role": "user", "content": "Pergunta: {x}"}
    ]

    with pytest.raises(ValueError, match="answer_prompt_role invalido"):
        build_generation_messages("pergunta", "prompt", "invalido")


def test_build_run_summary_aggregates_status_scores_and_timings(tmp_path):
    rows = [
        {
            "id": "q1",
            "category": "controle",
            "status": "ok",
            "total_score": 8,
            "duration_seconds": 1.2345,
        },
        {
            "id": "q2",
            "category": "comparacao",
            "status": "error: timeout",
            "duration_seconds": 2.0,
        },
        {
            "id": "q3",
            "category": "controle",
            "status": "ok",
            "total_score": 10,
            "duration_seconds": 3.0,
        },
    ]

    summary = build_run_summary(
        executed_at_utc="20260504T000000Z",
        finished_at_utc="20260504T000010Z",
        duration_seconds=10.1234,
        rows=rows,
        jsonl_path=tmp_path / "run.jsonl",
        md_path=tmp_path / "run.md",
        csv_path=tmp_path / "run.csv",
        config_path=tmp_path / "run.run_config.json",
        summary_path=tmp_path / "run.run_summary.json",
    )

    assert summary["duration_seconds"] == 10.123
    assert summary["questions"] == {"total": 3, "ok": 2, "error": 1}
    assert summary["scores"] == {"min": 8.0, "avg": 9.0, "max": 10.0}
    assert summary["timing"]["question_duration_seconds"] == {
        "min": 1.234,
        "avg": 2.078,
        "max": 3.0,
    }
    assert summary["question_timings"][1] == {
        "id": "q2",
        "category": "comparacao",
        "status": "error: timeout",
        "duration_seconds": 2.0,
    }
    assert summary["artifacts"]["run_summary"].endswith("run.run_summary.json")
