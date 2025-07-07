import io                       # Módulo 'io' para lidar com streams de dados em memória, como arquivos em bytes.
import logging                  # Módulo 'logging' para registrar informações, avisos e erros durante a execução,
                                # essencial para monitoramento e depuração.
import json                     # Módulo 'json' para trabalhar com dados no formato JSON, usado para parsear
                                # as respostas da API Gemini.
import mimetypes                # Módulo 'mimetypes' para ajudar a determinar o tipo MIME de um arquivo.
                                # Embora não usado diretamente para processar o arquivo aqui,
                                # o 'mime_type' é um parâmetro importante para a requisição ao Gemini.
from datetime import date       # Importa o tipo 'date' do módulo 'datetime', usado para representar datas
                                # de forma estruturada (ex: data de emissão).
from decimal import Decimal     # Importa o tipo 'Decimal' do módulo 'decimal'. FUNDAMENTAL para lidar
                                # com valores monetários, garantindo precisão numérica e evitando os
                                # problemas de arredondamento de floats binários.

import google.generativeai as genai # A biblioteca oficial do Google para interagir com seus modelos generativos,
                                    # como o Gemini.
from PyPDF2 import PdfReader    # Biblioteca para manipulação de arquivos PDF.
                                # Embora importada, neste código, o PDF é passado diretamente ao Gemini como bytes.
                                # Poderia ser usada para pré-processamento local, se necessário.
from PIL import Image           # Biblioteca Pillow (um fork do PIL) para processamento de imagens.
                                # Assim como PyPDF2, neste código, a imagem é passada diretamente ao Gemini como bytes.
                                # Seria usada para pré-processamento local de imagens, se necessário.

from fastapi import HTTPException, status # Importa 'HTTPException' para levantar exceções HTTP (erros que a API retorna ao cliente)
                                          # e 'status' para acessar códigos de status HTTP padrão (ex: 400, 500).
from app.core.config import settings    # Importa o objeto 'settings' do módulo de configuração (app/core/config.py).
                                          # Este objeto contém as configurações globais da aplicação, como a chave da API Gemini
                                          # e as credenciais do banco de dados.
from app.db.database import get_db_connection # Importa a função 'get_db_connection' do módulo de banco de dados (app/db/database.py).
                                              # Esta função é usada para obter uma conexão com o banco de dados PostgreSQL.

# --- Configuração inicial da API Gemini ---
# Este bloco tenta configurar a API Gemini usando a chave fornecida nas configurações.
# Ele é executado uma vez quando o módulo é carregado.
try:
    genai.configure(api_key=settings.GEMINI_API_KEY) # Configura a biblioteca Gemini com a chave de API.
                                                    # Se a chave não estiver configurada corretamente, isso pode falhar.
    gemini_model = genai.GenerativeModel('gemini-1.5-flash') # Instancia o modelo generativo 'gemini-1.5-flash'.
                                                            # Este é um modelo rápido e otimizado para muitas tarefas.
except Exception as e:
    # Se houver qualquer erro durante a configuração inicial do Gemini (ex: chave inválida, problema de rede inicial),
    # ele será capturado e registrado. Isso evita que a aplicação falhe completamente ao iniciar.
    logging.error(f"Erro ao configurar o Gemini API: {e}")

