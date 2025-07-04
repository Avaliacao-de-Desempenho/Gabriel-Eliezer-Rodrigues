import logging
import psycopg2
from psycopg2.extras import DictCursor # Pode ser útil para fetchall como dict
from fastapi import HTTPException, status
from app.core.config import settings

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados PostgreSQL."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT
        )
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        # Lança uma exceção HTTP para o FastAPI lidar
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível conectar ao banco de dados. Verifique as configurações."
        )

def create_invoices_table():
    """Cria a tabela 'invoices' se ela não existir."""
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS invoices (
                        id SERIAL PRIMARY KEY,
                        total_value NUMERIC(10, 2) NOT NULL,
                        issue_date DATE NOT NULL,
                        cnpj VARCHAR(18) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            conn.commit() # Confirma a transação
            logging.info("Tabela 'invoices' verificada/criada com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao criar tabela 'invoices': {e}")
        # Em um cenário real, você pode querer relançar ou lidar com este erro de forma mais robusta
    finally:
        if conn:
            conn.close() # Sempre fecha a conexão