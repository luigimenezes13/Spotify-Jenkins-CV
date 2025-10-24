import pytest
import time
from unittest.mock import AsyncMock, patch
from app.services.spotify_service import SpotifyService
from app.models.schemas import SpotifyTrack


class TestSpotifyServiceMoodMapping:
    def test_mood_mapping_contains_all_expected_moods(self):
        """Testa que o mapeamento contém todos os moods esperados"""
        service = SpotifyService()
        expected_moods = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
        
        for mood in expected_moods:
            assert mood in service.mood_mapping

    def test_angry_mood_mapping(self):
        """Testa mapeamento específico para mood angry"""
        service = SpotifyService()
        angry_features = service.mood_mapping["angry"]
        
        assert angry_features["valence"] == 0.2
        assert angry_features["energy"] == 0.9
        assert angry_features["danceability"] == 0.3
        assert angry_features["tempo"] == 150

    def test_happy_mood_mapping(self):
        """Testa mapeamento específico para mood happy"""
        service = SpotifyService()
        happy_features = service.mood_mapping["happy"]
        
        assert happy_features["valence"] == 0.9
        assert happy_features["energy"] == 0.8
        assert happy_features["danceability"] == 0.8
        assert happy_features["tempo"] == 120

    def test_neutral_mood_mapping(self):
        """Testa mapeamento específico para mood neutral"""
        service = SpotifyService()
        neutral_features = service.mood_mapping["neutral"]
        
        assert neutral_features["valence"] == 0.5
        assert neutral_features["energy"] == 0.5
        assert neutral_features["danceability"] == 0.5
        assert neutral_features["tempo"] == 110

    def test_disgust_mood_mapping(self):
        """Testa mapeamento específico para mood disgust"""
        service = SpotifyService()
        disgust_features = service.mood_mapping["disgust"]
        
        assert disgust_features["valence"] == 0.1
        assert disgust_features["energy"] == 0.4
        assert disgust_features["danceability"] == 0.2
        assert disgust_features["tempo"] == 100

    def test_surprise_mood_mapping(self):
        """Testa mapeamento específico para mood surprise"""
        service = SpotifyService()
        surprise_features = service.mood_mapping["surprise"]
        
        assert surprise_features["valence"] == 0.7
        assert surprise_features["energy"] == 0.9
        assert surprise_features["danceability"] == 0.6
        assert surprise_features["tempo"] == 140

    def test_fear_mood_mapping(self):
        """Testa mapeamento específico para mood fear"""
        service = SpotifyService()
        fear_features = service.mood_mapping["fear"]
        
        assert fear_features["valence"] == 0.2
        assert fear_features["energy"] == 0.6
        assert fear_features["danceability"] == 0.3
        assert fear_features["tempo"] == 130

    def test_sad_mood_mapping(self):
        """Testa mapeamento específico para mood sad"""
        service = SpotifyService()
        sad_features = service.mood_mapping["sad"]
        
        assert sad_features["valence"] == 0.2
        assert sad_features["energy"] == 0.3
        assert sad_features["danceability"] == 0.2
        assert sad_features["tempo"] == 90


class TestSpotifyServiceGenreMapping:
    def test_get_seed_genres_returns_correct_genres(self):
        """Testa que _get_seed_genres retorna gêneros corretos para cada mood"""
        service = SpotifyService()
        
        assert service._get_seed_genres("angry") == "metal,rock"
        assert service._get_seed_genres("disgust") == "ambient,classical"
        assert service._get_seed_genres("fear") == "ambient,industrial"
        assert service._get_seed_genres("happy") == "pop,dance"
        assert service._get_seed_genres("neutral") == "indie,alternative"
        assert service._get_seed_genres("sad") == "blues,soul"
        assert service._get_seed_genres("surprise") == "electronic,house"

    def test_get_seed_genres_returns_default_for_unknown_mood(self):
        """Testa que _get_seed_genres retorna gênero padrão para mood desconhecido"""
        service = SpotifyService()
        assert service._get_seed_genres("unknown_mood") == "pop"

    def test_get_seed_tracks_returns_correct_tracks_for_mood(self):
        """Testa que retorna tracks corretas para cada mood"""
        service = SpotifyService()
        
        # Testa mood angry
        tracks = service._get_seed_tracks("angry")
        assert tracks == "4iV5W9uYEdYUVa79Axb7Rh,3n3Ppam7vgaVa1iaRUmn9T"
        
        # Testa mood happy
        tracks = service._get_seed_tracks("happy")
        assert tracks == "3n3Ppam7vgaVa1iaRUmn9T,4uLU6hMCjMI75M1A2tKUQC"
        
        # Testa mood desconhecido (deve retornar default)
        tracks = service._get_seed_tracks("unknown_mood")
        assert tracks == "4uLU6hMCjMI75M1A2tKUQC,1hChLm1BtxXDBXntBQzKbQ"


