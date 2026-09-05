"""Julga cegamente o pool com duas passagens de LLM e adjudicação automática."""

from __future__ import annotations

import json
import os
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Literal

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
from pydantic import BaseModel, Field
from sklearn.metrics import cohen_kappa_score


RAIZ = Path(__file__).resolve().parents[1]
MODELO = "gpt-5.4-mini-2026-03-17"
MAX_TRABALHADORES = 4
ARQUIVO_CHECKPOINT = RAIZ / "resultados/julgamentos_llm_checkpoint.jsonl"
TRAVA_ESCRITA = threading.Lock()


class Julgamento(BaseModel):
    relevancia: Literal[0, 1, 2] = Field(description="Grau de relevância conforme a rubrica")
    informacao_suficiente: bool
    confianca: Literal["baixa", "media", "alta"]
    justificativa: str = Field(max_length=500)
    evidencia: str = Field(max_length=500)


INSTRUCOES = """Você é um avaliador de recuperação de informação legislativa.
Julgue se o pronunciamento ajuda a responder à pergunta, usando apenas o material fornecido.

Rubrica obrigatória:
2 = diretamente relevante: contém informação que responde substancialmente ao aspecto específico.
1 = parcialmente relevante: trata do tema ou fornece contexto, mas não responde ao aspecto específico.
0 = não relevante: coincidência incidental, superficial ou assunto diferente.

Não presuma relevância pela identidade do autor, partido ou período. Não recompense mera repetição de
palavras da pergunta. Se o material não permitir decisão segura, marque informacao_suficiente=false,
confianca=baixa e atribua o rótulo mais conservador. Copie em evidencia uma passagem curta do material;
se não houver evidência, escreva "Nenhuma evidência suficiente"."""


def carregar_checkpoint() -> dict[str, dict]:
    resultados: dict[str, dict] = {}
    if not ARQUIVO_CHECKPOINT.exists():
        return resultados
    for linha in ARQUIVO_CHECKPOINT.read_text(encoding="utf-8").splitlines():
        if linha.strip():
            registro = json.loads(linha)
            resultados[registro["chave"]] = registro
    return resultados


def salvar_checkpoint(registro: dict) -> None:
    ARQUIVO_CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    with TRAVA_ESCRITA, ARQUIVO_CHECKPOINT.open("a", encoding="utf-8") as saida:
        saida.write(json.dumps(registro, ensure_ascii=False) + "\n")
        saida.flush()


def montar_entrada(linha: pd.Series, passagem: int, texto_amplo: str | None = None) -> str:
    material = texto_amplo if texto_amplo is not None else (
        f"RESUMO OFICIAL:\n{linha.get('resumo_oficial', '')}\n\n"
        f"TRECHO DO TEXTO INTEGRAL:\n{linha.get('trecho_texto_integral', '')}"
    )
    if passagem == 2:
        return f"DOCUMENTO CANDIDATO:\n{material}\n\nPERGUNTA:\n{linha['pergunta']}"
    return f"PERGUNTA:\n{linha['pergunta']}\n\nDOCUMENTO CANDIDATO:\n{material}"


def chamar_julgador(cliente: OpenAI, chave: str, entrada: str, tipo: str) -> dict:
    resposta = None
    for tentativa in range(8):
        try:
            resposta = cliente.responses.parse(
                model=MODELO,
                instructions=INSTRUCOES,
                input=entrada,
                text_format=Julgamento,
                reasoning={"effort": "none"},
                temperature=0,
                max_output_tokens=500,
                store=False,
            )
            break
        except RateLimitError:
            if tentativa == 7:
                raise
            time.sleep(min(30, 2**tentativa) + random.random())
    assert resposta is not None
    julgamento = resposta.output_parsed
    if julgamento is None:
        raise RuntimeError(f"Resposta não analisável para {chave}")
    uso = resposta.usage
    registro = {
        "chave": chave,
        "tipo": tipo,
        "modelo": MODELO,
        **julgamento.model_dump(),
        "input_tokens": getattr(uso, "input_tokens", None),
        "output_tokens": getattr(uso, "output_tokens", None),
        "response_id": resposta.id,
    }
    salvar_checkpoint(registro)
    return registro


