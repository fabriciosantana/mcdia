# Design

## Context

O registro experimental expõe operações Python para inicializar o banco, criar execuções, consultar detalhes e validar hashes. O dashboard deve ser apenas uma camada de apresentação sobre essa API.

## Goals / Non-Goals

**Goals:**

- Permitir uso local por um pesquisador sem edição manual de arquivos.
- Reutilizar o banco e as regras de integridade existentes.
- Manter a interface simples, legível e adequada ao piloto.
- Tornar erros de entrada explícitos e não destrutivos.

**Non-Goals:**

- Autenticação, acesso remoto ou implantação pública.
- Execução de modelos, recuperação, geração ou avaliação dentro desta mudança.
- Alteração do esquema relacional.

## Decisions

1. **Streamlit:** escolhido por oferecer uma interface local rápida e adequada a um protótipo de pesquisa, sem criar uma API e um frontend separados.
2. **Camada fina:** o aplicativo chamará `experiment_registry` e não executará SQL diretamente; isso evita duplicar regras e preserva a possibilidade de trocar a interface.
3. **JSON explícito:** a configuração será informada em uma área de texto e validada antes da criação da execução, mantendo a serialização compatível com a API.
4. **Banco selecionável por variável de ambiente:** o dashboard usará `EXPERIMENTO_ROOT`, preservando o layout local e permitindo testes em diretório temporário.

## Risks / Trade-offs

- [Dependência adicional] → fixar Streamlit em `requirements.txt` e manter o CLI independente.
- [Estado de sessão] → recarregar a lista após operações e tratar o banco como fonte de verdade.
- [Uso indevido remoto] → documentar que o dashboard é local e não possui autenticação.
