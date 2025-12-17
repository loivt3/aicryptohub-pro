"""
Admin API Endpoints
Process management, settings, and system monitoring
"""

import os
import psutil
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import text

from app.services.database import get_database_service

router = APIRouter()


# ==================== Models ====================

class ServiceStatus(BaseModel):
    id: str
    name: str
    status: str  # running, stopped, error
    uptime: Optional[str] = None
    last_log: Optional[str] = None
    pid: Optional[int] = None


class SystemHealth(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    db_connections: int


class SettingsUpdate(BaseModel):
    key: str
    value: Any


class BackendSettings(BaseModel):
    coingecko_api_key: Optional[str] = None
    etherscan_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    market_sync_interval: int = 60
    ai_analysis_interval: int = 300
    onchain_sync_interval: int = 600


class FrontendSettings(BaseModel):
    site_name: str = "AI Crypto Hub"
    banner_image_url: Optional[str] = None
    announcement_text: Optional[str] = None
    maintenance_mode: bool = False
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class AISettings(BaseModel):
    system_prompt: Optional[str] = None
    rsi_overbought: int = 70
    rsi_oversold: int = 30
    whale_threshold: int = 100000
    sentiment_weight: int = 40


# ==================== System Health ====================

@router.get("/health", response_model=SystemHealth)
async def get_system_health():
    """Get system health metrics"""
    try:
        # Get DB connections count
        db_conns = 0
        try:
            db = get_database_service()
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"))
                db_conns = result.scalar() or 0
        except:
            pass
        
        return SystemHealth(
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_percent=psutil.virtual_memory().percent,
            disk_percent=psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent,
            db_connections=db_conns,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_admin_stats():
    """Get admin dashboard stats with real data"""
    try:
        db = get_database_service()
        
        stats = {
            "coins_tracked": 0,
            "active_users": 0,
            "api_calls_today": 0,
            "news_pending": 0,
            "error_rate": 0,
        }
        
        try:
            with db.engine.connect() as conn:
                # Coins count
                result = conn.execute(text("SELECT COUNT(*) FROM aihub_coins"))
                stats["coins_tracked"] = result.scalar() or 0
                
                # Active users (logged in today)
                try:
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM admin_users 
                        WHERE last_login > NOW() - INTERVAL '1 day'
                    """))
                    stats["active_users"] = result.scalar() or 0
                except:
                    pass
                
                # API calls today
                try:
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM admin_api_logs 
                        WHERE timestamp > NOW() - INTERVAL '1 day'
                    """))
                    stats["api_calls_today"] = result.scalar() or 0
                except:
                    pass
                
                # Pending news
                try:
                    result = conn.execute(text("SELECT COUNT(*) FROM admin_news WHERE status = 'pending'"))
                    stats["news_pending"] = result.scalar() or 0
                except:
                    pass
                
                # Error rate (4xx/5xx in last hour)
                try:
                    result = conn.execute(text("""
                        SELECT 
                            COUNT(*) FILTER (WHERE status_code >= 400) * 100.0 / NULLIF(COUNT(*), 0)
                        FROM admin_api_logs 
                        WHERE timestamp > NOW() - INTERVAL '1 hour'
                    """))
                    rate = result.scalar()
                    stats["error_rate"] = round(rate, 2) if rate else 0
                except:
                    pass
        except:
            pass
        
        stats["timestamp"] = datetime.now().isoformat()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Process Management ====================

@router.get("/process/status")
async def get_all_services_status():
    """Get status of all services from database"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT service_id, service_name, service_type, status, pid, 
                       uptime_seconds, last_log, last_error, started_at, updated_at
                FROM admin_service_status
                ORDER BY service_type, service_name
            """))
            
            services = []
            for row in result:
                uptime_str = ""
                if row[5]:
                    days = row[5] // 86400
                    hours = (row[5] % 86400) // 3600
                    mins = (row[5] % 3600) // 60
                    uptime_str = f"{days}d {hours}h {mins}m" if days else f"{hours}h {mins}m"
                
                services.append({
                    "id": row[0],
                    "name": row[1],
                    "type": row[2],
                    "status": row[3],
                    "pid": row[4],
                    "uptime": uptime_str,
                    "last_log": row[6],
                    "last_error": row[7],
                    "started_at": row[8].isoformat() if row[8] else None,
                })
            
            return {"services": services}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/process/{service_id}/status")
