import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_get_health_returns_200_and_health_data(self):
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["status"] == "OK"
        assert "timestamp" in data["data"]
        assert "uptime" in data["data"]
        assert "environment" in data["data"]
        assert data["message"] == "API está funcionando corretamente"
    
    def test_health_response_includes_timestamp_and_uptime(self):
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        health_data = data["data"]
        
        # Verificar se timestamp é uma string válida
        assert isinstance(health_data["timestamp"], str)
        timestamp = datetime.fromisoformat(health_data["timestamp"].replace("Z", "+00:00"))
        assert isinstance(timestamp, datetime)
        
        # Verificar se uptime é um número positivo
        assert isinstance(health_data["uptime"], (int, float))
        assert health_data["uptime"] >= 0
    
    def test_health_response_structure(self):
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estrutura da resposta
        assert "success" in data
        assert "data" in data
        assert "message" in data
        
        # Verificar estrutura dos dados de health
        health_data = data["data"]
        required_fields = ["status", "timestamp", "uptime", "environment"]
        for field in required_fields:
            assert field in health_data


class TestRootEndpoint:
    def test_root_endpoint_returns_success_message(self):
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "API REST Python + FastAPI está funcionando!" in data["message"]
        assert data["version"] == "1.0.0"


class TestNotFoundEndpoint:
    def test_nonexistent_endpoint_returns_404(self):
        response = client.get("/api/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        
        assert data["success"] is False
        assert data["error"] == "Endpoint não encontrado"
        assert data["message"] == "A rota solicitada não existe"
