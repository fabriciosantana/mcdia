"""Congela CSV e dicionário públicos da RFB, sem autenticação."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import requests

RAIZ = Path(__file__).resolve().parents[1]
FONTES = {
    'arrecadacao-estado.csv': 'https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv',
    'arrecadacao-estado-metadados.pdf': 'https://www.gov.br/receitafederal/dados/arrecadacao-estado-metadados.pdf',
}

def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    pasta = RAIZ / 'dados/brutos'
    pasta.mkdir(parents=True, exist_ok=True)
    manifesto = RAIZ / 'dados/proveniencia.json'
    if manifesto.exists():
        registros = json.loads(manifesto.read_text())
        for item in registros:
            p = pasta / item['arquivo']
            if not p.exists() or sha256(p) != item['sha256']:
                raise ValueError(f'Cópia congelada ausente ou alterada: {p}')
        print('Cópia congelada verificada; nenhum download necessário.')
        return
    registros = []
    for nome, url in FONTES.items():
        p = pasta / nome
        if p.exists():
            raise FileExistsError(f'Arquivo sem manifesto: {p}; inspecione antes de prosseguir.')
        r = requests.get(url, timeout=90)
        r.raise_for_status()
        if nome.endswith('.pdf') and not r.content.startswith(b'%PDF'):
            raise ValueError('Resposta não é PDF')
        if nome.endswith('.csv') and not r.content.startswith(b'Ano;'):
            raise ValueError('Cabeçalho CSV inesperado')
        p.write_bytes(r.content)
        registros.append(dict(arquivo=nome, url=url, url_final=r.url,
            coletado_em_utc=datetime.now(timezone.utc).isoformat(),
            sha256=sha256(p), bytes=len(r.content),
            last_modified=r.headers.get('Last-Modified')))
    manifesto.write_text(json.dumps(registros, ensure_ascii=False, indent=2)+'\n')
    print('CSV e dicionário congelados em dados/brutos/.')

if __name__ == '__main__':
    main()