# --- Função principal para processar o arquivo com a API Gemini ---
async def process_file_with_gemini(file_content: bytes, mime_type: str):
    """
    Envia o conteúdo binário de um arquivo (imagem ou PDF) para a API Gemini para extração de dados.
    Esta função é responsável por formatar a requisição para o Gemini e parsear sua resposta.

    Args:
        file_content (bytes): O conteúdo binário do arquivo (ex: uma imagem JPG, um documento PDF).
        mime_type (str): O tipo MIME do arquivo (ex: "image/jpeg", "application/pdf"),
                         usado pelo Gemini para interpretar o conteúdo.

    Returns:
        dict: Um dicionário contendo os dados extraídos (valor total, data de emissão, CNPJ),
              com os tipos de dados Python corretos (Decimal, date).

    Raises:
        HTTPException: Se a chave da API Gemini não estiver configurada, o tipo de arquivo não for suportado,
                       ou ocorrerem erros durante a comunicação com o Gemini ou o processamento de sua resposta.
    """
    # Validação crucial: verifica se a chave da API Gemini está disponível nas configurações.
    # Se não estiver, levanta um erro HTTP 500 (Erro Interno do Servidor) para o cliente.
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chave da API Gemini não configurada. Verifique seu arquivo .env"
        )

    parts = [] # Lista para construir a requisição multi-modal para o Gemini.
               # O Gemini 1.5 pode receber texto e múltiplos arquivos em uma única requisição.

    # Adiciona o conteúdo do arquivo à lista de partes da requisição Gemini,
    # identificando o tipo MIME correto.
    if mime_type.startswith('image/'): # Se o arquivo for uma imagem (JPG, PNG, etc.)
        parts.append({
            "mime_type": mime_type, # Tipo MIME da imagem.
            "data": file_content    # Conteúdo binário da imagem.
        })
    elif mime_type == 'application/pdf': # Se o arquivo for um PDF
        # O Gemini 1.5-Flash (e Pro) pode processar PDFs diretamente como uma 'part'.
        parts.append({
            "mime_type": mime_type, # Tipo MIME do PDF.
            "data": file_content    # Conteúdo binário do PDF.
        })
    else:
        # Se o tipo de arquivo não for uma imagem ou PDF, levanta um erro HTTP 400 (Bad Request).
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de arquivo não suportado. Por favor, envie .jpg, .jpeg, .png ou .pdf."
        )

    # --- Definição do Prompt para o Gemini ---
    # O prompt é o texto que guia a IA sobre o que ela deve fazer.
    # É ajustado para extrair informações específicas e retornar em um formato JSON estrito.
    prompt_parts = [
        parts[0], # A primeira parte da requisição é o documento (imagem ou PDF) que o Gemini deve analisar.
        """
        Analise o documento da nota fiscal fornecido (que pode ser uma imagem ou um PDF). Extraia as seguintes informações:
        1.  **Valor Total da Nota Fiscal**: O valor monetário total, formatado como número decimal (ex: 123.45).
        2.  **Data de Emissão**: A data em que a nota fiscal foi emitida, no formato YYYY-MM-DD.
        3.  **CNPJ**: O CNPJ do emissor da nota fiscal, no formato XX.XXX.XXX/XXXX-XX.

        Retorne estas informações estritamente em um objeto JSON válido, seguindo este formato:
        {
            "total_value": <Valor Total como float ou Decimal>,
            "issue_date": "<Data de Emissão no formato YYYY-MM-DD>",
            "cnpj": "<CNPJ no formato XX.XXX.XXX/XXXX-XX>"
        }

        Se alguma informação não for encontrada, retorne `null` para aquele campo. Não inclua texto adicional antes ou depois do JSON.
        """
    ]

    try:
        logging.info(f"Enviando requisição ao Gemini API com tipo: {mime_type}...")
        # Faz a chamada assíncrona para a API Gemini para gerar conteúdo baseado no prompt e no documento.
        response = gemini_model.generate_content(prompt_parts)
        logging.info(f"Resposta bruta do Gemini: {response.text}") # Loga a resposta completa do Gemini para inspeção.

        # Tenta extrair o JSON da resposta do Gemini.
        gemini_response_text = response.text.strip()
        # O Gemini às vezes encapsula o JSON em blocos de código Markdown (ex: ```json...```).
        # Este bloco remove esses marcadores para obter o JSON puro.
        if gemini_response_text.startswith("```json") and gemini_response_text.endswith("```"):
            gemini_response_text = gemini_response_text[len("```json"): -len("```")].strip()

        # Deserializa a string JSON em um dicionário Python.
        extracted_data = json.loads(gemini_response_text)

        # Validação básica: verifica se todos os campos esperados estão presentes no JSON retornado pelo Gemini.
        required_fields = ["total_value", "issue_date", "cnpj"]
        for field in required_fields:
            if field not in extracted_data:
                # Se um campo obrigatório estiver faltando, levanta um erro de valor.
                raise ValueError(f"Campo '{field}' ausente na resposta do Gemini.")

        # --- Conversão de tipos de dados ---
        # Converte os dados extraídos para os tipos Python desejados (Decimal, date),
        # tratando o caso em que o Gemini retorna 'null' (None em Python).
        extracted_data['total_value'] = Decimal(str(extracted_data['total_value'])) if extracted_data['total_value'] is not None else None
        extracted_data['issue_date'] = date.fromisoformat(extracted_data['issue_date']) if extracted_data['issue_date'] is not None else None
        # O CNPJ já deve vir como string; apenas garante que seja None se o Gemini retornou null.
        extracted_data['cnpj'] = extracted_data['cnpj'] if extracted_data['cnpj'] is not None else None


        return extracted_data # Retorna o dicionário com os dados já convertidos para os tipos corretos.

    except json.JSONDecodeError as e:
        # Captura erros se a resposta do Gemini não for um JSON válido, mesmo após a limpeza do Markdown.
        logging.error(f"Erro ao decodificar JSON da resposta do Gemini: {e}. Resposta: {response.text}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar a resposta do Gemini. Formato JSON inválido. Resposta: {response.text}"
        )
    except ValueError as e:
        # Captura erros se a validação dos campos falhar (ex: campo ausente)
        # ou se a conversão de tipos falhar (ex: data em formato inválido).
        logging.error(f"Erro de validação ou conversão de dados do Gemini: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dados extraídos do Gemini inválidos: {e}. Resposta: {response.text}"
        )
    except Exception as e:
        # Captura qualquer outro erro inesperado que possa ocorrer durante a chamada à API Gemini
        # ou o processamento de sua resposta (ex: problemas de rede, limites de taxa).
        logging.error(f"Erro inesperado ao chamar Gemini API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao comunicar com a API Gemini: {e}. Verifique sua chave e o serviço."
        )

