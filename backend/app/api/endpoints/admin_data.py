"""
Admin Data Management API - Real Database Implementation
CRUD operations for coins, news, and market corrections
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text

from app.services.database import get_database_service

router = APIRouter()


# ==================== Models ====================

class CoinUpdate(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    is_visible: Optional[bool] = None


class MarketCorrection(BaseModel):
    coin_id: str
    new_price: float
    reason: str


class NewsArticle(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    coin_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class NewsUpdate(BaseModel):
    status: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None


# ==================== Coins CRUD ====================

@router.get("/coins")
async def list_coins(
    limit: int = Query(100, le=500),
    offset: int = 0,
    search: Optional[str] = None,
    visible_only: bool = False
):
    """List all coins with pagination and search"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            where_clauses = ["1=1"]
            params = {"limit": limit, "offset": offset}
            
            if search:
                where_clauses.append("(LOWER(name) LIKE :search OR LOWER(symbol) LIKE :search)")
                params["search"] = f"%{search.lower()}%"
            
            where_sql = " AND ".join(where_clauses)
            
            query = f"""
                SELECT 
                    coin_id, symbol, name, image_url as image, 
                    rank, price, change_24h, market_cap, volume_24h
                FROM aihub_coins
                WHERE {where_sql}
                ORDER BY rank ASC NULLS LAST
                LIMIT :limit OFFSET :offset
            """
            
            result = conn.execute(text(query), params)
            coins = []
            for row in result:
                coins.append({
                    "coin_id": row[0],
                    "symbol": row[1],
                    "name": row[2],
                    "image": row[3],
                    "rank": row[4],
                    "price": float(row[5]) if row[5] else 0,
                    "change_24h": float(row[6]) if row[6] else 0,
                    "market_cap": float(row[7]) if row[7] else 0,
                    "volume_24h": float(row[8]) if row[8] else 0,
                })
            
            # Get total count
            count_result = conn.execute(text(f"SELECT COUNT(*) FROM aihub_coins WHERE {where_sql}"), params)
            total = count_result.scalar() or 0
            
            return {
                "coins": coins,
                "total": total,
                "limit": limit,
                "offset": offset,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/coins/{coin_id}")
async def get_coin(coin_id: str):
    """Get single coin details"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM aihub_coins WHERE coin_id = :coin_id"),
                {"coin_id": coin_id}
            )
            row = result.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Coin not found")
            
            columns = result.keys()
            return {col: (float(val) if isinstance(val, (int, float)) and col not in ['coin_id', 'symbol', 'name', 'image_url'] else val) for col, val in zip(columns, row)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/coins/{coin_id}")
async def update_coin(coin_id: str, update: CoinUpdate):
    """Update coin metadata"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            updates = []
            params = {"coin_id": coin_id}
            
            if update.name is not None:
                updates.append("name = :name")
                params["name"] = update.name
            if update.symbol is not None:
                updates.append("symbol = :symbol")
                params["symbol"] = update.symbol
            if update.image_url is not None:
                updates.append("image_url = :image_url")
                params["image_url"] = update.image_url
            
            if not updates:
                return {"success": True, "message": "No updates provided"}
            
            updates.append("last_updated = NOW()")
            
            conn.execute(
                text(f"UPDATE aihub_coins SET {', '.join(updates)} WHERE coin_id = :coin_id"),
                params
            )
            conn.commit()
            
            return {"success": True, "message": f"Coin {coin_id} updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Market Corrections ====================

@router.get("/corrections")
async def list_corrections(limit: int = 50):
    """List market correction history"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT c.id, c.coin_id, co.name as coin_name, c.old_price, c.new_price, 
                       c.reason, c.applied_by, c.created_at
                FROM admin_market_corrections c
                LEFT JOIN aihub_coins co ON co.coin_id = c.coin_id
                ORDER BY c.created_at DESC
                LIMIT :limit
            """), {"limit": limit})
            
            corrections = []
            for row in result:
                corrections.append({
                    "id": row[0],
                    "coin_id": row[1],
                    "coin_name": row[2] or row[1],
                    "old_price": float(row[3]) if row[3] else 0,
                    "new_price": float(row[4]) if row[4] else 0,
                    "reason": row[5],
                    "applied_by": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                })
            
            return {"corrections": corrections, "total": len(corrections)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/corrections")
async def create_correction(correction: MarketCorrection):
    """Apply a manual price correction"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            # Get current price
            result = conn.execute(
                text("SELECT price FROM aihub_coins WHERE coin_id = :coin_id"),
                {"coin_id": correction.coin_id}
            )
            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Coin not found")
            
            old_price = float(row[0]) if row[0] else 0
            
            # Update price in aihub_coins
            conn.execute(
                text("UPDATE aihub_coins SET price = :price, last_updated = NOW() WHERE coin_id = :coin_id"),
                {"coin_id": correction.coin_id, "price": correction.new_price}
            )
            
            # Log correction
            conn.execute(
                text("""
                    INSERT INTO admin_market_corrections (coin_id, old_price, new_price, reason, applied_by)
                    VALUES (:coin_id, :old_price, :new_price, :reason, 'admin')
                """),
                {
                    "coin_id": correction.coin_id,
                    "old_price": old_price,
                    "new_price": correction.new_price,
                    "reason": correction.reason,
                }
            )
            conn.commit()
            
            return {
                "success": True,
                "coin_id": correction.coin_id,
                "old_price": old_price,
                "new_price": correction.new_price,
                "reason": correction.reason,
                "timestamp": datetime.now().isoformat(),
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== News CRUD ====================

@router.get("/news")
async def list_news(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None
):
    """List news articles with filters"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            where_clauses = ["1=1"]
            params = {"limit": limit, "offset": offset}
            
            if status:
                where_clauses.append("status = :status")
                params["status"] = status
            
            where_sql = " AND ".join(where_clauses)
            
            result = conn.execute(text(f"""
                SELECT id, title, excerpt, source, status, image_url, created_at, published_at
                FROM admin_news
                WHERE {where_sql}
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """), params)
            
            articles = []
            for row in result:
                articles.append({
                    "id": row[0],
                    "title": row[1],
                    "excerpt": row[2],
                    "source": row[3],
                    "status": row[4],
                    "image_url": row[5],
                    "created_at": row[6].isoformat() if row[6] else None,
                    "published_at": row[7].isoformat() if row[7] else None,
                })
            
            # Get total and stats
            stats_result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'pending') as pending,
                    COUNT(*) FILTER (WHERE status = 'approved') as approved,
                    COUNT(*) FILTER (WHERE status = 'rejected') as rejected
                FROM admin_news
            """))
            stats = stats_result.fetchone()
            
            return {
                "articles": articles,
                "total": stats[0] if stats else 0,
                "stats": {
                    "pending": stats[1] if stats else 0,
                    "approved": stats[2] if stats else 0,
                    "rejected": stats[3] if stats else 0,
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/news")
async def create_news(article: NewsArticle):
    """Create a new article"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            result = conn.execute(
                text("""
                    INSERT INTO admin_news (title, content, excerpt, source, source_url, image_url, coin_ids, tags)
                    VALUES (:title, :content, :excerpt, :source, :source_url, :image_url, :coin_ids, :tags)
                    RETURNING id
                """),
                {
                    "title": article.title,
                    "content": article.content,
                    "excerpt": article.excerpt or article.content[:200] if article.content else "",
                    "source": article.source,
                    "source_url": article.source_url,
                    "image_url": article.image_url,
                    "coin_ids": article.coin_ids or [],
                    "tags": article.tags or [],
                }
            )
            conn.commit()
            article_id = result.fetchone()[0]
            
            return {"success": True, "id": article_id, "message": "Article created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/news/{article_id}")
async def update_news(article_id: int, update: NewsUpdate):
    """Update article (approve, reject, edit)"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            updates = []
            params = {"id": article_id}
            
            if update.status is not None:
                updates.append("status = :status")
                params["status"] = update.status
                if update.status == "approved":
                    updates.append("published_at = NOW()")
                    updates.append("reviewed_at = NOW()")
            if update.title is not None:
                updates.append("title = :title")
                params["title"] = update.title
            if update.content is not None:
                updates.append("content = :content")
                params["content"] = update.content
            if update.excerpt is not None:
                updates.append("excerpt = :excerpt")
                params["excerpt"] = update.excerpt
            
            if not updates:
                return {"success": True, "message": "No updates provided"}
            
            updates.append("updated_at = NOW()")
            
            conn.execute(
                text(f"UPDATE admin_news SET {', '.join(updates)} WHERE id = :id"),
                params
            )
            conn.commit()
            
            return {"success": True, "id": article_id, "message": f"Article {article_id} updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/news/{article_id}")
async def delete_news(article_id: int):
    """Delete an article"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            conn.execute(text("DELETE FROM admin_news WHERE id = :id"), {"id": article_id})
            conn.commit()
            return {"success": True, "message": f"Article {article_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
