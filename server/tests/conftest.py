import pytest
import os
from unittest.mock import AsyncMock, MagicMock
from app.models.schemas import SpotifyTrack


@pytest.fixture
def mock_spotify_tracks():
    """Fixture com dados de teste para tracks do Spotify"""
    return [
        SpotifyTrack(
            id="track1",
            name="Happy Song",
            artists=["Artist 1", "Artist 2"],
            uri="spotify:track:track1"
        ),
        SpotifyTrack(
            id="track2", 
            name="Another Happy Song",
            artists=["Artist 3"],
            uri="spotify:track:track2"
        ),
        SpotifyTrack(
            id="track3",
            name="Third Happy Song", 
            artists=["Artist 4", "Artist 5"],
            uri="spotify:track:track3"
        )
    ]


@pytest.fixture
def mock_spotify_recommendations_response():
    """Fixture com resposta mockada do endpoint /recommendations do Spotify"""
    return {
        "tracks": [
            {
                "id": "track1",
                "name": "Happy Song",
                "artists": [{"name": "Artist 1"}, {"name": "Artist 2"}],
                "uri": "spotify:track:track1"
            },
            {
                "id": "track2",
                "name": "Another Happy Song", 
                "artists": [{"name": "Artist 3"}],
                "uri": "spotify:track:track2"
            },
            {
                "id": "track3",
                "name": "Third Happy Song",
                "artists": [{"name": "Artist 4"}, {"name": "Artist 5"}],
                "uri": "spotify:track:track3"
            }
        ]
    }


@pytest.fixture
def mock_spotify_auth_response():
    """Fixture com resposta mockada do endpoint de autenticação do Spotify"""
    return {
        "access_token": "mock_access_token_12345",
        "token_type": "Bearer",
        "expires_in": 3600
    }


@pytest.fixture
def mock_httpx_client(monkeypatch):
    """Fixture para mockar httpx.AsyncClient"""
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={})
    mock_response.raise_for_status = AsyncMock(return_value=None)
    mock_response.status_code = 200
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    
    monkeypatch.setattr("httpx.AsyncClient", lambda: mock_client)
    return mock_client


@pytest.fixture
def test_spotify_credentials():
    """Fixture para configurar credenciais de teste do Spotify"""
    os.environ["SPOTIFY_CLIENT_ID"] = "test_client_id"
    os.environ["SPOTIFY_CLIENT_SECRET"] = "test_client_secret"
    yield
    # Cleanup após o teste
    os.environ.pop("SPOTIFY_CLIENT_ID", None)
    os.environ.pop("SPOTIFY_CLIENT_SECRET", None)


@pytest.fixture
def mock_spotify_service_success(monkeypatch, mock_spotify_tracks):
    """Fixture para mockar SpotifyService com sucesso"""
    mock_service = AsyncMock()
    mock_service.get_recommendations.return_value = mock_spotify_tracks
    monkeypatch.setattr("app.services.spotify_service.spotify_service", mock_service)
    return mock_service


@pytest.fixture
def mock_spotify_service_error(monkeypatch):
    """Fixture para mockar SpotifyService com erro"""
    mock_service = AsyncMock()
    mock_service.get_recommendations.side_effect = Exception("Spotify API Error")
    monkeypatch.setattr("app.services.spotify_service.spotify_service", mock_service)
    return mock_service


@pytest.fixture
def mock_spotify_service_403_error(monkeypatch):
    """Fixture para mockar SpotifyService com erro 403 (endpoint indisponível)"""
    mock_service = AsyncMock()
    mock_service.get_recommendations.side_effect = Exception("Serviço de recomendações temporariamente indisponível")
    monkeypatch.setattr("app.services.spotify_service.spotify_service", mock_service)
    return mock_service


@pytest.fixture
def mock_spotify_service_no_tracks(monkeypatch):
    """Fixture para mockar SpotifyService retornando lista vazia"""
    mock_service = AsyncMock()
    mock_service.get_recommendations.return_value = []
    monkeypatch.setattr("app.services.spotify_service.spotify_service", mock_service)
    return mock_service