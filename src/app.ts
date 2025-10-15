import express, { Application, Request, Response } from 'express';
import dotenv from 'dotenv';
import { logger } from '@/utils/logger';
import { corsHandler } from '@/middlewares/cors.middleware';
import { errorHandler, notFoundHandler } from '@/middlewares/error.middleware';
import healthRoutes from '@/routes/health.routes';

// Carregar variáveis de ambiente
dotenv.config();

const createApp = (): Application => {
  const app = express();

  // Middlewares globais
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));
  app.use(corsHandler);

  // Rota raiz
  app.get('/', (req: Request, res: Response) => {
    res.json({
      success: true,
      message: 'API REST Node.js + TypeScript está funcionando!',
      version: process.env.npm_package_version || '1.0.0',
    });
  });

  // Rotas da API
  app.use('/api', healthRoutes);

  // Middlewares de erro (devem vir por último)
  app.use(notFoundHandler);
  app.use(errorHandler);

  logger.info('Aplicação Express configurada com sucesso');
  return app;
};

export default createApp;
