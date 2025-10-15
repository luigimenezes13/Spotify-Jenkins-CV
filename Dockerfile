# Multi-stage build para otimização e segurança
FROM node:24.10.0-alpine3.22 AS builder

# Instalar dependências de sistema necessárias e limpar cache
RUN apk add --no-cache \
    dumb-init \
    && rm -rf /var/cache/apk/*

# Instalar pnpm com versão específica
RUN npm install -g pnpm@10.17.1

# Criar usuário não-root para build
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodeuser -u 1001 -G nodejs

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências primeiro (para melhor cache)
COPY package.json pnpm-lock.yaml ./

# Instalar dependências como usuário não-root
RUN chown -R nodeuser:nodejs /app
USER nodeuser

# Instalar dependências
RUN pnpm install --frozen-lockfile

# Copiar código fonte
COPY --chown=nodeuser:nodejs . .

# Build da aplicação
RUN pnpm run build

# Stage de produção
FROM node:24.10.0-alpine3.22 AS production

# Instalar dependências de sistema mínimas e limpar cache
RUN apk add --no-cache \
    dumb-init \
    && rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

# Instalar pnpm com versão específica
RUN npm install -g pnpm@10.17.1

# Criar usuário não-root para produção
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodeuser -u 1001 -G nodejs

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY package.json pnpm-lock.yaml ./

# Instalar apenas dependências de produção e limpar cache
RUN pnpm install --prod --frozen-lockfile && \
    pnpm store prune && \
    rm -rf /home/nodeuser/.cache /tmp/* /var/tmp/*

# Copiar build da aplicação
COPY --from=builder --chown=nodeuser:nodejs /app/dist ./dist

# Trocar para usuário não-root
USER nodeuser

# Expor porta
EXPOSE 3000

# Definir variáveis de ambiente de produção
ENV NODE_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0
ENV NODE_OPTIONS="--max-old-space-size=512"

# Health check com timeout mais robusto
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) }).on('error', () => process.exit(1))"

# Usar dumb-init como PID 1 para melhor gerenciamento de sinais
ENTRYPOINT ["dumb-init", "--"]

# Comando para iniciar a aplicação
CMD ["node", "dist/server.js"]
