"""
Public News API
Fetches approved news articles for the frontend
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy import text

from app.services.database import get_database_service

router = APIRouter()


@router.get("")
async def get_news(
    limit: int = Query(10, le=50),
    offset: int = 0,
):
    """Get latest approved news articles for public display"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            # Get approved/published news
            result = conn.execute(text("""
                SELECT 
                    id, title, excerpt, source, source_url, image_url, 
                    tags, coin_ids, published_at, created_at
                FROM admin_news
                WHERE status = 'approved'
                ORDER BY COALESCE(published_at, created_at) DESC
                LIMIT :limit OFFSET :offset
            """), {"limit": limit, "offset": offset})
            
            articles = []
            for row in result:
                # Calculate time ago
                pub_time = row[8] or row[9]
                time_ago = "Just now"
                if pub_time:
                    delta = datetime.now() - pub_time.replace(tzinfo=None)
                    if delta.days > 0:
                        time_ago = f"{delta.days}d ago"
                    elif delta.seconds > 3600:
                        time_ago = f"{delta.seconds // 3600}h ago"
                    elif delta.seconds > 60:
                        time_ago = f"{delta.seconds // 60}m ago"
                
                # Determine tag from tags array or use default
                tags = row[6] or []
                tag = tags[0].upper() if tags else "NEWS"
                
                articles.append({
                    "id": row[0],
                    "title": row[1],
                    "excerpt": row[2],
                    "source": row[3],
                    "source_url": row[4],
                    "image": row[5],
                    "tag": tag,
                    "coin_ids": row[7] or [],
                    "time_ago": time_ago,
                    "published_at": pub_time.isoformat() if pub_time else None,
                })
            
            # Get total count
            count_result = conn.execute(text("""
                SELECT COUNT(*) FROM admin_news WHERE status = 'approved'
            """))
            total = count_result.scalar() or 0
            
            return {
                "success": True,
                "articles": articles,
                "total": total,
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "articles": [],
            "total": 0,
        }


@router.get("/hero")
async def get_hero_news():
    """Get the latest hero/featured news article"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    id, title, excerpt, content, source, source_url, image_url, 
                    tags, published_at
                FROM admin_news
                WHERE status = 'approved' AND image_url IS NOT NULL AND image_url != ''
                ORDER BY COALESCE(published_at, created_at) DESC
                LIMIT 1
            """))
            
            row = result.fetchone()
            if row:
                pub_time = row[8]
                time_ago = "Just now"
                if pub_time:
                    delta = datetime.now() - pub_time.replace(tzinfo=None)
                    if delta.days > 0:
                        time_ago = f"{delta.days}d ago"
                    elif delta.seconds > 3600:
                        time_ago = f"{delta.seconds // 3600}h ago"
                    elif delta.seconds > 60:
                        time_ago = f"{delta.seconds // 60}m ago"
                
                tags = row[7] or []
                tag = tags[0].upper() if tags else "BREAKING"
                
                return {
                    "success": True,
                    "article": {
                        "id": row[0],
                        "title": row[1],
                        "excerpt": row[2],
                        "content": row[3],
                        "source": row[4],
                        "source_url": row[5],
                        "image": row[6],
                        "tag": tag,
                        "time_ago": time_ago,
                    },
                }
            
            return {"success": False, "article": None}
    except Exception as e:
        return {"success": False, "error": str(e), "article": None}
