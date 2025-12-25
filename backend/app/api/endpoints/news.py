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


@router.get("/live")
async def get_live_news(
    coin_id: str = Query("bitcoin", description="Coin ID for news (e.g., bitcoin, ethereum)"),
    limit: int = Query(10, le=20),
):
    """
    Get live news from CryptoPanic API via NewsAggregator.
    Falls back to mock data if no API key configured.
    """
    try:
        from app.services.news_aggregator import get_news_aggregator
        
        aggregator = get_news_aggregator()
        
        # Fetch news for specific coin
        news_items = await aggregator.fetch_news(coin_id=coin_id, limit=limit)
        
        articles = []
        for item in news_items:
            # Format time_ago
            if item.publish_time:
                delta = datetime.now() - item.publish_time.replace(tzinfo=None)
                if delta.days > 0:
                    time_ago = f"{delta.days}d ago"
                elif delta.seconds > 3600:
                    time_ago = f"{delta.seconds // 3600}h ago"
                elif delta.seconds > 60:
                    time_ago = f"{delta.seconds // 60}m ago"
                else:
                    time_ago = "Just now"
            else:
                time_ago = "Just now"
            
            # Map emotional tone to tag
            tag = item.emotional_tone.value.upper()
            if tag == "NEUTRAL":
                tag = "NEWS"
            
            articles.append({
                "id": item.event_id,
                "title": item.title,
                "excerpt": item.summary,
                "source": item.source,
                "source_url": item.source_url,
                "tag": tag,
                "category": item.category.value,
                "coin_id": item.coin_id,
                "symbol": item.symbol,
                "time_ago": time_ago,
                "intensity": item.news_intensity,
                "published_at": item.publish_time.isoformat() if item.publish_time else None,
            })
        
        return {
            "success": True,
            "articles": articles,
            "total": len(articles),
            "coin_id": coin_id,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "articles": [],
            "total": 0,
        }


@router.get("/feed")
async def get_news_feed(limit: int = Query(10, le=30)):
    """
    Get aggregated news feed for multiple major coins.
    Combines live news from BTC, ETH, and SOL.
    """
    try:
        from app.services.news_aggregator import get_news_aggregator
        
        aggregator = get_news_aggregator()
        
        all_articles = []
        
        # Fetch news for major coins
        for coin_id in ["bitcoin", "ethereum", "solana"]:
            try:
                items = await aggregator.fetch_news(coin_id=coin_id, limit=5)
                for item in items:
                    # Format time_ago
                    if item.publish_time:
                        delta = datetime.now() - item.publish_time.replace(tzinfo=None)
                        if delta.days > 0:
                            time_ago = f"{delta.days}d ago"
                        elif delta.seconds > 3600:
                            time_ago = f"{delta.seconds // 3600}h ago"
                        elif delta.seconds > 60:
                            time_ago = f"{delta.seconds // 60}m ago"
                        else:
                            time_ago = "Just now"
                    else:
                        time_ago = "Just now"
                    
                    tag = item.emotional_tone.value.upper()
                    if tag == "NEUTRAL":
                        tag = "NEWS"
                    
                    all_articles.append({
                        "id": item.event_id,
                        "title": item.title,
                        "excerpt": item.summary,
                        "source": item.source,
                        "tag": tag,
                        "category": item.category.value,
                        "coin_id": item.coin_id,
                        "symbol": item.symbol,
                        "time_ago": time_ago,
                        "intensity": item.news_intensity,
                        "published_at": item.publish_time.isoformat() if item.publish_time else None,
                    })
            except Exception as e:
                print(f"Failed to fetch news for {coin_id}: {e}")
        
        # Sort by publish time (most recent first)
        all_articles.sort(
            key=lambda x: x.get("published_at") or "", 
            reverse=True
        )
        
        return {
            "success": True,
            "articles": all_articles[:limit],
            "total": len(all_articles[:limit]),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "articles": [],
            "total": 0,
        }
