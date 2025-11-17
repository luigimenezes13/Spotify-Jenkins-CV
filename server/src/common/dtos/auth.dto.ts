import { z } from 'zod';
import { createZodDto } from 'nestjs-zod';

export const AuthStatusSchema = z.object({
  authenticated: z.boolean(),
  user_id: z.string().optional(),
  display_name: z.string().optional(),
});

export const SpotifyAuthCallbackSchema = z.object({
  code: z.string(),
  state: z.string().optional(),
});

export const AuthUrlResponseSchema = z.object({
  auth_url: z.string(),
  state: z.string(),
});

export class AuthStatusDto extends createZodDto(AuthStatusSchema) {}
export class SpotifyAuthCallbackDto extends createZodDto(
  SpotifyAuthCallbackSchema,
) {}
export class AuthUrlResponseDto extends createZodDto(AuthUrlResponseSchema) {}
