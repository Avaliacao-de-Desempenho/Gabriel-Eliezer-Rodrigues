import os                               # Importa o módulo 'os' para interagir com o sistema operacional,
                                        # principalmente para acessar variáveis de ambiente.
from pydantic_settings import BaseSettings, SettingsConfigDict # Importa classes chave da biblioteca 'pydantic-settings'.
                                                              # - BaseSettings: A classe base para definir as configurações da sua aplicação.
                                                              #                 Ela fornece a funcionalidade de carregar configurações
                                                              #                 automaticamente de variáveis de ambiente.
                                                              # - SettingsConfigDict: Usada para configurar o comportamento da BaseSettings,
                                                              #                       como a sensibilidade a maiúsculas/minúsculas dos nomes.
from dotenv import load_dotenv          # Importa a função 'load_dotenv' da biblioteca 'python-dotenv'.
                                        # Esta função é responsável por carregar pares CHAVE=VALOR
                                        # de um arquivo .env para as variáveis de ambiente do sistema.

# Carrega as variáveis de ambiente do arquivo .env.
# Esta linha é crucial e deve ser executada antes de tentar acessar qualquer variável de ambiente
# definida no seu arquivo .env. Ela busca o arquivo .env no diretório atual
# ou em diretórios pais e injeta seus conteúdos no ambiente do programa.
load_dotenv()

# Define a classe 'Settings' que herda de 'BaseSettings'.
# Esta classe representa o esquema de todas as configurações que sua aplicação precisa.
class Settings(BaseSettings):
    """
    Classe para carregar as configurações da aplicação a partir de variáveis de ambiente.
    Os atributos definidos aqui correspondem às variáveis de ambiente esperadas.
    'pydantic-settings' automaticamente mapeia as variáveis de ambiente para estes atributos,
    validando seus tipos e garantindo que as configurações obrigatórias estejam presentes.
    """
    # Configurações específicas para o comportamento da classe 'BaseSettings'.
    model_config = SettingsConfigDict(case_sensitive=True) # 'case_sensitive=True' significa que os nomes das variáveis
                                                          # de ambiente (ex: PROJECT_NAME) devem corresponder exatamente
                                                          # em maiúsculas e minúsculas aos atributos definidos na classe.

    # --- Configurações Gerais do Projeto ---
    # Estes atributos definem metadados básicos sobre a API.
    # Eles têm valores padrão ('API de Processamento de Notas Fiscais', etc.).
    # Se uma variável de ambiente correspondente (ex: PROJECT_NAME) for definida,
    # seu valor sobrescreverá o padrão.
    PROJECT_NAME: str = "API de Processamento de Notas Fiscais" # Título da sua API, usado na documentação (Swagger UI/Redoc).
    PROJECT_DESCRIPTION: str = "API para receber notas fiscais (imagem/PDF), extrair dados com Gemini e salvar no PostgreSQL." # Descrição detalhada da API.
    PROJECT_VERSION: str = "1.0.0"                              # Versão atual da API.

    # --- Configurações da API Google Gemini ---
    # Esta é a chave de API necessária para autenticar suas requisições ao Google Gemini.
    # Por não ter um valor padrão, 'pydantic-settings' a considera uma configuração OBRIGATÓRIA.
    # Se 'GEMINI_API_KEY' não estiver definida nas variáveis de ambiente (incluindo o .env),
    # a aplicação falhará ao iniciar, levantando um erro.
    GEMINI_API_KEY: str

    # --- Configurações do Banco de Dados PostgreSQL ---
    # Estes atributos são as credenciais e detalhes de conexão para o seu banco de dados PostgreSQL.
    # Assim como 'GEMINI_API_KEY', todos são OBRIGATÓRIOS, pois não possuem valores padrão.
    # 'pydantic-settings' tentará carregar e validar esses valores a partir do ambiente.
    DB_NAME: str        # Nome do banco de dados ao qual se conectar.
    DB_USER: str        # Nome de usuário para autenticação no banco de dados.
    DB_PASSWORD: str    # Senha para autenticação no banco de dados.
    DB_HOST: str        # Endereço do host onde o banco de dados está rodando (ex: 'localhost', 'db_container_name', um IP).
    DB_PORT: int        # Número da porta na qual o serviço de banco de dados está escutando (ex: 5432 para PostgreSQL).
                        # Note que Pydantic tentará converter o valor da variável de ambiente para um inteiro.

    # Você pode adicionar mais configurações aqui conforme seu projeto cresce.
    # Exemplos:
    # FILE_UPLOAD_MAX_SIZE_MB: int = 5    # Limite de tamanho de arquivo para uploads.
    # LOG_LEVEL: str = "INFO"             # Nível de log para a aplicação.

# Cria uma instância da classe 'Settings'.
# Quando esta linha é executada (na primeira vez que 'config.py' é importado por outro módulo),
# 'pydantic-settings' faz todo o trabalho de carregar, validar e atribuir os valores
# das variáveis de ambiente aos atributos da instância 'settings'.
# Esta instância 'settings' é então importada e utilizada por outros módulos da aplicação
# para acessar as configurações de forma consistente e segura.
settings = Settings()