"""Auditoria de publicação: controles estruturais e completude temporal explícita."""
from pathlib import Path
import hashlib
import json
import platform
import re
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[1]
CONFIG = json.loads((RAIZ / 'config/regras_temporais.json').read_text())
UFS = 'AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO'.split()
MESES = {m:i+1 for i,m in enumerate('Janeiro Fevereiro Março Abril Maio Junho Julho Agosto Setembro Outubro Novembro Dezembro'.split())}
CHAVES = ['Ano', 'Mês', 'UF']

def ler():
    p = RAIZ / 'dados/brutos/arrecadacao-estado.csv'
    manifesto = json.loads((RAIZ / 'dados/proveniencia.json').read_text())
    for item in manifesto:
        arquivo = RAIZ / 'dados/brutos' / item['arquivo']
        if hashlib.sha256(arquivo.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError(f'Hash divergente: {arquivo}')
    return pd.read_csv(p, sep=';', encoding='latin1', dtype=str, keep_default_na=False)

def datas(df):
    return pd.to_datetime(dict(year=pd.to_numeric(df['Ano'], errors='coerce'),
        month=df['Mês'].map(MESES), day=1), errors='coerce')

def auditar(df):
    """Executa controles, sem corrigir valores nem preencher ausências."""
    requeridas = CHAVES + [r['coluna'] for r in CONFIG['regras']]
    if set(requeridas) - set(df.columns):
        raise ValueError('Colunas obrigatórias ausentes: '+str(set(requeridas)-set(df.columns)))
    df = df.reset_index(drop=True).copy()
    dt = datas(df)
    eventos = []
    def evento(i, regra, coluna='', valor=''):
        row = df.iloc[i] if i is not None else {}
        eventos.append(dict(linha_csv=i+2 if i is not None else None,
            ano=row.get('Ano',''), mes=row.get('Mês',''), uf=row.get('UF',''),
            regra=regra, coluna=coluna, valor=valor))
    for i in df.index[dt.isna()]: evento(i,'data_invalida')
    for i in df.index[~df.UF.isin(UFS)]: evento(i,'uf_invalida')
    for i in df.index[df.duplicated(CHAVES)]: evento(i,'chave_duplicada')
    recorte = dt.between(CONFIG['inicio_recorte'], CONFIG['fim_recorte']) & df.UF.isin(UFS)
    atual = set(zip(dt[recorte],df.loc[recorte,'UF']))
    esperado = {(d,u) for d in pd.date_range(CONFIG['inicio_recorte'],CONFIG['fim_recorte'],freq='MS') for u in UFS}
    for d,u in sorted(esperado-atual): evento(None,'chave_ausente',valor=f'{d:%Y-%m}/{u}')
    if df.loc[recorte].duplicated(CHAVES).any() or esperado-atual:
        painel_completo = False
    else: painel_completo = True
    # A publicação mistura convenções numéricas. Não convertemos valores:
    # reconhecer a sintaxe não resolve a ambiguidade decimal/milhar.
    formatos = []
    for c in df.columns.difference(CHAVES):
        x = df[c].str.strip()
        br=x.str.fullmatch(r'[+-]?(?:\d+|\d{1,3}(?:\.\d{3})+)(?:,\d+)?',na=False)
        en=x.str.fullmatch(r'[+-]?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?',na=False)
        invalidos = recorte & x.ne('') & ~(br|en)
        formatos.append(dict(coluna=c,apenas_convencao_br=int((recorte&br&~en).sum()),
            apenas_convencao_en=int((recorte&en&~br).sum()),
            separador_ambiguo=int((recorte&br&en&x.str.contains(r'[.,]')).sum())))
        for i in df.index[invalidos]: evento(i,'numero_invalido',c,df.at[i,c])
    linhas = []
    status = []
    for r in CONFIG['regras']:
        c = r['coluna']; preenchido = df[c].str.strip().ne('')
        aplica = dt.ge(r['inicio']) & (dt.le(r['fim']) if r['fim'] else True)
        faltas = recorte & aplica & ~preenchido
        extras = recorte & ~aplica & preenchido
        for i in df.index[faltas]: evento(i,'ausencia_aplicavel',c)
        for i in df.index[extras]: evento(i,'presenca_fora_intervalo',c,df.at[i,c])
        linhas.append(dict(coluna=c, celulas=int(recorte.sum()),
            aplicaveis=int((recorte&aplica).sum()),
            ausencias_ingenuas=int((recorte&~preenchido).sum()),
            ausencias_previstas=int((recorte&~aplica&~preenchido).sum()),
            ausencias_aplicaveis=int(faltas.sum()), presencas_fora_intervalo=int(extras.sum())))
        for i in df.index[recorte]:
            situacao = ('preenchida_aplicavel' if preenchido[i] else 'ausencia_aplicavel') if aplica[i] else ('presenca_fora_intervalo' if preenchido[i] else 'ausencia_prevista')
            status.append(dict(linha_csv=int(i+2), data=dt[i].strftime('%Y-%m'),uf=df.at[i,'UF'],coluna=c,situacao=situacao))
    tabela = pd.DataFrame(linhas)
    ocorrencias = pd.DataFrame(eventos, columns=['linha_csv','ano','mes','uf','regra','coluna','valor'])
    resumo = dict(registros_arquivo=len(df), colunas_arquivo=len(df.columns),
        registros_recorte=int(recorte.sum()), meses_recorte=len(pd.date_range(CONFIG['inicio_recorte'],CONFIG['fim_recorte'],freq='MS')), ufs=len(UFS),
        painel_completo=painel_completo, regras_temporais=len(linhas),
        celulas_avaliadas=int(tabela.celulas.sum()),
        celulas_aplicaveis=int(tabela.aplicaveis.sum()),
        ausencias_ingenuas=int(tabela.ausencias_ingenuas.sum()),
        ausencias_previstas=int(tabela.ausencias_previstas.sum()),
        ausencias_aplicaveis=int(tabela.ausencias_aplicaveis.sum()),
        presencas_fora_intervalo=int(tabela.presencas_fora_intervalo.sum()),
        ocorrencias=len(eventos),
        formatos_apenas_en=sum(f['apenas_convencao_en'] for f in formatos),
        formatos_ambiguos=sum(f['separador_ambiguo'] for f in formatos),
        regras_sha256=hashlib.sha256((RAIZ/'config/regras_temporais.json').read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    resumo['completude_ingenua_pct'] = 100*(1-resumo['ausencias_ingenuas']/resumo['celulas_avaliadas'])
    resumo['completude_condicionada_pct'] = 100*(1-resumo['ausencias_aplicaveis']/resumo['celulas_aplicaveis'])
    return resumo,tabela,ocorrencias,pd.DataFrame(status)

def main():
    resumo,tabela,eventos,status = auditar(ler())
    out=RAIZ/'resultados'; out.mkdir(exist_ok=True)
    fig=RAIZ/'figuras'; fig.mkdir(exist_ok=True)
    (out/'resumo.json').write_text(json.dumps(resumo,ensure_ascii=False,indent=2)+'\n')
    tabela.to_csv(out/'completude_por_coluna.csv',index=False)
    eventos.to_csv(out/'ocorrencias.csv',index=False)
    status.to_csv(out/'classificacao_celulas.csv',index=False)
    (out/'ambiente.json').write_text(json.dumps(dict(python=platform.python_version(),pandas=pd.__version__,matplotlib=matplotlib.__version__),indent=2)+'\n')
    # Macros geradas impedem transcrição manual dos resultados para o artigo.
    nomes={'registros_recorte':'NRegistros','meses_recorte':'NMeses','celulas_avaliadas':'NCelulas','celulas_aplicaveis':'NAplicaveis','ausencias_ingenuas':'NAusencias','ausencias_aplicaveis':'NLacunas','ocorrencias':'NOcorrencias','completude_ingenua_pct':'CIngenua','completude_condicionada_pct':'CCondicionada'}
    def fmt(v): return (f'{v:,.2f}' if isinstance(v,float) else f'{v:,}').replace(',','X').replace('.',',').replace('X','.')
    (out/'indicadores.tex').write_text('\n'.join('\\newcommand{\\'+n+'}{'+fmt(resumo[k])+'}' for k,n in nomes.items())+'\n')
    anual=status.assign(ano=status.data.str[:4]).groupby('ano').situacao.agg(total='size',previstas=lambda s:s.eq('ausencia_prevista').sum(),faltas=lambda s:s.eq('ausencia_aplicavel').sum(),aplicaveis=lambda s:s.isin(['preenchida_aplicavel','ausencia_aplicavel']).sum())
    anual.to_csv(out/'completude_por_ano.csv')
    plt.rcParams.update({'font.size':10})
    f,ax=plt.subplots(figsize=(9,2.7))
    ax.plot(anual.index.astype(int),100*(1-(anual.previstas+anual.faltas)/anual.total),label='Completude sem regra temporal',marker='o',markersize=3)
    ax.plot(anual.index.astype(int),100*(1-anual.faltas/anual.aplicaveis),label='Completude condicionada (9 colunas)',linestyle='--')
    ax.set(xlabel='Ano',ylabel='Completude (%)',ylim=(0,108),xticks=[2000,2004,2010,2015,2020,2025])
    ax.grid(alpha=.2); ax.legend(loc='lower right'); f.tight_layout()
    f.savefig(fig/'completude.pdf'); f.savefig(fig/'completude.png',dpi=160); plt.close(f)
    print(json.dumps(resumo,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
