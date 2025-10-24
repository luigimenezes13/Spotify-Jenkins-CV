from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.models.schemas import ErrorResponse
from app.core.logging import logger
from app.core.config import settings


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            message="Erro na requisição"
        ).model_dump()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.error(f"Validation Error: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Dados de entrada inválidos",
            message="Verifique os dados enviados na requisição"
        ).model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Erro interno do servidor", exc)
    
    error_message = "Erro interno do servidor"
    if settings.node_env == "development":
        error_message = str(exc)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=error_message,
            message="Algo deu errado"
        ).model_dump()
    )


async def not_found_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="Endpoint não encontrado",
            message="A rota solicitada não existe"
        ).model_dump()
    )
