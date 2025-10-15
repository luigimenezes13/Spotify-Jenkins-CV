import { Request, Response } from 'express';
import { HealthController } from '../src/controllers/health.controller';

describe('HealthController', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let responseObject: unknown;

  beforeEach(() => {
    mockRequest = {};
    responseObject = {};

    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn().mockImplementation(result => {
        responseObject = result;
        return mockResponse;
      }),
    };
  });

  describe('getHealth', () => {
    it('deve retornar status 200 e dados de health check', () => {
      HealthController.getHealth(
        mockRequest as Request,
        mockResponse as Response
      );

      expect(mockResponse.status).toHaveBeenCalledWith(200);
      expect(mockResponse.json).toHaveBeenCalled();
      expect(responseObject).toMatchObject({
        success: true,
        data: {
          status: 'OK',
          environment: expect.any(String),
        },
        message: 'API está funcionando corretamente',
      });
    });

    it('deve incluir timestamp e uptime nos dados', () => {
      HealthController.getHealth(
        mockRequest as Request,
        mockResponse as Response
      );

      const response = responseObject as {
        data: { timestamp: string; uptime: number };
      };

      expect(response.data.timestamp).toBeDefined();
      expect(response.data.uptime).toBeGreaterThanOrEqual(0);
      expect(new Date(response.data.timestamp)).toBeInstanceOf(Date);
    });
  });
});
