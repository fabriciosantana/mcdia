# Tasks

## 1. Interface e dependência

- [x] 1.1 Fixar Streamlit em `requirements.txt` e verificar a instalação em ambiente virtual limpo.
- [x] 1.2 Criar função de parsing e validação de configurações JSON; verificar entradas válidas, inválidas e não objetuais.

## 2. Dashboard

- [x] 2.1 Criar o aplicativo Streamlit usando a API do registro; verificar a inicialização contra banco temporário.
- [x] 2.2 Implementar formulário de criação de execução e mensagens de erro; verificar que JSON inválido não cria registros.
- [x] 2.3 Implementar listagem, seleção e detalhes de execuções; verificar que artefatos e configuração aparecem na execução selecionada.
- [x] 2.4 Implementar ação de validação de integridade; verificar estados íntegro, alterado e removido.

## 3. Documentação e integração

- [x] 3.1 Documentar instalação e comando `streamlit run dashboard/app.py`; verificar que o comando está correto.
- [x] 3.2 Executar testes, compileall e `openspec validate --all`; registrar resultados e limites da interface.
