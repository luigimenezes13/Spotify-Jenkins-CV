import { Catch, ArgumentsHost, NotFoundException } from '@nestjs/common';
import { Request, Response } from 'express';
import { Logger } from '@/utils/logger';
import { ConfigService } from '@nestjs/config';
import { EnvConfig } from '@/config/env.config';

@Catch(NotFoundException)
export class NotFoundFilter {
  private readonly logger: Logger;

  constructor(private readonly configService: ConfigService<EnvConfig>) {
    this.logger = Logger.getInstance(configService);
  }

  catch(exception: NotFoundException, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    const errorResponse = {
      success: false,
      error: 'Rota não encontrada',
      message: `A rota ${request.method} ${request.url} não foi encontrada`,
      timestamp: new Date().toISOString(),
      path: request.url,
      method: request.method,
    };

    this.logger.warn(`404 Not Found: ${request.method} ${request.url}`, {
      url: request.url,
      method: request.method,
      userAgent: request.headers['user-agent'],
      ip: request.ip,
    });

    response.status(404).send(errorResponse);
  }
}
