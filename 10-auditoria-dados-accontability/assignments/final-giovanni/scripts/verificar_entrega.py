"""Confere artefatos calculados, notebook, referências e PDF; informa pendências."""
from pathlib import Path
import json
import re
import subprocess
import pandas as pd
from analisar_qualidade import RAIZ, ler

def main():
    ler()  # hashes do CSV e do dicionário
    r=RAIZ/'resultados'
    resumo=json.loads((r/'resumo.json').read_text())
    celulas=pd.read_csv(r/'classificacao_celulas.csv')
    contagem=celulas.situacao.value_counts()
    assert len(celulas)==resumo['celulas_avaliadas']
    assert contagem.get('ausencia_prevista',0)==resumo['ausencias_previstas']
    assert contagem.get('ausencia_aplicavel',0)==resumo['ausencias_aplicaveis']
    aplicaveis=celulas.situacao.isin(['preenchida_aplicavel','ausencia_aplicavel']).sum()
    assert aplicaveis==resumo['celulas_aplicaveis']
    assert len(pd.read_csv(r/'ocorrencias.csv'))==resumo['ocorrencias']
    testes=pd.read_csv(r/'testes_controlados.csv')
    assert len(testes)==13 and testes.aprovado.all()
    tex=(RAIZ/'main.tex').read_text()
    bib=(RAIZ/'referencias.bib').read_text()
    citacoes={k for grupo in re.findall(r'\\cite(?:online)?\{([^}]+)\}',tex) for k in grupo.split(',')}
    referencias=set(re.findall(r'@\w+\{([^,]+),',bib))
    assert citacoes==referencias, 'Citações sem referência ou referências não citadas'
    nb=json.loads((RAIZ/'analise_arrecadacao.ipynb').read_text())
    assert all(c.get('execution_count') is not None for c in nb['cells'] if c['cell_type']=='code')
    assert not any(o.get('output_type')=='error' for c in nb['cells'] for o in c.get('outputs',[]))
    log=(RAIZ/'out/main.log').read_text(errors='replace')
    assert not re.search(r'undefined|multiply defined|Overfull|Underfull|LaTeX Warning',log,re.I), 'Rever log LaTeX'
    pdf=RAIZ/'out/main.pdf'
    info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
    paginas=int(re.search(r'Pages:\s+(\d+)',info)[1])
    assert 4<=paginas<=5, f'Paginação fora da interseção do guia: {paginas}'
    texto=subprocess.check_output(['pdftotext',str(pdf),'-'],text=True)
    assert 'Giovanni Brígido' in texto
    for numero in ['8.424','75.816','46.656','29.160','61,54','100,00']:
        assert numero in texto, f'Indicador ausente no PDF: {numero}'
    print(f'Validação técnica aprovada: {paginas} páginas, {len(referencias)} referências, 13 testes, notebook executado.')
    if 'a informar pelo autor' in tex:
        print('PENDÊNCIA DE ENTREGA: preencher e-mail e obter revisão do autor.')

if __name__=='__main__': main()
