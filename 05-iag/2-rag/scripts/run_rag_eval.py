#!/usr/bin/env python3
"""Executa perguntas de avaliacao contra uma knowledge collection do Open WebUI.

Salva:
- JSONL com resposta completa
- Markdown resumido para revisao humana
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


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
    knowledge_id: str,
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
        "files": [{"type": "collection", "id": knowledge_id}],
        "stream": False,
    }

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
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


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
    questions = json.loads(questions_path.read_text(encoding="utf-8"))
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
            except Exception as exc:  # noqa: BLE001
                row = {
                    "id": item["id"],
                    "category": item["category"],
                    "question": item["question"],
                    "answer": "",
                    "status": f"error: {exc}",
                    "response": None,
                }
            rows.append(row)
            jsonl_file.write(json.dumps(row, ensure_ascii=True) + "\n")
            jsonl_file.flush()
            time.sleep(args.sleep_between)

    write_markdown_summary(md_path, rows)
    print(f"\nResultados salvos em:\n- {jsonl_path}\n- {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
