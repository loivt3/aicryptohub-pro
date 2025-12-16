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
    
    # Initialize database connection
    # TODO: Initialize DB pool
    
    # Start real-time streamer
    # TODO: Start WebSocket streamer
    
    yield
    
    # Cleanup
    logger.info("Shutting down AI Crypto Hub Pro API...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered cryptocurrency analysis API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

