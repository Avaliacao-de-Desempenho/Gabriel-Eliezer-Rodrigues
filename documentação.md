# 🚀 API de Processamento de Notas Fiscais com IA

## ✨ Visão Geral

Este projeto consiste em uma API RESTful desenvolvida com FastAPI, projetada para automatizar a extração e o processamento de dados de notas fiscais. Utiliza as capacidades avançadas de visão computacional e processamento de linguagem natural do modelo multimodal **Google Gemini 1.5-Flash** para extrair informações cruciais de documentos, sejam eles **imagens (JPG/PNG)** ou **arquivos PDF**. Os dados extraídos são então persistidos em um banco de dados **PostgreSQL**.

Ideal para soluções que requerem automação de tarefas financeiras, como categorização de despesas, auditoria de notas fiscais ou integração com sistemas contábeis.

## �� Funcionalidades Principais

*   **Extração Inteligente de Dados:** Utiliza o Google Gemini 1.5-Flash para extrair de forma precisa e estruturada (JSON) informações como Valor Total da Nota Fiscal, Data de Emissão e CNPJ do emissor.
*   **Suporte Abrangente a Documentos:** Processa nativamente tanto imagens (JPEG, PNG) quanto documentos PDF, sem a necessidade de conversão prévia manual do PDF para imagem.
*   **Persistência de Dados:** Salva os dados extraídos em um banco de dados PostgreSQL, com persistência garantida via Docker Volumes, para consulta e análise futuras.
*   **API RESTful:** Interface clara e bem definida com endpoints intuitivos para integração com outras aplicações.
*   **Documentação Interativa:** Inclui Swagger UI (`/docs`) e ReDoc (`/redoc`) para fácil exploração e teste dos endpoints da API.
*   **Containerização Completa:** O projeto é totalmente containerizado com Docker e Docker Compose, garantindo um ambiente de desenvolvimento e produção isolado, replicável e de fácil configuração.

## ��️ Tecnologias Utilizadas

*   **Backend:** Python 3.9+
*   **Framework Web:** [FastAPI](https://fastapi.tiangolo.com/)
*   **Servidor ASGI:** [Uvicorn](https://www.uvicorn.org/)
*   **Banco de Dados:** [PostgreSQL](https://www.postgresql.org/)
*   **Driver de Banco de Dados:** `psycopg2-binary`
*   **Modelo de IA:** [Google Gemini 1.5-Flash](https://ai.google.dev/models/gemini) (`google-generativeai`)
*   **Containerização:** [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/)
*   **Variáveis de Ambiente:** `python-dotenv`
*   **Processamento de Imagens:** `Pillow` (PIL) - *utilizado para operações internas, mas o Gemini 1.5-Flash processa imagens e PDFs diretamente.*
*   **Processamento de PDF (interno):** `PyPDF2` - *mantido para manipulações de PDF que não envolvem envio direto ao Gemini, mas o foco é o envio de PDF bruto ao modelo.*

## 📂 Estrutura do Projeto

.
├── app/
│   ├── api/
│   │   ├── endpoints.py # Definição dos endpoints da API (rotas).
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py # Configurações globais da aplicação (ex: variáveis de ambiente).
│   │   └── __init__.py
│   ├── db/
│   │   ├── database.py # Conexão com o banco de dados e criação da tabela.
│   │   └── __init__.py
│   ├── services/
│   │   ├── invoice_processor.py # Lógica principal de processamento com Gemini e persistência.
│   │   ├── __init__.py
│   │   └── pdf_converter.py # (Arquivo com pouca ou nenhuma implementação, pode ser removido ou expandido para outras conversões)
│   └── main.py # Ponto de entrada da aplicação FastAPI e ciclo de vida.
├── .env.example # Exemplo do arquivo de variáveis de ambiente.
├── Dockerfile # Define a imagem Docker para a aplicação FastAPI.
├── docker-compose.yml # Orquestração dos serviços Docker (API e Banco de Dados).
├── requirements.txt # Dependências Python do projeto.
└── README.md # Este arquivo de documentação.


## ⚡ Pré-requisitos

Antes de começar, certifique-se de ter o seguinte instalado em sua máquina:

*   **Docker Desktop:** (inclui Docker Engine e Docker Compose) instalado e em execução.
    *   [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)

### �� Obtenha sua Chave da API Gemini

1.  Acesse o [Google AI Studio](https://ai.google.dev/).
2.  Crie uma nova chave de API.
3.  Guarde essa chave, você precisará dela no próximo passo.

## ⚙️ Configuração do Projeto

1.  **Clone este repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd invoice_parser_api
    ```
    (Substitua `<URL_DO_SEU_REPOSITORIO>` pelo URL real do seu repositório Git.)

2.  **Crie o arquivo de variáveis de ambiente (`.env`):**
    *   Na raiz do projeto (`invoice_parser_api/`), crie um arquivo chamado `.env`.
    *   Copie o conteúdo de `.env.example` para `.env`.
    *   Preencha as variáveis com suas informações, especialmente a chave da API Gemini:

        ```dotenv
        GEMINI_API_KEY=SUA_CHAVE_DE_API_GEMINI_AQUI
        # Credenciais do Banco de Dados (podem ser mantidas como padrão para desenvolvimento)
        DB_NAME=invoicedb
        DB_USER=user
        DB_PASSWORD=password
        DB_HOST=db # 'db' é o nome do serviço no docker-compose.yml
        DB_PORT=5432
        ```

## 🚀 Como Rodar o Projeto

Com o Docker Desktop em execução e o arquivo `.env` configurado, você pode iniciar toda a aplicação com um único comando:

1.  **Construa as imagens Docker e inicie os contêineres:**
    *   No diretório raiz do projeto (`invoice_parser_api/`), execute o seguinte comando:
    ```bash
    docker compose up --build -d
    ```
    *   `--build`: Garante que as imagens Docker sejam construídas (ou reconstruídas se houver mudanças no `Dockerfile` ou dependências).
    *   `-d`: Roda os contêineres em modo "detached" (em segundo plano), liberando seu terminal. Para ver os logs, use `docker compose logs -f`.

2.  **Verifique se os contêineres estão rodando:**
    ```bash
    docker compose ps
    ```
    Você deverá ver os serviços `api` e `db` com status `running`.

3.  **Acesse a API:**
    *   Após a inicialização, a API estará acessível em: `http://localhost:8000`
    *   A documentação interativa (Swagger UI) estará disponível em: `http://localhost:8000/docs`
    *   Você também pode ver a documentação ReDoc em: `http://localhost:8000/redoc`

## 🧪 Testando a Extração de Notas Fiscais

1.  Acesse a documentação interativa em `http://localhost:8000/docs`.
2.  Expanda a rota `POST /invoice/process`.
3.  Clique em "Try it out".
4.  No campo `file`, clique em "Choose File" e selecione uma imagem (JPG/PNG) ou um arquivo PDF de uma nota fiscal.
5.  Clique no botão "Execute".
6.  A resposta da API deverá ser um JSON contendo os dados extraídos da nota fiscal (valor total, data de emissão, CNPJ) e o ID de registro no banco de dados.

### Exemplo de Teste com `curl`

Você pode usar `curl` para testar o endpoint diretamente. Substitua `path/to/your/invoice.jpg` (ou `.pdf`) pelo caminho real do arquivo em sua máquina:

```bash
# Para imagem JPG/PNG
curl -X POST \
  http://localhost:8000/invoice/process \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@path/to/your/invoice.jpg;type=image/jpeg'

# Para PDF
curl -X POST \
  http://localhost:8000/invoice/process \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@path/to/your/invoice.pdf;type=application/pdf'