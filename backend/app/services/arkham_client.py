"""
Arkham Intelligence API Client
Fetches whale transaction data and entity attribution from Arkham.
"""

import os
import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio
from functools import lru_cache

# Get API key from environment
ARKHAM_API_KEY = os.getenv("ARKHAM_API_KEY", "")
ARKHAM_BASE_URL = "https://api.arkhamintelligence.com"


class ArkhamClient:
    """Client for Arkham Intelligence API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or ARKHAM_API_KEY
        self.base_url = ARKHAM_BASE_URL
        self.headers = {
            "API-Key": self.api_key,
            "Content-Type": "application/json",
        }
        self._last_request_time = 0
        self._min_interval = 0.1  # 10 req/sec to be safe
        
    def is_configured(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)
    
    async def _rate_limit(self):
        """Simple rate limiting."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()
    
    async def _request(self, method: str, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make authenticated request to Arkham API."""
        if not self.is_configured():
            return None
            
        await self._rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    print("[Arkham] Invalid API key")
                    return None
                elif response.status_code == 429:
                    print("[Arkham] Rate limited, waiting...")
                    await asyncio.sleep(1)
                    return await self._request(method, endpoint, params)
                else:
                    print(f"[Arkham] Error {response.status_code}: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"[Arkham] Request failed: {e}")
            return None
    
    async def get_recent_transfers(
        self,
        limit: int = 20,
        min_usd: float = 1000000,  # $1M minimum
        chains: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent large transfers.
        
        Args:
            limit: Number of transfers to fetch
            min_usd: Minimum USD value to filter
            chains: List of chains to filter (e.g., ['ethereum', 'bitcoin'])
            
        Returns:
            List of transfer objects with entity attribution
        """
        params = {
            "limit": limit,
            "minUsd": min_usd,
        }
        
        if chains:
            params["chains"] = ",".join(chains)
        
        result = await self._request("GET", "/transfers", params)
        
        if result and "transfers" in result:
            return self._format_transfers(result["transfers"])
        
        return []
    
    async def get_entity_info(self, entity_id: str) -> Optional[Dict]:
        """
        Get information about a known entity (exchange, fund, etc).
        
        Args:
            entity_id: Entity identifier (e.g., 'binance', 'ftx-hacker')
            
        Returns:
            Entity information including addresses and metadata
        """
        result = await self._request("GET", f"/intelligence/entity/{entity_id}")
        return result
    
    async def get_address_attribution(self, address: str) -> Optional[Dict]:
        """
        Get entity attribution for an address.
        
        Args:
            address: Blockchain address to lookup
            
        Returns:
            Entity information if address is attributed
        """
        result = await self._request("GET", f"/intelligence/address/{address}")
        return result
    
    def _format_transfers(self, transfers: List[Dict]) -> List[Dict]:
        """Format transfers into standardized format."""
        formatted = []
        
        for tx in transfers:
            try:
                formatted.append({
                    "tx_hash": tx.get("transactionHash", ""),
                    "chain": tx.get("chain", "unknown"),
                    "from_address": tx.get("fromAddress", {}).get("address", ""),
                    "from_entity": tx.get("fromAddress", {}).get("arkhamEntity", {}).get("name", "Unknown Wallet"),
                    "from_label": tx.get("fromAddress", {}).get("arkhamLabel", {}).get("name", ""),
                    "to_address": tx.get("toAddress", {}).get("address", ""),
                    "to_entity": tx.get("toAddress", {}).get("arkhamEntity", {}).get("name", "Unknown Wallet"),
                    "to_label": tx.get("toAddress", {}).get("arkhamLabel", {}).get("name", ""),
                    "value_usd": float(tx.get("unitValue", 0)),
                    "token_symbol": tx.get("tokenSymbol", ""),
                    "token_amount": float(tx.get("tokenAmount", 0)),
                    "timestamp": tx.get("blockTimestamp", ""),
                    "source": "arkham",
                })
            except Exception as e:
                print(f"[Arkham] Error formatting transfer: {e}")
                continue
                
        return formatted


# Singleton instance
_arkham_client: Optional[ArkhamClient] = None


def get_arkham_client() -> ArkhamClient:
    """Get or create Arkham client singleton."""
    global _arkham_client
    if _arkham_client is None:
        _arkham_client = ArkhamClient()
    return _arkham_client
