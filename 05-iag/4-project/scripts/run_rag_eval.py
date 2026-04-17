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
import hashlib
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


def extract_answer(payload: Any) -> str:
    if payload is None:
        raise ValueError("Payload nulo retornado por /api/chat/completions.")
    if not isinstance(payload, dict):
        raise ValueError(f"Payload inesperado retornado por /api/chat/completions: {type(payload).__name__}")
    if "choices" in payload and payload["choices"]:
        message = payload["choices"][0].get("message") or {}
        content = message.get("content")
        if content is None:
            raise ValueError("Campo choices[0].message.content veio nulo.")
        return str(content)
    if "message" in payload and isinstance(payload["message"], dict):
        content = payload["message"].get("content")
        if content is None:
            raise ValueError("Campo message.content veio nulo.")
        return str(content)
    return json.dumps(payload, ensure_ascii=True)


def build_generation_messages(
    question: str,
    answer_prompt: str,
    answer_prompt_role: str,
) -> list[dict[str, str]]:
    if answer_prompt_role == "none":
        return [{"role": "user", "content": question}]

    if answer_prompt_role == "system":
        return [
            {"role": "system", "content": answer_prompt},
            {"role": "user", "content": question},
        ]

    if answer_prompt_role == "user_template":
        return [
            {
                "role": "user",
                "content": build_prompt_from_template(
                    answer_prompt,
                    {
                        "QUERY": question,
                        "question": question,
                    },
                ),
            }
        ]

    raise ValueError(f"answer_prompt_role invalido: {answer_prompt_role}")


def ask_openwebui(
    base_url: str,
    token: str,
    model: str,
    knowledge_id: str | None,
    messages: list[dict[str, str]],
    max_retries: int,
    initial_backoff: float,
    temperature: float | None = None,
    top_p: float | None = None,
    max_tokens: int | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    if temperature is not None:
        payload["temperature"] = temperature
    if top_p is not None:
        payload["top_p"] = top_p
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if seed is not None:
        payload["seed"] = seed
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
            if response.status_code >= 400:
                body = response.text.strip()
                body_excerpt = body[:2000] if body else "<vazio>"
                raise RuntimeError(
                    f"{response.status_code} error from /api/chat/completions: {body_excerpt}"
                )
            response.raise_for_status()
            data = response.json()
            if data is None:
                raise RuntimeError("Resposta nula retornada por /api/chat/completions.")
            if not isinstance(data, dict):
                raise RuntimeError(
                    "Resposta em formato inesperado retornada por /api/chat/completions: "
                    f"{type(data).__name__}"
                )
            return data
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


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def env_float(name: str) -> float | None:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    return float(raw)


def env_int(name: str) -> int | None:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    return int(raw)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def coerce_score(raw_value: Any, field_name: str) -> int:
    try:
        score = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} invalido: {raw_value!r}") from exc
    if score not in {0, 1, 2}:
        raise ValueError(f"{field_name} fora da escala 0-2: {score}")
    return score


def build_prompt_from_template(template: str, replacements: dict[str, str]) -> str:
    prompt = template
    for key, value in replacements.items():
        prompt = prompt.replace(f"{{{key}}}", value.strip())
    return prompt


def collect_knowledge_artifact_fingerprints(project_root: Path) -> dict[str, dict[str, Any]]:
    candidates = {
        "build_metadata": project_root / "knowledge_openwebui" / "build_metadata.json",
        "discursos_chunks": project_root / "knowledge_openwebui" / "discursos_chunks.jsonl",
    }
    snapshots: dict[str, dict[str, Any]] = {}
    for label, path in candidates.items():
        if path.exists():
            snapshots[label] = {
                "path": str(path),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }

    md_dir = project_root / "knowledge_openwebui" / "md_batches"
    if md_dir.exists():
        batch_files = sorted(md_dir.glob("batch_*.md"))
        snapshots["md_batches"] = {
            "path": str(md_dir),
            "file_count": len(batch_files),
            "sample_first_file": batch_files[0].name if batch_files else "",
            "sample_first_file_sha256": sha256_file(batch_files[0]) if batch_files else "",
        }

    return snapshots


