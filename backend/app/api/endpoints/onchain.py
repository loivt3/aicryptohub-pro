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
    """Get on-chain summary for top coins"""
    try:
        db = get_database_service()
        data = db.get_onchain_summary()
        
        # Group by signal type
        summary = {
            "btc": None,
            "eth": None,
            "coins": [],
            "stats": {
                "bullish_count": 0,
                "bearish_count": 0,
                "neutral_count": 0,
            }
        }
        
        for coin in data:
            signal = coin.get("overall_signal", "NEUTRAL")
            if signal == "BULLISH":
                summary["stats"]["bullish_count"] += 1
            elif signal == "BEARISH":
                summary["stats"]["bearish_count"] += 1
            else:
                summary["stats"]["neutral_count"] += 1
            
            if coin.get("coin_id") == "bitcoin":
                summary["btc"] = coin
            elif coin.get("coin_id") == "ethereum":
                summary["eth"] = coin
            else:
                summary["coins"].append(coin)
        
        return {
            "success": True,
            "data": summary,
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
