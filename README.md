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
│   └── middlewares/     # Middlewares CORS e error
├── core/
│   ├── config.py        # Configurações e env vars
│   └── logging.py       # Logger singleton
├── models/
│   └── schemas.py       # Pydantic models (tipos)
└── main.py              # Aplicação FastAPI principal

tests/                   # Testes unitários e integração
└── test_*.py           # Arquivos de teste
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