# --- Função para salvar os dados extraídos no banco de dados ---
async def save_invoice_data(total_value: Decimal, issue_date: date, cnpj: str):
    """
    Salva os dados extraídos de uma nota fiscal (valor total, data de emissão, CNPJ)
    na tabela 'invoices' do banco de dados PostgreSQL.

    Args:
        total_value (Decimal): O valor total da nota fiscal a ser salvo.
        issue_date (date): A data de emissão da nota fiscal a ser salvo.
        cnpj (str): O CNPJ do emissor da nota fiscal a ser salvo.

    Returns:
        int: O ID do registro da nota fiscal recém-inserido no banco de dados.

    Raises:
        HTTPException: Se ocorrer qualquer erro durante a conexão ou a operação de inserção no banco de dados.
    """
    conn = None # Inicializa a variável de conexão como None.
    try:
        conn = get_db_connection() # Obtém uma conexão com o banco de dados usando a função do módulo 'database'.
        if conn: # Verifica se a conexão foi estabelecida com sucesso.
            with conn.cursor() as cur: # Cria um cursor para executar comandos SQL. O 'with' garante que o cursor seja fechado.
                # Executa a query INSERT para inserir os dados da nota fiscal na tabela 'invoices'.
                # `%s` são placeholders que o psycopg2 substitui pelos valores da tupla.
                # Isso é crucial para prevenir ataques de SQL Injection, pois os valores são tratados como dados, não como código SQL.
                # 'RETURNING id;' faz com que o ID gerado automaticamente para o novo registro seja retornado pela query.
                cur.execute(
                    """
                    INSERT INTO invoices (total_value, issue_date, cnpj)
                    VALUES (%s, %s, %s) RETURNING id;
                    """,
                    (total_value, issue_date, cnpj) # Os valores a serem inseridos, passados como uma tupla.
                )
                invoice_id = cur.fetchone()[0] # Obtém o ID retornado pela query (o primeiro elemento da primeira linha).
            conn.commit() # Confirma a transação no banco de dados.
                          # Esta operação é essencial para persistir as alterações (inserção) no DB.
            logging.info(f"Dados da nota fiscal salvos com sucesso. ID: {invoice_id}") # Registra o sucesso da operação.
            return invoice_id # Retorna o ID do registro que foi salvo.
    except Exception as e:
        # Captura qualquer erro que possa ocorrer durante a operação de salvamento no banco de dados.
        logging.error(f"Erro ao salvar dados no banco de dados: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar os dados da nota fiscal no banco de dados: {e}"
        )
    finally:
        # Este bloco 'finally' é executado sempre, independentemente de ter ocorrido um erro ou não.
        if conn:
            conn.close() # Garante que a conexão com o banco de dados seja sempre fechada,
                         # liberando recursos e evitando vazamento de conexões.