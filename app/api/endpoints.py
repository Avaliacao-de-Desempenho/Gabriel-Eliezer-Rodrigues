import logging
import mimetypes # Necessário para guess_type
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from app.services import invoice_processor # Importa o serviço de processamento

router = APIRouter()

@router.post("/invoice/process")
async def process_invoice_endpoint(file: UploadFile = File(...)):
    """
    Recebe uma imagem (JPG, PNG) ou PDF de uma nota fiscal,
    extrai Valor Total, Data de Emissão e CNPJ usando Gemini,
    salva no PostgreSQL e retorna os dados.
    """
    allowed_mimetypes = ["image/jpeg", "image/png", "application/pdf"]
    # mimetypes.guess_type retorna uma tupla (mimetype, encoding)
    file_mime_type, _ = mimetypes.guess_type(file.filename)

    if file_mime_type not in allowed_mimetypes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não suportado: {file.content_type}. Apenas JPG, PNG ou PDF são permitidos."
        )

    file_content = await file.read()

    # Chama o serviço para processar o arquivo com Gemini
    extracted_data = await invoice_processor.process_file_with_gemini(file_content, file_mime_type)

    total_value = extracted_data.get("total_value")
    issue_date = extracted_data.get("issue_date")
    cnpj = extracted_data.get("cnpj")

    # Validação final antes de salvar no DB
    if not all([total_value, issue_date, cnpj]):
        missing_fields = [k for k, v in {"Valor Total": total_value, "Data de Emissão": issue_date, "CNPJ": cnpj}.items() if v is None]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não foi possível extrair todas as informações necessárias da nota fiscal. Campos ausentes: {', '.join(missing_fields)}"
        )

    # Chama o serviço para salvar os dados no banco de dados
    await invoice_processor.save_invoice_data(total_value, issue_date, cnpj)

    return JSONResponse(content={
        "message": "Nota fiscal processada e dados salvos com sucesso!",
        "extracted_data": {
            "total_value": float(total_value), # Retorna como float para JSON (Decimal não é nativo JSON)
            "issue_date": issue_date.isoformat(),
            "cnpj": cnpj
        }
    })