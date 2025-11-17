import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios, { AxiosInstance } from 'axios';
import { Logger } from '@/utils/logger';
import { SpotifyTrackDto } from '@/common/dtos';
import { EnvConfig } from '@/config/env.config';
import { getErrorStatus } from '@/common/types/axios-error.types';

type MoodType =
  | 'angry'
  | 'disgust'
  | 'fear'
  | 'happy'
  | 'neutral'
  | 'sad'
  | 'surprise';

interface MoodMapping {
  valence: number;
  energy: number;
  danceability: number;
  tempo: number;
}

interface SpotifyUser {
  id: string;
  display_name?: string;
}

interface SpotifyPlaylist {
  id: string;
  name: string;
  external_urls: {
    spotify: string;
  };
}

interface SpotifyTrackResponse {
  id: string;
  name: string;
  artists: Array<{ name: string }>;
  uri: string;
}

interface SpotifySearchResponse {
  tracks: {
    items: SpotifyTrackResponse[];
  };
}

@Injectable()
export class SpotifyService {
  private readonly logger: Logger;
  private readonly httpClient: AxiosInstance;
  private accessToken: string | null = null;
  private tokenExpiresAt: number = 0;

  private readonly moodMapping: Record<MoodType, MoodMapping> = {
    angry: { valence: 0.2, energy: 0.9, danceability: 0.3, tempo: 150 },
    disgust: { valence: 0.1, energy: 0.4, danceability: 0.2, tempo: 100 },
    fear: { valence: 0.2, energy: 0.6, danceability: 0.3, tempo: 130 },
    happy: { valence: 0.9, energy: 0.8, danceability: 0.8, tempo: 120 },
    neutral: { valence: 0.5, energy: 0.5, danceability: 0.5, tempo: 110 },
    sad: { valence: 0.2, energy: 0.3, danceability: 0.2, tempo: 90 },
    surprise: { valence: 0.7, energy: 0.9, danceability: 0.6, tempo: 140 },
  };

  constructor(private readonly configService: ConfigService<EnvConfig>) {
    this.logger = Logger.getInstance(configService);
    this.httpClient = axios.create({
      baseURL: 'https://api.spotify.com/v1',
    });
  }

