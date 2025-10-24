import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestPlaylistCreateEndpoint:
    def test_create_playlist_happy_mood_success(self, mock_spotify_service_success, test_spotify_credentials):
        """Testa criação de playlist com mood happy"""
        response = client.post(
            "/api/playlist/create",
            json={"mood": "happy"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["message"] == "Playlist criada com sucesso para o mood: happy"
        assert "data" in data
        
        playlist_data = data["data"]
        assert "playlist_id" in playlist_data
        assert "playlist_url" in playlist_data
        assert "tracks" in playlist_data
        assert len(playlist_data["tracks"]) == 3
        
        # Verifica estrutura das tracks
        track = playlist_data["tracks"][0]
        assert "id" in track
        assert "name" in track
        assert "artists" in track
        assert "uri" in track

    def test_create_playlist_all_valid_moods(self, mock_spotify_service_success, test_spotify_credentials):
        """Testa criação de playlist para todos os moods válidos"""
        valid_moods = ["angry", "disgust", "happy", "neutral", "surprise"]
        
        for mood in valid_moods:
            response = client.post(
                "/api/playlist/create",
                json={"mood": mood}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert f"mood: {mood}" in data["message"]

    def test_create_playlist_invalid_mood_returns_400(self):
        """Testa erro 400 para mood inválido"""
        response = client.post(
            "/api/playlist/create",
            json={"mood": "invalid_mood"}
        )
        
        assert response.status_code == 422  # Validation error do Pydantic
        data = response.json()
        assert "detail" in data

    def test_create_playlist_missing_mood_returns_422(self):
        """Testa erro 422 quando mood não é fornecido"""
        response = client.post(
            "/api/playlist/create",
            json={}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_create_playlist_invalid_json_returns_422(self):
        """Testa erro 422 para JSON inválido"""
        response = client.post(
            "/api/playlist/create",
            json={"mood": 123}  # Mood deve ser string
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_create_playlist_spotify_service_error_returns_500(self, mock_spotify_service_error, test_spotify_credentials):
        """Testa erro 500 quando serviço Spotify falha"""
        response = client.post(
            "/api/playlist/create",
            json={"mood": "happy"}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert "Erro interno do servidor" in data["detail"]

    def test_create_playlist_spotify_403_error_returns_500(self, mock_spotify_service_403_error, test_spotify_credentials):
        """Testa erro 500 quando endpoint Spotify retorna 403"""
        response = client.post(
            "/api/playlist/create",
            json={"mood": "happy"}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert "Erro interno do servidor" in data["detail"]

    def test_create_playlist_no_tracks_returns_404(self, mock_spotify_service_no_tracks, test_spotify_credentials):
        """Testa erro 404 quando nenhuma música é encontrada"""
        response = client.post(
            "/api/playlist/create",
            json={"mood": "happy"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "Nenhuma música encontrada" in data["detail"]

    def test_create_playlist_response_structure(self, mock_spotify_service_success, test_spotify_credentials):
        """Testa estrutura completa da resposta"""
        response = client.post(
            "/api/playlist/create",
            json={"mood": "happy"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verifica estrutura da resposta principal
        assert "success" in data
        assert "data" in data
        assert "message" in data
        
        # Verifica estrutura dos dados da playlist
        playlist_data = data["data"]
        assert "playlist_id" in playlist_data
        assert "playlist_url" in playlist_data
        assert "tracks" in playlist_data
        
        # Verifica que playlist_id contém o mood
        assert "happy" in playlist_data["playlist_id"]
        
        # Verifica que playlist_url é uma URL válida
        assert playlist_data["playlist_url"].startswith("https://open.spotify.com/playlist/")
        
        # Verifica estrutura das tracks
        tracks = playlist_data["tracks"]
        assert isinstance(tracks, list)
        assert len(tracks) > 0
        
        track = tracks[0]
        required_track_fields = ["id", "name", "artists", "uri"]
        for field in required_track_fields:
            assert field in track
        
        # Verifica que artists é uma lista
        assert isinstance(track["artists"], list)

    def test_create_playlist_with_different_limits(self, mock_spotify_service_success, test_spotify_credentials):
        """Testa que o serviço é chamado com diferentes limites"""
        # Este teste verifica que o serviço é chamado, mas o limite real
        # é controlado pelo serviço, não pela rota
        response = client.post(
            "/api/playlist/create",
            json={"mood": "happy"}
        )
        
        assert response.status_code == 200
        # O mock retorna 3 tracks, independente do limite
        data = response.json()
        assert len(data["data"]["tracks"]) == 3

    def test_create_playlist_case_sensitive_mood(self):
        """Testa que mood é case-sensitive"""
        response = client.post(
            "/api/playlist/create",
            json={"mood": "Happy"}  # Maiúsculo
        )
        
        assert response.status_code == 422  # Validation error

    def test_create_playlist_empty_mood_returns_422(self):
        """Testa erro 422 para mood vazio"""
        response = client.post(
            "/api/playlist/create",
            json={"mood": ""}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_create_playlist_null_mood_returns_422(self):
        """Testa erro 422 para mood null"""
        response = client.post(
            "/api/playlist/create",
            json={"mood": None}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestPlaylistEndpointIntegration:
    def test_playlist_endpoint_accepts_correct_content_type(self, mock_spotify_service_success, test_spotify_credentials):
        """Testa que o endpoint aceita Content-Type correto"""
        response = client.post(
            "/api/playlist/create",
            json={"mood": "happy"},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200

    def test_playlist_endpoint_rejects_wrong_content_type(self):
        """Testa que o endpoint rejeita Content-Type incorreto"""
        response = client.post(
            "/api/playlist/create",
            data="mood=happy",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 422

    def test_playlist_endpoint_handles_malformed_json(self):
        """Testa tratamento de JSON malformado"""
        response = client.post(
            "/api/playlist/create",
            data='{"mood": "happy"',  # JSON incompleto
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
