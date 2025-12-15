"""
Binance Real-time Market Streamer Service
Integrated with Python-service FastAPI app

Consumes Binance WebSocket and publishes to Redis + Socket.io
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

# Configuration
BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/!miniTicker@arr"
REDIS_CHANNEL = "market_realtime_stream"
RECONNECT_DELAY = 5
MAX_RECONNECT_ATTEMPTS = 10


class MarketStreamer:
    """Integrated Binance WebSocket streamer with Redis + local broadcast"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self.running = False
        self.reconnect_count = 0
        self.message_count = 0
        self.last_update = None
        self.subscribers: List[Callable] = []
        self._task: Optional[asyncio.Task] = None
        
        # In-memory cache for quick access
        self.prices_cache: Dict[str, Dict] = {}
    
    async def connect_redis(self):
        """Connect to Redis"""
        try:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("Market Streamer: Connected to Redis")
        except Exception as e:
            logger.warning(f"Market Streamer: Redis connection failed: {e}")
            self.redis = None
    
    def process_ticker(self, ticker: Dict) -> Optional[Dict[str, Any]]:
        """Process single ticker from Binance miniTicker"""
        symbol = ticker.get("s", "")
        
        # Filter: Only USDT pairs
        if not symbol.endswith("USDT"):
            return None
        
        # Extract base symbol (remove USDT)
        base_symbol = symbol[:-4]
        
        try:
            close_price = float(ticker.get("c", 0))
            open_price = float(ticker.get("o", 0))
            high = float(ticker.get("h", 0))
            low = float(ticker.get("l", 0))
            volume = float(ticker.get("v", 0))
            
            # Calculate price change %
            if open_price > 0:
                change_pct = ((close_price - open_price) / open_price) * 100
            else:
                change_pct = 0
            
            return {
                "s": base_symbol,
                "p": round(close_price, 8),
                "c": round(change_pct, 2),
                "h": round(high, 8),
                "l": round(low, 8),
                "v": round(volume, 2),
            }
        except (ValueError, TypeError):
            return None
    
    async def process_and_publish(self, data: list):
        """Process ticker array and publish"""
        processed = []
        
        for ticker in data:
            result = self.process_ticker(ticker)
            if result:
                processed.append(result)
                # Update local cache
                self.prices_cache[result["s"]] = result
        
        if not processed:
            return
        
        timestamp = int(datetime.now().timestamp() * 1000)
        
        payload = {
            "t": timestamp,
            "d": processed,
            "c": len(processed)
        }
        
        # Publish to Redis if available
        if self.redis:
            try:
                message = json.dumps(payload, separators=(',', ':'))
                await self.redis.publish(REDIS_CHANNEL, message)
                
                # Store in Redis hash
                pipe = self.redis.pipeline()
                for item in processed:
                    key = f"price:{item['s']}"
                    pipe.hset(key, mapping={
                        "p": str(item["p"]),
                        "c": str(item["c"]),
                        "t": str(timestamp)
                    })
                    pipe.expire(key, 300)
                await pipe.execute()
            except Exception as e:
                logger.warning(f"Redis publish failed: {e}")
        
        # Broadcast to Socket.io clients
        try:
            from services.socketio_server import broadcast_prices
            await broadcast_prices(payload)
        except Exception as e:
            pass  # Socket.io not initialized yet
        
        # Notify local subscribers
        for callback in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(payload)
                else:
                    callback(payload)
            except Exception as e:
                logger.warning(f"Subscriber callback error: {e}")
        
        self.message_count += 1
        self.last_update = datetime.now()
        
        if self.message_count % 60 == 0:
            logger.info(f"Streamer: {len(processed)} tickers (total: {self.message_count})")
    
    async def stream_handler(self):
        """Main WebSocket stream handler"""
        # Import here to avoid issues if not installed
        try:
            import websockets
        except ImportError:
            logger.error("websockets not installed. Run: pip install websockets")
            return
        
        while self.running:
            try:
                logger.info("Connecting to Binance WebSocket...")
                
                async with websockets.connect(
                    BINANCE_WS_URL,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=5
                ) as ws:
                    logger.info("Connected to Binance WebSocket!")
                    self.reconnect_count = 0
                    
                    async for message in ws:
                        if not self.running:
                            break
                        
                        try:
                            data = json.loads(message)
                            if isinstance(data, list):
                                await self.process_and_publish(data)
                        except json.JSONDecodeError:
                            continue
                            
            except Exception as e:
                logger.warning(f"WebSocket error: {e}")
            
            # Reconnection
            if self.running:
                self.reconnect_count += 1
                if self.reconnect_count > MAX_RECONNECT_ATTEMPTS:
                    logger.error("Max reconnection attempts reached")
                    break
                
                wait_time = min(RECONNECT_DELAY * self.reconnect_count, 60)
                logger.info(f"Reconnecting in {wait_time}s...")
                await asyncio.sleep(wait_time)
    
    async def start(self):
        """Start the streamer as background task"""
        if self.running:
            return
        
        self.running = True
        await self.connect_redis()
        self._task = asyncio.create_task(self.stream_handler())
        logger.info("Market Streamer started")
    
    async def stop(self):
        """Stop the streamer"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self.redis:
            await self.redis.close()
        logger.info("Market Streamer stopped")
    
    def subscribe(self, callback: Callable):
        """Add subscriber callback"""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable):
        """Remove subscriber callback"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def get_price(self, symbol: str) -> Optional[Dict]:
        """Get cached price for symbol"""
        return self.prices_cache.get(symbol.upper())
    
    def get_all_prices(self) -> Dict[str, Dict]:
        """Get all cached prices"""
        return self.prices_cache.copy()
    
    def get_status(self) -> Dict:
        """Get streamer status"""
        return {
            "running": self.running,
            "connected": self.running and self.reconnect_count == 0,
            "message_count": self.message_count,
            "cached_symbols": len(self.prices_cache),
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "redis_connected": self.redis is not None
        }


# Singleton
_streamer: Optional[MarketStreamer] = None


def get_market_streamer(redis_url: str = None) -> MarketStreamer:
    """Get or create market streamer singleton"""
    global _streamer
    if _streamer is None:
        from config import get_settings
        settings = get_settings()
        url = redis_url or getattr(settings, 'redis_url', 'redis://localhost:6379/0')
        _streamer = MarketStreamer(url)
    return _streamer


async def start_streamer():
    """Start the global streamer"""
    streamer = get_market_streamer()
    await streamer.start()


async def stop_streamer():
    """Stop the global streamer"""
    global _streamer
    if _streamer:
        await _streamer.stop()
        _streamer = None
