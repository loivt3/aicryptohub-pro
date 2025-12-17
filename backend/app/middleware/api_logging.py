"""
API Request Logging Middleware
Logs all API requests to database for audit purposes
"""

import time
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text

from app.services.database import get_database_service

logger = logging.getLogger(__name__)


class APILoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests to database"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for health checks and static files
        path = request.url.path
        if path in ["/health", "/docs", "/openapi.json", "/redoc"] or path.startswith("/static"):
            return await call_next(request)
        
        # Start timer
        start_time = time.time()
        
        # Get request info
        method = request.method
        endpoint = path
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")[:500]  # Limit length
        
        # Get user ID from auth header if present (simplified)
        user_id = None
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # TODO: Decode JWT to get user_id
            pass
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log to database (async to not block response)
            try:
                self._log_to_db(
                    method=method,
                    endpoint=endpoint,
                    status_code=response.status_code,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    user_id=user_id,
                    duration_ms=duration_ms,
                )
            except Exception as e:
                logger.error(f"Failed to log API request: {e}")
            
            return response
            
        except Exception as e:
            # Log error
            duration_ms = int((time.time() - start_time) * 1000)
            
            try:
                self._log_to_db(
                    method=method,
                    endpoint=endpoint,
                    status_code=500,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    user_id=user_id,
                    duration_ms=duration_ms,
                    error_message=str(e)[:500],
                )
            except Exception:
                pass
            
            raise
    
    def _log_to_db(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        ip_address: str,
        user_agent: str,
        user_id: int = None,
        duration_ms: int = 0,
        error_message: str = None,
    ):
        """Insert log entry into database"""
        try:
            db = get_database_service()
            with db.engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO admin_api_logs 
                        (method, endpoint, status_code, ip_address, user_agent, user_id, duration_ms, error_message)
                        VALUES (:method, :endpoint, :status_code, :ip, :ua, :user_id, :duration, :error)
                    """),
                    {
                        "method": method,
                        "endpoint": endpoint,
                        "status_code": status_code,
                        "ip": ip_address,
                        "ua": user_agent,
                        "user_id": user_id,
                        "duration": duration_ms,
                        "error": error_message,
                    }
                )
                conn.commit()
        except Exception as e:
            # Don't fail if logging fails
            logger.warning(f"API log insert failed: {e}")


def log_login_attempt(
    user_email: str,
    success: bool,
    ip_address: str,
    user_agent: str,
    user_id: int = None,
    failure_reason: str = None,
    location: str = None,
):
    """Log a login attempt to database"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO admin_login_history 
                    (user_id, user_email, ip_address, location, user_agent, success, failure_reason)
                    VALUES (:user_id, :email, :ip, :location, :ua, :success, :reason)
                """),
                {
                    "user_id": user_id,
                    "email": user_email,
                    "ip": ip_address,
                    "location": location,
                    "ua": user_agent[:500] if user_agent else None,
                    "success": success,
                    "reason": failure_reason,
                }
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to log login attempt: {e}")


def log_admin_action(
    admin_id: int,
    admin_email: str,
    action: str,
    target_type: str = None,
    target_id: str = None,
    details: dict = None,
    ip_address: str = None,
):
    """Log an admin action to audit trail"""
    try:
        import json
        db = get_database_service()
        with db.engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO admin_audit_log 
                    (admin_id, admin_email, action, target_type, target_id, details, ip_address)
                    VALUES (:admin_id, :email, :action, :target_type, :target_id, :details, :ip)
                """),
                {
                    "admin_id": admin_id,
                    "email": admin_email,
                    "action": action,
                    "target_type": target_type,
                    "target_id": target_id,
                    "details": json.dumps(details) if details else None,
                    "ip": ip_address,
                }
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to log admin action: {e}")
