# Spotify Jenkins CV - API REST

API REST desenvolvida com Python, FastAPI e pip, preparada para integração com Jenkins CI/CD.

## 🚀 Tecnologias

- **Python** 3.12
- **FastAPI** 0.104+
- **Pydantic** 2.5+ (validação e serialização)
- **Uvicorn** (servidor ASGI)
- **pytest** (testes)
- **ruff** + **black** (qualidade de código)
- **Docker** (containerização)
- **Jenkins** (CI/CD)

## 📁 Estrutura do Projeto

```
app/
├── api/
│   ├── routes/          # Routers do FastAPI
│   │   ├── health.py    # Health check endpoint
│   │   ├── playlist.py  # Playlist por mood endpoint
│   │   └── auth.py      # Autenticação OAuth 2.0
│   └── middlewares/     # Middlewares CORS e error
├── core/
│   ├── config.py        # Configurações e env vars
│   └── logging.py       # Logger singleton
├── models/
│   └── schemas.py       # Pydantic models (tipos)
├── services/
│   ├── spotify_service.py # Integração com Spotify API
│   └── spotify_auth_service.py # Autenticação OAuth 2.0
└── main.py              # Aplicação FastAPI principal

tests/                   # Testes unitários e integração
├── unit/                # Testes unitários
│   ├── test_schemas.py  # Testes dos schemas Pydantic
│   └── test_spotify_service.py # Testes do serviço Spotify
├── test_health.py       # Testes do health endpoint
├── test_playlist.py     # Testes e2e da playlist
└── conftest.py          # Fixtures compartilhadas
```

## 🛠️ Instalação e Desenvolvimento

### Pré-requisitos

- Python >= 3.12
- pip

### Instalação

```bash
# Clonar o repositório
git clone <repository-url>
cd spotify-jenkins-cv

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -e .[dev]

# Configurar variáveis de ambiente
cp .env.example .env
```

### Scripts Disponíveis

```bash
# Desenvolvimento
uvicorn app.main:app --reload --host 0.0.0.0 --port 3000

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 3000

# Qualidade de código
ruff check app/ tests/           # Executa linting
black app/ tests/                # Formata código
black --check app/ tests/        # Verifica formatação

# Testes
pytest                           # Executa todos os testes
pytest --cov=app                # Executa testes com cobertura
pytest --cov=app --cov-report=html  # Gera relatório HTML
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
  "message": "API REST Python + FastAPI está funcionando!",
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

- **`app/services/spotify_service.py`**: Serviço principal com busca de músicas e criação de playlists
- **`app/services/spotify_auth_service.py`**: Serviço de autenticação OAuth 2.0 Authorization Code Flow
- **`app/api/routes/playlist.py`**: Rota da API para criação de playlists reais
- **`app/api/routes/auth.py`**: Rotas de autenticação OAuth 2.0
- **`app/models/schemas.py`**: Modelos Pydantic para request/response
- **`app/core/config.py`**: Configurações do Spotify

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
2. **Setup Environment** - Instalação Python 3.12
3. **Install Dependencies** - Instalação das dependências
4. **Lint** - Verificação de qualidade de código com ruff
5. **Format Check** - Verificação de formatação com black
6. **Test** - Execução de testes com cobertura
7. **Build Docker Image** - Construção da imagem Docker
8. **Deploy** - Deploy automático (staging/produção)

### Configuração no Jenkins

1. Criar novo pipeline job
2. Configurar para usar `Jenkinsfile` do repositório
3. Configurar credenciais do Docker Registry (se necessário)
4. Configurar webhooks do Git para trigger automático

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar testes com cobertura
pytest --cov=app

# Executar com relatório HTML
pytest --cov=app --cov-report=html
```

Os relatórios de cobertura são gerados em `htmlcov/index.html`.

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

- **ruff** - Linting de código Python
- **black** - Formatação automática
- **pytest** - Framework de testes

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
