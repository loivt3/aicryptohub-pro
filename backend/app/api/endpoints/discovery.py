"""
Market Discovery API Endpoints
Fast access to pre-computed market metrics.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query, Depends, BackgroundTasks

from app.services.database import DatabaseService, get_db_service
from app.services.discovery_engine import DiscoveryEngine, get_discovery_engine

router = APIRouter()


@router.get("/top-gainers")
async def get_top_gainers(
    timeframe: str = Query(default="1h", description="1h, 4h, 24h, or 7d"),
    limit: int = Query(default=10, le=50),
):
    """
    Get top gaining coins.
    
    Args:
        timeframe: Time period for % change (1h, 4h, 24h, 7d)
        limit: Number of results (max 50)
        
    Returns:
        List of top gainers sorted by % change DESC
    """
    engine = get_discovery_engine()
    data = engine.get_top_gainers(timeframe=timeframe, limit=limit)
    
    return {
        "success": True,
        "data": data,
        "meta": {
            "timeframe": timeframe,
            "count": len(data),
            "timestamp": datetime.now().isoformat(),
        }
    }


@router.get("/top-losers")
async def get_top_losers(
    timeframe: str = Query(default="1h", description="1h, 4h, 24h, or 7d"),
    limit: int = Query(default=10, le=50),
):
    """
    Get top losing coins.
    
    Args:
        timeframe: Time period for % change (1h, 4h, 24h, 7d)
        limit: Number of results (max 50)
        
    Returns:
        List of top losers sorted by % change ASC
    """
    engine = get_discovery_engine()
    data = engine.get_top_losers(timeframe=timeframe, limit=limit)
    
    return {
        "success": True,
        "data": data,
        "meta": {
            "timeframe": timeframe,
            "count": len(data),
            "timestamp": datetime.now().isoformat(),
        }
    }


@router.get("/sudden-pump")
async def get_sudden_pumps(
    limit: int = Query(default=10, le=50),
):
    """
    Get coins with sudden pump signals.
    
    Criteria:
    - change_1h > 3%
    - volume_1h > 2x average hourly volume
    - volume_24h > $100k (filter low liquidity)
    
    Returns:
        List of sudden pump candidates
    """
    engine = get_discovery_engine()
    data = engine.get_sudden_pumps(limit=limit)
    
    return {
        "success": True,
        "data": data,
        "meta": {
            "detection_criteria": {
                "min_change_1h": "3%",
                "min_volume_spike": "2x average",
                "min_volume_24h": "$100k",
            },
            "count": len(data),
            "timestamp": datetime.now().isoformat(),
        }
    }


@router.get("/sudden-dump")
async def get_sudden_dumps(
    limit: int = Query(default=10, le=50),
):
    """
    Get coins with sudden dump/crash signals.
    
    Criteria:
    - change_1h < -3%
    - volume_1h > 2x average hourly volume
    - volume_24h > $100k (filter low liquidity)
    
    Returns:
        List of sudden dump candidates
    """
    engine = get_discovery_engine()
    data = engine.get_sudden_dumps(limit=limit)
    
    return {
        "success": True,
        "data": data,
        "meta": {
            "detection_criteria": {
                "max_change_1h": "-3%",
                "min_volume_spike": "2x average",
                "min_volume_24h": "$100k",
            },
            "count": len(data),
            "timestamp": datetime.now().isoformat(),
        }
    }


@router.get("/most-traded")
async def get_most_traded(
    limit: int = Query(default=10, le=50),
):
    """
    Get most traded coins by 24h volume.
    
    Returns:
        List of most traded coins sorted by volume DESC
    """
    engine = get_discovery_engine()
    data = engine.get_most_traded(limit=limit)
    
    return {
        "success": True,
        "data": data,
        "meta": {
            "count": len(data),
            "timestamp": datetime.now().isoformat(),
        }
    }


@router.post("/refresh")
async def refresh_discovery_snapshot(
    background_tasks: BackgroundTasks,
    db: DatabaseService = Depends(get_db_service),
):
    """
    Trigger a refresh of the discovery snapshot.
    
    Note: This is usually handled by the scheduler (every 5 min).
    Use this endpoint for manual refresh.
    """
    engine = DiscoveryEngine(db)
    
    async def run_update():
        await engine.update_snapshot()
    
    background_tasks.add_task(run_update)
    
    return {
        "success": True,
        "message": "Discovery snapshot refresh scheduled",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/status")
async def get_discovery_status():
    """Get current discovery snapshot status."""
    from sqlalchemy import text
    
    db = get_db_service()
    
    try:
        with db.engine.connect() as conn:
            # Get snapshot stats
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_coins,
                    COUNT(CASE WHEN is_sudden_pump THEN 1 END) as pumps,
                    COUNT(CASE WHEN is_sudden_dump THEN 1 END) as dumps,
                    MAX(updated_at) as last_update
                FROM market_discovery_snapshot
            """))
            row = result.fetchone()
            
            if row:
                return {
                    "success": True,
                    "data": {
                        "total_coins": row[0],
                        "active_pumps": row[1],
                        "active_dumps": row[2],
                        "last_update": row[3].isoformat() if row[3] else None,
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "No snapshot data found",
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@router.get("/pattern-accuracy")
async def get_pattern_accuracy():
    """
    Get historical accuracy of candlestick patterns.
    
    Tracks how well each pattern predicted price movement.
    Returns:
        Accuracy stats per pattern type
    """
    from sqlalchemy import text
    
    db = get_db_service()
    
    try:
        with db.engine.connect() as conn:
            # Get pattern accuracy from historical data
            result = conn.execute(text("""
                WITH pattern_outcomes AS (
                    SELECT 
                        p.pattern,
                        p.direction,
                        p.coin_id,
                        p.detected_at,
                        -- Check price 4h after pattern
                        CASE 
                            WHEN p.direction = 'BULLISH' AND 
                                 COALESCE(c.change_1h, 0) + COALESCE(c.change_24h * 4/24, 0) > 0 
                            THEN TRUE
                            WHEN p.direction = 'BEARISH' AND 
                                 COALESCE(c.change_1h, 0) + COALESCE(c.change_24h * 4/24, 0) < 0 
                            THEN TRUE
                            ELSE FALSE
                        END as was_correct
                    FROM aihub_patterns p
                    LEFT JOIN coins c ON p.coin_id = c.coin_id
                    WHERE p.detected_at > NOW() - INTERVAL '7 days'
                )
                SELECT 
                    pattern,
                    direction,
                    COUNT(*) as total_signals,
                    COUNT(CASE WHEN was_correct THEN 1 END) as correct_signals,
                    ROUND(COUNT(CASE WHEN was_correct THEN 1 END)::numeric / NULLIF(COUNT(*), 0) * 100, 1) as accuracy_pct
                FROM pattern_outcomes
                GROUP BY pattern, direction
                ORDER BY accuracy_pct DESC NULLS LAST
            """))
            rows = result.fetchall()
            
            patterns = []
            for row in rows:
                patterns.append({
                    "pattern": row[0],
                    "direction": row[1],
                    "total_signals": row[2],
                    "correct_signals": row[3],
                    "accuracy_pct": float(row[4]) if row[4] else 0,
                })
            
            # Get overall stats
            total = sum(p["total_signals"] for p in patterns)
            correct = sum(p["correct_signals"] for p in patterns)
            
            return {
                "success": True,
                "data": {
                    "patterns": patterns,
                    "summary": {
                        "total_patterns_detected": total,
                        "total_correct": correct,
                        "overall_accuracy": round(correct / total * 100, 1) if total > 0 else 0,
                        "period": "7 days",
                    }
                },
                "timestamp": datetime.now().isoformat(),
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@router.get("/technical-signals")
async def get_technical_signals(
    limit: int = Query(default=20, le=50),
    signal_type: str = Query(default="all", description="all, bullish, bearish"),
):
    """
    Get coins with strong technical signals.
    
    Includes:
    - Candlestick patterns
    - RSI divergence
    - MACD signals
    - Bollinger Band signals
    - Multi-factor confirmations
    
    Returns:
        List of coins with technical analysis data
    """
    from sqlalchemy import text
    
    db = get_db_service()
    
    try:
        # Build direction filter
        direction_filter = ""
        if signal_type == "bullish":
            direction_filter = "AND (pattern_direction = 'BULLISH' OR divergence_type = 'BULLISH_DIV')"
        elif signal_type == "bearish":
            direction_filter = "AND (pattern_direction = 'BEARISH' OR divergence_type = 'BEARISH_DIV')"
        
        with db.engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT 
                    mds.coin_id, mds.symbol, mds.name, mds.image,
                    COALESCE(ac.price, mds.price) as price,
                    COALESCE(ac.price_change_1h, mds.change_1h) as change_1h,
                    COALESCE(ac.change_24h, mds.change_24h) as change_24h,
                    mds.pattern_name, mds.pattern_direction, mds.pattern_reliability,
                    mds.divergence_type, mds.rsi_14,
                    mds.macd_signal_type, mds.macd_histogram,
                    mds.bb_position, mds.bb_squeeze, mds.bb_width,
                    mds.confirmation_count, mds.confirmation_score,
                    mds.signal_strength, mds.discovery_score,
                    COALESCE(ac.volume_24h, mds.volume_24h) as volume_24h,
                    COALESCE(ac.rank, mds.market_cap_rank) as market_cap_rank
                FROM market_discovery_snapshot mds
                LEFT JOIN aihub_coins ac ON UPPER(mds.symbol) = ac.symbol
                WHERE (mds.pattern_name IS NOT NULL OR mds.divergence_type IS NOT NULL)
                  AND COALESCE(ac.volume_24h, mds.volume_24h) > 100000
                  {direction_filter}
                ORDER BY mds.confirmation_count DESC, mds.discovery_score DESC
                LIMIT :limit
            """), {"limit": limit})
            
            rows = result.fetchall()
            columns = result.keys()
            
            signals = []
            for row in rows:
                signal = {col: (
                    round(float(row[i]), 4) if isinstance(row[i], (float,)) else row[i]
                ) for i, col in enumerate(columns)}
                signals.append(signal)
            
            return {
                "success": True,
                "data": signals,
                "meta": {
                    "signal_type": signal_type,
                    "count": len(signals),
                    "timestamp": datetime.now().isoformat(),
                }
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@router.get("/hidden-gems")
async def get_hidden_gems(
    limit: int = Query(default=10, le=30),
):
    """
    Get potential hidden gem coins (v2 - enhanced criteria).
    
    Stricter Criteria:
    - High discovery score (≥75, was 70)
    - At least 2 confirmations
    - Market cap rank > 50 (include mid-caps)
    - Outperforming BTC and market
    - Not recently pumped (change_24h < 30%)
    - Sufficient volume ($100k+)
    
    Returns:
        List of potential hidden gems with technical details
    """
    from sqlalchemy import text
    
    db = get_db_service()
    
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    mds.coin_id, mds.symbol, mds.name, mds.image,
                    COALESCE(ac.price, mds.price) as price,
                    COALESCE(ac.price_change_1h, mds.change_1h) as change_1h,
                    COALESCE(ac.change_24h, mds.change_24h) as change_24h,
                    COALESCE(ac.price_change_7d, mds.change_7d) as change_7d,
                    mds.momentum_score, mds.rs_score, mds.discovery_score,
                    mds.rs_vs_btc, mds.rs_vs_market,
                    mds.pattern_name, mds.pattern_direction,
                    mds.divergence_type, mds.rsi_14,
                    mds.bb_position, mds.macd_signal_type,
                    mds.confirmation_count, mds.signal_strength,
                    mds.is_accumulating, mds.accumulation_score,
                    COALESCE(ac.volume_24h, mds.volume_24h) as volume_24h,
                    mds.volume_ratio, 
                    COALESCE(ac.market_cap, mds.market_cap) as market_cap,
                    COALESCE(ac.rank, mds.market_cap_rank) as market_cap_rank
                FROM market_discovery_snapshot mds
                LEFT JOIN aihub_coins ac ON UPPER(mds.symbol) = ac.symbol
                WHERE mds.discovery_score >= 70
                  AND mds.market_cap_rank > 50
                  AND COALESCE(ac.change_24h, mds.change_24h) < 30
                  AND COALESCE(ac.volume_24h, mds.volume_24h) > 100000
                ORDER BY 
                    CASE WHEN mds.is_accumulating THEN 1 ELSE 0 END DESC,
                    mds.discovery_score DESC, 
                    mds.confirmation_count DESC
                LIMIT :limit
            """), {"limit": limit})
            
            rows = result.fetchall()
            columns = result.keys()
            
            gems = []
            for row in rows:
                gem = {col: (
                    round(float(row[i]), 4) if isinstance(row[i], (float,)) else row[i]
                ) for i, col in enumerate(columns)}
                gems.append(gem)
            
            # Get success rate stats if available
            success_stats = None
            try:
                stats_result = conn.execute(text("""
                    SELECT * FROM v_gems_overall_stats LIMIT 1
                """))
                stats_row = stats_result.fetchone()
                if stats_row:
                    success_stats = {
                        "total_gems_tracked": stats_row[0],
                        "success_count": stats_row[1],
                        "success_rate_pct": float(stats_row[10]) if stats_row[10] else None,
                        "avg_return_7d": float(stats_row[3]) if stats_row[3] else None,
                        "avg_return_30d": float(stats_row[4]) if stats_row[4] else None,
                        "alpha_30d": float(stats_row[7]) if stats_row[7] else None,
                    }
            except:
                pass  # View may not exist yet
            
            return {
                "success": True,
                "data": gems,
                "meta": {
                    "criteria": {
                        "min_discovery_score": 70,
                        "min_confirmations": 1,
                        "min_market_cap_rank": 50,
                        "max_recent_pump": "30%",
                        "outperforming_or_accumulating": True,
                        "min_volume_24h": "$100k",
                    },
                    "success_stats": success_stats,
                    "count": len(gems),
                    "timestamp": datetime.now().isoformat(),
                }
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@router.get("/high-rich")
async def get_high_rich(
    limit: int = Query(default=10, le=30),
):
    """
    Get High Rich coins - simpler criteria, shorter timeframe.
    
    Criteria (Simpler):
    - Strong 1h momentum (change_1h > 1%)
    - High ASI score (asi_score >= 60)
    - Volume spike (volume_ratio > 1.2)
    - Not recently over-pumped (change_24h < 50%)
    
    Focus on SHORT-TERM opportunities.
    """
    from sqlalchemy import text
    
    db = get_db_service()
    
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    ac.coin_id, ac.symbol, ac.name, ac.image,
                    ac.price, 
                    COALESCE(ac.price_change_1h, mds.change_1h, 0) as change_1h,
                    COALESCE(ac.change_24h, mds.change_24h, 0) as change_24h, 
                    COALESCE(ac.price_change_7d, mds.change_7d, 0) as change_7d,
                    COALESCE(ac.asi_score, 50) as asi_score, 
                    ac.ai_signal,
                    COALESCE(ac.volume_24h, mds.volume_24h, 0) as volume_24h, 
                    COALESCE(ac.market_cap, mds.market_cap, 0) as market_cap, 
                    COALESCE(ac.rank, mds.market_cap_rank, 500) as market_cap_rank,
                    mds.volume_ratio, mds.rsi_14, mds.momentum_score,
                    mds.discovery_score
                FROM aihub_coins ac
                LEFT JOIN market_discovery_snapshot mds ON UPPER(mds.symbol) = ac.symbol
                WHERE COALESCE(ac.price_change_1h, mds.change_1h, 0) > 0
                  AND COALESCE(ac.rank, mds.market_cap_rank, 500) > 20
                  AND COALESCE(ac.volume_24h, mds.volume_24h, 0) > 50000
                ORDER BY 
                    COALESCE(mds.discovery_score, 0) DESC,
                    COALESCE(ac.price_change_1h, mds.change_1h, 0) DESC
                LIMIT :limit
            """), {"limit": limit})
            
            rows = result.fetchall()
            columns = result.keys()
            
            high_rich = []
            for row in rows:
                item = {col: (
                    round(float(row[i]), 4) if isinstance(row[i], (float,)) else row[i]
                ) for i, col in enumerate(columns)}
                high_rich.append(item)
            
            return {
                "success": True,
                "data": high_rich,
                "meta": {
                    "criteria": {
                        "min_change_1h": "1%",
                        "min_asi_score": 60,
                        "min_volume_ratio": 1.0,
                        "max_change_24h": "50%",
                        "timeframe": "1H (Short-term)",
                    },
                    "count": len(high_rich),
                    "timestamp": datetime.now().isoformat(),
                }
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
