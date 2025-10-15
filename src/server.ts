import { createServer } from 'http';
import dotenv from 'dotenv';
import { logger } from '@/utils/logger';
import app from './app';

// Carregar variáveis de ambiente
dotenv.config();

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

const startServer = (): void => {
  const server = createServer(app);

  server.listen(Number(PORT), HOST, () => {
    logger.info(`🚀 Servidor rodando em http://${HOST}:${PORT}`);
    logger.info(
      `📊 Health check disponível em http://${HOST}:${PORT}/api/health`
    );
    logger.info(`🌍 Ambiente: ${process.env.NODE_ENV || 'development'}`);
  });

  // Graceful shutdown
  const gracefulShutdown = (signal: string): void => {
    logger.info(`Recebido sinal ${signal}. Iniciando shutdown graceful...`);

    server.close(() => {
      logger.info('Servidor HTTP fechado com sucesso');
      process.exit(0);
    });

    // Forçar fechamento após 10 segundos
    setTimeout(() => {
      logger.error('Forçando fechamento do servidor após timeout');
      process.exit(1);
    }, 10000);
  };

  process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
  process.on('SIGINT', () => gracefulShutdown('SIGINT'));

  // Capturar erros não tratados
  process.on('uncaughtException', error => {
    logger.error('Erro não capturado:', error);
    process.exit(1);
  });

  process.on(
    'unhandledRejection',
    (reason: unknown, promise: Promise<unknown>) => {
      logger.error('Promise rejeitada não tratada:', reason as Error, promise);
      process.exit(1);
    }
  );
};

startServer();
