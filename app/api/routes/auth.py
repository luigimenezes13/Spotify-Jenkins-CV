import secrets
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import (
    AuthStatus,
    SpotifyAuthCallback,
    AuthUrlResponse,
    ApiResponse
)
from app.services.spotify_auth_service import spotify_auth_service
from app.core.logging import logger

router = APIRouter()


@router.get("/auth/login", response_model=ApiResponse[AuthUrlResponse])
async def login() -> ApiResponse[AuthUrlResponse]:
    """
    Inicia o fluxo de autenticação OAuth 2.0 com o Spotify.
    
    Retorna a URL de autorização que o usuário deve acessar para fazer login.
    """
    try:
        state = secrets.token_urlsafe(32)
        auth_url = spotify_auth_service.get_authorization_url(state)
        
        auth_response = AuthUrlResponse(
            auth_url=auth_url,
            state=state
        )
        
        logger.info(f"URL de login gerada para state: {state}")
        
        return ApiResponse[AuthUrlResponse](
            success=True,
            data=auth_response,
            message="Acesse a URL de autorização para fazer login no Spotify"
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar URL de login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao gerar URL de login"
        )


@router.get("/auth/callback", response_model=ApiResponse[AuthStatus])
async def callback(
    code: str = Query(..., description="Código de autorização do Spotify"),
    state: str = Query(..., description="Estado para validação de segurança")
) -> ApiResponse[AuthStatus]:
    """
    Callback do OAuth 2.0 do Spotify.
    
    Processa o código de autorização e obtém o token de acesso.
    """
    try:
        # Trocar código por token
        token_data = await spotify_auth_service.exchange_code_for_token(code, state)
        
        # Obter informações do usuário
        user_data = await spotify_auth_service.get_current_user(token_data["access_token"])
        
        # Armazenar token
        spotify_auth_service.store_user_token(state, token_data)
        
        auth_status = AuthStatus(
            authenticated=True,
            user_id=user_data["id"],
            display_name=user_data.get("display_name", user_data.get("id"))
        )
        
        logger.info(f"Usuário autenticado com sucesso: {auth_status.display_name}")
        
        return ApiResponse[AuthStatus](
            success=True,
            data=auth_status,
            message="Autenticação realizada com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro no callback de autenticação: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno na autenticação"
        )


@router.get("/auth/status", response_model=ApiResponse[AuthStatus])
async def get_auth_status(
    state: str = Query(..., description="Estado para verificar autenticação")
) -> ApiResponse[AuthStatus]:
    """
    Verifica o status de autenticação do usuário.
    
    Retorna informações sobre o usuário autenticado se válido.
    """
    try:
        token_data = spotify_auth_service.get_user_token(state)
        
        if not token_data:
            auth_status = AuthStatus(authenticated=False)
            return ApiResponse[AuthStatus](
                success=True,
                data=auth_status,
                message="Usuário não autenticado"
            )
        
        # Verificar se o token ainda é válido obtendo dados do usuário
        try:
            user_data = await spotify_auth_service.get_current_user(token_data["access_token"])
            
            auth_status = AuthStatus(
                authenticated=True,
                user_id=user_data["id"],
                display_name=user_data.get("display_name", user_data.get("id"))
            )
            
            return ApiResponse[AuthStatus](
                success=True,
                data=auth_status,
                message="Usuário autenticado"
            )
            
        except Exception:
            # Token expirado, tentar renovar
            if "refresh_token" in token_data:
                try:
                    new_token_data = await spotify_auth_service.refresh_access_token(
                        token_data["refresh_token"]
                    )
                    spotify_auth_service.store_user_token(state, new_token_data)
                    
                    user_data = await spotify_auth_service.get_current_user(new_token_data["access_token"])
                    
                    auth_status = AuthStatus(
                        authenticated=True,
                        user_id=user_data["id"],
                        display_name=user_data.get("display_name", user_data.get("id"))
                    )
                    
                    return ApiResponse[AuthStatus](
                        success=True,
                        data=auth_status,
                        message="Usuário autenticado (token renovado)"
                    )
                    
                except Exception:
                    # Não foi possível renovar, remover token
                    spotify_auth_service.remove_user_token(state)
                    auth_status = AuthStatus(authenticated=False)
                    return ApiResponse[AuthStatus](
                        success=True,
                        data=auth_status,
                        message="Sessão expirada, faça login novamente"
                    )
            else:
                # Sem refresh token, remover
                spotify_auth_service.remove_user_token(state)
                auth_status = AuthStatus(authenticated=False)
                return ApiResponse[AuthStatus](
                    success=True,
                    data=auth_status,
                    message="Sessão expirada, faça login novamente"
                )
        
    except Exception as e:
        logger.error(f"Erro ao verificar status de autenticação: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao verificar autenticação"
        )


@router.post("/auth/logout", response_model=ApiResponse[dict])
async def logout(
    state: str = Query(..., description="Estado para fazer logout")
) -> ApiResponse[dict]:
    """
    Faz logout do usuário removendo o token armazenado.
    """
    try:
        spotify_auth_service.remove_user_token(state)
        
        logger.info(f"Logout realizado para state: {state}")
        
        return ApiResponse[dict](
            success=True,
            data={},
            message="Logout realizado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao fazer logout: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao fazer logout"
        )
