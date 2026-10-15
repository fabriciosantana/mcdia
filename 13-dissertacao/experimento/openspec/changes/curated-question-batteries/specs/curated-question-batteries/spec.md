# Baterias e referências de curadoria

## ADDED Requirements

### Requirement: Integridade da pergunta
O sistema SHALL separar respondibilidade de elegibilidade experimental, normalizar booleanos explicitamente e preservar campos omitidos em edições parciais. A categoria parcial SHALL permanecer pendente de decisão documentada para sua projeção binária.

#### Scenario: Editar pergunta existente
- **WHEN** o operador altera somente o texto ou importa a string 0
- **THEN** graus, autores, categorias secundárias e proveniência são preservados e a string 0 não se torna verdadeira

### Requirement: Conjunto de referência
O sistema SHALL manter julgamentos por pergunta, versão de chunk, grau 0/1/2, suficiência, anotador, justificativa e revisão; não julgado SHALL ser diferente de irrelevante.

#### Scenario: Validar pergunta
- **WHEN** o operador solicita validação
- **THEN** pergunta respondível exige evidência suficiente existente na versão escolhida; não respondível exige justificativa e escopo de busca documentados; nenhum item é validado automaticamente

### Requirement: Baterias versionadas
O sistema SHALL administrar baterias, membros e divisões piloto/avaliação final, congelando revisões e distribuição por categoria, ano, tamanho e tipo de fonte quando aplicável.

#### Scenario: Registrar o piloto existente
- **WHEN** o piloto de 24 itens é importado por proveniência
- **THEN** IDs P são mapeados aos D por origem, sem duplicar perguntas, preservando os dois itens por categoria e relatando ausência de metadados

### Requirement: Imutabilidade e administração
O sistema SHALL permitir criar, revisar, arquivar e restaurar perguntas e baterias; revisões após congelamento SHALL originar nova versão sem modificar snapshots de execuções anteriores.

#### Scenario: Revisar depois de executar
- **WHEN** uma referência do catálogo é corrigida
- **THEN** o resultado anterior conserva o gold original e eventual recálculo recebe versão e justificativa próprias
