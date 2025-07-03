# 🚀 API de Processamento de Notas Fiscais

Uma API em Python (FastAPI) para extrair dados (Valor Total, Data de Emissão, CNPJ) de imagens ou PDFs de notas fiscais usando a API Google Gemini, salvando-os em um banco de dados PostgreSQL. Tudo orquestrado localmente com Docker Compose.

## ✨ Funcionalidades

*   Recebe arquivos JPG, PNG ou PDF de notas fiscais.
*   Utiliza a API Google Gemini Pro Vision para reconhecimento e extração de dados.
*   Salva o Valor Total, Data de Emissão e CNPJ em um banco de dados PostgreSQL.
*   Retorna os dados extraídos em formato JSON.
*   Todos os serviços (API e DB) são executados em contêineres Docker.
*   Persistência de dados do PostgreSQL garantida via Docker Volumes.

## ��️ Tecnologias Utilizadas

*   **Python 3.12**
*   **FastAPI**
*   **Uvicorn**
*   **Google Gemini API** (`google-generativeai`)
*   **PostgreSQL**
*   **Docker**
*   **Docker Compose**
*   **`python-dotenv`**
*   **`psycopg2-binary`**
*   **`PyPDF2`**, **`Pillow`** (para pré-processamento de arquivos, se necessário)

## ⚡ Pré-requisitos

Antes de começar, certifique-se de ter o seguinte instalado em sua máquina:

*   **Python 3.12**
*   **pip** (gerenciador de pacotes do Python)
*   **Docker Desktop** (inclui Docker Engine e Docker Compose)
    *   [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 🔑 Obtenha sua Chave da API Gemini

1.  Acesse o [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Crie uma nova chave de API.
3.  Guarde essa chave, você precisará dela no próximo passo.

## ⚙️ Configuração do Projeto

1.  **Clone este repositório (ou crie a estrutura de pastas manualmente):**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd invoice_parser_api
    ```
2.  **Crie o arquivo de variáveis de ambiente (`.env`):**
    Na raiz do projeto (`invoice_parser_api/`), crie um arquivo chamado `.env` e adicione o seguinte conteúdo, substituindo `SUA_CHAVE_API_DO_GEMINI` pela chave que você obteve:

    ```dotenv
    GEMINI_API_KEY="SUA_CHAVE_API_DO_GEMINI"
    DB_NAME="invoice_db"
    DB_USER="user"
    DB_PASSWORD="password"
    DB_HOST="db"
    DB_PORT="5432"
    ```

## 🚀 Como Rodar o Projeto

Com o Docker Desktop em execução e o arquivo `.env` configurado, você pode iniciar toda a aplicação com um único comando:

1.  **Construa as imagens Docker e inicie os contêineres:**
    No diretório raiz do projeto (`invoice_parser_api/`), execute:
    ```bash
    docker compose up --build -d
    ```
    *   `--build`: Garante que as imagens Docker sejam construídas (ou reconstruídas se houver mudanças).
    *   `-d`: Roda os contêineres em modo "detached" (em segundo plano).

2.  **Verifique se os contêineres estão rodando:**
    ```bash
    docker compose ps
    ```
    Você deverá ver os serviços `app` e `db` com status `running`.

3.  **Acesse a API:**
    A API estará disponível em: `http://localhost:8000`
    Você pode testar o endpoint principal: `http://localhost:8000/`

## 🧪 Testando a API

Você pode usar ferramentas como [Postman](https://www.postman.com/downloads/) ou `curl` para testar a API.

### Endpoint: `/invoice/process` (POST)

*   **URL:** `http://localhost:8000/invoice/process`
*   **Método:** `POST`
*   **Header:** `Content-Type: multipart/form-data`
*   **Body:** `form-data` com um campo `file` do tipo `File`, onde você fará o upload da sua imagem (.jpg, .jpeg, .png) de nota fiscal.

**Exemplo com `curl` (substitua `path/to/your/invoice.jpg` pelo caminho real):**

```bash
curl -X POST \
  http://localhost:8000/invoice/process \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@path/to/your/invoice.jpg;type=image/jpeg'