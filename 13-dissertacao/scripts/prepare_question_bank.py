#!/usr/bin/env python3
"""Normaliza a bateria v4 para o protocolo da dissertação."""
from __future__ import annotations
import argparse, csv, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

CATEGORY_MAP = {
    "factual_simple": "factual",
    "author_focus": "foco_autor",
    "author_disambiguation": "desambiguacao",
    "negative_evidence": "evidencia_negativa",
    "comparison": "comparacao_autores",
    "temporal_comparison": "comparacao_temporal",
    "numeric": "pergunta_numerica",
    "synthesis": "sintese_tematica",
    "multi_hop": "multiplas_etapas",
    "cross_author_confusion": "autoria_cruzada",
    "scope_control": "controle_escopo",
    "context_limits": "controle_escopo",
    "retrieval_stress": "estresse_recuperacao",
    "broad_multifocal": "sintese_tematica",
    "hallucination_trap": "controle_escopo",
    "citation_source_verification": "controle_escopo",
}
PRIMARY = ("factual", "foco_autor", "desambiguacao", "evidencia_negativa", "comparacao_autores", "comparacao_temporal", "pergunta_numerica", "sintese_tematica", "multiplas_etapas", "autoria_cruzada", "controle_escopo", "estresse_recuperacao")
DIFFICULTY = {"easy": 0, "medium": 1, "hard": 2}
ANSWERABILITY = {"yes": "sim", "partial": "parcial", "no": "nao"}

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def corpus_ids(path: Path) -> set[str]:
    try:
        import pandas as pd
        return set(pd.read_parquet(path, columns=["id"])["id"].astype(str))
    except Exception:
        return set()

def normalize(source: dict, local_id: str, source_path: Path) -> dict:
    source_category = source["category"]
    primary = CATEGORY_MAP[source_category]
    answerability = ANSWERABILITY[source["answerable"]]
    return {
        "question_id": local_id,
        "source_question_id": source["id"],
        "query": source["question"],
        "category": primary,
        "source_category": source_category,
        "secondary_categories": ";".join(source.get("secondary_categories", [])),
        "difficulty": source.get("difficulty", ""),
        "answerability": answerability,
        "respondible": "1" if answerability in {"sim", "parcial"} else "0",
        "expected_authors": ";".join(source.get("expected_authors", [])),
        "reference_doc_ids": ";".join(str(x) for x in source.get("relevant_sources_hint", [])),
        "reference_chunk_ids": "",
        "relevance_judgments": "",
        "expected_answer_criteria": source.get("expected_answer_criteria", ""),
        "evaluation_risks": source.get("evaluation_risks", ""),
        "status": "rascunho",
        "curation_notes": "Importada da bateria v4; documentos e trechos ainda precisam de validação humana.",
        "source_file": str(source_path),
    }

def select_pilot(rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        groups[row["category"]].append(row)
    selected = []
    for category in PRIMARY:
        candidates = groups[category]
        if not candidates:
            raise ValueError(f"categoria sem perguntas: {category}")
        yes = [r for r in candidates if r["answerability"] == "sim"]
        non_yes = [r for r in candidates if r["answerability"] != "sim"]
        chosen = []
        if yes:
            chosen.append(sorted(yes, key=lambda r: (DIFFICULTY.get(r["difficulty"], 9), r["source_question_id"]))[0])
        if non_yes:
            chosen.append(sorted(non_yes, key=lambda r: (DIFFICULTY.get(r["difficulty"], 9), r["source_question_id"]))[0])
        for candidate in sorted(candidates, key=lambda r: (DIFFICULTY.get(r["difficulty"], 9), r["source_question_id"])):
            if len(chosen) >= 2: break
            if candidate not in chosen: chosen.append(candidate)
        for index, row in enumerate(chosen[:2], 1):
            item = dict(row)
            item["question_id"] = f"P{len(selected)+1:03d}"
            item["pilot_position"] = str(index)
            selected.append(item)
    return selected

def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else ["question_id"]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("/workspaces/mcdia/06-inteligencia-artificial-generativa/4-project/eval/discursos_questions_v4_200.json"))
    parser.add_argument("--corpus", type=Path, default=Path("dados/data/full/discursos_2019-02-01_2023-01-31.parquet"))
    parser.add_argument("--output-dir", type=Path, default=Path("dados/piloto"))
    args = parser.parse_args()
    source = args.source.resolve()
    raw = json.loads(source.read_text(encoding="utf-8"))
    if len(raw) != 200 or len({item["id"] for item in raw}) != 200:
        raise ValueError("a fonte v4 precisa conter 200 IDs únicos")
    rows = [normalize(item, f"D{i:03d}", source) for i, item in enumerate(raw, 1)]
    missing = sorted({ref for row in rows for ref in row["reference_doc_ids"].split(";") if ref} - corpus_ids(args.corpus.resolve()))
    if missing:
        raise ValueError(f"IDs ausentes no corpus: {missing[:10]}")
    pilot = select_pilot(rows)
    source_hash = sha256(source)
    manifest = {
        "version": "1.0",
        "source": str(source),
        "source_sha256": source_hash,
        "corpus": str(args.corpus.resolve()),
        "corpus_sha256": sha256(args.corpus.resolve()),
        "canonical_count": len(rows),
        "pilot_count": len(pilot),
        "primary_categories": list(PRIMARY),
        "canonical_category_counts": dict(Counter(row["category"] for row in rows)),
        "pilot_category_counts": dict(Counter(row["category"] for row in pilot)),
        "status_policy": "rascunho; nenhuma pergunta foi validada automaticamente",
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "banco_perguntas_dissertacao_v1.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "bateria_piloto_dissertacao_24_v1.json").write_text(json.dumps(pilot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(args.output_dir / "banco_perguntas_dissertacao_v1.csv", rows)
    write_csv(args.output_dir / "bateria_piloto_dissertacao_24_v1.csv", pilot)
    (args.output_dir / "banco_perguntas_dissertacao_v1.manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

