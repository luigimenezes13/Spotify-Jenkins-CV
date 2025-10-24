import { Module } from '@nestjs/common';
import { SpotifyModule } from '../spotify/spotify.module';
import { AuthModule } from '../auth/auth.module';
import { PlaylistController } from './playlist.controller';

@Module({
  imports: [SpotifyModule, AuthModule],
  controllers: [PlaylistController],
})
export class PlaylistModule {}
