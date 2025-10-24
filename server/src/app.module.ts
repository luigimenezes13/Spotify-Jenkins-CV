import { Module, Controller, Get } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { HealthModule } from './modules/health/health.module';
import { SpotifyModule } from './modules/spotify/spotify.module';
import { AuthModule } from './modules/auth/auth.module';
import { PlaylistModule } from './modules/playlist/playlist.module';

@Controller()
export class AppController {
  @Get()
  async root() {
    return {
      success: true,
      message: 'API REST TypeScript + NestJS está funcionando!',
      version: '1.0.0',
    };
  }
}

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
    HealthModule,
    SpotifyModule,
    AuthModule,
    PlaylistModule,
  ],
  controllers: [AppController],
})
export class AppModule {}
