import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv() # Carrega as variáveis de ambiente do arquivo .env

class Settings(BaseSettings):
    """
    Classe para carregar as configurações da aplicação a partir de variáveis de ambiente.
    """
    model_config = SettingsConfigDict(case_sensitive=True)

    PROJECT_NAME: str = "API de Processamento de Notas Fiscais"
    PROJECT_DESCRIPTION: str = "API para receber notas fiscais (imagem/PDF), extrair dados com Gemini e salvar no PostgreSQL."
    PROJECT_VERSION: str = "1.0.0"

    # Configurações da API Gemini
    GEMINI_API_KEY: str

    # Configurações do Banco de Dados PostgreSQL
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    # Você pode adicionar mais configurações aqui, como limites de tamanho de arquivo, etc.

settings = Settings()