def write_run_config(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def judge_answer(
    base_url: str,
    token: str,
    model: str,
    rubric_text: str,
    judge_system_prompt: str,
    judge_user_template: str,
    question: str,
    answer: str,
    max_retries: int,
    initial_backoff: float,
) -> dict[str, Any]:
    judge_prompt = build_prompt_from_template(
        template=judge_user_template,
        replacements={
            "rubric_text": rubric_text,
            "question": question,
            "answer": answer,
        },
    )
    response = ask_openwebui(
        base_url=base_url,
        token=token,
        model=model,
        knowledge_id="",
        messages=[
            {"role": "system", "content": judge_system_prompt},
            {"role": "user", "content": judge_prompt},
        ],
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
        "--answer-system-prompt-file",
        default="eval/prompts/rag_prompt.md",
        help="Arquivo de prompt usado na geracao. No protocolo A, este arquivo referencia o template RAG configurado no Open WebUI.",
    )
    parser.add_argument(
        "--answer-prompt-role",
        choices=("none", "system", "user_template"),
        default="none",
        help="Como aplicar o prompt de geracao. `none` reproduz melhor o fluxo padrao do Open WebUI, deixando o servidor aplicar o RAG_TEMPLATE configurado.",
    )
    parser.add_argument(
        "--judge-system-prompt-file",
        default="eval/prompts/rag_judge_system.md",
        help="Arquivo de prompt de sistema usado pelo juiz automatico.",
    )
    parser.add_argument(
        "--judge-user-prompt-file",
        default="eval/prompts/rag_judge_user.md",
        help="Template do prompt de usuario do juiz. Suporta {rubric_text}, {question} e {answer}.",
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
    parser.add_argument(
        "--temperature",
        type=float,
        default=env_float("RAG_EVAL_TEMPERATURE"),
        help="Temperatura enviada ao modelo gerador. Default: usar `RAG_EVAL_TEMPERATURE` se definido; caso contrario, usar o padrao do provedor.",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=env_float("RAG_EVAL_TOP_P"),
        help="Top-p enviado ao modelo gerador. Default: usar `RAG_EVAL_TOP_P` se definido; caso contrario, usar o padrao do provedor.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=env_int("RAG_EVAL_MAX_TOKENS"),
        help="Limite de tokens de saida para o modelo gerador. Default: usar `RAG_EVAL_MAX_TOKENS` se definido.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=env_int("RAG_EVAL_SEED"),
        help="Seed enviada ao modelo gerador, quando suportado. Default: usar `RAG_EVAL_SEED` se definido.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    base_url = require_env("OPENWEBUI_URL").rstrip("/")
    token = require_env("OPENWEBUI_API_KEY")
    questions_path = (project_root / args.questions_file).resolve()
    rubric_path = (project_root / args.rubric_file).resolve()
    answer_system_prompt_path = (project_root / args.answer_system_prompt_file).resolve()
    judge_system_prompt_path = (project_root / args.judge_system_prompt_file).resolve()
    judge_user_prompt_path = (project_root / args.judge_user_prompt_file).resolve()
    questions = json.loads(questions_path.read_text(encoding="utf-8"))
    rubric_text = rubric_path.read_text(encoding="utf-8")
    answer_system_prompt = load_text(answer_system_prompt_path)
    judge_system_prompt = load_text(judge_system_prompt_path)
    judge_user_template = load_text(judge_user_prompt_path)
    judge_model = args.judge_model.strip() or args.model
    if args.limit > 0:
        questions = questions[: args.limit]

    knowledge_id = get_knowledge_id(base_url, token, args.knowledge_name)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = project_root / "eval" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / f"rag_eval_{ts}.jsonl"
    md_path = output_dir / f"rag_eval_{ts}.md"
    csv_path = output_dir / f"rag_eval_{ts}.csv"
    config_path = output_dir / f"rag_eval_{ts}.run_config.json"

    run_config = {
        "protocol_variant": "A",
        "executed_at_utc": ts,
        "openwebui_base_url": base_url,
        "knowledge_name": args.knowledge_name,
        "knowledge_id": knowledge_id,
        "questions_file": {
            "path": str(questions_path),
            "sha256": sha256_file(questions_path),
            "count": len(questions),
        },
        "generator": {
            "model": args.model,
            "prompt_file": str(answer_system_prompt_path),
            "prompt_sha256": sha256_file(answer_system_prompt_path),
            "prompt_text_sha256": sha256_text(answer_system_prompt),
            "prompt_application_role": args.answer_prompt_role,
            "prompt_application_note": (
                "No modo `none`, o script nao injeta o template como mensagem; "
                "ele assume que o Open WebUI aplicara o RAG_TEMPLATE configurado no servidor."
            ),
            "temperature": args.temperature,
            "top_p": args.top_p,
            "max_tokens": args.max_tokens,
            "seed": args.seed,
        },
        "judge": {
            "model": judge_model,
            "system_prompt_file": str(judge_system_prompt_path),
            "system_prompt_sha256": sha256_file(judge_system_prompt_path),
            "user_prompt_file": str(judge_user_prompt_path),
            "user_prompt_sha256": sha256_file(judge_user_prompt_path),
            "same_model_as_generator": judge_model == args.model,
            "auto_score_enabled": not args.no_auto_score,
        },
        "rubric": {
            "path": str(rubric_path),
            "sha256": sha256_file(rubric_path),
        },
        "knowledge_artifacts": collect_knowledge_artifact_fingerprints(project_root),
    }
    write_run_config(config_path, run_config)

    rows: list[dict[str, Any]] = []
    with jsonl_path.open("w", encoding="utf-8") as jsonl_file:
        for index, item in enumerate(questions, start=1):
            print(f"[{index}/{len(questions)}] {item['id']} - {item['question']}")
            try:
                generation_messages = build_generation_messages(
                    question=item["question"],
                    answer_prompt=answer_system_prompt,
                    answer_prompt_role=args.answer_prompt_role,
                )
                response = ask_openwebui(
                    base_url=base_url,
                    token=token,
                    model=args.model,
                    knowledge_id=knowledge_id,
                    messages=generation_messages,
                    max_retries=args.max_retries,
                    initial_backoff=args.initial_backoff,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    max_tokens=args.max_tokens,
                    seed=args.seed,
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
                        judge_system_prompt=judge_system_prompt,
                        judge_user_template=judge_user_template,
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
    print(f"\nResultados salvos em:\n- {jsonl_path}\n- {md_path}\n- {csv_path}\n- {config_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
