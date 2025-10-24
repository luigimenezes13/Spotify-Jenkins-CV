import time
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    PlaylistCreateRequest, 
    PlaylistCreateResponse, 
    ApiResponse,
    SpotifyTrack
)
from app.services.spotify_service import spotify_service
from app.core.logging import logger

router = APIRouter()


@router.post("/playlist/create", response_model=ApiResponse[PlaylistCreateResponse])
async def create_playlist(request: PlaylistCreateRequest) -> ApiResponse[PlaylistCreateResponse]:
    """
    Cria uma playlist baseada no mood do usuário.
    
    Moods suportados:
    - angry: Músicas com alta energia e baixa positividade
    - disgust: Músicas calmas e melancólicas
    - happy: Músicas alegres e dançantes
    - neutral: Músicas equilibradas
    - surprise: Músicas energéticas e variadas
    """
    try:
        logger.info(f"Criando playlist para mood: {request.mood}")
        
        # Obter recomendações do Spotify
        tracks = await spotify_service.get_recommendations(request.mood, limit=20)
        
        if not tracks:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma música encontrada para o mood especificado"
            )
        
        # Simular criação de playlist (em uma implementação real, 
        # seria necessário criar a playlist no Spotify)
        playlist_id = f"mood_playlist_{request.mood}_{int(time.time())}"
        playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
        
        playlist_response = PlaylistCreateResponse(
            playlist_id=playlist_id,
            playlist_url=playlist_url,
            tracks=tracks
        )
        
        logger.info(f"Playlist criada com sucesso: {playlist_id}")
        
        return ApiResponse[PlaylistCreateResponse](
            success=True,
            data=playlist_response,
            message=f"Playlist criada com sucesso para o mood: {request.mood}"
        )
        
    except ValueError as e:
        logger.error(f"Erro de validação: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"Erro ao criar playlist: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao criar playlist"
        )
