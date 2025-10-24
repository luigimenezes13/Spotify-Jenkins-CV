# Multi-stage build para otimização e segurança
FROM python:3.12-alpine3.22 AS builder

# Instalar dependências de sistema necessárias e limpar cache
RUN apk add --no-cache \
    dumb-init \
    gcc \
    musl-dev \
    && rm -rf /var/cache/apk/*

# Criar usuário não-root para build
RUN addgroup -g 1001 -S python && \
    adduser -S pythonuser -u 1001 -G python

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências primeiro (para melhor cache)
COPY pyproject.toml ./

# Instalar dependências como usuário não-root
RUN chown -R pythonuser:python /app
USER pythonuser

# Criar ambiente virtual e instalar dependências
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel
RUN pip install -e .

# Copiar código fonte
COPY --chown=pythonuser:python . .

# Stage de produção
FROM python:3.12-alpine3.22 AS production

# Instalar dependências de sistema mínimas e limpar cache
RUN apk add --no-cache \
    dumb-init \
    && rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

# Criar usuário não-root para produção
RUN addgroup -g 1001 -S python && \
    adduser -S pythonuser -u 1001 -G python

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY pyproject.toml ./

# Criar ambiente virtual e instalar apenas dependências de produção
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel
RUN pip install -e . --no-deps

# Copiar código fonte
COPY --chown=pythonuser:python . .

# Trocar para usuário não-root
USER pythonuser

# Expor porta
EXPOSE 3000

# Definir variáveis de ambiente de produção
ENV NODE_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0

# Health check com timeout mais robusto
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000/api/health')"

# Usar dumb-init como PID 1 para melhor gerenciamento de sinais
ENTRYPOINT ["dumb-init", "--"]

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
