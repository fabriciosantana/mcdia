# Contexto para retomada

Data: 5 de setembro de 2026.

Giovanni Brígido é Auditor-Fiscal da Receita Federal, conforme informação do
solicitante. Nome e órgão usados sem presumir especialidade ou lotação. E-mail
informado: `giovannibrigido@gmail.com`. Minuta depende de revisão do autor por exigência de
individualidade no guia. Não registrar a condição de saúde nos artefatos.

Tema escolhido: auditoria da completude temporal da arrecadação por UF.
O problema deriva de intervalos explícitos do dicionário oficial, evitando
interpretação de todo vazio como erro. Usa qualidade e cruzamento de dados,
uma das técnicas aceitas; não utiliza RAG nem exige chaves.

Os dados e o dicionário foram baixados diretamente do domínio da Receita e
congelados com hashes. Recorte 2000–2025: 8.424 linhas, 312 meses, 27 UFs;
75.816 células em nove colunas de Cofins, PIS/Pasep e CSLL; 46.656 aplicáveis;
29.160 ausências previstas. Completude simples 61,54%, temporal 100%; nenhuma
ocorrência nas regras. Há mistura de convenções numéricas, por isso os valores
permanecem como texto e não são usados em cálculos monetários.

Treze cenários controlados aprovados. Notebook executado. Artigo em LaTeX,
cinco páginas, cinco referências, citações azuis. Fonte Times equivalente,
12 pontos, margens 2,5 cm, espaçamento 1,15. PDF de revisão em
`revisao/minuta_giovanni_brigido.pdf`.

Consultar README, NOTA_METODOLOGICA e REVISAO_AUTOR. O usuário anterior já
submeteu seu trabalho em `../final`; não alterar aquele projeto.

Próximos passos: leitura/adaptação por Giovanni; confirmar condições
de apoio/autoria com a disciplina; recompilar e preparar versão para submissão.
