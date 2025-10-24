import time
import base64
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
            "fear": {"valence": 0.2, "energy": 0.6, "danceability": 0.3, "tempo": 130},
            "happy": {"valence": 0.9, "energy": 0.8, "danceability": 0.8, "tempo": 120},
            "neutral": {"valence": 0.5, "energy": 0.5, "danceability": 0.5, "tempo": 110},
            "sad": {"valence": 0.2, "energy": 0.3, "danceability": 0.2, "tempo": 90},
            "surprise": {"valence": 0.7, "energy": 0.9, "danceability": 0.6, "tempo": 140}
        }

    async def _get_access_token(self) -> str:
        """Obtém token de acesso do Spotify usando OAuth 2.0 Client Credentials Flow com Basic Authentication"""
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        if not settings.spotify_client_id or not settings.spotify_client_secret:
            raise ValueError("Spotify client credentials não configuradas")

        # Codificar credenciais em Base64 para Basic Authentication
        credentials = f"{settings.spotify_client_id}:{settings.spotify_client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        auth_data = {"grant_type": "client_credentials"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.auth_url,
                    data=auth_data,
                    headers=headers
                )
                response.raise_for_status()
                
                token_data = response.json()
                self._access_token = token_data["access_token"]
                self._token_expires_at = time.time() + token_data["expires_in"] - 60  # 60s de margem
                
                logger.info("Token de acesso do Spotify obtido com sucesso usando OAuth 2.0")
                return self._access_token
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Erro ao obter token do Spotify: {e.response.status_code}")
                raise Exception(f"Falha na autenticação com Spotify: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Erro inesperado ao obter token: {str(e)}")
                raise

    async def get_recommendations(self, mood: str, limit: int = 20) -> List[SpotifyTrack]:
        """Obtém músicas baseadas no mood usando busca por gênero (endpoint /recommendations foi descontinuado)"""
        if mood not in self.mood_mapping:
            raise ValueError(f"Mood inválido: {mood}")

        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Obter gêneros para o mood
        genres = self._get_seed_genres(mood).split(',')
        tracks = []
        
        # Buscar músicas por gênero para cada mood
        search_queries = self._get_search_queries(mood)
        
        async with httpx.AsyncClient() as client:
            try:
                for query in search_queries:
                    if len(tracks) >= limit:
                        break
                        
                    params = {
                        "q": query,
                        "type": "track",
                        "limit": min(10, limit - len(tracks)),
                        "market": "BR"
                    }
                    
                    response = await client.get(
                        f"{self.base_url}/search",
                        params=params,
                        headers=headers
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    for track in data.get("tracks", {}).get("items", []):
                        if len(tracks) >= limit:
                            break
                            
                        artists = [artist["name"] for artist in track["artists"]]
                        tracks.append(SpotifyTrack(
                            id=track["id"],
                            name=track["name"],
                            artists=artists,
                            uri=track["uri"]
                        ))
                
                logger.info(f"Obtidas {len(tracks)} músicas para mood: {mood}")
                return tracks[:limit]
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Erro ao buscar músicas: {e.response.status_code}")
                raise Exception(f"Erro na API do Spotify: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Erro inesperado ao buscar músicas: {str(e)}")
                raise

    def _get_seed_genres(self, mood: str) -> str:
        """Retorna gêneros de semente baseados no mood (apenas gêneros válidos do Spotify)"""
        genre_mapping = {
            "angry": "metal,rock",
            "disgust": "ambient,classical",
            "fear": "ambient,industrial",
            "happy": "pop,dance",
            "neutral": "indie,alternative",
            "sad": "blues,soul",
            "surprise": "electronic,house"
        }
        return genre_mapping.get(mood, "pop")

    def _get_seed_tracks(self, mood: str) -> str:
        """Retorna IDs de tracks populares como seeds baseados no mood"""
        # IDs de tracks populares conhecidas do Spotify
        seed_tracks_mapping = {
            "angry": "4iV5W9uYEdYUVa79Axb7Rh,3n3Ppam7vgaVa1iaRUmn9T",  # Metallica - Enter Sandman, AC/DC - Thunderstruck
            "disgust": "4uLU6hMCjMI75M1A2tKUQC,1hChLm1BtxXDBXntBQzKbQ",  # Enya - Orinoco Flow, Ludovico Einaudi - Nuvole Bianche
            "fear": "2TpxZ7JUBn3uw46aR7qd6V,3n3Ppam7vgaVa1iaRUmn9T",  # Nine Inch Nails - Closer, AC/DC - Thunderstruck
            "happy": "3n3Ppam7vgaVa1iaRUmn9T,4uLU6hMCjMI75M1A2tKUQC",  # Pharrell Williams - Happy, Bruno Mars - Uptown Funk
            "neutral": "4uLU6hMCjMI75M1A2tKUQC,1hChLm1BtxXDBXntBQzKbQ",  # Coldplay - Yellow, Radiohead - Creep
            "sad": "1hChLm1BtxXDBXntBQzKbQ,4uLU6hMCjMI75M1A2tKUQC",  # Adele - Someone Like You, Sam Smith - Stay With Me
            "surprise": "3n3Ppam7vgaVa1iaRUmn9T,4uLU6hMCjMI75M1A2tKUQC"  # Daft Punk - One More Time, Calvin Harris - Summer
        }
        return seed_tracks_mapping.get(mood, "4uLU6hMCjMI75M1A2tKUQC,1hChLm1BtxXDBXntBQzKbQ")  # Default: tracks populares

    def _get_search_queries(self, mood: str) -> List[str]:
        """Retorna queries de busca específicas para cada mood"""
        search_queries_mapping = {
            "angry": ["genre:metal", "genre:rock", "year:2020-2024 metal", "year:2020-2024 rock"],
            "disgust": ["genre:ambient", "genre:classical", "year:2020-2024 ambient", "year:2020-2024 classical"],
            "fear": ["genre:ambient", "genre:industrial", "year:2020-2024 ambient", "year:2020-2024 industrial"],
            "happy": ["genre:pop", "genre:dance", "year:2020-2024 pop", "year:2020-2024 dance"],
            "neutral": ["genre:indie", "genre:alternative", "year:2020-2024 indie", "year:2020-2024 alternative"],
            "sad": ["genre:blues", "genre:soul", "year:2020-2024 blues", "year:2020-2024 soul"],
            "surprise": ["genre:electronic", "genre:house", "year:2020-2024 electronic", "year:2020-2024 house"]
        }
        return search_queries_mapping.get(mood, ["genre:pop", "year:2020-2024 pop"])

    async def get_current_user(self, user_token: str) -> Dict:
        """Obtém informações do usuário atual usando token de usuário"""
        headers = {"Authorization": f"Bearer {user_token}"}
        
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

    async def create_playlist(self, user_token: str, user_id: str, name: str, description: str, public: bool = True) -> Dict:
        """Cria uma playlist real no Spotify"""
        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }
        
        playlist_data = {
            "name": name,
            "description": description,
            "public": public
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/users/{user_id}/playlists",
                    json=playlist_data,
                    headers=headers
                )
                response.raise_for_status()
                
                playlist = response.json()
                logger.info(f"Playlist criada com sucesso: {playlist['id']} - {playlist['name']}")
                return playlist
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Erro ao criar playlist: {e.response.status_code}")
                raise Exception(f"Falha ao criar playlist: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Erro inesperado ao criar playlist: {str(e)}")
                raise

    async def add_tracks_to_playlist(self, user_token: str, playlist_id: str, track_uris: List[str]) -> Dict:
        """Adiciona tracks a uma playlist do Spotify"""
        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }
        
        # Spotify permite adicionar até 100 tracks por vez
        tracks_data = {"uris": track_uris}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/playlists/{playlist_id}/tracks",
                    json=tracks_data,
                    headers=headers
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Adicionadas {len(track_uris)} tracks à playlist {playlist_id}")
                return result
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Erro ao adicionar tracks à playlist: {e.response.status_code}")
                raise Exception(f"Falha ao adicionar tracks: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Erro inesperado ao adicionar tracks: {str(e)}")
                raise


# Instância global do serviço
spotify_service = SpotifyService()
