"""
Admin Users and Audit API - Real Database Implementation
User management, audit logs, and security features
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy import text

from app.services.database import get_database_service

router = APIRouter()


# ==================== Models ====================

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str = "user"


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class IPBlacklistEntry(BaseModel):
    ip: str
    reason: str
    expires_at: Optional[datetime] = None


# ==================== Users CRUD ====================

@router.get("/users")
async def list_users(
    limit: int = Query(50, le=200),
    offset: int = 0,
    role: Optional[str] = None,
    search: Optional[str] = None
):
    """List all users with filters"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            # Build query
            where_clauses = ["1=1"]
            params = {"limit": limit, "offset": offset}
            
            if role:
                where_clauses.append("role = :role")
                params["role"] = role
            
            if search:
                where_clauses.append("(LOWER(name) LIKE :search OR LOWER(email) LIKE :search)")
                params["search"] = f"%{search.lower()}%"
            
            where_sql = " AND ".join(where_clauses)
            
            # Get users
            query = f"""
                SELECT id, email, name, role, is_active, last_login, login_count, created_at
                FROM admin_users
                WHERE {where_sql}
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """
            result = conn.execute(text(query), params)
            users = []
            for row in result:
                users.append({
                    "id": row[0],
                    "email": row[1],
                    "name": row[2],
                    "role": row[3],
                    "is_active": row[4],
                    "last_login": row[5].isoformat() if row[5] else None,
                    "login_count": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                })
            
            # Get stats
            stats_result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE role = 'premium') as premium,
                    COUNT(*) FILTER (WHERE role = 'admin') as admins,
                    COUNT(*) FILTER (WHERE last_login > NOW() - INTERVAL '1 day') as active_today
                FROM admin_users
            """))
            stats_row = stats_result.fetchone()
            
            return {
                "users": users,
                "total": stats_row[0] if stats_row else 0,
                "stats": {
                    "total_users": stats_row[0] if stats_row else 0,
                    "premium_users": stats_row[1] if stats_row else 0,
                    "admin_users": stats_row[2] if stats_row else 0,
                    "active_today": stats_row[3] if stats_row else 0,
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get user details"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, email, name, role, is_active, last_login, created_at FROM admin_users WHERE id = :id"),
                {"id": user_id}
            )
            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="User not found")
            
            return {
                "id": row[0],
                "email": row[1],
                "name": row[2],
                "role": row[3],
                "is_active": row[4],
                "last_login": row[5].isoformat() if row[5] else None,
                "created_at": row[6].isoformat() if row[6] else None,
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users")
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            # Hash password (in production, use proper hashing)
            import hashlib
            password_hash = hashlib.sha256(user.password.encode()).hexdigest()
            
            result = conn.execute(
                text("""
                    INSERT INTO admin_users (email, password_hash, name, role)
                    VALUES (:email, :password_hash, :name, :role)
                    RETURNING id
                """),
                {
                    "email": user.email,
                    "password_hash": password_hash,
                    "name": user.name,
                    "role": user.role,
                }
            )
            conn.commit()
            user_id = result.fetchone()[0]
            
            return {
                "success": True,
                "id": user_id,
                "message": f"User {user.email} created",
            }
    except Exception as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{user_id}")
async def update_user(user_id: int, update: UserUpdate):
    """Update user"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            updates = []
            params = {"id": user_id}
            
            if update.name is not None:
                updates.append("name = :name")
                params["name"] = update.name
            if update.role is not None:
                updates.append("role = :role")
                params["role"] = update.role
            if update.is_active is not None:
                updates.append("is_active = :is_active")
                params["is_active"] = update.is_active
            
            if not updates:
                return {"success": True, "message": "No updates provided"}
            
            updates.append("updated_at = NOW()")
            
            conn.execute(
                text(f"UPDATE admin_users SET {', '.join(updates)} WHERE id = :id"),
                params
            )
            conn.commit()
            
            return {"success": True, "id": user_id, "message": "User updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Delete user"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            conn.execute(text("DELETE FROM admin_users WHERE id = :id"), {"id": user_id})
            conn.commit()
            return {"success": True, "message": f"User {user_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{user_id}/ban")
async def ban_user(user_id: int, reason: str = ""):
    """Ban a user"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            conn.execute(
                text("UPDATE admin_users SET is_active = FALSE, updated_at = NOW() WHERE id = :id"),
                {"id": user_id}
            )
            conn.commit()
            return {"success": True, "message": f"User {user_id} banned", "reason": reason}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Audit Logs ====================

@router.get("/audit/api-logs")
async def get_api_logs(
    limit: int = Query(100, le=500),
    offset: int = 0,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    endpoint: Optional[str] = None
):
    """Get API request logs"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            where_clauses = ["1=1"]
            params = {"limit": limit, "offset": offset}
            
            if method:
                where_clauses.append("method = :method")
                params["method"] = method
            if status_code:
                where_clauses.append("status_code = :status_code")
                params["status_code"] = status_code
            if endpoint:
                where_clauses.append("endpoint LIKE :endpoint")
                params["endpoint"] = f"%{endpoint}%"
            
            where_sql = " AND ".join(where_clauses)
            
            result = conn.execute(text(f"""
                SELECT id, timestamp, method, endpoint, status_code, ip_address, user_agent, duration_ms
                FROM admin_api_logs
                WHERE {where_sql}
                ORDER BY timestamp DESC
                LIMIT :limit OFFSET :offset
            """), params)
            
            logs = []
            for row in result:
                logs.append({
                    "id": row[0],
                    "timestamp": row[1].isoformat() if row[1] else None,
                    "method": row[2],
                    "endpoint": row[3],
                    "status_code": row[4],
                    "ip": row[5],
                    "user_agent": row[6],
                    "duration_ms": row[7],
                })
            
            # Get total count
            count_result = conn.execute(text(f"SELECT COUNT(*) FROM admin_api_logs WHERE {where_sql}"), params)
            total = count_result.scalar() or 0
            
            return {"logs": logs, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/login-history")
async def get_login_history(
    limit: int = 50,
    user_id: Optional[int] = None,
    success_only: bool = False
):
    """Get login history"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            where_clauses = ["1=1"]
            params = {"limit": limit}
            
            if user_id:
                where_clauses.append("user_id = :user_id")
                params["user_id"] = user_id
            if success_only:
                where_clauses.append("success = TRUE")
            
            where_sql = " AND ".join(where_clauses)
            
            result = conn.execute(text(f"""
                SELECT id, user_email, timestamp, ip_address, location, user_agent, success, failure_reason
                FROM admin_login_history
                WHERE {where_sql}
                ORDER BY timestamp DESC
                LIMIT :limit
            """), params)
            
            history = []
            for row in result:
                history.append({
                    "id": row[0],
                    "user_email": row[1],
                    "timestamp": row[2].isoformat() if row[2] else None,
                    "ip": row[3],
                    "location": row[4],
                    "user_agent": row[5],
                    "success": row[6],
                    "failure_reason": row[7],
                })
            
            return {"history": history, "total": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/admin-actions")
async def get_admin_actions(limit: int = 50):
    """Get admin action audit trail"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, admin_email, action, target_type, target_id, details, ip_address, timestamp
                FROM admin_audit_log
                ORDER BY timestamp DESC
                LIMIT :limit
            """), {"limit": limit})
            
            actions = []
            for row in result:
                actions.append({
                    "id": row[0],
                    "admin_email": row[1],
                    "action": row[2],
                    "target_type": row[3],
                    "target_id": row[4],
                    "details": row[5],
                    "ip_address": row[6],
                    "timestamp": row[7].isoformat() if row[7] else None,
                })
            
            return {"actions": actions, "total": len(actions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== IP Blacklist ====================

@router.get("/security/blacklist")
async def get_ip_blacklist():
    """Get IP blacklist"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, ip_address, reason, added_by, expires_at, created_at
                FROM admin_ip_blacklist
                WHERE expires_at IS NULL OR expires_at > NOW()
                ORDER BY created_at DESC
            """))
            
            blacklist = []
            for row in result:
                blacklist.append({
                    "id": row[0],
                    "ip": row[1],
                    "reason": row[2],
                    "added_by": row[3],
                    "expires_at": row[4].isoformat() if row[4] else None,
                    "added_at": row[5].isoformat() if row[5] else None,
                })
            
            return {"blacklist": blacklist, "total": len(blacklist)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/security/blacklist")
async def add_to_blacklist(entry: IPBlacklistEntry):
    """Add IP to blacklist"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO admin_ip_blacklist (ip_address, reason, added_by, expires_at)
                VALUES (:ip, :reason, 'admin', :expires_at)
            """), {
                "ip": entry.ip,
                "reason": entry.reason,
                "expires_at": entry.expires_at,
            })
            conn.commit()
            
            return {"success": True, "ip": entry.ip, "message": f"IP {entry.ip} added to blacklist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/security/blacklist/{ip}")
async def remove_from_blacklist(ip: str):
    """Remove IP from blacklist"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            conn.execute(text("DELETE FROM admin_ip_blacklist WHERE ip_address = :ip"), {"ip": ip})
            conn.commit()
            return {"success": True, "message": f"IP {ip} removed from blacklist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Security Stats ====================

@router.get("/security/stats")
async def get_security_stats():
    """Get security dashboard stats"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            # Get failed logins in 24h
            failed = conn.execute(text("""
                SELECT COUNT(*) FROM admin_login_history 
                WHERE success = FALSE AND timestamp > NOW() - INTERVAL '1 day'
            """)).scalar() or 0
            
            # Get blacklisted IPs
            blacklisted = conn.execute(text("""
                SELECT COUNT(*) FROM admin_ip_blacklist 
                WHERE expires_at IS NULL OR expires_at > NOW()
            """)).scalar() or 0
            
            return {
                "failed_logins_24h": failed,
                "blocked_requests_24h": 0,  # TODO: From API logs
                "blacklisted_ips": blacklisted,
                "active_sessions": 0,  # TODO: From sessions
                "suspicious_activities": 0,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
