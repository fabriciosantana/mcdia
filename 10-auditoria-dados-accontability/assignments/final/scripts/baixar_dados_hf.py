"""Baixa o corpus de discursos diretamente do Hugging Face Hub."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download


REPO_ID = "fabriciosantana/discursos-senado-legislatura-56"
DESTINO_PADRAO = Path(__file__).resolve().parents[1] / "dados"


def sha256(arquivo: Path) -> str:
    resumo = hashlib.sha256()
    with arquivo.open("rb") as entrada:
        for bloco in iter(lambda: entrada.read(1024 * 1024), b""):
            resumo.update(bloco)
    return resumo.hexdigest()


def selecionar_parquet(arquivos: list[str], solicitado: str | None) -> str:
    parquets = sorted(nome for nome in arquivos if nome.lower().endswith(".parquet"))
    if solicitado:
        if solicitado not in parquets:
            raise ValueError(f"Arquivo Parquet não encontrado no dataset: {solicitado}")
        return solicitado
    if not parquets:
        raise RuntimeError("O dataset não contém arquivos Parquet.")
    if len(parquets) > 1:
        nomes = "\n  - ".join(parquets)
        raise RuntimeError(
            "Há mais de um Parquet disponível. Use --arquivo para escolher:\n"
            f"  - {nomes}"
        )
    return parquets[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arquivo", help="caminho do Parquet dentro do dataset")
    parser.add_argument("--destino", type=Path, default=DESTINO_PADRAO)
    args = parser.parse_args()

    info = HfApi().dataset_info(REPO_ID, files_metadata=True)
    nomes = [item.rfilename for item in info.siblings]
    arquivo_remoto = selecionar_parquet(nomes, args.arquivo)

    args.destino.mkdir(parents=True, exist_ok=True)
    cache = hf_hub_download(
        repo_id=REPO_ID,
        repo_type="dataset",
        filename=arquivo_remoto,
    )
    origem = Path(cache)
    destino = args.destino / Path(arquivo_remoto).name
    destino.write_bytes(origem.read_bytes())

    proveniencia = {
        "repo_id": REPO_ID,
        "revision": info.sha,
        "arquivo_remoto": arquivo_remoto,
        "url": f"https://huggingface.co/datasets/{REPO_ID}/resolve/{info.sha}/{arquivo_remoto}",
        "baixado_em_utc": datetime.now(timezone.utc).isoformat(),
        "arquivo_local": destino.name,
        "tamanho_bytes": destino.stat().st_size,
        "sha256": sha256(destino),
    }
    (args.destino / "proveniencia.json").write_text(
        json.dumps(proveniencia, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Dados salvos em: {destino}")
    print(f"Proveniência: {args.destino / 'proveniencia.json'}")


if __name__ == "__main__":
    main()

