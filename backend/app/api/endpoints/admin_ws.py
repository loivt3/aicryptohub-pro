"""
WebSocket endpoints for real-time admin logs
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Connected clients
connected_clients: Set[WebSocket] = set()

logger = logging.getLogger(__name__)


class LogBroadcaster:
    """Broadcast logs to all connected WebSocket clients"""
    
    def __init__(self):
        self.clients: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.clients.add(websocket)
        logger.info(f"Admin log client connected. Total: {len(self.clients)}")
    
    def disconnect(self, websocket: WebSocket):
        self.clients.discard(websocket)
        logger.info(f"Admin log client disconnected. Total: {len(self.clients)}")
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        disconnected = set()
        for client in self.clients:
            try:
                await client.send_json(message)
            except Exception:
                disconnected.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected


# Global broadcaster instance
log_broadcaster = LogBroadcaster()


async def emit_log(service: str, level: str, message: str):
    """Emit a log message to all connected admin clients"""
    log_entry = {
        "id": int(datetime.now().timestamp() * 1000),
        "timestamp": datetime.now().isoformat(),
        "service": service,
        "type": level.lower(),
        "message": message,
    }
    await log_broadcaster.broadcast(log_entry)


@router.websocket("/ws/admin/logs")
async def admin_logs_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time admin logs"""
    await log_broadcaster.connect(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "id": int(datetime.now().timestamp() * 1000),
            "timestamp": datetime.now().isoformat(),
            "service": "system",
            "type": "info",
            "message": "Connected to admin log stream",
        })
        
        # Keep connection alive and listen for client messages
        while True:
            try:
                # Wait for any message from client (ping/pong or filter requests)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # Handle client commands
                if data == "ping":
                    await websocket.send_text("pong")
                    
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat(),
                })
                
    except WebSocketDisconnect:
        log_broadcaster.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        log_broadcaster.disconnect(websocket)


# Helper to integrate with Python logging
class WebSocketLogHandler(logging.Handler):
    """Custom log handler that broadcasts to WebSocket clients"""
    
    def __init__(self, broadcaster: LogBroadcaster, service_name: str = "backend"):
        super().__init__()
        self.broadcaster = broadcaster
        self.service_name = service_name
    
    def emit(self, record):
        try:
            asyncio.create_task(emit_log(
                service=self.service_name,
                level=record.levelname,
                message=self.format(record)
            ))
        except Exception:
            pass


def setup_websocket_logging():
    """Setup WebSocket log handler for the application"""
    handler = WebSocketLogHandler(log_broadcaster, "backend")
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(message)s'))
    
    # Add to root logger
    logging.getLogger().addHandler(handler)
