from typing import Generic, TypeVar, Optional, Literal, List
from pydantic import BaseModel

T = TypeVar('T')


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    uptime: float
    environment: str


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: Optional[str] = None


class SpotifyTrack(BaseModel):
    id: str
    name: str
    artists: List[str]
    uri: str


class PlaylistCreateRequest(BaseModel):
    mood: Literal["angry", "disgust", "happy", "neutral", "surprise"]


class PlaylistCreateResponse(BaseModel):
    playlist_id: str
    playlist_url: str
    tracks: List[SpotifyTrack]
