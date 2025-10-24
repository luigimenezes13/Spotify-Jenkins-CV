# Spotify Jenkins CV - API REST

API REST desenvolvida com TypeScript, NestJS e pnpm, preparada para integração com Jenkins CI/CD.

## 🚀 Tecnologias

- **Node.js** 20 LTS
- **TypeScript** 5+
- **NestJS** 10+ com Fastify adapter
- **Zod** (validação de schemas)
- **Winston** (logging)
- **Jest** (testes)
- **ESLint** + **Prettier** (qualidade de código)
- **pnpm** (gerenciador de pacotes)
- **Docker** (containerização)
- **Jenkins** (CI/CD)

## 📁 Estrutura do Projeto

```
src/
├── main.ts                    # Entrada da aplicação
├── app.module.ts              # Módulo raiz
├── config/
│   ├── config.module.ts       # Módulo de configuração
│   └── env.config.ts          # Validação de variáveis de ambiente
├── common/
│   ├── filters/               # Exception filters
│   ├── interceptors/          # Response interceptors
│   └── dtos/                  # DTOs compartilhados
├── modules/
│   ├── health/
│   │   ├── health.controller.ts
│   │   └── health.module.ts
│   ├── spotify/
│   │   ├── spotify.service.ts
│   │   └── spotify.module.ts
│   ├── auth/
│   │   ├── auth.controller.ts
│   │   ├── auth.service.ts
│   │   └── auth.module.ts
│   └── playlist/
│       ├── playlist.controller.ts
│       └── playlist.module.ts
└── utils/
    └── logger.ts              # Logger personalizado

dist/                          # Código compilado
test/                          # Testes (Jest)
```

## 🛠️ Instalação e Desenvolvimento

### Pré-requisitos

- Node.js >= 20 LTS
- pnpm

### Instalação

```bash
# Clonar o repositório
git clone <repository-url>
cd spotify-jenkins-cv

# Instalar dependências
pnpm install

# Configurar variáveis de ambiente
cp env.example .env
```

### Scripts Disponíveis

```bash
# Desenvolvimento
pnpm run start:dev

# Produção
pnpm run start:prod

# Build
pnpm run build

# Qualidade de código
pnpm run lint:check              # Executa linting
pnpm run lint                    # Executa linting e corrige
pnpm run format:check            # Verifica formatação
pnpm run format                  # Formata código
pnpm run typecheck               # Verifica tipos TypeScript

# Testes
pnpm run test                    # Executa todos os testes
pnpm run test:watch              # Executa testes em modo watch
pnpm run test:cov                # Executa testes com cobertura
pnpm run test:e2e                # Executa testes e2e
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
  "message": "API REST TypeScript + NestJS está funcionando!",
  "version": "1.0.0"
}
```

### Autenticação OAuth 2.0

#### Login
```http
GET /api/auth/login
```

#### Callback
```http
GET /api/auth/callback?code=AUTHORIZATION_CODE&state=STATE_TOKEN
```

#### Status de Autenticação
```http
GET /api/auth/status?state=STATE_TOKEN
```

#### Logout
```http
POST /api/auth/logout?state=STATE_TOKEN
```

## 🎵 Integração com Spotify - Playlist por Mood

### Visão Geral

Esta funcionalidade permite criar **playlists reais no Spotify** baseadas no mood do usuário. A aplicação implementa **OAuth 2.0 Authorization Code Flow** para autenticação de usuários e criação de playlists, além de usar busca por gênero para encontrar músicas relevantes (já que o endpoint `/recommendations` foi descontinuado pelo Spotify em novembro de 2024).

### Configuração do Spotify

#### 1. Credenciais do Spotify

