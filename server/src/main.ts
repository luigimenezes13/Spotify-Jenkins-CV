import { NestFactory } from '@nestjs/core';
import { FastifyAdapter, NestFastifyApplication } from '@nestjs/platform-fastify';
import { ValidationPipe, Logger as NestLogger } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app.module';
import { GlobalExceptionFilter, NotFoundFilter } from './common/filters';
import { ResponseInterceptor } from './common/interceptors';
import { Logger } from './utils/logger';
import { ConfigService } from '@nestjs/config';
import { EnvConfig } from './config/env.config';

async function bootstrap() {
  const app = await NestFactory.create<NestFastifyApplication>(
    AppModule,
    new FastifyAdapter({
      logger: false,
    }),
  );

  const configService = app.get(ConfigService<EnvConfig>);
  const logger = Logger.getInstance(configService);
  const nestLogger = new NestLogger('Bootstrap');

  const port = configService.get('PORT', { infer: true });
  const host = configService.get('HOST', { infer: true });
  const nodeEnv = configService.get('NODE_ENV', { infer: true });

  app.setGlobalPrefix('api');

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: {
        enableImplicitConversion: true,
      },
    }),
  );

  app.useGlobalFilters(
    new GlobalExceptionFilter(configService),
    new NotFoundFilter(configService),
  );

  app.useGlobalInterceptors(new ResponseInterceptor());

  app.enableCors({
    origin: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true,
  });

  if (nodeEnv !== 'production') {
    const config = new DocumentBuilder()
      .setTitle('Spotify Jenkins CV API')
      .setDescription('API REST desenvolvida com TypeScript, NestJS e integração Jenkins')
      .setVersion('1.0.0')
      .addTag('health', 'Health check endpoints')
      .addTag('auth', 'Autenticação OAuth 2.0 com Spotify')
      .addTag('playlist', 'Criação de playlists baseadas em mood')
      .build();

    const document = SwaggerModule.createDocument(app, config);
    SwaggerModule.setup('api/docs', app, document);
  }

  const gracefulShutdown = (signal: string) => {
    logger.info(`Recebido sinal ${signal}. Iniciando shutdown graceful...`);
    app.close().then(() => {
      logger.info('Aplicação finalizada com sucesso');
      process.exit(0);
    });
  };

  process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
  process.on('SIGINT', () => gracefulShutdown('SIGINT'));

  await app.listen(port, host);

  logger.info(`🚀 Aplicação NestJS iniciada com sucesso`);
  logger.info(`📡 Servidor rodando em http://${host}:${port}`);
  logger.info(`📚 Documentação disponível em http://${host}:${port}/api/docs`);
  logger.info(`🌍 Ambiente: ${nodeEnv}`);

  nestLogger.log(`Application is running on: http://${host}:${port}/api`);
}

bootstrap().catch((error) => {
  console.error('Erro ao iniciar aplicação:', error);
  process.exit(1);
});
