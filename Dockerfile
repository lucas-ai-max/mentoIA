# Use Python 3.11 slim para imagem menor
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema (necessárias para algumas bibliotecas)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv (ferramenta rápida de gerenciamento de pacotes Python em Rust)
RUN pip install uv

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependências usando uv (muito mais rápido que pip, resolve em segundos)
RUN uv pip install --system --no-cache -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta (Cloud Run usa a variável PORT)
ENV PORT=8000
EXPOSE 8000

# Comando para iniciar o servidor (formato JSON array - resolve aviso JSONArgsRecommended)
CMD ["python", "-c", "import os, uvicorn; uvicorn.run('api_server:app', host='0.0.0.0', port=int(os.getenv('PORT', 8000)), workers=1)"]
