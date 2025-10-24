import pytest
from pydantic import ValidationError
from app.models.schemas import (
    PlaylistCreateRequest,
    PlaylistCreateResponse,
    SpotifyTrack,
    ApiResponse
)


class TestPlaylistCreateRequest:
    def test_valid_moods_are_accepted(self):
        """Testa que todos os moods válidos são aceitos"""
        valid_moods = ["angry", "disgust", "happy", "neutral", "surprise"]
        
        for mood in valid_moods:
            request = PlaylistCreateRequest(mood=mood)
            assert request.mood == mood

    def test_invalid_mood_raises_validation_error(self):
        """Testa que moods inválidos geram erro de validação"""
        invalid_moods = ["sad", "excited", "calm", "energetic", "melancholic", ""]
        
        for mood in invalid_moods:
            with pytest.raises(ValidationError) as exc_info:
                PlaylistCreateRequest(mood=mood)
            
            assert "Input should be" in str(exc_info.value)

    def test_mood_is_case_sensitive(self):
        """Testa que o mood é case-sensitive"""
        with pytest.raises(ValidationError):
            PlaylistCreateRequest(mood="Happy")  # Maiúsculo

    def test_mood_accepts_none_raises_error(self):
        """Testa que mood None gera erro de validação"""
        with pytest.raises(ValidationError):
            PlaylistCreateRequest(mood=None)


class TestSpotifyTrack:
    def test_valid_track_creation(self):
        """Testa criação de track válida"""
        track = SpotifyTrack(
            id="track123",
            name="Test Song",
            artists=["Artist 1", "Artist 2"],
            uri="spotify:track:track123"
        )
        
        assert track.id == "track123"
        assert track.name == "Test Song"
        assert track.artists == ["Artist 1", "Artist 2"]
        assert track.uri == "spotify:track:track123"

    def test_track_with_single_artist(self):
        """Testa track com um único artista"""
        track = SpotifyTrack(
            id="track456",
            name="Single Artist Song",
            artists=["Solo Artist"],
            uri="spotify:track:track456"
        )
        
        assert len(track.artists) == 1
        assert track.artists[0] == "Solo Artist"

    def test_track_with_empty_artists_list(self):
        """Testa track com lista vazia de artistas"""
        track = SpotifyTrack(
            id="track789",
            name="Unknown Artist Song",
            artists=[],
            uri="spotify:track:track789"
        )
        
        assert track.artists == []

    def test_track_requires_all_fields(self):
        """Testa que todos os campos são obrigatórios"""
        with pytest.raises(ValidationError):
            SpotifyTrack(
                id="track123",
                name="Test Song"
                # Faltando artists e uri
            )


class TestPlaylistCreateResponse:
    def test_valid_playlist_response_creation(self, mock_spotify_tracks):
        """Testa criação de resposta de playlist válida"""
        response = PlaylistCreateResponse(
            playlist_id="playlist123",
            playlist_url="https://open.spotify.com/playlist/playlist123",
            tracks=mock_spotify_tracks
        )
        
        assert response.playlist_id == "playlist123"
        assert response.playlist_url == "https://open.spotify.com/playlist/playlist123"
        assert len(response.tracks) == 3
        assert isinstance(response.tracks[0], SpotifyTrack)

    def test_playlist_response_with_empty_tracks(self):
        """Testa resposta de playlist com lista vazia de tracks"""
        response = PlaylistCreateResponse(
            playlist_id="empty_playlist",
            playlist_url="https://open.spotify.com/playlist/empty_playlist",
            tracks=[]
        )
        
        assert response.playlist_id == "empty_playlist"
        assert response.tracks == []

    def test_playlist_response_requires_all_fields(self):
        """Testa que todos os campos são obrigatórios"""
        with pytest.raises(ValidationError):
            PlaylistCreateResponse(
                playlist_id="playlist123"
                # Faltando playlist_url e tracks
            )


class TestApiResponse:
    def test_successful_api_response(self, mock_spotify_tracks):
        """Testa resposta de API bem-sucedida"""
        playlist_data = PlaylistCreateResponse(
            playlist_id="playlist123",
            playlist_url="https://open.spotify.com/playlist/playlist123",
            tracks=mock_spotify_tracks
        )
        
        response = ApiResponse[PlaylistCreateResponse](
            success=True,
            data=playlist_data,
            message="Playlist criada com sucesso"
        )
        
        assert response.success is True
        assert response.data == playlist_data
        assert response.message == "Playlist criada com sucesso"
        assert response.error is None

    def test_error_api_response(self):
        """Testa resposta de API com erro"""
        response = ApiResponse[PlaylistCreateResponse](
            success=False,
            error="Erro interno do servidor",
            message="Algo deu errado"
        )
        
        assert response.success is False
        assert response.error == "Erro interno do servidor"
        assert response.message == "Algo deu errado"
        assert response.data is None

    def test_api_response_with_only_success(self):
        """Testa resposta de API com apenas success definido"""
        response = ApiResponse[PlaylistCreateResponse](success=True)
        
        assert response.success is True
        assert response.data is None
        assert response.message is None
        assert response.error is None
