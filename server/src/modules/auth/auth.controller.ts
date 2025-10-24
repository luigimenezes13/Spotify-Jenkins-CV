import { Controller, Get, Post, Query, HttpException, HttpStatus } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiQuery } from '@nestjs/swagger';
import { randomBytes } from 'crypto';
import { AuthService } from './auth.service';
import { AuthStatusDto, AuthUrlResponseDto } from '@/common/dtos';
import { Logger } from '@/utils/logger';
import { ConfigService } from '@nestjs/config';
import { EnvConfig } from '@/config/env.config';

@ApiTags('auth')
@Controller('auth')
export class AuthController {
  private readonly logger: Logger;

  constructor(
    private readonly authService: AuthService,
    private readonly configService: ConfigService<EnvConfig>,
  ) {
    this.logger = Logger.getInstance(configService);
  }

  @Get('login')
  @ApiOperation({ summary: 'Inicia o fluxo de autenticação OAuth 2.0 com o Spotify' })
  @ApiResponse({
    status: 200,
    description: 'URL de autorização gerada com sucesso',
    schema: {
      type: 'object',
      properties: {
        success: { type: 'boolean' },
        data: {
          type: 'object',
          properties: {
            auth_url: { type: 'string' },
            state: { type: 'string' },
          },
        },
        message: { type: 'string' },
      },
    },
  })
  async login(): Promise<{
    success: boolean;
    data: AuthUrlResponseDto;
    message: string;
  }> {
    try {
      const state = randomBytes(32).toString('base64url');
      const authUrl = this.authService.getAuthorizationUrl(state);

      const authResponse: AuthUrlResponseDto = {
        auth_url: authUrl,
        state,
      };

      this.logger.info(`URL de login gerada para state: ${state}`);

      return {
        success: true,
        data: authResponse,
        message: 'Acesse a URL de autorização para fazer login no Spotify',
      };
    } catch (error) {
      this.logger.error('Erro ao gerar URL de login', error);
      throw new HttpException(
        'Erro interno ao gerar URL de login',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Get('callback')
  @ApiOperation({ summary: 'Callback do OAuth 2.0 do Spotify' })
  @ApiQuery({ name: 'code', description: 'Código de autorização do Spotify' })
  @ApiQuery({ name: 'state', description: 'Estado para validação de segurança' })
  @ApiResponse({
    status: 200,
    description: 'Autenticação realizada com sucesso',
    schema: {
      type: 'object',
      properties: {
        success: { type: 'boolean' },
        data: {
          type: 'object',
          properties: {
            authenticated: { type: 'boolean' },
            user_id: { type: 'string' },
            display_name: { type: 'string' },
          },
        },
        message: { type: 'string' },
      },
    },
  })
  async callback(
    @Query('code') code: string,
    @Query('state') state: string,
  ): Promise<{
    success: boolean;
    data: AuthStatusDto;
    message: string;
  }> {
    try {
      const tokenData = await this.authService.exchangeCodeForToken(code, state);
      const userData = await this.authService.getCurrentUser(tokenData.access_token);
      this.authService.storeUserToken(state, tokenData);

      const authStatus: AuthStatusDto = {
        authenticated: true,
        user_id: userData.id,
        display_name: userData.display_name || userData.id,
      };

      this.logger.info(`Usuário autenticado com sucesso: ${authStatus.display_name}`);

      return {
        success: true,
        data: authStatus,
        message: 'Autenticação realizada com sucesso',
      };
    } catch (error) {
      this.logger.error('Erro no callback de autenticação', error);
      throw new HttpException(
        'Erro interno na autenticação',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Get('status')
  @ApiOperation({ summary: 'Verifica o status de autenticação do usuário' })
  @ApiQuery({ name: 'state', description: 'Estado para verificar autenticação' })
  @ApiResponse({
    status: 200,
    description: 'Status de autenticação verificado',
    schema: {
      type: 'object',
      properties: {
        success: { type: 'boolean' },
        data: {
          type: 'object',
          properties: {
            authenticated: { type: 'boolean' },
            user_id: { type: 'string' },
            display_name: { type: 'string' },
          },
        },
        message: { type: 'string' },
      },
    },
  })
  async getAuthStatus(
    @Query('state') state: string,
  ): Promise<{
    success: boolean;
    data: AuthStatusDto;
    message: string;
  }> {
    try {
      const tokenData = this.authService.getUserToken(state);

      if (!tokenData) {
        const authStatus: AuthStatusDto = { authenticated: false };
        return {
          success: true,
          data: authStatus,
          message: 'Usuário não autenticado',
        };
      }

      try {
        const userData = await this.authService.getCurrentUser(tokenData.access_token);
        const authStatus: AuthStatusDto = {
          authenticated: true,
          user_id: userData.id,
          display_name: userData.display_name || userData.id,
        };

        return {
          success: true,
          data: authStatus,
          message: 'Usuário autenticado',
        };
      } catch (error) {
        if (tokenData.refresh_token) {
          try {
            const newTokenData = await this.authService.refreshAccessToken(tokenData.refresh_token);
            this.authService.storeUserToken(state, newTokenData);

            const userData = await this.authService.getCurrentUser(newTokenData.access_token);
            const authStatus: AuthStatusDto = {
              authenticated: true,
              user_id: userData.id,
              display_name: userData.display_name || userData.id,
            };

            return {
              success: true,
              data: authStatus,
              message: 'Usuário autenticado (token renovado)',
            };
          } catch (refreshError) {
            this.authService.removeUserToken(state);
            const authStatus: AuthStatusDto = { authenticated: false };
            return {
              success: true,
              data: authStatus,
              message: 'Sessão expirada, faça login novamente',
            };
          }
        } else {
          this.authService.removeUserToken(state);
          const authStatus: AuthStatusDto = { authenticated: false };
          return {
            success: true,
            data: authStatus,
            message: 'Sessão expirada, faça login novamente',
          };
        }
      }
    } catch (error) {
      this.logger.error('Erro ao verificar status de autenticação', error);
      throw new HttpException(
        'Erro interno ao verificar autenticação',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Post('logout')
  @ApiOperation({ summary: 'Faz logout do usuário removendo o token armazenado' })
  @ApiQuery({ name: 'state', description: 'Estado para fazer logout' })
  @ApiResponse({
    status: 200,
    description: 'Logout realizado com sucesso',
    schema: {
      type: 'object',
      properties: {
        success: { type: 'boolean' },
        data: { type: 'object' },
        message: { type: 'string' },
      },
    },
  })
  async logout(
    @Query('state') state: string,
  ): Promise<{
    success: boolean;
    data: Record<string, never>;
    message: string;
  }> {
    try {
      this.authService.removeUserToken(state);
      this.logger.info(`Logout realizado para state: ${state}`);

      return {
        success: true,
        data: {},
        message: 'Logout realizado com sucesso',
      };
    } catch (error) {
      this.logger.error('Erro ao fazer logout', error);
      throw new HttpException(
        'Erro interno ao fazer logout',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}
