# Spotify Jenkins CV - API REST

API REST desenvolvida com Node.js, TypeScript e pnpm, preparada para integração com Jenkins CI/CD.

## 🚀 Tecnologias

- **Node.js** 18.18.0
- **TypeScript** 5.2.2
- **Express.js** 4.18.2
- **pnpm** 8.15.0
- **Jest** (testes)
- **ESLint** + **Prettier** (qualidade de código)
- **Docker** (containerização)
- **Jenkins** (CI/CD)

## 📁 Estrutura do Projeto

```
src/
├── controllers/     # Controllers da API
├── routes/         # Definição das rotas
├── middlewares/    # Middlewares personalizados
├── services/       # Lógica de negócio
├── types/          # Definições TypeScript
├── utils/          # Utilitários
├── app.ts          # Configuração do Express
└── server.ts       # Inicialização do servidor

tests/              # Testes unitários e integração
├── setup.ts        # Configuração dos testes
└── *.test.ts       # Arquivos de teste
```

## 🛠️ Instalação e Desenvolvimento

### Pré-requisitos

- Node.js >= 18.0.0
- pnpm >= 8.0.0

### Instalação

```bash
# Clonar o repositório
git clone <repository-url>
cd spotify-jenkins-cv

# Instalar dependências
pnpm install

# Configurar variáveis de ambiente
cp .env.example .env
```

### Scripts Disponíveis

```bash
# Desenvolvimento
pnpm dev              # Inicia servidor em modo desenvolvimento

# Build
pnpm build            # Compila TypeScript para JavaScript
pnpm start            # Inicia servidor em produção

# Qualidade de código
pnpm lint             # Executa ESLint
pnpm lint:fix         # Corrige problemas do ESLint
pnpm format           # Formata código com Prettier
pnpm format:check     # Verifica formatação

# Testes
pnpm test             # Executa todos os testes
pnpm test:watch       # Executa testes em modo watch
pnpm test:coverage    # Executa testes com relatório de cobertura
```

## 🌐 Endpoints

### Health Check

```http
GET /api/health
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "status": "OK",
    "timestamp": "2024-01-01T00:00:00.000Z",
    "uptime": 123.456,
    "environment": "development"
  },
  "message": "API está funcionando corretamente"
}
```

### Rota Raiz

```http
GET /
```

**Resposta:**
```json
{
  "success": true,
  "message": "API REST Node.js + TypeScript está funcionando!",
  "version": "1.0.0"
}
```

## 🐳 Docker

### Build da imagem

```bash
docker build -t spotify-jenkins-cv .
```

### Executar container

```bash
docker run -p 3000:3000 spotify-jenkins-cv
```

## 🔄 Jenkins CI/CD

O projeto inclui um `Jenkinsfile` configurado com pipeline completo:

1. **Checkout** - Clonagem do código
2. **Setup Environment** - Instalação Node.js e pnpm
3. **Install Dependencies** - Instalação das dependências
4. **Lint** - Verificação de qualidade de código
5. **Format Check** - Verificação de formatação
6. **Type Check** - Verificação de tipos TypeScript
7. **Test** - Execução de testes com cobertura
8. **Build Docker Image** - Construção da imagem Docker
9. **Deploy** - Deploy automático (staging/produção)

### Configuração no Jenkins

1. Criar novo pipeline job
2. Configurar para usar `Jenkinsfile` do repositório
3. Configurar credenciais do Docker Registry (se necessário)
4. Configurar webhooks do Git para trigger automático

## 🧪 Testes

```bash
# Executar todos os testes
pnpm test

# Executar testes em modo watch
pnpm test:watch

# Executar com cobertura
pnpm test:coverage
```

Os relatórios de cobertura são gerados em `coverage/lcov-report/index.html`.

## 📝 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
NODE_ENV=development
PORT=3000
HOST=0.0.0.0
```

## 🔧 Configuração do Editor

O projeto inclui configurações para:

- **ESLint** - Linting de código
- **Prettier** - Formatação automática
- **EditorConfig** - Configuração consistente entre editores

## 📊 Monitoramento

### Health Check

O endpoint `/api/health` fornece informações sobre:

- Status da aplicação
- Timestamp da requisição
- Tempo de uptime
- Ambiente de execução

### Logs

A aplicação utiliza um sistema de logging personalizado com níveis:

- `INFO` - Informações gerais
- `WARN` - Avisos
- `ERROR` - Erros
- `DEBUG` - Informações de debug (apenas em desenvolvimento)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença ISC. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

Para suporte, entre em contato através dos issues do repositório.
