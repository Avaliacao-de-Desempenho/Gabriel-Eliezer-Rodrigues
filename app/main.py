from contextlib import asynccontextmanager # Importa asynccontextmanager para criar gerentes de contexto assíncronos,
                                            # usados para o ciclo de vida da aplicação (startup/shutdown).
from fastapi import FastAPI                 # Importa a classe FastAPI para criar a aplicação web.
from app.api.endpoints import router as api_router # Importa o objeto 'router' que contém todas as rotas (endpoints) da sua API,
                                                    # definido em 'app/api/endpoints.py'. Renomeado para 'api_router' para clareza.
from app.db.database import create_invoices_table # Importa a função 'create_invoices_table' do módulo de banco de dados.
                                                    # Esta função será responsável por garantir que a tabela de faturas exista.
from app.core.config import settings        # Importa o objeto 'settings' do módulo de configuração.
                                            # Ele contém as configurações globais da aplicação (nome, descrição, chaves, etc.).

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Função de gerenciamento de ciclo de vida da aplicação.
    Esta função é executada em dois momentos:
    1. Antes da aplicação começar a aceitar requisições (bloco 'startup', antes do 'yield').
    2. Depois da aplicação parar de aceitar requisições (bloco 'shutdown', depois do 'yield').
    """
    print("Iniciando a API de Processamento de Notas Fiscais...") # Loga que a API está iniciando.

    # --- Bloco de Startup (executado ao iniciar a aplicação) ---
    # Chamada para criar a tabela do banco de dados na inicialização.
    # Isso garante que a estrutura do DB esteja pronta antes que a API receba requisições.
    create_invoices_table()
    print("Tabela 'invoices' verificada/criada.") # Confirma que a tabela foi verificada ou criada.

    yield # Este ponto marca o fim do bloco de startup e o início do ciclo de vida ativo da aplicação.
          # A partir daqui, a aplicação está pronta para receber e processar requisições.

    # --- Bloco de Shutdown (executado ao desligar a aplicação) ---
    print("Desligando a API de Processamento de Notas Fiscais...") # Loga que a API está desligando.
    # Aqui você poderia adicionar lógica para fechar conexões com banco de dados,
    # limpar recursos, desalocar memória, etc., antes do desligamento completo da aplicação.
    # Exemplo: fechar pool de conexões de banco de dados.

# Instância principal da aplicação FastAPI
# 'lifespan' é o gerenciador de contexto assíncrono que controla o ciclo de vida da aplicação.
app = FastAPI(
    title=settings.PROJECT_NAME,        # Define o título da API, obtido das configurações.
    description=settings.PROJECT_DESCRIPTION, # Define a descrição da API, obtida das configurações.
    version=settings.PROJECT_VERSION,   # Define a versão da API, obtida das configurações.
    lifespan=lifespan                   # Associa a função 'lifespan' para gerenciar o ciclo de vida.
)

# Inclui o roteador (router) de endpoints na aplicação principal.
# Todas as rotas definidas em 'api_router' (que vem de 'app/api/endpoints.py')
# são agora parte da sua aplicação FastAPI.
app.include_router(api_router)

# Endpoint de raiz (root) para verificar o status da API.
# Quando você acessa a URL base da sua API (ex: http://localhost:8000/),
# esta função é executada e retorna uma mensagem de status.
@app.get("/")
async def root():
    return {"message": "API de Processamento de Notas Fiscais - Status: OK"}