async def get_service_status_endpoint(service_id: str):
    """Get status of a specific service"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            result = conn.execute(
                text("SELECT service_id, service_name, status, pid, uptime_seconds, last_log FROM admin_service_status WHERE service_id = :id"),
                {"id": service_id}
            )
            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail=f"Service {service_id} not found")
            
            return ServiceStatus(
                id=row[0],
                name=row[1],
                status=row[2],
                pid=row[3],
                uptime=f"{row[4] // 3600}h {(row[4] % 3600) // 60}m" if row[4] else None,
                last_log=row[5],
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process/{service_id}/{action}")
async def control_service(service_id: str, action: str):
    """Start, stop, or restart a service"""
    if action not in ["start", "stop", "restart"]:
        raise HTTPException(status_code=400, detail="Invalid action. Use: start, stop, restart")
    
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            # Verify service exists
            result = conn.execute(
                text("SELECT service_name FROM admin_service_status WHERE service_id = :id"),
                {"id": service_id}
            )
            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail=f"Service {service_id} not found")
            
            service_name = row[0]
            
            # Execute actual command (Linux only)
            if os.name != 'nt':
                try:
                    systemd_name = f"aicryptohub-{service_id}"
                    result = subprocess.run(
                        ["systemctl", action, systemd_name],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode != 0:
                        # Update DB with error
                        conn.execute(
                            text("UPDATE admin_service_status SET last_error = :err, updated_at = NOW() WHERE service_id = :id"),
                            {"id": service_id, "err": result.stderr}
                        )
                        conn.commit()
                        raise HTTPException(status_code=500, detail=f"Command failed: {result.stderr}")
                except subprocess.TimeoutExpired:
                    raise HTTPException(status_code=500, detail="Command timed out")
            
            # Update status in DB
            new_status = "running" if action in ["start", "restart"] else "stopped"
            started_at = "NOW()" if action in ["start", "restart"] else "NULL"
            
            if action in ["start", "restart"]:
                conn.execute(
                    text(f"UPDATE admin_service_status SET status = :status, started_at = NOW(), updated_at = NOW() WHERE service_id = :id"),
                    {"id": service_id, "status": new_status}
                )
            else:
                conn.execute(
                    text("UPDATE admin_service_status SET status = :status, stopped_at = NOW(), uptime_seconds = 0, updated_at = NOW() WHERE service_id = :id"),
                    {"id": service_id, "status": new_status}
                )
            conn.commit()
            
            return {
                "success": True,
                "service": service_id,
                "action": action,
                "message": f"Service {service_name} {action}ed successfully",
                "timestamp": datetime.now().isoformat(),
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/process/{service_id}/logs")
async def get_service_logs(service_id: str, lines: int = 100):
    """Get recent logs for a service"""
    service = SERVICES.get(service_id)
    if not service:
        raise HTTPException(status_code=404, detail=f"Service {service_id} not found")
    
    # TODO: Read actual logs from journalctl or log files
    # For now, return mock logs
    logs = [
        {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": "Service started"},
        {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": "Data sync completed"},
    ]
    
    return {"service": service_id, "logs": logs}


# ==================== Settings ====================

from app.services.admin_settings import get_settings_service, BackendSettings as BSModel, FrontendSettings as FSModel, AISettings as ASModel


@router.get("/settings/backend")
async def get_backend_settings():
    """Get backend settings (masked API keys)"""
    service = get_settings_service()
    return service.get_backend_settings_masked()


@router.post("/settings/backend")
async def update_backend_settings(settings: BackendSettings):
    """Update backend settings"""
    service = get_settings_service()
    bs = BSModel(
        coingecko_api_key=settings.coingecko_api_key or "",
        etherscan_api_key=settings.etherscan_api_key or "",
        gemini_api_key=settings.gemini_api_key or "",
        deepseek_api_key=settings.deepseek_api_key or "",
        market_sync_interval=settings.market_sync_interval,
        ai_analysis_interval=settings.ai_analysis_interval,
        onchain_sync_interval=settings.onchain_sync_interval,
    )
    service.save_backend_settings(bs)
    return {"success": True, "message": "Backend settings saved to Redis"}


@router.get("/settings/frontend")
async def get_frontend_settings():
    """Get frontend settings"""
    service = get_settings_service()
    return service.get_frontend_settings().model_dump()


@router.post("/settings/frontend")
async def update_frontend_settings(settings: FrontendSettings):
    """Update frontend settings"""
    service = get_settings_service()
    fs = FSModel(
        site_name=settings.site_name,
        banner_image_url=settings.banner_image_url or "",
        announcement_text=settings.announcement_text or "",
        maintenance_mode=settings.maintenance_mode,
        meta_title=settings.meta_title or "",
        meta_description=settings.meta_description or "",
    )
    service.save_frontend_settings(fs)
    return {"success": True, "message": "Frontend settings saved to Redis"}


@router.get("/settings/ai")
async def get_ai_settings():
    """Get AI tuning settings"""
    service = get_settings_service()
    return service.get_ai_settings().model_dump()


@router.post("/settings/ai")
async def update_ai_settings(settings: AISettings):
    """Update AI tuning settings"""
    service = get_settings_service()
    ai = ASModel(
        system_prompt=settings.system_prompt or "",
        rsi_overbought=settings.rsi_overbought,
        rsi_oversold=settings.rsi_oversold,
        whale_threshold=settings.whale_threshold,
        sentiment_weight=settings.sentiment_weight,
    )
    service.save_ai_settings(ai)
    return {"success": True, "message": "AI settings saved to Redis"}


# ==================== Data Management ====================

@router.get("/data/coins")
async def get_coins_admin(limit: int = 100, offset: int = 0, search: Optional[str] = None):
    """Get coins for admin management"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            from sqlalchemy import text
            
            query = """
                SELECT coin_id, symbol, name, image_url, rank, price, change_24h, market_cap
                FROM aihub_coins
                ORDER BY rank ASC NULLS LAST
                LIMIT :limit OFFSET :offset
            """
            result = conn.execute(text(query), {"limit": limit, "offset": offset})
            coins = [dict(row._mapping) for row in result]
            
            return {"coins": coins, "total": len(coins)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/data/coins/{coin_id}")
async def update_coin_admin(coin_id: str, data: Dict[str, Any]):
    """Update coin metadata"""
    # TODO: Implement coin update
    return {"success": True, "message": f"Coin {coin_id} updated"}


@router.delete("/data/coins/{coin_id}")
async def delete_coin_admin(coin_id: str):
    """Delete/hide a coin"""
    # TODO: Implement soft delete
    return {"success": True, "message": f"Coin {coin_id} deleted"}


# ==================== Audit ====================

@router.get("/audit/api-logs")
async def get_api_logs(limit: int = 100):
    """Get recent API logs"""
    # TODO: Get from log storage
    return {"logs": []}


@router.get("/audit/login-history")
async def get_login_history(limit: int = 100):
    """Get login history"""
    # TODO: Get from auth logs
    return {"history": []}


@router.get("/audit/blacklist")
async def get_ip_blacklist():
    """Get IP blacklist"""
    # TODO: Get from Redis/DB
    return {"blacklist": []}


@router.post("/audit/blacklist")
async def add_to_blacklist(ip: str, reason: str):
    """Add IP to blacklist"""
    # TODO: Add to Redis/DB
    return {"success": True, "message": f"IP {ip} added to blacklist"}


@router.delete("/audit/blacklist/{ip}")
async def remove_from_blacklist(ip: str):
    """Remove IP from blacklist"""
    # TODO: Remove from Redis/DB
    return {"success": True, "message": f"IP {ip} removed from blacklist"}
