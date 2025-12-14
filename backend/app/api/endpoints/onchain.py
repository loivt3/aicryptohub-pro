"""
On-Chain Data Endpoints
Port từ PHP class-rest-api.php và Python services
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class WhaleActivity(BaseModel):
    signal: str
    tx_count_24h: int
    change_24h_pct: float
    net_flow_usd: float


class NetworkHealth(BaseModel):
    signal: str
    dau_current: int
    dau_change_1d_pct: float
    trend: str


class OnChainSignals(BaseModel):
    coin_id: str
    overall_signal: str
    bullish_probability: float
    whale_activity: WhaleActivity
    network_health: NetworkHealth
    ai_prediction: Optional[str] = None
    ai_summary: Optional[str] = None
    last_updated: Optional[datetime] = None


@router.get("/summary")
async def get_onchain_summary():
    """Get all on-chain metrics summary"""
    return {
        "success": True,
        "data": {
            "btc": {},
            "eth": {},
            "defi": {},
        },
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/btc")
async def get_onchain_btc():
    """Get Bitcoin on-chain metrics"""
    return {
        "success": True,
        "data": {
            "hash_rate": None,
            "active_addresses": None,
            "exchange_reserves": None,
        },
    }


@router.get("/eth")
async def get_onchain_eth():
    """Get Ethereum on-chain metrics"""
    return {
        "success": True,
        "data": {
            "gas_price": None,
            "staking_rate": None,
            "defi_tvl": None,
        },
    }


@router.get("/signals/{coin_id}", response_model=OnChainSignals)
async def get_onchain_signals(coin_id: str):
    """Get on-chain signals for a specific coin"""
    return OnChainSignals(
        coin_id=coin_id,
        overall_signal="NEUTRAL",
        bullish_probability=50,
        whale_activity=WhaleActivity(
            signal="NEUTRAL",
            tx_count_24h=0,
            change_24h_pct=0,
            net_flow_usd=0,
        ),
        network_health=NetworkHealth(
            signal="NEUTRAL",
            dau_current=0,
            dau_change_1d_pct=0,
            trend="STABLE",
        ),
    )
