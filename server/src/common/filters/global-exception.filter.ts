import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { Request, Response } from 'express';
import { Logger } from '@/utils/logger';
import { ConfigService } from '@nestjs/config';
import { EnvConfig } from '@/config/env.config';

@Catch()
export class GlobalExceptionFilter implements ExceptionFilter {
  private readonly logger: Logger;

  constructor(private readonly configService: ConfigService<EnvConfig>) {
    this.logger = Logger.getInstance(configService);
  }

  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    let status = HttpStatus.INTERNAL_SERVER_ERROR;
    let message = 'Erro interno do servidor';
    let details: unknown = undefined;

    if (exception instanceof HttpException) {
      status = exception.getStatus();
      const exceptionResponse = exception.getResponse();
      
      if (typeof exceptionResponse === 'string') {
        message = exceptionResponse;
      } else if (typeof exceptionResponse === 'object' && exceptionResponse !== null) {
        const responseObj = exceptionResponse as Record<string, unknown>;
        message = (responseObj.message as string) || message;
        details = responseObj;
      }
    } else if (exception instanceof Error) {
      message = exception.message;
    }

    const errorResponse = {
      success: false,
      error: message,
      ...(details && { details }),
      timestamp: new Date().toISOString(),
      path: request.url,
      method: request.method,
    };

    this.logger.error(
      `HTTP ${status} Error: ${message}`,
      exception,
      {
        url: request.url,
        method: request.method,
        status,
        userAgent: request.headers['user-agent'],
        ip: request.ip,
      },
    );

    response.status(status).send(errorResponse);
  }
}
