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

# Copiar e tornar entrypoint.sh executável
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expor porta (Cloud Run define PORT automaticamente, padrão é 8080)
EXPOSE 8080

# Usar entrypoint script (garante que o servidor sempre inicia corretamente)
ENTRYPOINT ["/entrypoint.sh"]
