import io
import logging
import json
import mimetypes
from datetime import date
from decimal import Decimal

import google.generativeai as genai
from PyPDF2 import PdfReader
from PIL import Image

from fastapi import HTTPException, status
from app.core.config import settings
from app.db.database import get_db_connection

try:
    genai.configure(api_key=settings.GEMINI_API_KEY)

    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    logging.error(f"Erro ao configurar o Gemini API: {e}")



async def process_file_with_gemini(file_content: bytes, mime_type: str):
    """
    Envia o conteúdo do arquivo (imagem ou PDF) para a API Gemini para extração de dados.
    Espera uma resposta JSON do Gemini.
    """
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chave da API Gemini não configurada. Verifique seu arquivo .env"
        )

    parts = []


    if mime_type.startswith('image/'):
        parts.append({
            "mime_type": mime_type,
            "data": file_content
        })
    # SE FOR UM PDF, adicione-o diretamente como parte da requisição
    elif mime_type == 'application/pdf':
        parts.append({
            "mime_type": mime_type,
            "data": file_content
        })
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de arquivo não suportado. Por favor, envie .jpg, .jpeg, .png ou .pdf."
        )

    # Prompt para o Gemini (otimizado para extração JSON)
    # O prompt foi ajustado para ser agnóstico ao tipo de documento (imagem ou PDF)
    prompt_parts = [
        parts[0], # O conteúdo do documento (imagem ou PDF)
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
        response = gemini_model.generate_content(prompt_parts)
        logging.info(f"Resposta bruta do Gemini: {response.text}")

        # Tentar extrair o JSON da resposta
        gemini_response_text = response.text.strip()
        # Às vezes, o Gemini pode retornar markdown. Tenta remover ```json e ```
        if gemini_response_text.startswith("```json") and gemini_response_text.endswith("```"):
            gemini_response_text = gemini_response_text[len("```json"): -len("```")].strip()

        extracted_data = json.loads(gemini_response_text)

        # Validação básica dos campos esperados
        required_fields = ["total_value", "issue_date", "cnpj"]
        for field in required_fields:
            if field not in extracted_data:
                raise ValueError(f"Campo '{field}' ausente na resposta do Gemini.")

        # Conversão de tipos
        extracted_data['total_value'] = Decimal(str(extracted_data['total_value'])) if extracted_data['total_value'] is not None else None
        extracted_data['issue_date'] = date.fromisoformat(extracted_data['issue_date']) if extracted_data['issue_date'] is not None else None
        # O CNPJ já deve vir como string

        return extracted_data

    except json.JSONDecodeError as e:
        logging.error(f"Erro ao decodificar JSON da resposta do Gemini: {e}. Resposta: {response.text}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar a resposta do Gemini. Formato JSON inválido. Resposta: {response.text}"
        )
    except ValueError as e:
        logging.error(f"Erro de validação ou conversão de dados do Gemini: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dados extraídos do Gemini inválidos: {e}. Resposta: {response.text}"
        )
    except Exception as e:
        logging.error(f"Erro inesperado ao chamar Gemini API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao comunicar com a API Gemini: {e}. Verifique sua chave e o serviço."
        )

async def save_invoice_data(total_value: Decimal, issue_date: date, cnpj: str):
    """
    Salva os dados extraídos da nota fiscal no banco de dados.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO invoices (total_value, issue_date, cnpj)
                    VALUES (%s, %s, %s) RETURNING id;
                    """,
                    (total_value, issue_date, cnpj)
                )
                invoice_id = cur.fetchone()[0]
            conn.commit()
            logging.info(f"Dados da nota fiscal salvos com sucesso. ID: {invoice_id}")
            return invoice_id
    except Exception as e:
        logging.error(f"Erro ao salvar dados no banco de dados: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar os dados da nota fiscal no banco de dados: {e}"
        )
    finally:
        if conn:
            conn.close()
