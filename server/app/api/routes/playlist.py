import time
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import (
    PlaylistCreateRequest, 
    PlaylistCreateResponse, 
    ApiResponse,
    SpotifyTrack,
    AuthUrlResponse
)
from app.services.spotify_service import spotify_service
from app.services.spotify_auth_service import spotify_auth_service
from app.core.logging import logger

router = APIRouter()


@router.post("/playlist/create", response_model=ApiResponse[PlaylistCreateResponse])
async def create_playlist(
    request: PlaylistCreateRequest,
    state: str = Query(..., description="Estado de autenticação do usuário")
) -> ApiResponse[PlaylistCreateResponse]:
    """
    Cria uma playlist real no Spotify baseada no mood do usuário.
    
    Moods suportados:
    - angry: Músicas com alta energia e baixa positividade
    - disgust: Músicas calmas e melancólicas
    - happy: Músicas alegres e dançantes
    - neutral: Músicas equilibradas
    - surprise: Músicas energéticas e variadas
    """
    try:
        logger.info(f"Criando playlist para mood: {request.mood}")
        
        # Verificar se o usuário está autenticado
        token_data = spotify_auth_service.get_user_token(state)
        if not token_data:
            # Gerar URL de autenticação
            auth_url = spotify_auth_service.get_authorization_url(state)
            auth_response = AuthUrlResponse(auth_url=auth_url, state=state)
            
            raise HTTPException(
                status_code=401,
                detail={
                    "message": "Usuário não autenticado",
                    "auth_url": auth_url,
                    "state": state
                }
            )
        
        # Obter informações do usuário
        user_data = await spotify_service.get_current_user(token_data["access_token"])
        user_id = user_data["id"]
        user_name = user_data.get("display_name", user_data.get("id"))
        
        # Obter recomendações do Spotify
        tracks = await spotify_service.get_recommendations(request.mood, limit=20)
        
        if not tracks:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma música encontrada para o mood especificado"
            )
        
        # Criar playlist real no Spotify
        playlist_name = f"Mood Playlist - {request.mood.title()}"
        playlist_description = f"Playlist criada automaticamente baseada no mood: {request.mood}"
        
        playlist = await spotify_service.create_playlist(
            user_token=token_data["access_token"],
            user_id=user_id,
            name=playlist_name,
            description=playlist_description,
            public=True
        )
        
        # Adicionar tracks à playlist
        track_uris = [track.uri for track in tracks]
        await spotify_service.add_tracks_to_playlist(
            user_token=token_data["access_token"],
            playlist_id=playlist["id"],
            track_uris=track_uris
        )
        
        playlist_response = PlaylistCreateResponse(
            playlist_id=playlist["id"],
            playlist_url=playlist["external_urls"]["spotify"],
            tracks=tracks
        )
        
        logger.info(f"Playlist real criada com sucesso: {playlist['id']} - {playlist['name']}")
        
        return ApiResponse[PlaylistCreateResponse](
            success=True,
            data=playlist_response,
            message=f"Playlist criada com sucesso no Spotify para o mood: {request.mood}"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        logger.error(f"Erro de validação: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"Erro ao criar playlist: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao criar playlist"
        )
