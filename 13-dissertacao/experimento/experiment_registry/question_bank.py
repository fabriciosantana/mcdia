"""Catálogo persistente e curadoria de perguntas no SQLite."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def _json(value: Any, default: Any) -> str:
    if value is None or value == "":
        value = default
    if isinstance(value, str):
        if value.startswith("[") or value.startswith("{"):
            try:
                json.loads(value)
                return value
            except json.JSONDecodeError:
                pass
        value = [item.strip() for item in value.split(";") if item.strip()]
    return json.dumps(value, ensure_ascii=False)


def _list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except json.JSONDecodeError:
            pass
        return [item.strip() for item in value.split(";") if item.strip()]
    return [str(item) for item in value]


def _row(row) -> dict[str, Any]:
    result = dict(row)
    for field in ("secondary_categories_json", "expected_authors_json", "reference_doc_ids_json", "reference_chunk_ids_json", "relevance_judgments_json"):
        result[field.removesuffix("_json")] = json.loads(result.pop(field) or ("{}" if "judgments" in field else "[]"))
    result["respondible"] = bool(result["respondible"])
    return result


def list_catalog(connection, status: str | None = None) -> list[dict[str, Any]]:
    if status:
        rows = connection.execute("SELECT * FROM question_catalog WHERE status=? ORDER BY question_id", (status,))
    else:
        rows = connection.execute("SELECT * FROM question_catalog WHERE status <> 'arquivada' ORDER BY question_id")
    return [_row(row) for row in rows]


def get_catalog_question(connection, question_id: str) -> dict[str, Any] | None:
    row = connection.execute("SELECT * FROM question_catalog WHERE question_id=?", (question_id,)).fetchone()
    return _row(row) if row else None


def save_catalog_question(connection, question: dict[str, Any]) -> str:
    question_id = str(question.get("question_id", "")).strip()
    query = str(question.get("query", "")).strip()
    category = str(question.get("category", "")).strip()
    status = str(question.get("status", "rascunho")).strip().lower()
    if not question_id or not query or not category:
        raise ValueError("question_id, pergunta e categoria são obrigatórios")
    if status not in {"rascunho", "revisar", "validada", "arquivada"}:
        raise ValueError("status de pergunta inválido")
    def truth(value):
        if isinstance(value,str):
            normalized=value.strip().lower()
            if normalized in {"0","false","no","nao","não",""}: return False
            if normalized in {"1","true","yes","sim"}: return True
            raise ValueError("elegibilidade deve ser um booleano explícito")
        if value not in (True,False,0,1): raise ValueError("elegibilidade deve ser um booleano")
        return bool(value)
    old=get_catalog_question(connection,question_id)
    merged=dict(old or {})
    merged.update({key:value for key,value in question.items() if value is not None})
    merged.update({"question_id":question_id,"query":query,"category":category,"status":status})
    for field in ("secondary_categories","expected_authors","reference_doc_ids","reference_chunk_ids","relevance_judgments"):
        if field not in question and old:
            merged[field]=old[field]
    # Elegibilidade responde “pode entrar no estudo”; respondibilidade é o rótulo gold.
    eligible=truth(merged.get("eligible",True))
    answerability=str(merged.get("answerability") or "sim").strip().lower()
    respondible_value=merged.get("respondible", answerability not in {"nao","não","not_respondible"})
    with connection:
        connection.execute(
            """INSERT INTO question_catalog(
                question_id,source_question_id,query,category,source_category,secondary_categories_json,
                difficulty,answerability,respondible,expected_authors_json,reference_doc_ids_json,
                reference_chunk_ids_json,relevance_judgments_json,expected_answer_criteria,evaluation_risks,
                status,curation_notes,source_file,eligible
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(question_id) DO UPDATE SET source_question_id=excluded.source_question_id,
                query=excluded.query,category=excluded.category,source_category=excluded.source_category,
                secondary_categories_json=excluded.secondary_categories_json,difficulty=excluded.difficulty,
                answerability=excluded.answerability,respondible=excluded.respondible,
                expected_authors_json=excluded.expected_authors_json,reference_doc_ids_json=excluded.reference_doc_ids_json,
                reference_chunk_ids_json=excluded.reference_chunk_ids_json,relevance_judgments_json=excluded.relevance_judgments_json,
                expected_answer_criteria=excluded.expected_answer_criteria,evaluation_risks=excluded.evaluation_risks,
                status=excluded.status,curation_notes=excluded.curation_notes,source_file=excluded.source_file,
                updated_at=CURRENT_TIMESTAMP,eligible=excluded.eligible""",
            (question_id, merged.get("source_question_id"), query, category, merged.get("source_category"), _json(merged.get("secondary_categories"), []),
             merged.get("difficulty"), answerability, int(truth(respondible_value)), _json(merged.get("expected_authors"), []), _json(merged.get("reference_doc_ids"), []),
             _json(merged.get("reference_chunk_ids"), []), _json(merged.get("relevance_judgments"), {}), merged.get("expected_answer_criteria"), merged.get("evaluation_risks"), status,
             merged.get("curation_notes"), merged.get("source_file"),int(eligible)),
        )
        revision=connection.execute("SELECT current_revision FROM question_catalog WHERE question_id=?",(question_id,)).fetchone()[0]
        if answerability in {"parcial","partially_respondible"}:
            connection.execute("UPDATE question_catalog SET pending_review=COALESCE(pending_review,'Definir regra documentada para converter respondibilidade parcial em rótulo binário.') WHERE question_id=?",(question_id,))
        elif question.get("answerability") is not None:
            connection.execute("UPDATE question_catalog SET pending_review=NULL WHERE question_id=?",(question_id,))
        current_status=connection.execute("SELECT status FROM question_catalog WHERE question_id=?",(question_id,)).fetchone()[0]
        if current_status=="validada" and connection.execute("SELECT 1 FROM question_validation WHERE question_id=? AND question_revision=? LIMIT 1",(question_id,revision)).fetchone() is None:
            raise ValueError("validação requer decisão, evidência/escopo e justificativa registrados para a revisão atual")
        connection.execute("INSERT OR REPLACE INTO question_revisions(question_id,revision,question_json,change_reason) VALUES (?,?,?,?)",(question_id,revision,json.dumps(merged,ensure_ascii=False,sort_keys=True),question.get("change_reason", "catalog edit" if old else "initial import")))
    return question_id


def seed_question_catalog(connection, source: str | Path, overwrite: bool = False) -> int:
    """Importa uma vez o catálogo derivado; a operação normal passa a ser SQLite."""
    path = Path(source)
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("o arquivo inicial de perguntas deve conter uma lista JSON")
    if overwrite:
        with connection:
            connection.execute("DELETE FROM question_catalog")
    inserted = 0
    for record in records:
        if not get_catalog_question(connection, record.get("question_id", "")):
            imported=dict(record)
            answerability=str(imported.get("answerability", "")).strip().lower()
            if answerability in {"nao", "não", "not_respondible"}:
                imported["respondible"] = False
            imported.setdefault("eligible", True)
            if answerability in {"parcial", "partially_respondible"}:
                imported["status"] = "revisar"
            save_catalog_question(connection, imported)
            inserted += 1
    return inserted


def catalog_questions_for_run(connection, question_ids: Iterable[str] | None = None) -> list[dict[str, Any]]:
    params: list[str] = []
    query = "SELECT * FROM question_catalog WHERE status='validada' AND eligible=1"
    if question_ids is not None:
        ids = [str(item) for item in question_ids]
        if not ids:
            return []
        query += " AND question_id IN (" + ",".join("?" for _ in ids) + ")"
        params.extend(ids)
    query += " ORDER BY question_id"
    return [_row(row) for row in connection.execute(query, params)]


def add_reference_chunk(connection, question_id: str, chunk_set_id: str, chunk_id: str, grade: int, sufficient: bool, annotator: str, justification: str, review_state: str="draft") -> str:
    if grade not in (0,1,2) or isinstance(grade,bool): raise ValueError("grau de relevância deve ser 0, 1 ou 2")
    if not annotator.strip() or not justification.strip(): raise ValueError("anotador e justificativa são obrigatórios")
    q=get_catalog_question(connection,question_id)
    if not q: raise ValueError(f"pergunta inexistente: {question_id}")
    if connection.execute("SELECT 1 FROM document_chunks WHERE chunk_set_id=? AND chunk_id=?",(chunk_set_id,chunk_id)).fetchone() is None: raise ValueError("chunk não existe na segmentação selecionada")
    reference_id=str(__import__('uuid').uuid4())
    with connection:
        connection.execute("INSERT INTO question_reference_chunks(reference_id,question_id,question_revision,chunk_set_id,chunk_id,relevance_grade,sufficient,annotator,justification,review_state) VALUES (?,?,?,?,?,?,?,?,?,?)",(reference_id,question_id,q["current_revision"],chunk_set_id,chunk_id,grade,int(bool(sufficient)),annotator.strip(),justification.strip(),review_state))
    return reference_id


def validate_catalog_question(connection, question_id: str, chunk_set_id: str, decision: str, rationale: str, search_scope: str, validator: str) -> None:
    q=get_catalog_question(connection,question_id)
    if not q: raise ValueError("pergunta inexistente")
    if decision not in {"respondible","partially_respondible","not_respondible"}: raise ValueError("decisão de respondibilidade inválida")
    if not rationale.strip() or not search_scope.strip() or not validator.strip(): raise ValueError("justificativa, escopo de busca e avaliador são obrigatórios")
    canonical={"respondible":"sim","partially_respondible":"parcial","not_respondible":"nao"}[decision]
    if str(q.get("answerability") or "").lower() not in {canonical,decision}:
        raise ValueError(f"rótulo atual ({q.get('answerability')}) difere da decisão; atualize a pergunta antes de validar")
    refs=connection.execute("SELECT COUNT(*) FROM question_reference_chunks WHERE question_id=? AND question_revision=? AND chunk_set_id=? AND relevance_grade>0 AND sufficient=1 AND review_state IN ('validated','adjudicated')",(question_id,q["current_revision"],chunk_set_id)).fetchone()[0]
    if decision=="respondible" and refs==0: raise ValueError("pergunta respondível precisa de evidência suficiente validada")
    with connection:
        connection.execute("INSERT OR REPLACE INTO question_validation(question_id,question_revision,chunk_set_id,decision,rationale,search_scope,validated_by) VALUES (?,?,?,?,?,?,?)",(question_id,q["current_revision"],chunk_set_id,decision,rationale.strip(),search_scope.strip(),validator.strip()))
        binary_projection=q["respondible"] if decision=="partially_respondible" else int(decision=="respondible")
        connection.execute("UPDATE question_catalog SET respondible=?,status='validada',pending_review=?,updated_at=CURRENT_TIMESTAMP WHERE question_id=?",(int(binary_projection),"Respondibilidade parcial: projeção binária mantida conforme catálogo e pendente de regra analítica explícita." if decision=="partially_respondible" else None,question_id))


def create_battery(connection,name: str,purpose: str="",battery_id: str|None=None,parent_battery_id:str|None=None) -> str:
    import uuid
    battery_id=battery_id or str(uuid.uuid4())
    if not name.strip(): raise ValueError("nome da bateria é obrigatório")
    with connection: connection.execute("INSERT INTO question_batteries(battery_id,name,purpose,parent_battery_id) VALUES (?,?,?,?)",(battery_id,name.strip(),purpose.strip(),parent_battery_id))
    return battery_id


def add_battery_member(connection,battery_id: str,question_id: str,source_member_id: str|None=None,split: str="pilot",position: int=0) -> None:
    q=get_catalog_question(connection,question_id)
    if not q: raise ValueError(f"pergunta inexistente: {question_id}")
    with connection:
        connection.execute("INSERT INTO question_revisions(question_id,revision,question_json,change_reason) VALUES (?,?,?,?) ON CONFLICT DO NOTHING",(question_id,q["current_revision"],json.dumps(q,ensure_ascii=False),"battery snapshot"))
        connection.execute("INSERT INTO battery_members(battery_id,question_id,question_revision,source_member_id,split,position) VALUES (?,?,?,?,?,?)",(battery_id,question_id,q["current_revision"],source_member_id,split,position))


def freeze_battery(connection,battery_id: str,chunk_set_id: str) -> None:
    rows=connection.execute("SELECT question_id,question_revision FROM battery_members WHERE battery_id=?",(battery_id,)).fetchall()
    if not rows: raise ValueError("bateria vazia")
    if not chunk_set_id: raise ValueError("selecione a segmentação da bateria")
    for row in rows:
        if connection.execute("SELECT 1 FROM question_validation WHERE question_id=? AND question_revision=? AND chunk_set_id=?",(row['question_id'],row['question_revision'],chunk_set_id)).fetchone() is None:
            raise ValueError(f"pergunta {row['question_id']} ainda não foi validada para esta segmentação")
    with connection:
        connection.execute("UPDATE question_batteries SET chunk_set_id=?,state='frozen',frozen_at=CURRENT_TIMESTAMP WHERE battery_id=?",(chunk_set_id,battery_id))


def import_pilot_battery(connection, source: str|Path, battery_name: str="Piloto da dissertação — 24 perguntas") -> dict[str,Any]:
    """Mapeia IDs P para perguntas existentes por source_question_id sem duplicá-las."""
    records=json.loads(Path(source).read_text(encoding="utf-8"))
    if not isinstance(records,list): raise ValueError("arquivo piloto precisa conter uma lista")
    existing=connection.execute("SELECT battery_id FROM question_batteries WHERE name=?",(battery_name,)).fetchone()
    if existing:
        return {"battery_id":existing[0],"inserted":0,"mapped":connection.execute("SELECT COUNT(*) FROM battery_members WHERE battery_id=?",(existing[0],)).fetchone()[0],"unmatched":[]}
    bid=create_battery(connection,battery_name,"Bateria piloto importada por proveniência; itens ainda sujeitos à validação.")
    unmatched=[]; mapped=0;missing={};distribution={}
    by_source={str(r["source_question_id"]).strip().lower():r["question_id"] for r in connection.execute("SELECT source_question_id,question_id FROM question_catalog WHERE source_question_id IS NOT NULL")}
    by_id={str(r["question_id"]).strip().lower():r["question_id"] for r in connection.execute("SELECT question_id FROM question_catalog")}
    for position,item in enumerate(records,1):
        for field in ("source_category","expected_authors","reference_doc_ids","reference_chunk_ids","expected_answer_criteria"):
            if item.get(field) in (None,""): missing[field]=missing.get(field,0)+1
        category=str(item.get("category") or "sem categoria");distribution[category]=distribution.get(category,0)+1
        source_id=str(item.get("source_question_id","")).strip().lower()
        qid=by_source.get(source_id) or by_id.get(source_id)
        if not qid:
            unmatched.append({"pilot_id":item.get("question_id"),"source_question_id":item.get("source_question_id"),"reason":"pergunta de origem não encontrada no catálogo"}); continue
        add_battery_member(connection,bid,qid,str(item.get("question_id","")),"pilot",int(item.get("pilot_position",position)))
        mapped+=1
    return {"battery_id":bid,"inserted":mapped,"mapped":mapped,"unmatched":unmatched,"source_count":len(records),"category_distribution":distribution,"missing_metadata_counts":missing}

def clone_battery(connection,battery_id:str,name:str)->str:
    source=connection.execute("SELECT * FROM question_batteries WHERE battery_id=?",(battery_id,)).fetchone()
    if not source: raise ValueError("bateria inexistente")
    if not name.strip(): raise ValueError("nome da nova versão obrigatório")
    new_id=create_battery(connection,name,source['purpose'],parent_battery_id=battery_id)
    with connection:
        connection.execute("INSERT INTO battery_members(battery_id,question_id,question_revision,source_member_id,split,position) SELECT ?,question_id,question_revision,source_member_id,split,position FROM battery_members WHERE battery_id=?",(new_id,battery_id))
    return new_id
