import logging                  # Importa o módulo 'logging' para registrar informações, avisos e erros relacionados às operações de banco de dados.
import psycopg2                 # O driver oficial para Python interagir com bancos de dados PostgreSQL.
from psycopg2.extras import DictCursor # Importa 'DictCursor', que permite que os resultados das consultas sejam retornados como dicionários.
                                       # Embora importado, não está usado explicitamente neste código, mas pode ser útil para futuras funções de consulta.
from fastapi import HTTPException, status # Importa 'HTTPException' para levantar erros HTTP e 'status' para códigos de status HTTP padrão.
                                          # Isso permite que a API retorne respostas de erro claras quando há problemas de conexão com o DB.
from app.core.config import settings    # Importa o objeto 'settings' do seu módulo de configuração (app/core/config.py).
                                          # Isso centraliza o acesso às credenciais do banco de dados (nome, usuário, senha, host, porta)
                                          # de forma segura e configurável.

def get_db_connection():
    """
    Cria e retorna uma nova conexão com o banco de dados PostgreSQL.
    Esta função encapsula a lógica de conexão, tornando-a reutilizável em todo o módulo
    e isolando a complexidade de conexão.

    Raises:
        HTTPException: Levanta um erro HTTP 503 (Service Unavailable) se a conexão com o banco de dados falhar,
                       indicando que o serviço de banco de dados não está acessível.

    Returns:
        psycopg2.connection: Um objeto de conexão com o banco de dados PostgreSQL.
    """
    conn = None # Inicializa a variável 'conn' como None. Ela armazenará o objeto de conexão.
    try:
        # Tenta estabelecer uma conexão com o banco de dados PostgreSQL usando as configurações carregadas.
        # As credenciais e detalhes de conexão são obtidos de forma segura através do objeto 'settings'.
        conn = psycopg2.connect(
            dbname=settings.DB_NAME,    # Nome do banco de dados.
            user=settings.DB_USER,      # Nome de usuário do banco de dados.
            password=settings.DB_PASSWORD, # Senha do usuário do banco de dados.
            host=settings.DB_HOST,      # Endereço do host do banco de dados.
            port=settings.DB_PORT       # Porta do banco de dados.
        )
        return conn # Retorna o objeto de conexão se a conexão for bem-sucedida.
    except psycopg2.OperationalError as e:
        # Captura erros específicos de operação do PostgreSQL, como:
        # - Banco de dados offline.
        # - Credenciais de acesso incorretas.
        # - Host inacessível ou problema de rede.
        logging.error(f"Erro ao conectar ao banco de dados: {e}") # Registra o erro detalhadamente no log.
        # Lança uma exceção HTTP para o FastAPI lidar.
        # Isso transforma o erro interno do banco de dados em uma resposta HTTP clara para o cliente da API.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, # Código de status 503 indica que o serviço está temporariamente indisponível.
            detail="Não foi possível conectar ao banco de dados. Verifique as configurações." # Mensagem amigável para o cliente.
        )

def create_invoices_table():
    """
    Cria a tabela 'invoices' no banco de dados se ela ainda não existir.
    Esta função é projetada para ser idempotente, o que significa que pode ser chamada
    múltiplas vezes sem causar erros ou duplicações se a tabela já existe.
    Ela é normalmente chamada durante a inicialização da aplicação (startup).
    """
    conn = None # Inicializa a variável 'conn' como None.
    try:
        # Obtém uma nova conexão com o banco de dados usando a função 'get_db_connection()' definida acima.
        conn = get_db_connection()
        if conn: # Verifica se a conexão foi estabelecida com sucesso (ou seja, 'conn' não é None).
            # Usa um 'cursor' para executar comandos SQL no banco de dados.
            # O 'with' statement garante que o cursor seja fechado automaticamente após o uso.
            with conn.cursor() as cur:
                # Executa a query SQL para criar a tabela 'invoices'.
                # 'CREATE TABLE IF NOT EXISTS' é a cláusula que garante a idempotência:
                # a tabela só será criada se não existir previamente no banco de dados.
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS invoices (
                        id SERIAL PRIMARY KEY,              -- Coluna de ID: tipo SERIAL (inteiro sequencial e auto-incrementável),
                                                            -- definido como PRIMARY KEY (chave primária, única e não nula).
                        total_value NUMERIC(10, 2) NOT NULL,-- Valor total da fatura: tipo NUMERIC com 10 dígitos no total e 2 casas decimais.
                                                            -- NOT NULL significa que este campo é obrigatório e não pode ser vazio.
                        issue_date DATE NOT NULL,           -- Data de emissão da fatura: tipo DATE (apenas data).
                                                            -- NOT NULL significa que este campo é obrigatório.
                        cnpj VARCHAR(18) NOT NULL,          -- CNPJ do emissor: tipo VARCHAR com no máximo 18 caracteres (suficiente para formato XX.XXX.XXX/XXXX-XX).
                                                            -- NOT NULL significa que este campo é obrigatório.
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Timestamp da criação do registro: tipo TIMESTAMP (data e hora com precisão de segundos).
                                                            -- DEFAULT CURRENT_TIMESTAMP define o valor padrão para a data e hora atuais no momento da inserção.
                    );
                """)
            conn.commit() # Confirma a transação no banco de dados.
                          # Esta operação é crucial para tornar as alterações (a criação da tabela) permanentes no DB.
            logging.info("Tabela 'invoices' verificada/criada com sucesso.") # Registra uma mensagem de sucesso no log.
    except Exception as e:
        # Captura qualquer outra exceção genérica que possa ocorrer durante o processo de criação da tabela.
        logging.error(f"Erro ao criar tabela 'invoices': {e}") # Registra o erro detalhadamente.
        # Em um ambiente de produção ou em cenários mais complexos, você pode considerar:
        # - Relançar a exceção para que a aplicação falhe se a infraestrutura do DB não puder ser configurada.
        # - Usar um sistema de gerenciamento de migrações de banco de dados (como Alembic) para um controle mais robusto.
    finally:
        # Este bloco 'finally' é garantido para ser executado, independentemente de ter ocorrido uma exceção ou não.
        if conn:
            conn.close() # Garante que a conexão com o banco de dados seja sempre fechada.
                         # Isso é fundamental para liberar recursos do banco de dados e evitar vazamentos de conexão.