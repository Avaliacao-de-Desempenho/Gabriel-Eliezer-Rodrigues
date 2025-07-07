import logging                  # Importa o módulo 'logging' para registrar informações, avisos e erros.
                                # Essencial para depuração e monitoramento do comportamento da API.
import mimetypes                # Importa o módulo 'mimetypes' para ajudar a determinar o tipo MIME (ex: 'image/jpeg', 'application/pdf')
                                # de um arquivo com base em sua extensão, usando a função 'guess_type'.

from fastapi import APIRouter, UploadFile, File, HTTPException, status # Importa componentes essenciais do FastAPI:
                                                                    # - APIRouter: Permite criar grupos de rotas modulares para organizar a API.
                                                                    # - UploadFile: Uma classe para lidar com arquivos enviados via requisições HTTP.
                                                                    # - File: Uma função para declarar que um parâmetro da rota espera um arquivo.
                                                                    # - HTTPException: Usado para levantar erros HTTP padrão (ex: 400 Bad Request, 500 Internal Server Error).
                                                                    # - status: Um objeto que contém códigos de status HTTP predefinidos (ex: status.HTTP_400_BAD_REQUEST).
from fastapi.responses import JSONResponse              # Importa 'JSONResponse' para construir e retornar respostas HTTP no formato JSON.
from app.services import invoice_processor # Importa o módulo 'invoice_processor' do pacote 'app.services'.
                                            # Este módulo encapsula a lógica de negócio complexa, como a interação com a API Gemini
                                            # e a persistência de dados no banco, promovendo a separação de responsabilidades.

# Cria uma instância do APIRouter.
# Todas as rotas (endpoints) definidas neste arquivo serão anexadas a este objeto 'router'.
# Este 'router' será então incluído no 'app' principal em 'app/main.py'.
router = APIRouter()

# Define um endpoint HTTP POST para o caminho "/invoice/process".
# Quando uma requisição POST é feita para esta URL, a função 'process_invoice_endpoint' será executada.
@router.post("/invoice/process")
async def process_invoice_endpoint(file: UploadFile = File(...)):
    """
    Endpoint principal para processar notas fiscais.
    Recebe um arquivo (imagem JPG/PNG ou PDF), o envia para a API Gemini para extração de dados,
    salva os dados extraídos no PostgreSQL e retorna uma resposta JSON.

    Args:
        file (UploadFile): O arquivo da nota fiscal enviado na requisição.
                           FastAPI injeta o arquivo automaticamente.

    Returns:
        JSONResponse: Uma resposta JSON contendo uma mensagem de sucesso e os dados extraídos.

    Raises:
        HTTPException: Se o tipo de arquivo não for suportado, ou se informações cruciais não puderem ser extraídas.
    """
    # Define a lista de tipos MIME (Multipurpose Internet Mail Extensions) permitidos para upload.
    allowed_mimetypes = ["image/jpeg", "image/png", "application/pdf"]

    # Tenta adivinhar o tipo MIME do arquivo enviado com base em seu nome (extensão).
    # 'mimetypes.guess_type' retorna uma tupla (mimetype, encoding); usamos [0] para pegar apenas o mimetype.
    file_mime_type, _ = mimetypes.guess_type(file.filename)

    # Valida se o tipo MIME do arquivo está na lista de tipos permitidos.
    if file_mime_type not in allowed_mimetypes:
        # Se o tipo de arquivo não for suportado, levanta uma exceção HTTP 400 (Bad Request).
        # Isso informa ao cliente que a requisição é inválida devido ao tipo de arquivo.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não suportado: {file.content_type}. Apenas JPG, PNG ou PDF são permitidos."
        )

    # Lê o conteúdo binário completo do arquivo enviado.
    # 'await' é usado porque 'file.read()' é uma operação assíncrona de I/O (leitura de disco/rede).
    file_content = await file.read()

    # Delega a lógica de processamento do arquivo com a API Gemini para o módulo 'invoice_processor'.
    # O endpoint não precisa saber os detalhes de como o Gemini é chamado ou como os dados são parseados;
    # ele apenas espera os 'extracted_data' de volta.
    extracted_data = await invoice_processor.process_file_with_gemini(file_content, file_mime_type)

    # Extrai os campos específicos ('total_value', 'issue_date', 'cnpj') do dicionário retornado pelo Gemini.
    # Usa '.get()' para acessar as chaves de forma segura; se a chave não existir, retorna 'None'.
    total_value = extracted_data.get("total_value")
    issue_date = extracted_data.get("issue_date")
    cnpj = extracted_data.get("cnpj")

    # Realiza uma validação final para garantir que todos os campos essenciais foram extraídos com sucesso
    # antes de prosseguir com o salvamento no banco de dados.
    if not all([total_value, issue_date, cnpj]):
        # Se algum campo estiver faltando (for None), constrói uma lista de campos ausentes para o feedback.
        missing_fields = [k for k, v in {"Valor Total": total_value, "Data de Emissão": issue_date, "CNPJ": cnpj}.items() if v is None]
        # Levanta uma exceção HTTP 400 (Bad Request) informando quais campos não puderam ser extraídos.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não foi possível extrair todas as informações necessárias da nota fiscal. Campos ausentes: {', '.join(missing_fields)}"
        )

    # Delega a lógica de salvamento dos dados extraídos no banco de dados para o módulo 'invoice_processor'.
    # O endpoint apenas invoca a função, sem lidar com os detalhes de conexão ou queries SQL.
    await invoice_processor.save_invoice_data(total_value, issue_date, cnpj)

    # Retorna uma resposta JSON de sucesso para o cliente.
    # Inclui uma mensagem de confirmação e os dados que foram extraídos e salvos.
    # Conversões para JSON:
    # - 'float(total_value)': Converte o objeto Decimal (que é usado para precisão financeira) para float,
    #                         pois JSON não tem um tipo nativo para Decimal. O banco de dados continua usando Numeric.
    # - 'issue_date.isoformat()': Converte o objeto 'date' do Python para uma string no formato ISO 8601 (YYYY-MM-DD),
    #                             que é um formato padrão e legível em JSON.
    return JSONResponse(content={
        "message": "Nota fiscal processada e dados salvos com sucesso!",
        "extracted_data": {
            "total_value": float(total_value), # O valor total, convertido para float para a resposta JSON.
            "issue_date": issue_date.isoformat(), # A data de emissão, convertida para string ISO.
            "cnpj": cnpj # O CNPJ como string.
        }
    })