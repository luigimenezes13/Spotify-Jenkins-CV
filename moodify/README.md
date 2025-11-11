# Spotisite - Landing Page Spotify com ReactPy

Aplicação frontend desenvolvida com ReactPy que permite login com Spotify e criação de playlists baseadas no mood do usuário.

## Tecnologias

- **ReactPy**: Framework Python para criar interfaces React
- **Starlette**: Servidor ASGI para ReactPy
- **httpx**: Cliente HTTP assíncrono para comunicação com API

## Instalação

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações
```

## Execução

```bash
# Ativar ambiente virtual (se ainda não estiver ativado)
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Executar aplicação
python src/main.py
```

A aplicação estará disponível em `http://localhost:8000` (ou porta configurada em `.env`).

## Estrutura

```
spotisite/
├── src/
│   ├── components/     # Componentes ReactPy
│   ├── services/       # Serviços de API
│   ├── hooks/          # Hooks personalizados
│   ├── App.py          # Componente principal
│   └── main.py         # Entry point
├── static/
│   └── css/            # Estilos CSS
└── requirements.txt
```

## Variáveis de Ambiente

- `API_BASE_URL`: URL base da API backend (padrão: `http://localhost:3000`)
- `PORT`: Porta do servidor ReactPy (padrão: `8000`)

## Funcionalidades

- Login com Spotify via OAuth 2.0
- Seleção de mood para criação de playlist
- Criação de playlist real no Spotify
- Visualização de resultado com link para playlist

