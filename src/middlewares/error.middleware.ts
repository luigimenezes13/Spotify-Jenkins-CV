import { Request, Response, NextFunction } from 'express';
import { logger } from '@/utils/logger';
import { ErrorResponse } from '@/types';

export const errorHandler = (
  error: Error,
  _req: Request,
  res: Response<ErrorResponse>,
  _next: NextFunction
): void => {
  logger.error('Erro capturado pelo middleware de erro:', error);

  const statusCode = 500;
  const message =
    process.env.NODE_ENV === 'production'
      ? 'Erro interno do servidor'
      : error.message;

  res.status(statusCode).json({
    success: false,
    error: message,
    message: 'Algo deu errado',
  });
};

export const notFoundHandler = (
  _req: Request,
  res: Response<ErrorResponse>,
  _next: NextFunction
): void => {
  res.status(404).json({
    success: false,
    error: 'Endpoint não encontrado',
    message: 'A rota solicitada não existe',
  });
};
