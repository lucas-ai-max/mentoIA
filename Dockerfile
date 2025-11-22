# Use Python 3.11 slim para imagem menor
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema (necessárias para algumas bibliotecas)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Atualizar pip para versão mais recente (resolve dependências melhor)
RUN pip install --upgrade pip setuptools wheel

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependências Python com resolver mais rápido
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta (Cloud Run usa a variável PORT)
ENV PORT=8000
EXPOSE 8000

# Comando para iniciar o servidor
CMD exec uvicorn api_server:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1

