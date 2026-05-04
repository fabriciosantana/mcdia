import json

import pytest

from scripts.run_rag_eval import (
    build_generation_messages,
    build_prompt_from_template,
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
