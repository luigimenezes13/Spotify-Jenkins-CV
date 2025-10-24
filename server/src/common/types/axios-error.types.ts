export interface AxiosErrorResponse {
  response?: {
    status: number;
    data?: unknown;
  };
  message: string;
}

export function getErrorStatus(error: unknown): string {
  if (error && typeof error === 'object' && 'response' in error) {
    const axiosError = error as AxiosErrorResponse;
    return axiosError.response?.status?.toString() || 'Unknown';
  }
  return 'Unknown';
}
