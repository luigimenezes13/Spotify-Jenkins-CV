import { Controller, Get } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { ConfigService } from '@nestjs/config';
import { HealthCheckResponseDto } from '@/common/dtos';
import { Logger } from '@/utils/logger';
import { EnvConfig } from '@/config/env.config';

const startTime = Date.now();

@ApiTags('health')
@Controller('health')
export class HealthController {
  private readonly logger: Logger;

  constructor(private readonly configService: ConfigService<EnvConfig>) {
    this.logger = Logger.getInstance(configService);
  }

  @Get()
  @ApiOperation({ summary: 'Health check endpoint' })
  @ApiResponse({
    status: 200,
    description: 'API está funcionando corretamente',
    schema: {
      type: 'object',
      properties: {
        success: { type: 'boolean' },
        data: {
          type: 'object',
          properties: {
            status: { type: 'string' },
            timestamp: { type: 'string' },
            uptime: { type: 'number' },
            environment: { type: 'string' },
          },
        },
        message: { type: 'string' },
      },
    },
  })
  async getHealth(): Promise<{
    success: boolean;
    data: HealthCheckResponseDto;
    message: string;
  }> {
    try {
      const nodeEnv = this.configService.get('NODE_ENV', { infer: true });
      const uptime = (Date.now() - startTime) / 1000;

      const healthData: HealthCheckResponseDto = {
        status: 'OK',
        timestamp: new Date().toISOString(),
        uptime,
        environment: nodeEnv,
      };

      this.logger.info('Health check executado com sucesso', {
        uptime,
        environment: nodeEnv,
      });

      return {
        success: true,
        data: healthData,
        message: 'API está funcionando corretamente',
      };
    } catch (error) {
      this.logger.error('Erro no health check', error);
      throw error;
    }
  }
}