class TestSpotifyServiceAuthentication:
    @pytest.mark.asyncio
    async def test_get_access_token_success(self, test_spotify_credentials, mock_httpx_client, mock_spotify_auth_response):
        """Testa obtenção bem-sucedida de token de acesso usando OAuth 2.0 com Basic Authentication"""
        import base64
        
        service = SpotifyService()
        mock_httpx_client.post.return_value.json.return_value = mock_spotify_auth_response
        
        token = await service._get_access_token()
        
        # Verifica se o token foi obtido corretamente
        assert token == "mock_access_token_12345"
        assert service._access_token == "mock_access_token_12345"
        assert service._token_expires_at > time.time()
        
        # Verifica se a requisição foi feita com Basic Authentication
        mock_httpx_client.post.assert_called_once()
        call_args = mock_httpx_client.post.call_args
        
        # Verifica headers
        headers = call_args[1]["headers"]
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Basic ")
        assert headers["Content-Type"] == "application/x-www-form-urlencoded"
        
        # Verifica se as credenciais estão codificadas corretamente
        auth_header = headers["Authorization"]
        encoded_credentials = auth_header.replace("Basic ", "")
        decoded_credentials = base64.b64decode(encoded_credentials).decode()
        assert decoded_credentials == "test_client_id:test_client_secret"
        
        # Verifica se o body contém apenas grant_type
        data = call_args[1]["data"]
        assert data == {"grant_type": "client_credentials"}

    @pytest.mark.asyncio
    async def test_get_access_token_uses_cached_token(self, test_spotify_credentials, mock_httpx_client, mock_spotify_auth_response):
        """Testa que token em cache é reutilizado"""
        service = SpotifyService()
        service._access_token = "cached_token"
        service._token_expires_at = time.time() + 3600  # 1 hora no futuro
        
        token = await service._get_access_token()
        
        assert token == "cached_token"
        # Verifica que não foi feita nova chamada HTTP
        mock_httpx_client.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_access_token_raises_error_when_credentials_missing(self):
        """Testa erro quando credenciais não estão configuradas"""
        service = SpotifyService()
        
        with pytest.raises(ValueError, match="Spotify client credentials não configuradas"):
            await service._get_access_token()

    @pytest.mark.asyncio
    async def test_get_access_token_handles_http_error(self, test_spotify_credentials, mock_httpx_client):
        """Testa tratamento de erro HTTP na autenticação"""
        service = SpotifyService()
        mock_httpx_client.post.return_value.raise_for_status.side_effect = Exception("HTTP 401")
        
        with pytest.raises(Exception, match="Falha na autenticação com Spotify"):
            await service._get_access_token()


