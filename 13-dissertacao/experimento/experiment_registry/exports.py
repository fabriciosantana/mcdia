"""Exportação determinística de resultados para auditoria e redação."""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


def _escape_latex(value) -> str:
    text = "" if value is None else str(value)
    return text.replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")


def export_run(connection, outputs: str | Path, run_id: str) -> dict[str, str]:
    output_dir = Path(outputs); output_dir.mkdir(parents=True, exist_ok=True)
    metric = connection.execute("SELECT * FROM retrieval_metrics WHERE run_id=?", (run_id,)).fetchone()
    if metric is None:
        raise ValueError(f"execução sem métricas de recuperação: {run_id}")
    rows = [dict(row) for row in connection.execute("SELECT question_id,query,reference_doc_ids_json,respondible FROM questions WHERE run_id=? ORDER BY question_id", (run_id,))]
    metric_path = output_dir / f"{run_id}-metrics.csv"
    with metric_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(dict(metric).keys())); writer.writeheader(); writer.writerow(dict(metric))
    questions_path = output_dir / f"{run_id}-questions.csv"
    with questions_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()) if rows else ["question_id"]); writer.writeheader(); writer.writerows(rows)
    fields = ["run_id", "method", "recall_at_1", "recall_at_5", "recall_at_10", "precision_at_5", "hit_at_5", "mrr", "ndcg_at_5"]
    tex_path = output_dir / f"{run_id}-metrics.tex"
    values = [f"\\texttt{{{_escape_latex(dict(metric).get(field))}}}" if field == "run_id" else _escape_latex(dict(metric).get(field)) for field in fields]
    lines = [
        "% Gerado em " + datetime.now(timezone.utc).isoformat(),
        "% run_id: " + run_id,
        r"\begin{tabular}{lr}", r"\toprule", "Métrica & Valor \\", r"\midrule",
    ]
    lines.extend(("{} & {} ".format(_escape_latex(field), value) + "\\\\") for field, value in zip(fields[1:], values[1:]))
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    tex_path.write_text("\n".join(lines), encoding="utf-8")
    manifest = output_dir / f"{run_id}-export.json"
    manifest.write_text(json.dumps({"run_id": run_id, "generated_at": datetime.now(timezone.utc).isoformat(), "files": [str(metric_path), str(questions_path), str(tex_path)]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"metrics": str(metric_path), "questions": str(questions_path), "latex": str(tex_path), "manifest": str(manifest)}
