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
│   │   └── playlist.py  # Playlist por mood endpoint
│   └── middlewares/     # Middlewares CORS e error
├── core/
│   ├── config.py        # Configurações e env vars
│   └── logging.py       # Logger singleton
├── models/
│   └── schemas.py       # Pydantic models (tipos)
├── services/
│   └── spotify_service.py # Integração com Spotify API
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

## 🎵 Integração com Spotify - Playlist por Mood

### Visão Geral

Esta funcionalidade permite criar playlists no Spotify baseadas no mood do usuário, utilizando a API de recomendações do Spotify.

### Configuração do Spotify

#### 1. Credenciais do Spotify

1. Acesse o [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
2. Crie uma nova aplicação
3. Copie o `Client ID` e `Client Secret`
4. Configure as variáveis de ambiente:

```bash
# Edite o arquivo .env e adicione suas credenciais
SPOTIFY_CLIENT_ID=seu_client_id_aqui
SPOTIFY_CLIENT_SECRET=seu_client_secret_aqui
```

### API Endpoint - Playlist

#### POST `/api/playlist/create`

Cria uma playlist baseada no mood do usuário.

**Request Body:**
```json
{
  "mood": "happy"
}
```

**Moods Suportados:**
- `angry`: Músicas com alta energia e baixa positividade (rock, metal)
- `disgust`: Músicas calmas e melancólicas (ambient, experimental)
- `happy`: Músicas alegres e dançantes (pop, dance)
- `neutral`: Músicas equilibradas (indie, alternative)
- `surprise`: Músicas energéticas e variadas (electronic, house)

**Response:**
```json
{
  "success": true,
  "data": {
    "playlist_id": "mood_playlist_happy_1234567890",
    "playlist_url": "https://open.spotify.com/playlist/mood_playlist_happy_1234567890",
    "tracks": [
      {
        "id": "track_id",
        "name": "Nome da Música",
        "artists": ["Artista 1", "Artista 2"],
        "uri": "spotify:track:track_id"
      }
    ]
  },
  "message": "Playlist criada com sucesso para o mood: happy"
}
```

### Características de Áudio por Mood

| Mood    | Valence | Energy | Danceability | Tempo | Gêneros |
|---------|---------|--------|--------------|-------|---------|
| angry   | 0.2     | 0.9    | 0.3          | 150   | metal, rock, hardcore |
| disgust | 0.1     | 0.4    | 0.2          | 100   | ambient, classical, experimental |
| happy   | 0.9     | 0.8    | 0.8          | 120   | pop, dance, indie-pop |
| neutral | 0.5     | 0.5    | 0.5          | 110   | indie, alternative, folk |
| surprise| 0.7     | 0.9    | 0.6          | 140   | electronic, house, trance |

### Exemplo de Uso

```bash
# Criar playlist para mood "happy"
curl -X POST "http://localhost:3000/api/playlist/create" \
  -H "Content-Type: application/json" \
  -d '{"mood": "happy"}'
```

### Tratamento de Erros

- **400**: Mood inválido ou credenciais não configuradas
- **403**: Endpoint de recomendações não disponível (restrições da API do Spotify)
- **404**: Nenhuma música encontrada para o mood
- **500**: Erro interno do servidor

### Observações Importantes

⚠️ **Limitação da API do Spotify**: Em novembro de 2024, o Spotify restringiu o acesso ao endpoint `/recommendations` para alguns desenvolvedores. Se você receber erro 403, isso indica que o endpoint não está disponível para sua aplicação.

### Arquitetura da Integração

- **`app/services/spotify_service.py`**: Serviço de integração com a API do Spotify
- **`app/api/routes/playlist.py`**: Rota da API para criação de playlists
- **`app/models/schemas.py`**: Modelos Pydantic para request/response
- **`app/core/config.py`**: Configurações do Spotify

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
