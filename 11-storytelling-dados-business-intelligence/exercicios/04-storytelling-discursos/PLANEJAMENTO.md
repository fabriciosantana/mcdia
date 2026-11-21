# Planejamento — Vozes do Senado

Plano registrado antes da implementação. Público: estudantes, jornalistas e cidadãos interessados em explorar a 56ª legislatura. Pergunta: como o uso registrado da palavra varia no tempo, entre oradores e por assuntos?

## Etapas e entregáveis
1. Inspeção: consultar fontes primárias, card e metadados; identificar unidade de observação, cobertura e categorias.
2. Pipeline reproduzível: baixar revisão imutável do Parquet; verificar IDs, datas, valores ausentes, textos disponíveis e autores; gerar JSON compacto e manifesto com SHA-256. Não substituir dados reais por demonstrações.
3. Narrativa: contexto e indicadores; série mensal com denominador; distribuição entre oradores; assuntos detectados por regras transparentes; exploração dos resumos com link para o Senado.
4. Interface: HTML/CSS/JS sem build ou CDN, identidade editorial em português, telas responsivas, navegação por teclado, gráficos SVG com tabelas equivalentes; filtros de período, partido, UF, autor e tipo de pronunciamento; busca, reset e CSV.
5. Verificação: testes de integridade e agregação, testes reais de navegador, filtros combinados, vazio, exportação, links e tela móvel. Corrigir problemas observados e repetir os testes afetados até a primeira versão funcional.
6. Documentação: README de execução e atualização, metodologia, referências com escopo de consulta, auditoria e registro dos testes.

## Decisões analíticas
- O corpus, e não toda a atividade parlamentar, é a população descrita.
- Identificar categorias antes de definir o recorte inicial. Usar ID do parlamentar para evitar fragmentação de nomes.
- Barras com zero, denominadores explícitos e escalas identificadas; não comparar anos incompletos como completos.
- Temas por dicionários sobre resumo/indexação: multirrótulo e exploratório, sem inferir posicionamento ou sentimento.
- Frequência não mede produtividade, influência, tempo de fala ou qualidade. Não estimar legibilidade sem validação linguística.
- Textos e resumos são dados externos: renderizar como texto, nunca HTML executável.

## Skills avaliadas
- hf-cli e huggingface-datasets: descoberta e extração do corpus público.
- academic-research-suite: consulta dirigida e verificação de fontes; não é revisão sistemática nem revisão independente.
- sites: desenvolvimento e preview locais, sem publicação externa.
- imagegen, Gradio, treinamento e hospedagem: desnecessários para este dashboard estático.

## Critérios de conclusão
Corpus real disponível localmente; totais reconciliados; gráficos e texto respondem aos filtros; estado vazio e erro de carga tratados; origem e limites visíveis; navegação e exportação verificadas; comando simples de visualização documentado.

## Condições do checkout
Os documentos docs/agents/issue-tracker.md, triage-labels.md e domain.md citados pelo usuário não existem neste checkout. Arquivos preexistentes serão preservados. O sandbox falhou na criação de namespaces; comandos locais necessários usam a via de escalonamento autorizada pelo ambiente.

## Conclusão da primeira versão

Todas as seis etapas foram executadas. A auditoria definiu 12.414 pronunciamentos elegíveis e 4.045 discursos na visão inicial. O pipeline e a interface estão implementados e documentados. Seis testes analíticos e os cenários de navegador passaram após os ajustes registrados em VALIDACAO.md. A entrega é local, sem publicação externa. Limites remanescentes: classificação temática não validada por humanos, ausência de ajuste por mandato/sessão e nenhuma certificação de acessibilidade.
