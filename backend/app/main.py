"""
AI Crypto Hub Pro - Backend API
FastAPI Entry Point
"""

from contextlib import asynccontextmanager
from datetime import datetime
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.api.endpoints import admin_ws
from app.core.config import settings
from app.middleware.api_logging import APILoggingMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

startup_time = datetime.now()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Starting AI Crypto Hub Pro API...")
    
    # Setup WebSocket logging for admin console
    admin_ws.setup_websocket_logging()
    
    # Start background scheduler
    from app.services.scheduler import start_scheduler, stop_scheduler
    try:
        start_scheduler()
        logger.info("Background scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
    
    # Start real-time Binance WebSocket streamer
    from app.services.streamer import start_streamer, stop_streamer
    try:
        await start_streamer()
        logger.info("Real-time WebSocket streamer started successfully")
    except Exception as e:
        logger.error(f"Failed to start streamer: {e}")
    
    yield
    
    # Cleanup
    try:
        stop_scheduler()
    except Exception as e:
        logger.error(f"Failed to stop scheduler: {e}")
    
    try:
        await stop_streamer()
    except Exception as e:
        logger.error(f"Failed to stop streamer: {e}")
    
    logger.info("Shutting down AI Crypto Hub Pro API...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered cryptocurrency analysis API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS middleware - MUST be added LAST to be processed FIRST
# In development, allow all origins
cors_origins = settings.CORS_ORIGINS.copy()
if settings.DEBUG or True:  # Always add localhost for development
    cors_origins.extend([
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
    ])
    cors_origins = list(set(cors_origins))  # Deduplicate

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# API Logging middleware (logs to database)
app.add_middleware(APILoggingMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include WebSocket router for admin logs
app.include_router(admin_ws.router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION,
        "uptime_seconds": (datetime.now() - startup_time).total_seconds(),
    }


# ============================================================
# Socket.IO Integration for Real-time Price Updates
# ============================================================
# Wrap FastAPI app with Socket.IO ASGI app
# Use `socketio_app` when running uvicorn for WebSocket support:
#   uvicorn app.main:socketio_app --reload --host 0.0.0.0 --port 8000
# ============================================================

from app.services.socketio_server import init_socketio

# Create Socket.IO wrapped ASGI app
socketio_app = init_socketio(app)

logger.info("Socket.IO integration initialized - use 'socketio_app' for WebSocket support")

