import httpx
import os
from typing import Dict, Optional, Any
from dotenv import load_dotenv

load_dotenv()


class ApiClient:
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:3000")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def login(self) -> Dict[str, Any]:
        response = await self.client.get(f"{self.base_url}/api/auth/login")
        response.raise_for_status()
        return response.json()

    async def get_auth_status(self, state: str) -> Dict[str, Any]:
        response = await self.client.get(
            f"{self.base_url}/api/auth/status",
            params={"state": state}
        )
        response.raise_for_status()
        return response.json()

    async def create_playlist(self, mood: str, state: str) -> Dict[str, Any]:
        response = await self.client.post(
            f"{self.base_url}/api/playlist/create",
            params={"state": state},
            json={"mood": mood}
        )
        response.raise_for_status()
        return response.json()

    async def logout(self, state: str) -> Dict[str, Any]:
        response = await self.client.post(
            f"{self.base_url}/api/auth/logout",
            params={"state": state}
        )
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()


api_client = ApiClient()

