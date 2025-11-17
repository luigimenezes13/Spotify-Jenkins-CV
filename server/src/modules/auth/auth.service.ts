import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios from 'axios';
import { randomBytes } from 'crypto';
import { Logger } from '@/utils/logger';
import { EnvConfig } from '@/config/env.config';
import { getErrorStatus } from '@/common/types/axios-error.types';

interface SpotifyUser {
  id: string;
  display_name?: string;
}

interface TokenData {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
  scope: string;
}

@Injectable()
export class AuthService {
  private readonly logger: Logger;
  private readonly scopes =
    'playlist-modify-public playlist-modify-private user-read-private';
  private readonly userTokens: Map<string, TokenData> = new Map();

  constructor(private readonly configService: ConfigService<EnvConfig>) {
    this.logger = Logger.getInstance(configService);
  }

  getAuthorizationUrl(state?: string): string {
    if (!state) {
      state = randomBytes(32).toString('base64url');
    }

    const clientId = this.configService.get('SPOTIFY_CLIENT_ID', {
      infer: true,
    });
    const redirectUri = this.configService.get('SPOTIFY_REDIRECT_URI', {
      infer: true,
    });

    if (!clientId) {
      throw new Error('SPOTIFY_CLIENT_ID não configurado');
    }

    const params = new URLSearchParams({
      client_id: clientId,
      response_type: 'code',
      redirect_uri: redirectUri,
      scope: this.scopes,
      state,
    });

    const authUrl = `https://accounts.spotify.com/authorize?${params.toString()}`;
    this.logger.info(`URL de autorização gerada: ${authUrl}`);
    return authUrl;
  }

  async exchangeCodeForToken(code: string, state?: string): Promise<TokenData> {
    const clientId = this.configService.get('SPOTIFY_CLIENT_ID', {
      infer: true,
    });
    const clientSecret = this.configService.get('SPOTIFY_CLIENT_SECRET', {
      infer: true,
    });
    const redirectUri = this.configService.get('SPOTIFY_REDIRECT_URI', {
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
        new URLSearchParams({
          grant_type: 'authorization_code',
          code,
          redirect_uri: redirectUri,
        }),
        {
          headers: {
            Authorization: `Basic ${credentials}`,
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        },
      );

      const tokenData: TokenData = response.data;

      if (state) {
        this.userTokens.set(state, tokenData);
      }

      this.logger.info('Token de acesso obtido com sucesso via OAuth 2.0');
      return tokenData;
    } catch (error) {
      this.logger.error('Erro ao trocar código por token', error);
      const status = getErrorStatus(error);
      throw new Error(`Falha na autenticação OAuth: ${status}`);
    }
  }

  async refreshAccessToken(refreshToken: string): Promise<TokenData> {
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
        new URLSearchParams({
          grant_type: 'refresh_token',
          refresh_token: refreshToken,
        }),
        {
          headers: {
            Authorization: `Basic ${credentials}`,
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        },
      );

      this.logger.info('Token de acesso renovado com sucesso');
      return response.data;
    } catch (error) {
      this.logger.error('Erro ao renovar token', error);
      const status = getErrorStatus(error);
      throw new Error(`Falha ao renovar token: ${status}`);
    }
  }

  async getCurrentUser(accessToken: string): Promise<SpotifyUser> {
    try {
      const response = await axios.get<SpotifyUser>(
        'https://api.spotify.com/v1/me',
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        },
      );

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

  getUserToken(state: string): TokenData | undefined {
    return this.userTokens.get(state);
  }

  storeUserToken(state: string, tokenData: TokenData): void {
    this.userTokens.set(state, tokenData);
  }

  removeUserToken(state: string): void {
    this.userTokens.delete(state);
  }
}
