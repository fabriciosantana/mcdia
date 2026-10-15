# Análise H1–H3 e pacote de evidências

## ADDED Requirements

### Requirement: Protocolo analítico congelado
O sistema SHALL registrar decisões H1–H3, grupos, contrastes, regra para parcial/não respondível, pesos kappa, bootstrap, exclusões e desfechos antes da análise confirmatória. Alterações SHALL ser versionadas e identificadas como posteriores.

#### Scenario: Iniciar análise
- **WHEN** faltam definição de grupos ou regra de respondibilidade
- **THEN** a interface apresenta pendências e não produz decisão automática de hipótese

### Requirement: Resultados vinculados às hipóteses
O sistema SHALL produzir matriz H1 com casos e afirmações, contrastes H2 por grupos/dimensões e concordância H3 por avaliador/rodada, incluindo falsos positivos/negativos definidos no protocolo. Estatísticas SHALL informar denominadores, faltantes e não aplicáveis.

#### Scenario: Inspecionar H1 e H2
- **WHEN** o operador abre um grupo ou célula
- **THEN** é possível navegar aos pares pergunta–resposta e evidências; perguntas sem gold não entram em Hit como zero

### Requirement: Incerteza e concordância
O sistema SHALL calcular kappa ordinal com pesos declarados e resultado não estimável quando o denominador for zero. Bootstrap SHALL respeitar unidade pergunta e pareamento entre condições, sem tratar repetições como novas perguntas independentes.

#### Scenario: Amostra constante ou repetida
- **WHEN** notas são constantes ou existem repetições de uma pergunta
- **THEN** acordo exato continua disponível, kappa pode ser não estimável e intervalos identificam a unidade de reamostragem

### Requirement: Exportação e restauração
O sistema SHALL disponibilizar download de tabelas LaTeX/CSV, relatório e pacote de auditoria com referências às versões SQLite/Chroma, hashes, código, configurações e histórico; SHALL ocultar segredos e identidade dos avaliadores. Backup consistente SHALL restaurar vínculos e resultados.

#### Scenario: Exportar evidência final
- **WHEN** uma campanha elegível é concluída
- **THEN** tabelas compilam em documento LaTeX mínimo, totais reconciliam com SQLite e a restauração em ambiente limpo reproduz métricas sem nova geração
