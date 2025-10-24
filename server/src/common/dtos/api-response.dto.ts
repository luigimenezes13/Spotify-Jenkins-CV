import { z } from 'zod';
import { createZodDto } from 'nestjs-zod';

export const ApiResponseSchema = <T extends z.ZodType>(dataSchema: T) =>
  z.object({
    success: z.boolean(),
    data: dataSchema.optional(),
    message: z.string().optional(),
    error: z.string().optional(),
  });

export const ErrorResponseSchema = z.object({
  success: z.literal(false),
  error: z.string(),
  message: z.string().optional(),
});

export class ErrorResponseDto extends createZodDto(ErrorResponseSchema) {}
