import time
from typing import Dict, List, Optional, Tuple
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.models.schemas import SpotifyTrack


class SpotifyService:
    def __init__(self):
        self.base_url = "https://api.spotify.com/v1"
        self.auth_url = "https://accounts.spotify.com/api/token"
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        
        # Mapeamento de mood para características de áudio
        self.mood_mapping = {
            "angry": {"valence": 0.2, "energy": 0.9, "danceability": 0.3, "tempo": 150},
            "disgust": {"valence": 0.1, "energy": 0.4, "danceability": 0.2, "tempo": 100},
            "happy": {"valence": 0.9, "energy": 0.8, "danceability": 0.8, "tempo": 120},
            "neutral": {"valence": 0.5, "energy": 0.5, "danceability": 0.5, "tempo": 110},
            "surprise": {"valence": 0.7, "energy": 0.9, "danceability": 0.6, "tempo": 140}
        }

    async def _get_access_token(self) -> str:
        """Obtém token de acesso do Spotify usando Client Credentials Flow"""
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        if not settings.spotify_client_id or not settings.spotify_client_secret:
            raise ValueError("Spotify client credentials não configuradas")

        auth_data = {
            "grant_type": "client_credentials",
            "client_id": settings.spotify_client_id,
            "client_secret": settings.spotify_client_secret
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.auth_url,
                    data=auth_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                
                token_data = response.json()
                self._access_token = token_data["access_token"]
                self._token_expires_at = time.time() + token_data["expires_in"] - 60  # 60s de margem
                
                logger.info("Token de acesso do Spotify obtido com sucesso")
                return self._access_token
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Erro ao obter token do Spotify: {e.response.status_code}")
                raise Exception(f"Falha na autenticação com Spotify: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Erro inesperado ao obter token: {str(e)}")
                raise

    async def get_recommendations(self, mood: str, limit: int = 20) -> List[SpotifyTrack]:
        """Obtém recomendações de músicas baseadas no mood"""
        if mood not in self.mood_mapping:
            raise ValueError(f"Mood inválido: {mood}")

        audio_features = self.mood_mapping[mood]
        token = await self._get_access_token()

        params = {
            "limit": limit,
            "target_valence": audio_features["valence"],
            "target_energy": audio_features["energy"],
            "target_danceability": audio_features["danceability"],
            "target_tempo": audio_features["tempo"],
            "seed_genres": self._get_seed_genres(mood)
        }

        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/recommendations",
                    params=params,
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                tracks = []
                
                for track in data.get("tracks", []):
                    artists = [artist["name"] for artist in track["artists"]]
                    tracks.append(SpotifyTrack(
                        id=track["id"],
                        name=track["name"],
                        artists=artists,
                        uri=track["uri"]
                    ))
                
                logger.info(f"Obtidas {len(tracks)} recomendações para mood: {mood}")
                return tracks
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    logger.error("Endpoint /recommendations não disponível - restrições da API do Spotify")
                    raise Exception("Serviço de recomendações temporariamente indisponível")
                else:
                    logger.error(f"Erro ao obter recomendações: {e.response.status_code}")
                    raise Exception(f"Erro na API do Spotify: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Erro inesperado ao obter recomendações: {str(e)}")
                raise

    def _get_seed_genres(self, mood: str) -> str:
        """Retorna gêneros de semente baseados no mood"""
        genre_mapping = {
            "angry": "metal,rock,hardcore",
            "disgust": "ambient,classical,experimental",
            "happy": "pop,dance,indie-pop",
            "neutral": "indie,alternative,folk",
            "surprise": "electronic,house,trance"
        }
        return genre_mapping.get(mood, "pop")


# Instância global do serviço
spotify_service = SpotifyService()
