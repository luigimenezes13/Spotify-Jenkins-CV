// Tipos globais da aplicação

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  uptime: number;
  environment: string;
}

export interface ErrorResponse {
  success: false;
  error: string;
  message?: string;
}
