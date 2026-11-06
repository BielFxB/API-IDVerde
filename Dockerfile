# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Evita criação de arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

WORKDIR /app

# Instala dependências do sistema necessárias para Pillow/Scipy se requerido
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala requirements primeiro (aproveita cache de camadas do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação e o modelo treinado
COPY . .

# Expõe a porta configurada
EXPOSE 5000

# Executa com Gunicorn (1 worker para economizar memória em planos gratuitos, 4 threads para concorrência)
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 4 --timeout 120"]

