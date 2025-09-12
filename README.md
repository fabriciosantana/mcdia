# mcdia

Este repositório contém subrepositórios relacionados ao projeto MCDIA:

## Subrepositórios

### mcdia-python ✅
- **Status**: Adicionado com sucesso
- **URL**: git@github.com:fabriciosantana/mcdia-python.git
- **Diretório**: `mcdia-python/`

### mcdia-nivelamento ✅
- **Status**: Adicionado com sucesso
- **URL**: git@github.com:fabriciosantana/mcdia-nivelamento.git
- **Diretório**: `mcdia-nivelamento/`

## Como trabalhar com subrepositórios

### Pré-requisitos
Os subrepositórios estão configurados para acesso via SSH. Certifique-se de ter configurado sua chave SSH no GitHub:

1. [Gerar uma chave SSH](https://docs.github.com/pt/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
2. [Adicionar a chave SSH ao GitHub](https://docs.github.com/pt/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)

### Comandos básicos

Para clonar este repositório com todos os subrepositórios:
```bash
git clone --recursive git@github.com:fabriciosantana/mcdia.git
```

Para atualizar os subrepositórios:
```bash
git submodule update --init --recursive
```