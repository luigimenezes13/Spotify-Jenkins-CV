import { Request, Response } from 'express';
import { HealthCheckResponse, ApiResponse } from '@/types';

export class HealthController {
  public static getHealth = (
    _req: Request,
    res: Response<ApiResponse<HealthCheckResponse>>
  ): void => {
    try {
      const healthData: HealthCheckResponse = {
        status: 'OK',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        environment: process.env.NODE_ENV || 'development',
      };

      res.status(200).json({
        success: true,
        data: healthData,
        message: 'API está funcionando corretamente',
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: 'Erro interno do servidor',
        message: error instanceof Error ? error.message : 'Erro desconhecido',
      });
    }
  };
}
