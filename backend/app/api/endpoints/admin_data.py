"""
Admin Data Management API
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
    source: Optional[str] = None
    url: Optional[str] = None
    coin_ids: Optional[List[str]] = None


class NewsUpdate(BaseModel):
    status: Optional[str] = None  # pending, approved, rejected
    title: Optional[str] = None
    content: Optional[str] = None


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
            # Build query
            where_clauses = []
            params = {"limit": limit, "offset": offset}
            
            if search:
                where_clauses.append("(LOWER(name) LIKE :search OR LOWER(symbol) LIKE :search)")
                params["search"] = f"%{search.lower()}%"
            
            where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
            
            query = f"""
                SELECT 
                    coin_id, symbol, name, image_url as image, 
                    rank, price, change_24h, market_cap, volume_24h
                FROM aihub_coins
                {where_sql}
                ORDER BY rank ASC NULLS LAST
                LIMIT :limit OFFSET :offset
            """
            
            result = conn.execute(text(query), params)
            coins = [dict(row._mapping) for row in result]
            
            # Get total count
            count_query = f"SELECT COUNT(*) FROM aihub_coins {where_sql}"
            total = conn.execute(text(count_query), params).scalar() or 0
            
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
            query = """
                SELECT * FROM aihub_coins WHERE coin_id = :coin_id
            """
            result = conn.execute(text(query), {"coin_id": coin_id})
            row = result.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Coin not found")
            
            return dict(row._mapping)
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
            if update.category is not None:
                updates.append("category = :category")
                params["category"] = update.category
            
            if not updates:
                return {"success": True, "message": "No updates provided"}
            
            query = f"""
                UPDATE aihub_coins 
                SET {', '.join(updates)}, updated_at = NOW()
                WHERE coin_id = :coin_id
            """
            conn.execute(text(query), params)
            conn.commit()
            
            return {"success": True, "message": f"Coin {coin_id} updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Market Corrections ====================

@router.get("/corrections")
async def list_corrections(limit: int = 50):
    """List market correction history"""
    # TODO: Query from corrections table when available
    return {
        "corrections": [],
        "total": 0,
    }


@router.post("/corrections")
async def create_correction(correction: MarketCorrection):
    """Apply a manual price correction"""
    try:
        db = get_database_service()
        with db.engine.connect() as conn:
            # Get current price for logging
            result = conn.execute(
                text("SELECT price FROM aihub_coins WHERE coin_id = :coin_id"),
                {"coin_id": correction.coin_id}
            )
            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Coin not found")
            
            old_price = float(row[0]) if row[0] else 0
            
            # Update price
            conn.execute(
                text("""
                    UPDATE aihub_coins 
                    SET price = :price, last_updated = NOW()
                    WHERE coin_id = :coin_id
                """),
                {"coin_id": correction.coin_id, "price": correction.new_price}
            )
            conn.commit()
            
            # TODO: Log correction to audit table
            
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
    # TODO: Query from news table when available
    # For now return mock data
    return {
        "articles": [
            {
                "id": 1,
                "title": "Bitcoin Surges Past $90,000",
                "excerpt": "Bitcoin reaches new all-time high...",
                "source": "CoinDesk",
                "status": "pending",
                "created_at": datetime.now().isoformat(),
            }
        ],
        "total": 1,
    }


@router.post("/news")
async def create_news(article: NewsArticle):
    """Create a new article"""
    # TODO: Insert into news table
    return {
        "success": True,
        "id": 1,
        "message": "Article created",
    }


@router.put("/news/{article_id}")
async def update_news(article_id: int, update: NewsUpdate):
    """Update article (approve, reject, edit)"""
    # TODO: Update in database
    return {
        "success": True,
        "id": article_id,
        "message": f"Article {article_id} updated",
    }


@router.delete("/news/{article_id}")
async def delete_news(article_id: int):
    """Delete an article"""
    # TODO: Delete from database
    return {
        "success": True,
        "message": f"Article {article_id} deleted",
    }
