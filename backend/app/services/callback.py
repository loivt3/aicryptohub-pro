"""
AI Crypto Hub Pro - Callback Service
Handles callbacks to WordPress after async processing completes
"""

import logging
import hashlib
import hmac
import time
from typing import Dict, Any, Optional

import httpx

from config import get_settings

logger = logging.getLogger(__name__)


class CallbackService:
    """Service for sending callbacks to WordPress"""
    
    def __init__(self):
        settings = get_settings()
        self.callback_url = settings.wp_callback_url
        self.secret = settings.wp_callback_secret
        self.timeout = 10.0
    
    def is_configured(self) -> bool:
        """Check if callback is configured"""
        return bool(self.callback_url and self.secret)
    
    def generate_signature(self, payload: str, timestamp: int) -> str:
        """
        Generate HMAC-SHA256 signature for request
        
        Args:
            payload: JSON payload string
            timestamp: Unix timestamp
            
        Returns:
            Hex signature string
        """
        message = f"{timestamp}.{payload}"
        signature = hmac.new(
            self.secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def send_callback(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Send callback to WordPress
        
        Args:
            event_type: Type of event (analysis_complete, onchain_complete)
            data: Event data
            
        Returns:
            True if callback successful
        """
        if not self.is_configured():
            logger.debug("Callback not configured, skipping")
            return False
        
        timestamp = int(time.time())
        
        payload = {
            "event": event_type,
            "timestamp": timestamp,
            "data": data,
        }
        
        import json
        payload_str = json.dumps(payload, sort_keys=True)
        signature = self.generate_signature(payload_str, timestamp)
        
        headers = {
            "Content-Type": "application/json",
            "X-AIHub-Signature": signature,
            "X-AIHub-Timestamp": str(timestamp),
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.callback_url,
                    content=payload_str,
                    headers=headers,
                    timeout=self.timeout,
                )
                
                if response.status_code == 200:
                    logger.info(f"Callback sent successfully: {event_type}")
                    return True
                else:
                    logger.warning(
                        f"Callback failed: {response.status_code} - {response.text}"
                    )
                    return False
                    
        except Exception as e:
            logger.error(f"Callback error: {e}")
            return False
    
    async def notify_analysis_complete(
        self,
        job_id: str,
        success_count: int,
        failed_count: int,
        results: list
    ) -> bool:
        """Notify WordPress that analysis is complete"""
        return await self.send_callback("analysis_complete", {
            "job_id": job_id,
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results[:10],  # Limit to 10 for payload size
        })
    
    async def notify_onchain_complete(
        self,
        job_id: str,
        chain_slug: str,
        tokens_synced: int
    ) -> bool:
        """Notify WordPress that on-chain sync is complete"""
        return await self.send_callback("onchain_complete", {
            "job_id": job_id,
            "chain_slug": chain_slug,
            "tokens_synced": tokens_synced,
        })


# Singleton instance
_callback_service: Optional[CallbackService] = None


def get_callback_service() -> CallbackService:
    """Get callback service instance"""
    global _callback_service
    if _callback_service is None:
        _callback_service = CallbackService()
    return _callback_service
