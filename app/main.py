from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.db.database import create_invoices_table
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Função de gerenciamento de ciclo de vida da aplicação.
    Executa tarefas de inicialização (startup) e desligamento (shutdown).
    """
    print("Iniciando a API de Processamento de Notas Fiscais...")
    # Chamada para criar a tabela do banco de dados na inicialização
    # (se ela ainda não existir)
    create_invoices_table()
    print("Tabela 'invoices' verificada/criada.")

    yield # Ponto onde a aplicação começa a receber requisições

    print("Desligando a API de Processamento de Notas Fiscais...")
    # Aqui você poderia adicionar lógica para fechar conexões com banco de dados,
    # limpar recursos, etc., antes do desligamento completo da aplicação.

# Instância da aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan
)

# Inclui o roteador de endpoints da API
app.include_router(api_router)

# Endpoint de raiz para verificar se a API está no ar
@app.get("/")
async def root():
    return {"message": "API de Processamento de Notas Fiscais - Status: OK"}
