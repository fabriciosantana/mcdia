# Checklist de entrega

## Conferência pela rubrica

- **Clareza e relevância do problema (25%)**: o problema está delimitado como
  dificuldade de localizar e comparar pronunciamentos em grande corpus textual;
  público-alvo, natureza assistiva e limites de uso estão explícitos.
- **Adequação metodológica e técnica (35%)**: o artigo descreve aquisição,
  auditoria, segmentação, TF--IDF, embeddings, RRF, avaliação em item conhecido,
  pool de relevância e LLM como juiz. O notebook e os scripts reproduzem o fluxo.
- **Viabilidade de dados e governança (15%)**: fonte, cobertura, ausências,
  duplicidades, período, hash, LAI e LGPD estão documentados.
- **Impacto e resultados (15%)**: há métricas para três métodos, tabela
  comparativa, benefícios operacionais e limitações de recuperação, geração e
  julgamento automatizado.
- **Estrutura, clareza e formatação (10%)**: PDF em A4 com cinco páginas, Times
  New Roman equivalente, corpo 12, referências 11, margens de 2,5 cm,
  espaçamento 1,15 e referências no padrão autor-data da ABNT.

## Validação técnica

```bash
python scripts/verificar_consistencia_artigo.py
latexmk -pdf main.tex
```

Os comandos devem terminar sem erro. O PDF esperado está em `out/main.pdf`.

## Arquivo para submissão

- `entrega/trabalho_final_fabricio_santana.pdf`

O canal da disciplina solicita somente o PDF. Não enviar `.env`, cache de
embeddings, checkpoint do LLM ou o Parquet local. Esses itens permanecem
necessários apenas para reprodução no ambiente de trabalho.