def executar_pendentes(
    cliente: OpenAI,
    tarefas: list[tuple[str, str, str]],
    existentes: dict[str, dict],
) -> dict[str, dict]:
    pendentes = [(chave, entrada, tipo) for chave, entrada, tipo in tarefas if chave not in existentes]
    if not pendentes:
        return existentes
    with ThreadPoolExecutor(max_workers=MAX_TRABALHADORES) as executor:
        futuros = {
            executor.submit(chamar_julgador, cliente, chave, entrada, tipo): chave
            for chave, entrada, tipo in pendentes
        }
        concluidos = 0
        for futuro in as_completed(futuros):
            registro = futuro.result()
            existentes[registro["chave"]] = registro
            concluidos += 1
            if concluidos % 25 == 0 or concluidos == len(pendentes):
                print(f"{concluidos}/{len(pendentes)} julgamentos novos concluídos")
    return existentes


def main() -> None:
    load_dotenv(RAIZ / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY ausente no arquivo .env")
    pool_path = RAIZ / "resultados/pool_avaliacao.xlsx"
    pool = pd.read_excel(pool_path, sheet_name="Pool", dtype={"codigo_pronunciamento": str})
    parquets = sorted((RAIZ / "dados").glob("*.parquet"))
    if len(parquets) != 1:
        raise RuntimeError(f"Esperado exatamente um parquet: {parquets}")
    corpus = pd.read_parquet(parquets[0])
    textos = dict(zip(
        corpus["CodigoPronunciamento"].astype(str),
        corpus["TextoDiscursoIntegral"].fillna("").astype(str),
    ))
    cliente = OpenAI(max_retries=5, timeout=120.0)
    existentes = carregar_checkpoint()

    tarefas = []
    for _, linha in pool.iterrows():
        for passagem in (1, 2):
            chave = f"{linha['item_id']}|p{passagem}"
            tarefas.append((chave, montar_entrada(linha, passagem), f"passagem_{passagem}"))
    existentes = executar_pendentes(cliente, tarefas, existentes)

    adjudicar: list[tuple[str, str, str]] = []
    for _, linha in pool.iterrows():
        p1, p2 = existentes[f"{linha['item_id']}|p1"], existentes[f"{linha['item_id']}|p2"]
        precisa = (
            p1["relevancia"] != p2["relevancia"]
            or not p1["informacao_suficiente"]
            or not p2["informacao_suficiente"]
            or p1["confianca"] == "baixa"
            or p2["confianca"] == "baixa"
        )
        if precisa:
            texto = textos.get(str(linha["codigo_pronunciamento"]), "")[:30_000]
            entrada = montar_entrada(linha, 3, texto_amplo=f"TEXTO INTEGRAL (até 30 mil caracteres):\n{texto}")
            adjudicar.append((f"{linha['item_id']}|adj", entrada, "adjudicacao"))
    existentes = executar_pendentes(cliente, adjudicar, existentes)

    saida = pool.copy()
    registros_finais = []
    for _, linha in pool.iterrows():
        p1, p2 = existentes[f"{linha['item_id']}|p1"], existentes[f"{linha['item_id']}|p2"]
        adj = existentes.get(f"{linha['item_id']}|adj")
        final = adj or p1
        registros_finais.append({
            "llm_passagem_1": p1["relevancia"],
            "llm_passagem_2": p2["relevancia"],
            "divergencia_passagens": p1["relevancia"] != p2["relevancia"],
            "houve_adjudicacao": adj is not None,
            "relevancia_final": final["relevancia"],
            "confianca_final": final["confianca"],
            "informacao_suficiente_final": final["informacao_suficiente"],
            "justificativa_llm": final["justificativa"],
            "evidencia_llm": final["evidencia"],
            "modelo_julgador": MODELO,
        })
    saida = pd.concat([saida.reset_index(drop=True), pd.DataFrame(registros_finais)], axis=1)
    saida.to_csv(RAIZ / "resultados/pool_julgado_llm.csv", index=False)
    saida.to_excel(RAIZ / "resultados/pool_julgado_llm.xlsx", index=False)

    todos_registros = list(existentes.values())
    resumo = {
        "modelo": MODELO,
        "itens": len(saida),
        "concordancia_exata_passagens": float((saida["llm_passagem_1"] == saida["llm_passagem_2"]).mean()),
        "kappa_ponderado_quadratico": float(cohen_kappa_score(
            saida["llm_passagem_1"], saida["llm_passagem_2"], weights="quadratic"
        )),
        "divergencias": int(saida["divergencia_passagens"].sum()),
        "adjudicacoes": int(saida["houve_adjudicacao"].sum()),
        "distribuicao_rotulos": saida["relevancia_final"].value_counts().sort_index().to_dict(),
        "input_tokens": sum(item.get("input_tokens") or 0 for item in todos_registros),
        "output_tokens": sum(item.get("output_tokens") or 0 for item in todos_registros),
    }
    (RAIZ / "resultados/resumo_julgamento_llm.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
