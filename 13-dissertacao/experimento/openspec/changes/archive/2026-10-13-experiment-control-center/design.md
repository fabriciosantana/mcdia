# Desenho

A interface usa quatro abas: visão geral, configurações, experimentos e questões/respostas. Cada ação chama as APIs existentes do registro; não há SQL de domínio duplicado no dashboard.

A migração 004 cria `configuration_profiles`, com JSON canônico e hash. A aba Experimentos chama `run_retrieval` e `generate_responses`; a aba Questões e respostas chama `record_human_evaluation`. O modelo é lido do campo `OPENAI_MODEL` quando não informado na tela.

A geração de respostas é uma ação explícita, porque pode consumir a API configurada. O dashboard reporta falhas de validação e mantém a validação de integridade dos artefatos.