class TestSpotifyServiceRecommendations:
    @pytest.mark.asyncio
    async def test_get_recommendations_success(self, test_spotify_credentials, mock_httpx_client, mock_spotify_recommendations_response):
        """Testa obtenção bem-sucedida de recomendações"""
        service = SpotifyService()
        mock_httpx_client.post.return_value.json.return_value = {"access_token": "token", "expires_in": 3600}
        mock_httpx_client.get.return_value.json.return_value = mock_spotify_recommendations_response
        
        tracks = await service.get_recommendations("happy", limit=3)
        
        assert len(tracks) == 3
        assert all(isinstance(track, SpotifyTrack) for track in tracks)
        assert tracks[0].name == "Happy Song"
        assert tracks[0].artists == ["Artist 1", "Artist 2"]

    @pytest.mark.asyncio
    async def test_get_recommendations_with_different_moods(self, test_spotify_credentials, mock_httpx_client, mock_spotify_recommendations_response):
        """Testa recomendações para diferentes moods"""
        service = SpotifyService()
        mock_httpx_client.post.return_value.json.return_value = {"access_token": "token", "expires_in": 3600}
        mock_httpx_client.get.return_value.json.return_value = mock_spotify_recommendations_response
        
        moods = ["angry", "disgust", "happy", "neutral", "surprise"]
        
        for mood in moods:
            tracks = await service.get_recommendations(mood, limit=5)
            assert len(tracks) == 3  # Baseado no mock
            assert all(isinstance(track, SpotifyTrack) for track in tracks)

    @pytest.mark.asyncio
    async def test_get_recommendations_invalid_mood_raises_error(self, test_spotify_credentials):
        """Testa erro para mood inválido"""
        service = SpotifyService()
        
        with pytest.raises(ValueError, match="Mood inválido: invalid_mood"):
            await service.get_recommendations("invalid_mood")

    @pytest.mark.asyncio
    async def test_get_recommendations_handles_403_error(self, test_spotify_credentials, mock_httpx_client):
        """Testa tratamento de erro 403 (endpoint indisponível)"""
        service = SpotifyService()
        mock_httpx_client.post.return_value.json.return_value = {"access_token": "token", "expires_in": 3600}
        
        # Simula erro 403
        from httpx import HTTPStatusError
        mock_response = AsyncMock()
        mock_response.status_code = 403
        mock_httpx_client.get.side_effect = HTTPStatusError("403", request=AsyncMock(), response=mock_response)
        
        with pytest.raises(Exception, match="Serviço de recomendações temporariamente indisponível"):
            await service.get_recommendations("happy")

    @pytest.mark.asyncio
    async def test_get_recommendations_handles_other_http_errors(self, test_spotify_credentials, mock_httpx_client):
        """Testa tratamento de outros erros HTTP"""
        service = SpotifyService()
        mock_httpx_client.post.return_value.json.return_value = {"access_token": "token", "expires_in": 3600}
        
        # Simula erro 500
        from httpx import HTTPStatusError
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_httpx_client.get.side_effect = HTTPStatusError("500", request=AsyncMock(), response=mock_response)
        
        with pytest.raises(Exception, match="Erro na API do Spotify: 500"):
            await service.get_recommendations("happy")

    @pytest.mark.asyncio
    async def test_get_recommendations_handles_general_exception(self, test_spotify_credentials, mock_httpx_client):
        """Testa tratamento de exceção geral"""
        service = SpotifyService()
        mock_httpx_client.post.return_value.json.return_value = {"access_token": "token", "expires_in": 3600}
        mock_httpx_client.get.side_effect = Exception("Network error")
        
        with pytest.raises(Exception, match="Network error"):
            await service.get_recommendations("happy")

    @pytest.mark.asyncio
    async def test_get_recommendations_uses_correct_parameters(self, test_spotify_credentials, mock_httpx_client, mock_spotify_recommendations_response):
        """Testa que os parâmetros corretos são enviados para a API"""
        service = SpotifyService()
        
        # Configurar mock para autenticação
        auth_response = AsyncMock()
        auth_response.json = AsyncMock(return_value={"access_token": "token", "expires_in": 3600})
        auth_response.raise_for_status = AsyncMock(return_value=None)
        mock_httpx_client.post.return_value = auth_response
        
        # Configurar mock para recomendações
        rec_response = AsyncMock()
        rec_response.json = AsyncMock(return_value=mock_spotify_recommendations_response)
        rec_response.raise_for_status = AsyncMock(return_value=None)
        mock_httpx_client.get.return_value = rec_response
        
        await service.get_recommendations("angry", limit=10)
        
        # Verifica que a chamada GET foi feita com os parâmetros corretos
        mock_httpx_client.get.assert_called_once()
        call_args = mock_httpx_client.get.call_args
        
        assert call_args[0][0] == "https://api.spotify.com/v1/recommendations"
        
        params = call_args[1]["params"]
        assert params["limit"] == 10
        assert params["target_valence"] == 0.2  # angry mood
        assert params["target_energy"] == 0.9   # angry mood
        assert params["target_danceability"] == 0.3  # angry mood
        assert params["target_tempo"] == 150    # angry mood
        assert params["seed_genres"] == "metal,rock"  # angry mood (corrigido)
        assert "seed_tracks" in params  # Verifica se seed_tracks está presente
        assert params["seed_tracks"] == "4iV5W9uYEdYUVa79Axb7Rh,3n3Ppam7vgaVa1iaRUmn9T"  # angry mood tracks
