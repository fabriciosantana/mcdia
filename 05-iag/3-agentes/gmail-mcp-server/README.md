# Servidor MCP do Gmail

Este é um servidor Model Context Protocol (MCP) que permite enviar e-mails via Gmail.

## Pré-requisitos

1.  **Python 3.10+** instalado.
2.  Uma conta no **Google Cloud Console**.

## Configuração das Credenciais do Google

Para que o script funcione, você precisa de um arquivo `credentials.json` na mesma pasta do projeto:

1.  Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2.  Crie um novo projeto (ou selecione um existente).
3.  Vá em **APIs & Services > Library** e pesquise por **Gmail API**. Ative-a.
4.  Vá em **APIs & Services > OAuth consent screen**:
    *   Escolha **External**.
    *   Preencha as informações obrigatórias.
    *   Em **Scopes**, adicione `https://www.googleapis.com/auth/gmail.send`.
    *   Adicione seu próprio e-mail como **Test User**.
5.  Vá em **APIs & Services > Credentials**:
    *   Clique em **Create Credentials > OAuth client ID**.
    *   Selecione **Desktop App**.
    *   Baixe o JSON gerado e renomeie-o para `credentials.json` na pasta deste projeto.

## Como Executar

### 1. Instalar as dependências
Certifique-se de usar o ambiente python configurado:
```bash
pip install -r requirements.txt
```

### 2. Autenticação Inicial (Obrigatório)
Antes de conectar qualquer cliente MCP, você precisa autorizar o acesso à sua conta:
```bash
python main.py auth
```
*Isso abrirá uma janela do navegador. Após autorizar, o arquivo `token.json` será gerado automaticamente. Você só precisa fazer isso uma vez.*

### 3. Executando o Servidor

Você tem duas opções de transporte HTTP dependendo do seu cliente MCP:

#### Opção A: Modo STDIO (Claude Desktop / Cursor)
Execute sem argumentos para usar a comunicação via entrada/saída padrão:
```bash
python main.py
```
*Observação: O terminal ficará travado esperando conexões JSON-RPC. Isso é normal.*

#### Opção B: Modo SSE (Dify, chamadas HTTP)
Execute com o parâmetro `sse` para iniciar um servidor local na porta 8000:
```bash
python main.py sse
```
Endpoint padrão: `http://localhost:8000/sse`

> **Note para uso com Docker (Ex: Dify local):** Como o Dify roda em um container, ele não enxerga o `localhost` da sua máquina. Você deve usar a URL **`http://host.docker.internal:8000/sse`** no campo Endpoint do Dify. O servidor já está configurado (`host="0.0.0.0"`) para aceitar essa conexão externa.

## Uso com Docker

Se desejar executar o servidor MCP isolado ou conectá-lo ao Dify/outras ferramentas suportadas via rede, você pode usar os arquivos Docker disponíveis.

### Pré-requisito: Autenticação
É **obrigatório** possuir o `credentials.json` e ter gerado o `token.json` localmente **antes** de subir o container, pois o Docker mapeia esses arquivos como volumes para dentro da imagem.

> **⚠️ IMPORTANTE:** Se o arquivo `token.json` não existir no seu diretório local no momento em que o comando Docker for executado, o Docker criará automaticamente um **diretório vazio** com esse nome (em vez de um arquivo), o que causará erro no script Python.
> 
> **Solução:** Execute o passo `python main.py auth` no seu ambiente local primeiro. Se você não tiver o Python instalado localmente, pelo menos crie um arquivo vazio antes: `touch token.json` e `touch credentials.json`.

### Executando com Docker Compose (Recomendado)
```bash
docker-compose up -d
```
O servidor estará acessível via HTTP SSE na porta 8000 da sua máquina (`http://localhost:8000/sse` ou `http://host.docker.internal:8000/sse` dentro de outros containers como Dify).

### Executando com Docker puro
```bash
docker build -t gmail-mcp-server .
docker run -d --name gmail-mcp -p 8000:8000 \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  -v $(pwd)/token.json:/app/token.json \
  gmail-mcp-server
```

## Uso com MCP (Ex: Claude Desktop)

Adicione a seguinte configuração ao seu arquivo `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "python",
      "args": ["/Caminho/Absoluto/Para/Gmail MCP Server/main.py"],
      "env": {
        "PYTHONPATH": "/Caminho/Absoluto/Para/Gmail MCP Server"
      }
    }
  }
}
```
*(Nota: Certifique-se de alterar o comando e o caminho para o ambiente virtual de Python correto, se usar um conda/venv)*
