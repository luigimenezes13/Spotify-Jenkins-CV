import signal
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger
from app.api.middlewares.cors import setup_cors_middleware
from app.api.middlewares.error import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    not_found_handler
)
from app.api.routes.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando aplicação FastAPI...")
    yield
    logger.info("🛑 Finalizando aplicação FastAPI...")


app = FastAPI(
    title="Spotify Jenkins CV API",
    description="API REST desenvolvida com Python, FastAPI e integração Jenkins",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar middlewares
setup_cors_middleware(app)

# Registrar routers
app.include_router(health_router, prefix="/api", tags=["health"])

# Rota raiz
@app.get("/")
async def root():
    return {
        "success": True,
        "message": "API REST Python + FastAPI está funcionando!",
        "version": "1.0.0"
    }

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Handler para rotas não encontradas
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    return await not_found_handler(request, exc)


def signal_handler(signum, frame):
    logger.info(f"Recebido sinal {signum}. Iniciando shutdown graceful...")
    sys.exit(0)


# Configurar handlers de sinal para graceful shutdown
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

logger.info("Aplicação FastAPI configurada com sucesso")
