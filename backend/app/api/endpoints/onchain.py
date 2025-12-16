"""
On-Chain Data Endpoints
Port từ PHP class-rest-api.php và Python services
"""

from datetime import datetime
from typing import Optional
import random

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


# Realistic mock data for popular coins
MOCK_ONCHAIN_DATA = {
    "bitcoin": {
        "overall_signal": "BULLISH",
        "bullish_probability": 65.5,
        "whale_tx": 1284,
        "whale_change": 8.5,
        "net_flow": -45200000,  # Negative = outflow from exchanges (bullish)
        "dau": 892000,
        "dau_change": 4.2,
        "trend": "INCREASING"
    },
    "ethereum": {
        "overall_signal": "NEUTRAL",
        "bullish_probability": 52.3,
        "whale_tx": 2156,
        "whale_change": -2.1,
        "net_flow": 12500000,
        "dau": 456000,
        "dau_change": -1.5,
        "trend": "STABLE"
    },
    "solana": {
        "overall_signal": "BULLISH",
        "bullish_probability": 72.8,
        "whale_tx": 567,
        "whale_change": 15.3,
        "net_flow": -8900000,
        "dau": 245000,
        "dau_change": 12.4,
        "trend": "INCREASING"
    }
}


def get_mock_data_for_coin(coin_id: str) -> dict:
    """Get mock on-chain data for a coin"""
    if coin_id in MOCK_ONCHAIN_DATA:
        return MOCK_ONCHAIN_DATA[coin_id]
    
    # Generate random but reasonable values for other coins
    signals = ["BULLISH", "NEUTRAL", "BEARISH"]
    trends = ["INCREASING", "STABLE", "DECREASING"]
    
    return {
        "overall_signal": random.choice(signals),
        "bullish_probability": round(random.uniform(35, 75), 1),
        "whale_tx": random.randint(50, 500),
        "whale_change": round(random.uniform(-10, 15), 1),
        "net_flow": random.randint(-10000000, 10000000),
        "dau": random.randint(10000, 200000),
        "dau_change": round(random.uniform(-5, 10), 1),
        "trend": random.choice(trends)
    }


@router.get("/summary")
async def get_onchain_summary():
    """Get all on-chain metrics summary"""
    return {
        "success": True,
        "data": {
            "btc": MOCK_ONCHAIN_DATA.get("bitcoin", {}),
            "eth": MOCK_ONCHAIN_DATA.get("ethereum", {}),
            "defi": {
                "tvl": 45200000000,
                "tvl_change_24h": 2.5,
            },
        },
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/btc")
async def get_onchain_btc():
    """Get Bitcoin on-chain metrics"""
    return {
        "success": True,
        "data": {
            "hash_rate": 580000000,
            "active_addresses": 892000,
            "exchange_reserves": 2100000,
            "exchange_flow_24h": -45200000,
        },
    }


@router.get("/eth")
async def get_onchain_eth():
    """Get Ethereum on-chain metrics"""
    return {
        "success": True,
        "data": {
            "gas_price": 25.5,
            "staking_rate": 27.8,
            "defi_tvl": 45200000000,
            "exchange_flow_24h": 12500000,
        },
    }


@router.get("/signals/{coin_id}", response_model=OnChainSignals)
async def get_onchain_signals(coin_id: str):
    """Get on-chain signals for a specific coin"""
    data = get_mock_data_for_coin(coin_id)
    
    # Determine whale signal based on net flow
    whale_signal = "BULLISH" if data["net_flow"] < 0 else "BEARISH" if data["net_flow"] > 5000000 else "NEUTRAL"
    # Determine network signal based on DAU change
    network_signal = "BULLISH" if data["dau_change"] > 5 else "BEARISH" if data["dau_change"] < -5 else "NEUTRAL"
    
    return OnChainSignals(
        coin_id=coin_id,
        overall_signal=data["overall_signal"],
        bullish_probability=data["bullish_probability"],
        whale_activity=WhaleActivity(
            signal=whale_signal,
            tx_count_24h=data["whale_tx"],
            change_24h_pct=data["whale_change"],
            net_flow_usd=data["net_flow"],
        ),
        network_health=NetworkHealth(
            signal=network_signal,
            dau_current=data["dau"],
            dau_change_1d_pct=data["dau_change"],
            trend=data["trend"],
        ),
        ai_prediction=f"{data['overall_signal']} - {data['bullish_probability']:.1f}% probability",
        ai_summary=f"On-chain data for {coin_id} suggests {data['overall_signal'].lower()} sentiment",
        last_updated=datetime.now(),
    )

