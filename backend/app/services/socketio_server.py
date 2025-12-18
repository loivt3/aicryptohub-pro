"""
Socket.io Real-time Broadcaster
Integrated into FastAPI - replaces Node.js server

Broadcasts real-time prices to frontend clients via WebSocket
"""
import logging
from typing import Dict, Any, Set, Optional
import asyncio

logger = logging.getLogger(__name__)

# Store for connected clients and their subscriptions
class SocketIOManager:
    """Manages Socket.io server and client connections"""
    
    def __init__(self):
        self.sio = None
        self.app = None
        self.connected_clients: Set[str] = set()
        self.subscriptions: Dict[str, Set[str]] = {}  # symbol -> set of sids
        self._initialized = False
    
    def init_app(self, fastapi_app):
        """Initialize Socket.io with FastAPI app"""
        try:
            import socketio
            
            # Create Socket.io server with CORS
            self.sio = socketio.AsyncServer(
                async_mode='asgi',
                cors_allowed_origins=[
                    'https://aicryptohub.io',
                    'http://localhost:3000',
                    'http://localhost:8080',
                    '*'  # Allow all for development
                ],
                logger=False,
                engineio_logger=False
            )
            
            # Create ASGI app
            self.app = socketio.ASGIApp(
                self.sio,
                other_asgi_app=fastapi_app,
                socketio_path='/socket.io'
            )
            
            # Register event handlers
            self._register_handlers()
            
            self._initialized = True
            logger.info("Socket.io server initialized")
            
            return self.app
            
        except ImportError:
            logger.warning("python-socketio not installed. Run: pip install python-socketio")
            return fastapi_app
        except Exception as e:
            logger.error(f"Socket.io init failed: {e}")
            return fastapi_app
    
    def _register_handlers(self):
        """Register Socket.io event handlers"""
        if not self.sio:
            return
        
        @self.sio.event
        async def connect(sid, environ):
            self.connected_clients.add(sid)
            logger.info(f"Client connected: {sid} (Total: {len(self.connected_clients)})")
            await self.sio.emit('connected', {
                'status': 'connected',
                'sid': sid,
                'clients': len(self.connected_clients)
            }, room=sid)
        
        @self.sio.event
        async def disconnect(sid):
            self.connected_clients.discard(sid)
            # Remove from all subscriptions
            for symbol_sids in self.subscriptions.values():
                symbol_sids.discard(sid)
            logger.info(f"Client disconnected: {sid}")
        
        @self.sio.event
        async def subscribe(sid, data):
            """Subscribe to specific symbols"""
            if isinstance(data, list):
                for symbol in data:
                    symbol = symbol.upper()
                    if symbol not in self.subscriptions:
                        self.subscriptions[symbol] = set()
                    self.subscriptions[symbol].add(sid)
                logger.info(f"Client {sid} subscribed to {len(data)} symbols")
        
        @self.sio.event
        async def unsubscribe(sid, data):
            """Unsubscribe from symbols"""
            if isinstance(data, list):
                for symbol in data:
                    symbol = symbol.upper()
                    if symbol in self.subscriptions:
                        self.subscriptions[symbol].discard(sid)
        
        @self.sio.event
        async def get_price(sid, symbol):
            """Get single price from cache"""
            from app.services.streamer import get_market_streamer
            streamer = get_market_streamer()
            price = streamer.get_price(symbol.upper())
            return {'success': True, 'data': price} if price else {'success': False}
    
    async def broadcast_ticker_update(self, payload: Dict[str, Any]):
        """Broadcast ticker update to all connected clients"""
        if not self.sio or not self._initialized:
            return
        
        if not self.connected_clients:
            return
        
        try:
            # Broadcast to all clients
            await self.sio.emit('ticker_update', payload)
        except Exception as e:
            logger.warning(f"Broadcast failed: {e}")
    
    async def broadcast_to_symbol(self, symbol: str, data: Dict):
        """Broadcast update to clients subscribed to specific symbol"""
        if not self.sio:
            return
        
        symbol = symbol.upper()
        sids = self.subscriptions.get(symbol, set())
        
        for sid in sids:
            try:
                await self.sio.emit('price_update', data, room=sid)
            except:
                pass
    
    def get_stats(self) -> Dict:
        """Get connection stats"""
        return {
            'initialized': self._initialized,
            'connected_clients': len(self.connected_clients),
            'subscribed_symbols': len(self.subscriptions),
            'total_subscriptions': sum(len(s) for s in self.subscriptions.values())
        }
    
    async def broadcast_intent_alert(self, alert_data: Dict[str, Any]):
        """Broadcast intent divergence alert to all connected clients (Shadow Radar)"""
        if not self.sio or not self._initialized:
            return
        
        if not self.connected_clients:
            return
        
        try:
            await self.sio.emit('intent_alert', alert_data)
            logger.info(f"Intent alert broadcast: {alert_data.get('divergence_type', 'unknown')} for {alert_data.get('coin_id', 'unknown')}")
        except Exception as e:
            logger.warning(f"Intent alert broadcast failed: {e}")


# Singleton
_socket_manager: Optional[SocketIOManager] = None


def get_socket_manager() -> SocketIOManager:
    """Get or create socket manager singleton"""
    global _socket_manager
    if _socket_manager is None:
        _socket_manager = SocketIOManager()
    return _socket_manager


def init_socketio(fastapi_app):
    """Initialize Socket.io with FastAPI app"""
    manager = get_socket_manager()
    return manager.init_app(fastapi_app)


async def broadcast_prices(payload: Dict[str, Any]):
    """Broadcast price update to all clients"""
    manager = get_socket_manager()
    await manager.broadcast_ticker_update(payload)
