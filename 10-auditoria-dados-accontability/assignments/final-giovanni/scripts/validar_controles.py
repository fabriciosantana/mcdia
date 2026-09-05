"""Testes controlados em cópias; o CSV original nunca é alterado."""
import pandas as pd
from analisar_qualidade import RAIZ, auditar, ler

def main():
    original=ler()
    resultados=[]
    antigo=original.index[(original.Ano=='2003')&(original['Mês']=='Dezembro')&(original.UF=='AC')][0]
    novo=original.index[(original.Ano=='2004')&(original['Mês']=='Janeiro')&(original.UF=='AC')][0]
    casos=[
        ('sem_mutacao',None,None,None,set()),
        ('nulo_aplicavel',novo,'COFINS - FINANCEIRAS','',{'ausencia_aplicavel'}),
        ('valor_fora_intervalo',novo,'COFINS','123',{'presenca_fora_intervalo'}),
        ('numero_invalido',novo,'COFINS - FINANCEIRAS','texto',{'numero_invalido'}),
        ('mes_invalido',novo,'Mês','Mes13',{'data_invalida','chave_ausente'}),
        ('uf_invalida',novo,'UF','XX',{'uf_invalida','chave_ausente'}),
        ('zero_legitimo',novo,'COFINS - FINANCEIRAS','0',set()),
        ('milhar_decimal',novo,'COFINS - FINANCEIRAS','1.234,56',set()),
        ('sinal_negativo',novo,'COFINS - FINANCEIRAS','-123,45',set()),
        ('limite_dezembro_2003',antigo,'COFINS','',{'ausencia_aplicavel'}),
        ('limite_janeiro_2004',novo,'CSLL - DEMAIS','',{'ausencia_aplicavel'}),
        ('duplicacao',novo,None,None,{'chave_duplicada'}),
        ('remocao_registro',novo,None,None,{'chave_ausente'}),
    ]
    for nome,i,c,v,esperado in casos:
        copia=original.copy()
        if nome=='duplicacao': copia=pd.concat([copia,copia.loc[[i]]],ignore_index=True)
        elif nome=='remocao_registro': copia=copia.drop(index=i).reset_index(drop=True)
        elif c: copia.at[i,c]=v
        _,_,ocorrencias,_=auditar(copia)
        observado=set(ocorrencias.regra)
        ok=observado==esperado
        resultados.append(dict(cenario=nome,esperado=';'.join(sorted(esperado)),observado=';'.join(sorted(observado)),aprovado=ok))
    saida=pd.DataFrame(resultados)
    saida.to_csv(RAIZ/'resultados/testes_controlados.csv',index=False)
    print(saida.to_string(index=False))
    if not saida.aprovado.all(): raise AssertionError('Falha em teste controlado')
    print(f'{len(saida)} cenários aprovados. Isto não estima acurácia operacional.')

if __name__=='__main__': main()
