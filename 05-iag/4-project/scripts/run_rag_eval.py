#!/usr/bin/env python3
"""Executa perguntas de avaliacao contra uma knowledge collection do Open WebUI.

Salva:
- JSONL com resposta completa
- Markdown resumido para revisao humana
- CSV com metricas preenchidas automaticamente a partir da rubrica
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


def json_dumps_compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))


def load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value and len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Variavel obrigatoria ausente: {name}")
    return value


def api_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def get_knowledge_id(base_url: str, token: str, knowledge_name: str) -> str:
    response = requests.get(f"{base_url}/api/v1/knowledge/", headers=api_headers(token), timeout=30)
    response.raise_for_status()
    items = response.json().get("items", [])
    for item in items:
        if item.get("name") == knowledge_name:
            return item["id"]
    raise SystemExit(f'Knowledge com nome "{knowledge_name}" nao encontrada.')


def extract_answer(payload: dict[str, Any]) -> str:
    if "choices" in payload and payload["choices"]:
        return payload["choices"][0]["message"]["content"]
    if "message" in payload and isinstance(payload["message"], dict):
        return str(payload["message"].get("content", ""))
    return json.dumps(payload, ensure_ascii=True)


def ask_openwebui(
    base_url: str,
    token: str,
    model: str,
    knowledge_id: str | None,
    question: str,
    system_prompt: str,
    max_retries: int,
    initial_backoff: float,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        "stream": False,
    }
    if knowledge_id:
        payload["files"] = [{"type": "collection", "id": knowledge_id}]

    attempt = 0
    while True:
        try:
            response = requests.post(
                f"{base_url}/api/chat/completions",
                headers=api_headers(token),
                json=payload,
                timeout=300,
            )
            if response.status_code == 429:
                raise RuntimeError("429 rate limit")
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # noqa: BLE001
            attempt += 1
            if attempt > max_retries:
                raise RuntimeError(f"Falha apos {max_retries} retries: {exc}") from exc
            sleep_seconds = initial_backoff * (2 ** (attempt - 1)) + random.uniform(0, 1)
            print(f"  retry {attempt}/{max_retries} em {sleep_seconds:.1f}s por erro: {exc}")
            time.sleep(sleep_seconds)


def parse_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if not text:
        raise ValueError("Resposta vazia ao tentar interpretar JSON.")
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or start >= end:
            raise
        value = json.loads(text[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("O payload de avaliacao nao e um objeto JSON.")
    return value


def coerce_score(raw_value: Any, field_name: str) -> int:
    try:
        score = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} invalido: {raw_value!r}") from exc
    if score not in {0, 1, 2}:
        raise ValueError(f"{field_name} fora da escala 0-2: {score}")
    return score


def build_judge_prompt(rubric_text: str, question: str, answer: str) -> str:
    return (
        "Voce e um avaliador estrito de RAG.\n"
        "Aplique a rubrica abaixo para avaliar a resposta do assistente.\n"
        "Use apenas a escala 0, 1 ou 2 em cada criterio.\n"
        "Retorne somente um objeto JSON valido, sem markdown, sem comentarios extras.\n"
        "Campos obrigatorios do JSON: "
        "adherence_score, factual_score, source_focus_score, synthesis_score, "
        "hallucination_score, review_notes.\n"
        "review_notes deve ser uma string curta em portugues com os principais achados.\n\n"
        f"RUBRICA:\n{rubric_text.strip()}\n\n"
        f"PERGUNTA:\n{question.strip()}\n\n"
        f"RESPOSTA:\n{answer.strip()}\n"
    )


def judge_answer(
    base_url: str,
    token: str,
    model: str,
    rubric_text: str,
    question: str,
    answer: str,
    max_retries: int,
    initial_backoff: float,
) -> dict[str, Any]:
    judge_prompt = build_judge_prompt(rubric_text=rubric_text, question=question, answer=answer)
    response = ask_openwebui(
        base_url=base_url,
        token=token,
        model=model,
        knowledge_id="",
        question=judge_prompt,
        system_prompt=(
            "Voce eh um avaliador automatico. "
            "Responda apenas com JSON valido e estrito."
        ),
        max_retries=max_retries,
        initial_backoff=initial_backoff,
    )
    parsed = parse_json_object(extract_answer(response))
    adherence_score = coerce_score(parsed.get("adherence_score"), "adherence_score")
    factual_score = coerce_score(parsed.get("factual_score"), "factual_score")
    source_focus_score = coerce_score(parsed.get("source_focus_score"), "source_focus_score")
    synthesis_score = coerce_score(parsed.get("synthesis_score"), "synthesis_score")
    hallucination_score = coerce_score(parsed.get("hallucination_score"), "hallucination_score")
    review_notes = str(parsed.get("review_notes", "")).strip()
    return {
        "adherence_score": adherence_score,
        "factual_score": factual_score,
        "source_focus_score": source_focus_score,
        "synthesis_score": synthesis_score,
        "hallucination_score": hallucination_score,
        "total_score": (
            adherence_score
            + factual_score
            + source_focus_score
            + synthesis_score
            + hallucination_score
        ),
        "review_notes": review_notes,
        "judge_response": response,
    }


def write_markdown_summary(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = ["# RAG Eval Results", ""]
    for row in rows:
        lines.append(f"## {row['id']} - {row['category']}")
        lines.append("")
        lines.append(f"**Pergunta**: {row['question']}")
        lines.append("")
        lines.append("**Resposta**:")
        lines.append("")
        lines.append(row["answer"].strip() or "<vazio>")
        lines.append("")
        lines.append(f"**Status**: {row['status']}")
        if row.get("adherence_score", "") != "":
            lines.append("")
            lines.append(
                "**Metricas**: "
                f"aderencia={row['adherence_score']} | "
                f"precisao={row['factual_score']} | "
                f"fontes={row['source_focus_score']} | "
                f"sintese={row['synthesis_score']} | "
                f"confianca={row['hallucination_score']} | "
                f"total={row['total_score']}"
            )
        if row.get("review_notes"):
            lines.append("")
            lines.append(f"**Notas de revisao**: {row['review_notes']}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_csv_template(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "id",
        "category",
        "question",
        "execution_status",
        "answer",
        "adherence_score",
        "factual_score",
        "source_focus_score",
        "synthesis_score",
        "hallucination_score",
        "total_score",
        "review_notes",
    ]

    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "id": row["id"],
                    "category": row["category"],
                    "question": row["question"],
                    "execution_status": row["status"],
                    "answer": row["answer"],
                    "adherence_score": row.get("adherence_score", ""),
                    "factual_score": row.get("factual_score", ""),
                    "source_focus_score": row.get("source_focus_score", ""),
                    "synthesis_score": row.get("synthesis_score", ""),
                    "hallucination_score": row.get("hallucination_score", ""),
                    "total_score": row.get("total_score", ""),
                    "review_notes": row.get("review_notes", ""),
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa perguntas de avaliacao no Open WebUI com RAG.")
    parser.add_argument(
        "--questions-file",
        default="eval/discursos_questions.json",
        help="Arquivo JSON com as perguntas.",
    )
    parser.add_argument(
        "--knowledge-name",
        default="Discursos do plenário do Senado 2019-2023",
        help="Nome da Knowledge Base no Open WebUI.",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENWEBUI_EVAL_MODEL", "gpt-5-nano"),
        help="Modelo a usar via Open WebUI.",
    )
    parser.add_argument(
        "--judge-model",
        default=os.getenv("OPENWEBUI_JUDGE_MODEL", ""),
        help="Modelo para aplicar a rubrica. Default: reutiliza --model.",
    )
    parser.add_argument(
        "--rubric-file",
        default="eval/RUBRIC.md",
        help="Arquivo Markdown com a rubrica de avaliacao.",
    )
    parser.add_argument(
        "--no-auto-score",
        action="store_true",
        help="Nao preenche automaticamente as metricas no CSV.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Quantidade maxima de perguntas a executar. 0 = todas.",
    )
    parser.add_argument(
        "--sleep-between",
        type=float,
        default=3.0,
        help="Pausa entre perguntas.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=4,
        help="Retries para rate limit/erros transitorios.",
    )
    parser.add_argument(
        "--initial-backoff",
        type=float,
        default=5.0,
        help="Backoff inicial em segundos.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    base_url = require_env("OPENWEBUI_URL").rstrip("/")
    token = require_env("OPENWEBUI_API_KEY")
    questions_path = (project_root / args.questions_file).resolve()
    rubric_path = (project_root / args.rubric_file).resolve()
    questions = json.loads(questions_path.read_text(encoding="utf-8"))
    rubric_text = rubric_path.read_text(encoding="utf-8")
    judge_model = args.judge_model.strip() or args.model
    if args.limit > 0:
        questions = questions[: args.limit]

    knowledge_id = get_knowledge_id(base_url, token, args.knowledge_name)

    system_prompt = (
        "Responda usando prioritariamente o contexto recuperado. "
        "Nao invente fatos. Se nao encontrar a resposta no contexto, diga isso claramente. "
        "Responda em portugues e distribua citacoes ao longo da resposta quando aplicavel."
    )

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = project_root / "eval" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / f"rag_eval_{ts}.jsonl"
    md_path = output_dir / f"rag_eval_{ts}.md"
    csv_path = output_dir / f"rag_eval_{ts}.csv"

    rows: list[dict[str, Any]] = []
    with jsonl_path.open("w", encoding="utf-8") as jsonl_file:
        for index, item in enumerate(questions, start=1):
            print(f"[{index}/{len(questions)}] {item['id']} - {item['question']}")
            try:
                response = ask_openwebui(
                    base_url=base_url,
                    token=token,
                    model=args.model,
                    knowledge_id=knowledge_id,
                    question=item["question"],
                    system_prompt=system_prompt,
                    max_retries=args.max_retries,
                    initial_backoff=args.initial_backoff,
                )
                answer = extract_answer(response)
                row = {
                    "id": item["id"],
                    "category": item["category"],
                    "question": item["question"],
                    "answer": answer,
                    "status": "ok",
                    "response": response,
                }
                if not args.no_auto_score:
                    print(f"  avaliando com rubrica via modelo {judge_model}")
                    judge = judge_answer(
                        base_url=base_url,
                        token=token,
                        model=judge_model,
                        rubric_text=rubric_text,
                        question=item["question"],
                        answer=answer,
                        max_retries=args.max_retries,
                        initial_backoff=args.initial_backoff,
                    )
                    row.update(judge)
            except Exception as exc:  # noqa: BLE001
                row = {
                    "id": item["id"],
                    "category": item["category"],
                    "question": item["question"],
                    "answer": "",
                    "status": f"error: {exc}",
                    "response": None,
                    "review_notes": "",
                }
            rows.append(row)
            jsonl_file.write(json_dumps_compact(row) + "\n")
            jsonl_file.flush()
            time.sleep(args.sleep_between)

    write_markdown_summary(md_path, rows)
    write_csv_template(csv_path, rows)
    print(f"\nResultados salvos em:\n- {jsonl_path}\n- {md_path}\n- {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
