# Tasks

## 1. Estrutura e dependências

- [x] 1.1 Criar o módulo Python do registro, o diretório de migrações e a configuração de caminhos; verificar a estrutura com `python -m compileall`.
- [x] 1.2 Fixar as dependências mínimas em um arquivo próprio do subprojeto; verificar a instalação em ambiente limpo.

## 2. Persistência relacional

- [x] 2.1 Implementar a criação versionada do banco SQLite com tabelas de execuções, configurações e artefatos; verificar a criação em banco temporário.
- [x] 2.2 Implementar criação de execução com UUID, estado, timestamps e hash de configuração; verificar os cenários de sucesso e configuração ausente.
- [x] 2.3 Implementar registro imutável de configuração serializada; verificar que configurações repetidas preservam hashes e execuções distintas.
- [x] 2.4 Implementar associação de artefatos com tipo, caminho e hash; verificar rejeição de arquivos inexistentes.

## 3. Consultas e integridade

- [x] 3.1 Implementar listagem e consulta detalhada de execuções; verificar a ordenação e os campos retornados.
- [x] 3.2 Implementar validação de hashes de configurações e artefatos; verificar detecção de arquivo alterado ou removido.
- [x] 3.3 Criar um comando de demonstração que registre uma execução sintética e produza um relatório JSON; verificar que o relatório é reproduzível.

## 4. Integração documental

- [x] 4.1 Documentar o esquema, os comandos e o layout de artefatos no README do subprojeto; verificar que os comandos documentados executam em uma instalação limpa.
- [x] 4.2 Registrar no OpenSpec os resultados dos testes e os limites da primeira versão; verificar `openspec validate --all`.
