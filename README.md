## SEMANA 1: Analizador de documentos via IA
### Objetivo: Integrar API FastAPI com API do Gemini 
**02/07 - 04/07**
- **Backlog Semanal**
    - Estruturar arquivos do Projeto✅
    - Organizar ferramentas que serão utilizadas ✅
    - criar uma interface simples para upload imagem ✅
    - Fazer a integração com a API do Gemini ✅
    - Criar e Configurar Dockerfile e docker-compose.yml ✅
    - Documentação do projeto![image](https://github.com/user-attachments/assets/80c27c04-a8e6-4120-a9d7-8f5a59df81a2)
    - Testar aplicação.![image](https://github.com/user-attachments/assets/90b6c8fe-0f22-4c4f-bd9c-bd1bafd7a3ab)


- **Resultado Esperado**
    - Criar a API com a integração com o Gemini, receber imagens e obter um retorno do Gemini.
      - **02/07** - Inicialmente estou criando a estrutura do projeto e ja estruturando ele para trabalhar no docker, pretendo que o projeto esteja aceitando imagens e pdf e obtendo um retorno o Gemini até o fim da semana.
        - **Evolução**: 45%
        - **TODO**: Desenvolver a estrutura do projeto, criar a API FastpAPI, receber imagem, integrar com gemini e receber um retorno. 

- **Dúvidas do Aluno/Impedimentos Encontrados**
    - \<DÚVIDAS\>

- **Questões para o Aluno**
    - \<QUESTÕES\>

- **Respostas das Questões**
    - \<RESPOSTAS\>

## SEMANA 2: \<NOME DO PROJETO\>
### Objetivo: \<OBJETIVO DA SEMANA\>
**07/07 - 11/07**
- **Backlog Semanal**
    - \<QUEBRAR O OBJETIVO DA SEMANA EM PARTES MENORES\>

- **Resultado Esperado**
    - \<QUAL ENTREGÁVEL SERÁ PRODUZIDO QUANDO O OBJETIVO FOR ALCANÇADO (FINAL DA SEMANA)\>
    - Evolução: \<0% - 100%\>

- **Dúvidas do Aluno/Impedimentos Encontrados**
    - \<DÚVIDAS\>

- **Questões para o Aluno**
    - \<QUESTÕES\>

- **Respostas das Questões**
    - \<RESPOSTAS\>

## SEMANA 3: \<NOME DO PROJETO\>
### Objetivo: \<OBJETIVO DA SEMANA\>
**14/07 - 17/07**
- **Backlog Semanal**
    - \<QUEBRAR O OBJETIVO DA SEMANA EM PARTES MENORES\>

- **Resultado Esperado**
    - \<QUAL ENTREGÁVEL SERÁ PRODUZIDO QUANDO O OBJETIVO FOR ALCANÇADO (FINAL DA SEMANA)\>
    - Evolução: \<0% - 100%\>

- **Dúvidas do Aluno/Impedimentos Encontrados**
    - \<DÚVIDAS\>

- **Questões para o Aluno**
    - \<QUESTÕES\>

- **Respostas das Questões**
    - \<RESPOSTAS\>
---
## Descrição do Projeto
Criar uma API em Python, usando FastAPI, que receba uma imagem (.jpg, .jpeg, .png) ou um PDF de uma Nota Fiscal; salve o Valor Total, Data de Emissão e CNPJ no banco de dados Postgres e retorne os mesmos campos em formato json.

A API e o banco de dados devem rodar localmente em docker e o projeto como um todo deve poder ser iniciado usando o "docker compose". Também é necessário que os dados persistam mesmo que os dockers sejam pausados ou desligados.

O ambiente local deve estar num ambiente virtual, criado com o "venv", e os pacotes devem estar listados no arquivo "requirements.txt".

## Stack
- Python
- Postgres
- FastAPI
- Docker
    - Dockerfile
    - Docker compose
- Gemini
    - API

## Referências
- Python
    - https://www.python.org/downloads/
    - https://www.python.org/doc/
- Repositório de pacotes python
    - https://pypi.org/
- Ambiente virtual
    - https://docs.python.org/pt-br/3/library/venv.html
- Docker
    - Dockerfile, build de imagem e rodar container: https://docs.docker.com/build/concepts/dockerfile/
    - Docker compose: https://docs.docker.com/compose/
- FastAPI
    - https://fastapi.tiangolo.com/tutorial/
    - https://fastapi.tiangolo.com/tutorial/first-steps/#step-4-define-the-path-operation-function
    - https://pypi.org/project/fastapi/
    - https://www.youtube.com/watch?v=7eCdONqaHDc
- Banco de dados
    - https://www.postgresql.org/
    - https://pypi.org/project/SQLAlchemy/
    - https://pypi.org/project/psycopg/
- Gemini
    - https://aistudio.google.com/apikey

## Passo a Passo do Projeto
1. Fazer o setup do ambiente
    - criar repositório
    - instalar dependências
    - instalar docker
1. Criar api do projeto com o FastAPI
1. Fazer a extração de campos com Gemini
1. Adicionar integração com banco de dados

## Benchmarks
- Semana 1
    - setup inicial: repositório, pacotes, docker
    - testar fastapi
    - testar gemini
- Semana 2
    - desenvolver api para fazer extração de campos
- Semana 3
    - integrar com banco de dados
    - finalizar documentação
    - apresentação final

## Diretivas
- **Reuniões**  
    **07/07 (segunda)** - report de progresso e impedimentos  
    **10/07 (quinta)** - report de progresso e impedimentos  
    **15/07 (terça)** - report de progresso e impedimentos  
    **17/07 (quinta, apresentação final)** - apresentação do resultado final  
- Documentar código e processos durante todo o projeto  
- Fazer update diário do relatório  
- Fazer update diário do código  
- O repositório deve ter um nome padrão: \<NOME DO ALUNO\>-AVALIAÇÃO

## Avaliação
- Evolução técnica com base nos resultados semanais
- Autonomia no desenvolvimento e impedimentos
- Organização (repositório, report, documentação, git)
