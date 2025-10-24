import { Controller, Post, Body, Query, HttpException, HttpStatus } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiQuery } from '@nestjs/swagger';
import { SpotifyService } from '../spotify/spotify.service';
import { AuthService } from '../auth/auth.service';
import { PlaylistCreateRequestDto, PlaylistCreateResponseDto, AuthUrlResponseDto } from '@/common/dtos';
import { Logger } from '@/utils/logger';
import { ConfigService } from '@nestjs/config';
import { EnvConfig } from '@/config/env.config';

@ApiTags('playlist')
@Controller('playlist')
export class PlaylistController {
  private readonly logger: Logger;

  constructor(
    private readonly spotifyService: SpotifyService,
    private readonly authService: AuthService,
    private readonly configService: ConfigService<EnvConfig>,
  ) {
    this.logger = Logger.getInstance(configService);
  }

  @Post('create')
  @ApiOperation({ 
    summary: 'Cria uma playlist real no Spotify baseada no mood do usuário',
    description: `
      Moods suportados:
      - angry: Músicas com alta energia e baixa positividade
      - disgust: Músicas calmas e melancólicas
      - fear: Músicas tensas e atmosféricas
      - happy: Músicas alegres e dançantes
      - neutral: Músicas equilibradas
      - sad: Músicas melancólicas e emotivas
      - surprise: Músicas energéticas e variadas
    `
  })
  @ApiQuery({ name: 'state', description: 'Estado de autenticação do usuário' })
  @ApiResponse({
    status: 200,
    description: 'Playlist criada com sucesso',
    schema: {
      type: 'object',
      properties: {
        success: { type: 'boolean' },
        data: {
          type: 'object',
          properties: {
            playlist_id: { type: 'string' },
            playlist_url: { type: 'string' },
            tracks: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  name: { type: 'string' },
                  artists: { type: 'array', items: { type: 'string' } },
                  uri: { type: 'string' },
                },
              },
            },
          },
        },
        message: { type: 'string' },
      },
    },
  })
  @ApiResponse({
    status: 401,
    description: 'Usuário não autenticado',
    schema: {
      type: 'object',
      properties: {
        detail: {
          type: 'object',
          properties: {
            message: { type: 'string' },
            auth_url: { type: 'string' },
            state: { type: 'string' },
          },
        },
      },
    },
  })
  async createPlaylist(
    @Body() request: PlaylistCreateRequestDto,
    @Query('state') state: string,
  ): Promise<{
    success: boolean;
    data: PlaylistCreateResponseDto;
    message: string;
  }> {
    try {
      this.logger.info(`Criando playlist para mood: ${request.mood}`);

      const tokenData = this.authService.getUserToken(state);
      if (!tokenData) {
        const authUrl = this.authService.getAuthorizationUrl(state);
        const authResponse: AuthUrlResponseDto = {
          auth_url: authUrl,
          state,
        };

        throw new HttpException(
          {
            message: 'Usuário não autenticado',
            auth_url: authUrl,
            state,
          },
          HttpStatus.UNAUTHORIZED,
        );
      }

      const userData = await this.spotifyService.getCurrentUser(tokenData.access_token);
      const userId = userData.id;
      const userName = userData.display_name || userData.id;

      const tracks = await this.spotifyService.getRecommendations(request.mood, 20);

      if (tracks.length === 0) {
        throw new HttpException(
          'Nenhuma música encontrada para o mood especificado',
          HttpStatus.NOT_FOUND,
        );
      }

      const playlistName = `Mood Playlist - ${request.mood.charAt(0).toUpperCase() + request.mood.slice(1)}`;
      const playlistDescription = `Playlist criada automaticamente baseada no mood: ${request.mood}`;

      const playlist = await this.spotifyService.createPlaylist(
        tokenData.access_token,
        userId,
        playlistName,
        playlistDescription,
        true,
      );

      const trackUris = tracks.map((track) => track.uri);
      await this.spotifyService.addTracksToPlaylist(
        tokenData.access_token,
        playlist.id,
        trackUris,
      );

      const playlistResponse: PlaylistCreateResponseDto = {
        playlist_id: playlist.id,
        playlist_url: playlist.external_urls.spotify,
        tracks,
      };

      this.logger.info(`Playlist real criada com sucesso: ${playlist.id} - ${playlist.name}`);

      return {
        success: true,
        data: playlistResponse,
        message: `Playlist criada com sucesso no Spotify para o mood: ${request.mood}`,
      };
    } catch (error) {
      if (error instanceof HttpException) {
        throw error;
      }

      if (error instanceof Error && error.message.includes('Mood inválido')) {
        this.logger.error(`Erro de validação: ${error.message}`);
        throw new HttpException(error.message, HttpStatus.BAD_REQUEST);
      }

      this.logger.error('Erro ao criar playlist', error);
      throw new HttpException(
        'Erro interno do servidor ao criar playlist',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}
