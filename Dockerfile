# Usa uma imagem oficial do Python como base
FROM python:3.11-slim-bookworm

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação para o container
COPY . .

# Expõe a porta que a aplicação irá rodar
EXPOSE 8000

# Comando padrão para rodar a aplicação (pode ser sobrescrito pelo docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]