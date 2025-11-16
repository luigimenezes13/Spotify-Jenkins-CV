import { z } from 'zod';
import { createZodDto } from 'nestjs-zod';
import { IsEnum } from 'class-validator';

export const SpotifyTrackSchema = z.object({
  id: z.string(),
  name: z.string(),
  artists: z.array(z.string()),
  uri: z.string(),
});

export const PlaylistCreateRequestSchema = z.object({
  mood: z.enum(['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']),
});

export const PlaylistCreateResponseSchema = z.object({
  playlist_id: z.string(),
  playlist_url: z.string(),
  tracks: z.array(SpotifyTrackSchema),
});

export class SpotifyTrackDto extends createZodDto(SpotifyTrackSchema) {}
export class PlaylistCreateRequestDto extends createZodDto(PlaylistCreateRequestSchema) {
  @IsEnum(['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise'])
  mood: 'angry' | 'disgust' | 'fear' | 'happy' | 'neutral' | 'sad' | 'surprise';
}
export class PlaylistCreateResponseDto extends createZodDto(PlaylistCreateResponseSchema) {}