1. Acesse o [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
2. Crie uma nova aplicação
3. Copie o `Client ID` e `Client Secret`
4. **Configure o Redirect URI**: `http://localhost:3000/api/auth/callback`
5. Configure as variáveis de ambiente:

```bash
# Edite o arquivo .env e adicione suas credenciais
SPOTIFY_CLIENT_ID=seu_client_id_aqui
SPOTIFY_CLIENT_SECRET=seu_client_secret_aqui
SPOTIFY_REDIRECT_URI=http://localhost:3000/api/auth/callback
```

### Autenticação OAuth 2.0

A aplicação implementa **OAuth 2.0 Authorization Code Flow** para autenticação de usuários:

#### 1. Iniciar Login

```http
GET /api/auth/login
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "auth_url": "https://accounts.spotify.com/authorize?client_id=...&response_type=code&redirect_uri=...&scope=playlist-modify-public playlist-modify-private user-read-private&state=...",
    "state": "unique_state_token"
  },
  "message": "Acesse a URL de autorização para fazer login no Spotify"
}
```

#### 2. Callback de Autenticação

Após o usuário autorizar no Spotify, ele será redirecionado para:
```
http://localhost:3000/api/auth/callback?code=AUTHORIZATION_CODE&state=STATE_TOKEN
```

#### 3. Verificar Status de Autenticação

```http
GET /api/auth/status?state=STATE_TOKEN
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "authenticated": true,
    "user_id": "spotify_user_id",
    "display_name": "Nome do Usuário"
  },
  "message": "Usuário autenticado"
}
```

### API Endpoint - Playlist

#### POST `/api/playlist/create`

Cria uma playlist **real no Spotify** baseada no mood do usuário.

**Parâmetros:**
- `state` (query parameter): Token de estado da autenticação

**Request Body:**
```json
{
  "mood": "happy"
}
```

**Moods Suportados:**
- `angry`: Músicas com alta energia e baixa positividade (rock, metal)
- `disgust`: Músicas calmas e melancólicas (ambient, experimental)
- `fear`: Músicas tensas e atmosféricas (dark-ambient, industrial)
- `happy`: Músicas alegres e dançantes (pop, dance)
- `neutral`: Músicas equilibradas (indie, alternative)
- `sad`: Músicas melancólicas e emotivas (blues, soul)
- `surprise`: Músicas energéticas e variadas (electronic, house)

**Response (Sucesso):**
```json
{
  "success": true,
  "data": {
    "playlist_id": "37i9dQZF1DXcBWIGoYBM5M",
    "playlist_url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
    "tracks": [
      {
        "id": "4uUG5RXrOk84mYEfFvj3cK",
        "name": "I'm Good (Blue)",
        "artists": ["David Guetta", "Bebe Rexha"],
        "uri": "spotify:track:4uUG5RXrOk84mYEfFvj3cK"
      }
    ]
  },
  "message": "Playlist criada com sucesso no Spotify para o mood: happy"
}
```

**Response (Não Autenticado):**
```json
{
  "detail": {
    "message": "Usuário não autenticado",
    "auth_url": "https://accounts.spotify.com/authorize?client_id=...&response_type=code&redirect_uri=...&scope=playlist-modify-public playlist-modify-private user-read-private&state=...",
    "state": "unique_state_token"
  }
}
```

### Características de Áudio por Mood

| Mood    | Valence | Energy | Danceability | Tempo | Gêneros |
|---------|---------|--------|--------------|-------|---------|
| angry   | 0.2     | 0.9    | 0.3          | 150   | metal, rock |
| disgust | 0.1     | 0.4    | 0.2          | 100   | ambient, classical |
| fear    | 0.2     | 0.6    | 0.3          | 130   | ambient, industrial |
| happy   | 0.9     | 0.8    | 0.8          | 120   | pop, dance |
| neutral | 0.5     | 0.5    | 0.5          | 110   | indie, alternative |
| sad     | 0.2     | 0.3    | 0.2          | 90    | blues, soul |
| surprise| 0.7     | 0.9    | 0.6          | 140   | electronic, house |

### Exemplo de Uso Completo

```bash
# 1. Obter URL de login
curl -X GET "http://localhost:3000/api/auth/login"

# 2. Acessar a URL retornada no navegador e fazer login no Spotify
# 3. Após autorizar, você será redirecionado para o callback

# 4. Verificar status de autenticação
curl -X GET "http://localhost:3000/api/auth/status?state=SEU_STATE_TOKEN"

# 5. Criar playlist (usando o state retornado no login)
curl -X POST "http://localhost:3000/api/playlist/create?state=SEU_STATE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mood": "happy"}'
```

### Fluxo Simplificado

```bash
# Se não estiver autenticado, a API retornará a URL de login automaticamente
curl -X POST "http://localhost:3000/api/playlist/create?state=test123" \
  -H "Content-Type: application/json" \
  -d '{"mood": "happy"}'
# Resposta: {"detail": {"message": "Usuário não autenticado", "auth_url": "..."}}
```

### Documentação Swagger

A documentação interativa da API está disponível em:
- **Desenvolvimento**: http://localhost:3000/api/docs
- **Produção**: http://localhost:3000/api/docs (se NODE_ENV != production)

### Tratamento de Erros

- **400**: Mood inválido ou credenciais não configuradas
- **401**: Usuário não autenticado (retorna URL de login)
- **404**: Nenhuma música encontrada para o mood
- **500**: Erro interno do servidor

### Observações Importantes

✅ **Solução Implementada**: O endpoint `/recommendations` foi descontinuado pelo Spotify em novembro de 2024. A aplicação agora usa **busca por gênero** para encontrar músicas relevantes baseadas no mood.

✅ **Playlists Reais**: As playlists são criadas **diretamente no Spotify** do usuário autenticado e ficam disponíveis em sua conta.

⚠️ **Configuração Obrigatória**: É necessário configurar o **Redirect URI** no Spotify Developer Dashboard: `http://localhost:3000/api/auth/callback`

### Arquitetura da Integração

- **`src/modules/spotify/spotify.service.ts`**: Serviço principal com busca de músicas e criação de playlists
- **`src/modules/auth/auth.service.ts`**: Serviço de autenticação OAuth 2.0 Authorization Code Flow
- **`src/modules/playlist/playlist.controller.ts`**: Controller da API para criação de playlists reais
- **`src/modules/auth/auth.controller.ts`**: Controllers de autenticação OAuth 2.0
- **`src/common/dtos/`**: DTOs e schemas Zod para request/response
- **`src/config/env.config.ts`**: Configurações do Spotify

### Autenticação OAuth 2.0

A aplicação implementa o fluxo **Authorization Code Flow** do OAuth 2.0:

1. **Authorization URL**: Usuário é redirecionado para Spotify para autorização
2. **Callback**: Spotify redireciona de volta com código de autorização
3. **Token Exchange**: Código é trocado por access token e refresh token
4. **Token Management**: Tokens são armazenados e renovados automaticamente
5. **User Authentication**: Permite criar playlists na conta do usuário

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
2. **Setup Environment** - Instalação Node.js 20 via nvm
3. **Install Dependencies** - Instalação das dependências com pnpm
4. **Lint** - Verificação de qualidade de código com ESLint
5. **Format Check** - Verificação de formatação com Prettier
6. **Type Check** - Verificação de tipos TypeScript
7. **Test** - Execução de testes com cobertura
8. **Build** - Compilação da aplicação TypeScript
9. **Build Docker Image** - Construção da imagem Docker
10. **Deploy** - Deploy automático (staging/produção)

### Configuração no Jenkins

1. Criar novo pipeline job
2. Configurar para usar `Jenkinsfile` do repositório
3. Configurar credenciais do Docker Registry (se necessário)
4. Configurar webhooks do Git para trigger automático

## 🧪 Testes

```bash
# Executar todos os testes
pnpm run test

# Executar testes com cobertura
pnpm run test:cov

# Executar testes e2e
pnpm run test:e2e

# Executar testes em modo watch
pnpm run test:watch
```

Os relatórios de cobertura são gerados em `coverage/lcov-report/index.html`.

## 📝 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
NODE_ENV=development
PORT=3000
HOST=0.0.0.0

# Spotify API Configuration
# Obtenha essas credenciais em: https://developer.spotify.com/dashboard/applications
SPOTIFY_CLIENT_ID=seu_client_id_aqui
SPOTIFY_CLIENT_SECRET=seu_client_secret_aqui
SPOTIFY_REDIRECT_URI=http://localhost:3000/api/auth/callback
```

## 🔧 Configuração do Editor

O projeto inclui configurações para:

- **ESLint** - Linting de código TypeScript
- **Prettier** - Formatação automática
- **Jest** - Framework de testes
- **TypeScript** - Verificação de tipos

## 📊 Monitoramento

### Health Check

O endpoint `/api/health` fornece informações sobre:

- Status da aplicação
- Timestamp da requisição
- Tempo de uptime
- Ambiente de execução

### Logs

A aplicação utiliza Winston para logging com níveis:

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
