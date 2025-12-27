"""
Whale Alert API Client
Fetches large transaction alerts from Whale Alert.
"""

import os
import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio

# Get API key from environment
WHALE_ALERT_API_KEY = os.getenv("WHALE_ALERT_API_KEY", "")
WHALE_ALERT_BASE_URL = "https://api.whale-alert.io/v1"


class WhaleAlertClient:
    """Client for Whale Alert API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or WHALE_ALERT_API_KEY
        self.base_url = WHALE_ALERT_BASE_URL
        self._last_request_time = 0
        self._min_interval = 6.0  # 10 req/min = 1 per 6 seconds for free tier
        
    def is_configured(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)
    
    async def _rate_limit(self):
        """Simple rate limiting for free tier (10 req/min)."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()
    
    async def _request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make authenticated request to Whale Alert API."""
        if not self.is_configured():
            return None
            
        await self._rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        # Add API key to params
        if params is None:
            params = {}
        params["api_key"] = self.api_key
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    print("[WhaleAlert] Invalid API key")
                    return None
                elif response.status_code == 429:
                    print("[WhaleAlert] Rate limited, waiting...")
                    await asyncio.sleep(60)  # Wait 1 minute for free tier
                    return await self._request(endpoint, params)
                else:
                    print(f"[WhaleAlert] Error {response.status_code}: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"[WhaleAlert] Request failed: {e}")
            return None
    
    async def check_status(self) -> Dict[str, Any]:
        """
        Check API status and remaining quota.
        
        Returns:
            Status information including blockchain sync status
        """
        result = await self._request("/status")
        
        if result and result.get("result") == "success":
            return {
                "status": "online",
                "blockchains": result.get("blockchains", []),
            }
        
        return {"status": "offline"}
    
    async def get_recent_transactions(
        self,
        min_value: int = 500000,  # $500k minimum (Whale Alert default)
        limit: int = 20,
        currency: str = None,
        start_time: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent large transactions.
        
        Args:
            min_value: Minimum USD value to filter
            limit: Number of transactions to fetch (max 100)
            currency: Filter by specific currency (e.g., 'btc', 'eth')
            start_time: Start time for transactions (default: 1 hour ago)
            
        Returns:
            List of formatted transaction objects
        """
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(hours=24)
        
        params = {
            "min_value": min_value,
            "limit": min(limit, 100),
            "start": int(start_time.timestamp()),
        }
        
        if currency:
            params["currency"] = currency.lower()
        
        result = await self._request("/transactions", params)
        
        if result and result.get("result") == "success":
            return self._format_transactions(result.get("transactions", []))
        
        return []
    
    async def get_transaction(self, tx_hash: str, blockchain: str) -> Optional[Dict]:
        """
        Get specific transaction by hash.
        
        Args:
            tx_hash: Transaction hash
            blockchain: Blockchain name (e.g., 'bitcoin', 'ethereum')
            
        Returns:
            Transaction details if found
        """
        params = {"hash": tx_hash}
        result = await self._request(f"/transaction/{blockchain}", params)
        
        if result and result.get("result") == "success":
            txs = result.get("transactions", [])
            if txs:
                formatted = self._format_transactions(txs)
                return formatted[0] if formatted else None
        
        return None
    
    def _format_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Format transactions into standardized format."""
        formatted = []
        
        for tx in transactions:
            try:
                # Determine if it's exchange related
                from_type = tx.get("from", {}).get("owner_type", "")
                to_type = tx.get("to", {}).get("owner_type", "")
                
                # Determine transaction type
                if to_type == "exchange":
                    tx_type = "exchange_deposit"  # Potential sell
                elif from_type == "exchange":
                    tx_type = "exchange_withdrawal"  # Potential buy/accumulation
                else:
                    tx_type = "transfer"
                
                formatted.append({
                    "tx_hash": tx.get("hash", ""),
                    "chain": tx.get("blockchain", "unknown"),
                    "from_address": tx.get("from", {}).get("address", ""),
                    "from_entity": tx.get("from", {}).get("owner", "Unknown Wallet"),
                    "from_type": from_type,
                    "to_address": tx.get("to", {}).get("address", ""),
                    "to_entity": tx.get("to", {}).get("owner", "Unknown Wallet"),
                    "to_type": to_type,
                    "value_usd": float(tx.get("amount_usd", 0)),
                    "token_symbol": tx.get("symbol", "").upper(),
                    "token_amount": float(tx.get("amount", 0)),
                    "timestamp": datetime.fromtimestamp(tx.get("timestamp", 0)).isoformat(),
                    "tx_type": tx_type,
                    "source": "whale_alert",
                })
            except Exception as e:
                print(f"[WhaleAlert] Error formatting transaction: {e}")
                continue
                
        return formatted
    
    def format_whale_message(self, tx: Dict) -> str:
        """
        Format transaction into human-readable whale message.
        
        Args:
            tx: Formatted transaction dict
            
        Returns:
            Human-readable message string
        """
        symbol = tx.get("token_symbol", "CRYPTO")
        value = tx.get("value_usd", 0)
        amount = tx.get("token_amount", 0)
        from_entity = tx.get("from_entity", "Unknown")
        to_entity = tx.get("to_entity", "Unknown")
        tx_type = tx.get("tx_type", "transfer")
        
        # Format value
        if value >= 1e9:
            value_str = f"${value/1e9:.2f}B"
        elif value >= 1e6:
            value_str = f"${value/1e6:.2f}M"
        elif value >= 1e3:
            value_str = f"${value/1e3:.0f}K"
        else:
            value_str = f"${value:.0f}"
        
        # Format amount
        if amount >= 1e6:
            amount_str = f"{amount/1e6:.2f}M"
        elif amount >= 1e3:
            amount_str = f"{amount/1e3:.1f}K"
        else:
            amount_str = f"{amount:.2f}"
        
        if tx_type == "exchange_deposit":
            return f"🔴 {from_entity} moved {amount_str} ${symbol} ({value_str}) to {to_entity}. Potential sell pressure."
        elif tx_type == "exchange_withdrawal":
            return f"🟢 {from_entity} withdrew {amount_str} ${symbol} ({value_str}) to cold wallet. Accumulation signal."
        else:
            return f"🐋 {amount_str} ${symbol} ({value_str}) transferred from {from_entity} to {to_entity}."


# Singleton instance
_whale_alert_client: Optional[WhaleAlertClient] = None


def get_whale_alert_client() -> WhaleAlertClient:
    """Get or create Whale Alert client singleton."""
    global _whale_alert_client
    if _whale_alert_client is None:
        _whale_alert_client = WhaleAlertClient()
    return _whale_alert_client
