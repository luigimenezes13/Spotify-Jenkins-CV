import secrets
import base64
from typing import Dict, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger


class SpotifyAuthService:
    def __init__(self):
        self.base_url = "https://api.spotify.com/v1"
        self.auth_url = "https://accounts.spotify.com/authorize"
        self.token_url = "https://accounts.spotify.com/api/token"
        self.scopes = "playlist-modify-public playlist-modify-private user-read-private"
        
        # Armazenamento temporário de tokens (em produção, usar Redis/DB)
        self._user_tokens: Dict[str, Dict] = {}

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Gera URL de autorização para OAuth 2.0"""
        if not state:
            state = secrets.token_urlsafe(32)
            
        params = {
            "client_id": settings.spotify_client_id,
            "response_type": "code",
            "redirect_uri": settings.spotify_redirect_uri,
            "scope": self.scopes,
            "state": state
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        auth_url = f"{self.auth_url}?{query_string}"
        
        logger.info(f"URL de autorização gerada: {auth_url}")
        return auth_url

    async def exchange_code_for_token(self, code: str, state: Optional[str] = None) -> Dict:
        """Troca código de autorização por access token"""
        if not settings.spotify_client_id or not settings.spotify_client_secret:
            raise ValueError("Spotify client credentials não configuradas")

        # Codificar credenciais em Base64 para Basic Authentication
        credentials = f"{settings.spotify_client_id}:{settings.spotify_client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.spotify_redirect_uri
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_url,
                    data=data,
                    headers=headers
                )
                response.raise_for_status()
                
                token_data = response.json()
                
                # Armazenar token temporariamente
                if state:
                    self._user_tokens[state] = token_data
                
                logger.info("Token de acesso obtido com sucesso via OAuth 2.0")
                return token_data
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Erro ao trocar código por token: {e.response.status_code}")
                raise Exception(f"Falha na autenticação OAuth: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Erro inesperado ao trocar código por token: {str(e)}")
                raise

    async def refresh_access_token(self, refresh_token: str) -> Dict:
        """Renova access token usando refresh token"""
        if not settings.spotify_client_id or not settings.spotify_client_secret:
            raise ValueError("Spotify client credentials não configuradas")

        # Codificar credenciais em Base64 para Basic Authentication
        credentials = f"{settings.spotify_client_id}:{settings.spotify_client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_url,
                    data=data,
                    headers=headers
                )
                response.raise_for_status()
                
                token_data = response.json()
                logger.info("Token de acesso renovado com sucesso")
                return token_data
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Erro ao renovar token: {e.response.status_code}")
                raise Exception(f"Falha ao renovar token: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Erro inesperado ao renovar token: {str(e)}")
                raise

    async def get_current_user(self, access_token: str) -> Dict:
        """Obtém informações do usuário atual"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/me",
                    headers=headers
                )
                response.raise_for_status()
                
                user_data = response.json()
                logger.info(f"Informações do usuário obtidas: {user_data.get('display_name', 'N/A')}")
                return user_data
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Erro ao obter usuário: {e.response.status_code}")
                raise Exception(f"Falha ao obter usuário: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Erro inesperado ao obter usuário: {str(e)}")
                raise

    def get_user_token(self, state: str) -> Optional[Dict]:
        """Obtém token armazenado para um usuário"""
        return self._user_tokens.get(state)

    def store_user_token(self, state: str, token_data: Dict) -> None:
        """Armazena token para um usuário"""
        self._user_tokens[state] = token_data

    def remove_user_token(self, state: str) -> None:
        """Remove token de um usuário"""
        self._user_tokens.pop(state, None)


# Instância global do serviço de autenticação
spotify_auth_service = SpotifyAuthService()
