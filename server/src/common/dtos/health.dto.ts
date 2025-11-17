import { z } from 'zod';
import { createZodDto } from 'nestjs-zod';

export const HealthCheckResponseSchema = z.object({
  status: z.string(),
  timestamp: z.string(),
  uptime: z.number(),
  environment: z.string(),
});

export class HealthCheckResponseDto extends createZodDto(
  HealthCheckResponseSchema,
) {}