  private async getAccessToken(): Promise<string> {
    if (this.accessToken && Date.now() < this.tokenExpiresAt) {
      return this.accessToken;
    }

    const clientId = this.configService.get('SPOTIFY_CLIENT_ID', {
      infer: true,
    });
    const clientSecret = this.configService.get('SPOTIFY_CLIENT_SECRET', {
      infer: true,
    });

    if (!clientId || !clientSecret) {
      throw new Error('Spotify client credentials não configuradas');
    }

    const credentials = Buffer.from(`${clientId}:${clientSecret}`).toString(
      'base64',
    );

    try {
      const response = await axios.post(
        'https://accounts.spotify.com/api/token',
        'grant_type=client_credentials',
        {
          headers: {
            Authorization: `Basic ${credentials}`,
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        },
      );

      this.accessToken = response.data.access_token;
      this.tokenExpiresAt = Date.now() + (response.data.expires_in - 60) * 1000;

      this.logger.info(
        'Token de acesso do Spotify obtido com sucesso usando OAuth 2.0',
      );
      return this.accessToken;
    } catch (error) {
      this.logger.error('Erro ao obter token do Spotify', error);
      const status = getErrorStatus(error);
      throw new Error(`Falha na autenticação com Spotify: ${status}`);
    }
  }

  async getRecommendations(
    mood: MoodType,
    limit: number = 20,
  ): Promise<SpotifyTrackDto[]> {
    if (!(mood in this.moodMapping)) {
      throw new Error(`Mood inválido: ${mood}`);
    }

    const token = await this.getAccessToken();
    const searchQueries = this.getSearchQueries(mood);
    const tracks: SpotifyTrackDto[] = [];

    try {
      for (const query of searchQueries) {
        if (tracks.length >= limit) {
          break;
        }

        const response = await this.httpClient.get<SpotifySearchResponse>(
          '/search',
          {
            params: {
              q: query,
              type: 'track',
              limit: Math.min(10, limit - tracks.length),
              market: 'BR',
            },
            headers: {
              Authorization: `Bearer ${token}`,
            },
          },
        );

        for (const track of response.data.tracks.items) {
          if (tracks.length >= limit) {
            break;
          }

          tracks.push({
            id: track.id,
            name: track.name,
            artists: track.artists.map((artist) => artist.name),
            uri: track.uri,
          });
        }
      }

      this.logger.info(`Obtidas ${tracks.length} músicas para mood: ${mood}`);
      return tracks.slice(0, limit);
    } catch (error) {
      this.logger.error('Erro ao buscar músicas', error);
      const status = getErrorStatus(error);
      throw new Error(`Erro na API do Spotify: ${status}`);
    }
  }

  private getSearchQueries(mood: MoodType): string[] {
    const searchQueriesMapping: Record<MoodType, string[]> = {
      angry: [
        'genre:metal',
        'genre:rock',
        'year:2020-2024 metal',
        'year:2020-2024 rock',
      ],
      disgust: [
        'genre:ambient',
        'genre:classical',
        'year:2020-2024 ambient',
        'year:2020-2024 classical',
      ],
      fear: [
        'genre:ambient',
        'genre:industrial',
        'year:2020-2024 ambient',
        'year:2020-2024 industrial',
      ],
      happy: [
        'genre:pop',
        'genre:dance',
        'year:2020-2024 pop',
        'year:2020-2024 dance',
      ],
      neutral: [
        'genre:indie',
        'genre:alternative',
        'year:2020-2024 indie',
        'year:2020-2024 alternative',
      ],
      sad: [
        'genre:blues',
        'genre:soul',
        'year:2020-2024 blues',
        'year:2020-2024 soul',
      ],
      surprise: [
        'genre:electronic',
        'genre:house',
        'year:2020-2024 electronic',
        'year:2020-2024 house',
      ],
    };

    return searchQueriesMapping[mood] || ['genre:pop', 'year:2020-2024 pop'];
  }

  async getCurrentUser(userToken: string): Promise<SpotifyUser> {
    try {
      const response = await this.httpClient.get<SpotifyUser>('/me', {
        headers: {
          Authorization: `Bearer ${userToken}`,
        },
      });

      this.logger.info(
        `Informações do usuário obtidas: ${response.data.display_name || 'N/A'}`,
      );
      return response.data;
    } catch (error) {
      this.logger.error('Erro ao obter usuário', error);
      const status = getErrorStatus(error);
      throw new Error(`Falha ao obter usuário: ${status}`);
    }
  }

  async createPlaylist(
    userToken: string,
    userId: string,
    name: string,
    description: string,
    isPublic: boolean = true,
  ): Promise<SpotifyPlaylist> {
    try {
      const response = await this.httpClient.post<SpotifyPlaylist>(
        `/users/${userId}/playlists`,
        {
          name,
          description,
          public: isPublic,
        },
        {
          headers: {
            Authorization: `Bearer ${userToken}`,
            'Content-Type': 'application/json',
          },
        },
      );

      this.logger.info(
        `Playlist criada com sucesso: ${response.data.id} - ${response.data.name}`,
      );
      return response.data;
    } catch (error) {
      this.logger.error('Erro ao criar playlist', error);
      const status = getErrorStatus(error);
      throw new Error(`Falha ao criar playlist: ${status}`);
    }
  }

  async addTracksToPlaylist(
    userToken: string,
    playlistId: string,
    trackUris: string[],
  ): Promise<unknown> {
    try {
      const response = await this.httpClient.post(
        `/playlists/${playlistId}/tracks`,
        {
          uris: trackUris,
        },
        {
          headers: {
            Authorization: `Bearer ${userToken}`,
            'Content-Type': 'application/json',
          },
        },
      );

      this.logger.info(
        `Adicionadas ${trackUris.length} tracks à playlist ${playlistId}`,
      );
      return response.data;
    } catch (error) {
      this.logger.error('Erro ao adicionar tracks à playlist', error);
      const status = getErrorStatus(error);
      throw new Error(`Falha ao adicionar tracks: ${status}`);
    }
  }
}
