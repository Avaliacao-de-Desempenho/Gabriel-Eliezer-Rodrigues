from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import Optional

class ExtractedInvoiceData(BaseModel):
    total_value: Optional[Decimal] = Field(..., description="Valor total da nota fiscal.")
    issue_date: Optional[date] = Field(..., description="Data de emissão da nota fiscal no formato YYYY-MM-DD.")
    cnpj: Optional[str] = Field(..., description="CNPJ do emissor da nota fiscal no formato XX.XXX.XXX/XXXX-XX.")

class InvoiceProcessResponse(BaseModel):
    message: str = Field(..., description="Mensagem de status do processamento.")
    extracted_data: ExtractedInvoiceData = Field(..., description="Dados extraídos da nota fiscal.")