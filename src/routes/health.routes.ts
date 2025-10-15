import { Router } from 'express';
import { HealthController } from '@/controllers/health.controller';

const router: Router = Router();

// Health check endpoint
router.get('/health', HealthController.getHealth);

export default router;
