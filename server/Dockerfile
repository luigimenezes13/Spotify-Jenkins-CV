# Multi-stage build para otimização e segurança
FROM node:20-alpine AS builder

# Instalar pnpm e dependências de sistema
RUN npm install -g pnpm@latest
RUN apk add --no-cache \
    dumb-init \
    && rm -rf /var/cache/apk/*

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
FROM node:20-alpine AS production

# Instalar pnpm e dependências de sistema mínimas
RUN npm install -g pnpm@latest
RUN apk add --no-cache \
    dumb-init \
    && rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

# Criar usuário não-root para produção
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodeuser -u 1001 -G nodejs

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY package.json pnpm-lock.yaml ./

# Instalar apenas dependências de produção
RUN pnpm install --frozen-lockfile --prod

# Copiar código compilado do stage anterior
COPY --from=builder --chown=nodeuser:nodejs /app/dist ./dist

# Criar diretório de logs
RUN mkdir -p logs && chown -R nodeuser:nodejs logs

# Trocar para usuário não-root
USER nodeuser

# Expor porta
EXPOSE 3000

# Definir variáveis de ambiente de produção
ENV NODE_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# Usar dumb-init como PID 1 para melhor gerenciamento de sinais
ENTRYPOINT ["dumb-init", "--"]

# Comando para iniciar a aplicação
CMD ["node", "dist/main.js"]
