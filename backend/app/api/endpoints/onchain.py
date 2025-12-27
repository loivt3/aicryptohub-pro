"""
On-Chain Data Endpoints
Fetches real on-chain data from database
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.database import get_database_service

router = APIRouter()


class WhaleActivity(BaseModel):
    signal: str
    tx_count_24h: int
    change_24h_pct: float
    net_flow_usd: float
    inflow_usd: float = 0
    outflow_usd: float = 0


class NetworkHealth(BaseModel):
    signal: str
    dau_current: int
    dau_change_1d_pct: float
    trend: str


class HolderSignals(BaseModel):
    signal: str
    top10_change_pct: float
    accumulation_score: float


class OnChainSignals(BaseModel):
    coin_id: str
    overall_signal: str
    bullish_probability: float
    confidence_score: float = 50.0
    whale_activity: WhaleActivity
    network_health: NetworkHealth
    holder_signals: Optional[HolderSignals] = None
    ai_prediction: Optional[str] = None
    ai_summary: Optional[str] = None
    last_updated: Optional[datetime] = None


@router.get("/summary")
async def get_onchain_summary():
    """Get on-chain summary for top coins including whale transactions"""
    try:
        db = get_database_service()
        from sqlalchemy import text
        
        # Get signals summary
        signals_data = db.get_onchain_summary()
        
        # Get recent whale transactions (7 days to ensure data availability)
        whale_query = text("""
            SELECT coin_id, tx_type, value_usd, from_address, to_address, 
                   exchange_name, tx_timestamp
            FROM whale_transactions
            WHERE tx_timestamp > NOW() - INTERVAL '7 days'
            ORDER BY tx_timestamp DESC
            LIMIT 20
        """)
        
        recent_whale_txs = []
        try:
            with db.engine.connect() as conn:
                result = conn.execute(whale_query)
                for row in result.fetchall():
                    recent_whale_txs.append({
                        "coin_id": row[0],
                        "tx_type": row[1],
                        "value_usd": float(row[2]) if row[2] else 0,
                        "from_address": row[3],
                        "to_address": row[4],
                        "exchange_name": row[5],
                        "tx_timestamp": row[6].isoformat() if row[6] else None,
                    })
        except Exception as e:
            print(f"Error fetching whale txs: {e}")
        
        # Calculate aggregates
        total_inflow = sum(
            t["value_usd"] for t in recent_whale_txs 
            if t.get("tx_type") == "exchange_deposit"
        )
        total_outflow = sum(
            t["value_usd"] for t in recent_whale_txs 
            if t.get("tx_type") == "exchange_withdraw"
        )
        
        # Group signals by type
        stats = {"bullish_count": 0, "bearish_count": 0, "neutral_count": 0}
        btc_data = None
        eth_data = None
        other_coins = []
        
        for coin in signals_data:
            signal = coin.get("overall_signal", "NEUTRAL")
            if signal == "BULLISH":
                stats["bullish_count"] += 1
            elif signal == "BEARISH":
                stats["bearish_count"] += 1
            else:
                stats["neutral_count"] += 1
            
            if coin.get("coin_id") == "bitcoin":
                btc_data = coin
            elif coin.get("coin_id") == "ethereum":
                eth_data = coin
            else:
                other_coins.append(coin)
        
        # Top signals by accumulation score
        top_signals = sorted(
            signals_data, 
            key=lambda x: x.get("bullish_probability", 50), 
            reverse=True
        )[:10]
        
        return {
            "success": True,
            "btc": btc_data,
            "eth": eth_data,
            "coins": other_coins,
            "stats": stats,
            "recent_whale_txs": recent_whale_txs,
            "top_signals": top_signals,
            "total_inflow_24h": total_inflow,
            "total_outflow_24h": total_outflow,
            "gas_price_gwei": 28,  # TODO: fetch from API
            "active_addresses_24h": 0,  # TODO: calculate
            "stablecoin_inflow_24h": 0,  # TODO: calculate
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None,
        }


@router.get("/btc")
async def get_onchain_btc():
    """Get Bitcoin on-chain metrics"""
    try:
        db = get_database_service()
        data = db.get_onchain_signals("bitcoin")
        
        if not data:
            return {
                "success": False,
                "error": "No on-chain data for bitcoin",
                "data": None,
            }
        
        return {
            "success": True,
            "data": {
                "whale_tx_count_24h": data.get("whale_tx_count_24h", 0),
                "whale_net_flow_usd": data.get("whale_net_flow_usd", 0),
                "whale_signal": data.get("whale_signal", "NEUTRAL"),
                "dau_current": data.get("dau_current", 0),
                "dau_change_1d_pct": data.get("dau_change_1d_pct", 0),
                "network_signal": data.get("network_signal", "NEUTRAL"),
                "overall_signal": data.get("overall_signal", "NEUTRAL"),
                "bullish_probability": data.get("bullish_probability", 50),
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None,
        }


@router.get("/eth")
async def get_onchain_eth():
    """Get Ethereum on-chain metrics"""
    try:
        db = get_database_service()
        data = db.get_onchain_signals("ethereum")
        
        if not data:
            return {
                "success": False,
                "error": "No on-chain data for ethereum",
                "data": None,
            }
        
        return {
            "success": True,
            "data": {
                "whale_tx_count_24h": data.get("whale_tx_count_24h", 0),
                "whale_net_flow_usd": data.get("whale_net_flow_usd", 0),
                "whale_signal": data.get("whale_signal", "NEUTRAL"),
                "dau_current": data.get("dau_current", 0),
                "dau_change_1d_pct": data.get("dau_change_1d_pct", 0),
                "network_signal": data.get("network_signal", "NEUTRAL"),
                "overall_signal": data.get("overall_signal", "NEUTRAL"),
                "bullish_probability": data.get("bullish_probability", 50),
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None,
        }


@router.get("/signals/{coin_id}")
async def get_onchain_signals(coin_id: str):
    """Get on-chain signals for a specific coin"""
    try:
        db = get_database_service()
        data = db.get_onchain_signals(coin_id)
        
        if not data:
            # Return empty/neutral data if no signals exist
            return OnChainSignals(
                coin_id=coin_id,
                overall_signal="NEUTRAL",
                bullish_probability=50.0,
                confidence_score=0.0,
                whale_activity=WhaleActivity(
                    signal="NEUTRAL",
                    tx_count_24h=0,
                    change_24h_pct=0.0,
                    net_flow_usd=0.0,
                    inflow_usd=0.0,
                    outflow_usd=0.0,
                ),
                network_health=NetworkHealth(
                    signal="NEUTRAL",
                    dau_current=0,
                    dau_change_1d_pct=0.0,
                    trend="STABLE",
                ),
                ai_summary=f"No on-chain data available for {coin_id}",
            )
        
        # Build response from database data
        return OnChainSignals(
            coin_id=coin_id,
            overall_signal=data.get("overall_signal") or "NEUTRAL",
            bullish_probability=float(data.get("bullish_probability") or 50),
            confidence_score=float(data.get("confidence_score") or 50),
            whale_activity=WhaleActivity(
                signal=data.get("whale_signal") or "NEUTRAL",
                tx_count_24h=int(data.get("whale_tx_count_24h") or 0),
                change_24h_pct=float(data.get("whale_tx_change_pct") or 0),
                net_flow_usd=float(data.get("whale_net_flow_usd") or 0),
                inflow_usd=float(data.get("whale_inflow_usd") or 0),
                outflow_usd=float(data.get("whale_outflow_usd") or 0),
            ),
            network_health=NetworkHealth(
                signal=data.get("network_signal") or "NEUTRAL",
                dau_current=int(data.get("dau_current") or 0),
                dau_change_1d_pct=float(data.get("dau_change_1d_pct") or 0),
                trend=data.get("dau_trend") or "STABLE",
            ),
            holder_signals=HolderSignals(
                signal=data.get("holder_signal") or "NEUTRAL",
                top10_change_pct=float(data.get("top10_change_pct") or 0),
                accumulation_score=float(data.get("accumulation_score") or 50),
            ) if data.get("holder_signal") else None,
            ai_prediction=data.get("ai_prediction"),
            ai_summary=data.get("ai_summary"),
            last_updated=data.get("updated_at"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/whale-stream")
async def get_whale_stream(limit: int = 10):
    """
    Get aggregated whale stream data from multiple sources.
    
    Sources:
    - Arkham Intelligence (if API key configured)
    - Whale Alert (if API key configured)
    - Internal whale_transactions table
    
    Returns:
        Combined list of whale transactions with source attribution
    """
    from app.services.arkham_client import get_arkham_client
    from app.services.whale_alert_client import get_whale_alert_client
    import asyncio
    
    all_transactions = []
    sources_status = {
        "arkham": False,
        "whale_alert": False,
        "internal": False,
    }
    
    # Fetch from Arkham Intelligence
    arkham = get_arkham_client()
    if arkham.is_configured():
        try:
            arkham_txs = await arkham.get_recent_transfers(limit=limit, min_usd=500000)
            all_transactions.extend(arkham_txs)
            sources_status["arkham"] = True
        except Exception as e:
            print(f"[WhaleStream] Arkham error: {e}")
    
    # Fetch from Whale Alert
    whale_alert = get_whale_alert_client()
    if whale_alert.is_configured():
        try:
            wa_txs = await whale_alert.get_recent_transactions(min_value=500000, limit=limit)
            all_transactions.extend(wa_txs)
            sources_status["whale_alert"] = True
        except Exception as e:
            print(f"[WhaleStream] Whale Alert error: {e}")
    
    # Fetch from internal database
    try:
        db = get_database_service()
        from sqlalchemy import text
        
        internal_query = text("""
            SELECT coin_id, tx_type, value_usd, from_address, to_address, 
                   exchange_name, tx_timestamp, tx_hash
            FROM whale_transactions
            WHERE tx_timestamp > NOW() - INTERVAL '24 hours'
              AND value_usd > 100000
            ORDER BY tx_timestamp DESC
            LIMIT :limit
        """)
        
        with db.engine.connect() as conn:
            result = conn.execute(internal_query, {"limit": limit})
            for row in result.fetchall():
                all_transactions.append({
                    "tx_hash": row[7] if len(row) > 7 else "",
                    "chain": "ethereum" if row[0] == "ethereum" else "bitcoin",
                    "from_address": row[3] or "",
                    "from_entity": "Unknown Wallet",
                    "to_address": row[4] or "",
                    "to_entity": row[5] or "Unknown",
                    "value_usd": float(row[2]) if row[2] else 0,
                    "token_symbol": row[0].upper() if row[0] else "",
                    "timestamp": row[6].isoformat() if row[6] else "",
                    "tx_type": row[1] or "transfer",
                    "source": "internal",
                })
        sources_status["internal"] = True
    except Exception as e:
        print(f"[WhaleStream] Internal DB error: {e}")
    
    # Sort all by timestamp (newest first)
    all_transactions.sort(
        key=lambda x: x.get("timestamp", ""),
        reverse=True
    )
    
    # Deduplicate by tx_hash
    seen_hashes = set()
    unique_txs = []
    for tx in all_transactions:
        tx_hash = tx.get("tx_hash", "")
        if tx_hash and tx_hash in seen_hashes:
            continue
        if tx_hash:
            seen_hashes.add(tx_hash)
        unique_txs.append(tx)
    
    # Limit results
    unique_txs = unique_txs[:limit]
    
    return {
        "success": True,
        "transactions": unique_txs,
        "sources": sources_status,
        "count": len(unique_txs),
        "timestamp": datetime.now().isoformat(),
    }

