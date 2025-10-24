import { createLogger, format, transports, Logger as WinstonLogger } from 'winston';
import { ConfigService } from '@nestjs/config';
import { EnvConfig } from '@/config/env.config';

class Logger {
  private static instance: Logger;
  private winstonLogger: WinstonLogger;

  private constructor(configService: ConfigService<EnvConfig>) {
    const nodeEnv = configService.get('NODE_ENV', { infer: true });
    const logLevel = configService.get('LOG_LEVEL', { infer: true });

    this.winstonLogger = createLogger({
      level: logLevel,
      format: format.combine(
        format.timestamp({
          format: 'YYYY-MM-DDTHH:mm:ss.SSSZ',
        }),
        format.errors({ stack: true }),
        format.json(),
      ),
      defaultMeta: { service: 'spotify-jenkins-cv' },
      transports: [
        new transports.Console({
          format: format.combine(
            format.colorize(),
            format.simple(),
            format.printf(({ timestamp, level, message, ...meta }) => {
              return `[${level}] ${timestamp} - ${message} ${
                Object.keys(meta).length ? JSON.stringify(meta) : ''
              }`;
            }),
          ),
        }),
      ],
    });

    if (nodeEnv === 'production') {
      this.winstonLogger.add(
        new transports.File({
          filename: 'logs/error.log',
          level: 'error',
          format: format.combine(format.timestamp(), format.json()),
        }),
      );
      this.winstonLogger.add(
        new transports.File({
          filename: 'logs/combined.log',
          format: format.combine(format.timestamp(), format.json()),
        }),
      );
    }
  }

  public static getInstance(configService?: ConfigService<EnvConfig>): Logger {
    if (!Logger.instance) {
      if (!configService) {
        throw new Error('ConfigService é necessário para inicializar o Logger');
      }
      Logger.instance = new Logger(configService);
    }
    return Logger.instance;
  }

  public info(message: string, meta?: Record<string, unknown>): void {
    this.winstonLogger.info(message, meta);
  }

  public error(message: string, error?: Error | unknown, meta?: Record<string, unknown>): void {
    if (error instanceof Error) {
      this.winstonLogger.error(message, { error: error.message, stack: error.stack, ...meta });
    } else {
      this.winstonLogger.error(message, { error, ...meta });
    }
  }

  public warn(message: string, meta?: Record<string, unknown>): void {
    this.winstonLogger.warn(message, meta);
  }

  public debug(message: string, meta?: Record<string, unknown>): void {
    this.winstonLogger.debug(message, meta);
  }
}

export { Logger };
