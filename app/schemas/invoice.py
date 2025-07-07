# app/schemas/invoice.py

from pydantic import BaseModel, Field # Importa classes chave da biblioteca Pydantic:
                                     # - BaseModel: A classe base para criar modelos de dados. Ao herdar dela, suas classes
                                     #              ganham recursos de validação, serialização e documentação automática.
                                     # - Field: Uma função usada para adicionar metadados e validações extras aos campos do modelo.
                                     #          O '...' (Ellipsis) usado com Field indica que o campo é obrigatório.
from datetime import date           # Importa o tipo 'date' do módulo datetime para representar datas
                                     # sem informações de tempo (ex: YYYY-MM-DD).
from decimal import Decimal         # Importa o tipo 'Decimal' do módulo decimal. É crucial para representar
                                     # valores monetários e outras quantidades decimais com precisão exata,
                                     # evitando os problemas de arredondamento inerentes aos números de ponto flutuante (float).
from typing import Optional         # Importa 'Optional' do módulo typing. Usado para indicar que um campo
                                     # pode ser de um tipo específico (ex: Decimal, date, str) OU None (nulo).

class ExtractedInvoiceData(BaseModel):
    """
    Define o esquema (estrutura) para os dados que são esperados
    serem extraídos de uma nota fiscal pela API Gemini ou qualquer outro método de extração.
    Estes modelos são usados para validar os dados recebidos e garantir sua conformidade.
    """
    # total_value: Representa o valor total da nota fiscal.
    # Optional[Decimal] indica que o campo pode ser um objeto Decimal ou None.
    # Field(..., description="...") indica que o campo é considerado obrigatório na estrutura,
    # mas o valor em si pode ser None devido ao 'Optional'.
    # A 'description' será exibida na documentação automática da API (Swagger UI/OpenAPI).
    total_value: Optional[Decimal] = Field(..., description="Valor total da nota fiscal.")
    
    # issue_date: Representa a data de emissão da nota fiscal.
    # Optional[date] indica que o campo pode ser um objeto date ou None.
    # O formato esperado para entrada e saída é geralmente YYYY-MM-DD, que o Pydantic lida automaticamente.
    issue_date: Optional[date] = Field(..., description="Data de emissão da nota fiscal no formato YYYY-MM-DD.")
    
    # cnpj: Representa o CNPJ (Cadastro Nacional da Pessoa Jurídica) do emissor da nota fiscal.
    # Optional[str] indica que o campo pode ser uma string ou None.
    # O formato usual do CNPJ é XX.XXX.XXX/XXXX-XX.
    cnpj: Optional[str] = Field(..., description="CNPJ do emissor da nota fiscal no formato XX.XXX.XXX/XXXX-XX.")

class InvoiceProcessResponse(BaseModel):
    """
    Define o esquema da resposta JSON que a API enviará de volta ao cliente
    após o processamento bem-sucedido de uma nota fiscal.
    Este modelo estrutura a saída da sua API, tornando-a previsível e fácil de ser consumida.
    """
    # message: Uma mensagem de status ou feedback para o cliente sobre o processamento.
    # É uma string e é um campo obrigatório.
    message: str = Field(..., description="Mensagem de status do processamento.")
    
    # extracted_data: Contém os dados que foram extraídos da nota fiscal.
    # O tipo deste campo é o modelo 'ExtractedInvoiceData' definido acima.
    # Isso demonstra o aninhamento de modelos Pydantic, permitindo que você construa
    # respostas complexas e bem estruturadas, reutilizando modelos existentes.
    # O Pydantic irá validar a estrutura de 'extracted_data' de acordo com 'ExtractedInvoiceData'.
    extracted_data: ExtractedInvoiceData = Field(..., description="Dados extraídos da nota fiscal.")
