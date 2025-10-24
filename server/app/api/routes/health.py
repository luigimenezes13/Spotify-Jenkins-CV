import time
from datetime import datetime, timezone
from fastapi import APIRouter
from app.models.schemas import HealthCheckResponse, ApiResponse
from app.core.logging import logger
from app.core.config import settings

router = APIRouter()

# Variável global para armazenar o tempo de início da aplicação
_start_time = time.time()


@router.get("/health", response_model=ApiResponse[HealthCheckResponse])
async def get_health() -> ApiResponse[HealthCheckResponse]:
    try:
        health_data = HealthCheckResponse(
            status="OK",
            timestamp=datetime.now(timezone.utc).isoformat(),
            uptime=time.time() - _start_time,
            environment=settings.node_env
        )
        
        return ApiResponse[HealthCheckResponse](
            success=True,
            data=health_data,
            message="API está funcionando corretamente"
        )
    except Exception as error:
        logger.error("Erro no health check", error)
        raise
