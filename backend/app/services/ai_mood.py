"""
AI Market Mood Service

Calculates a proprietary AI Market Mood score by combining multiple market signals:
- Fear & Greed Index (30%)
- Average ASI of top coins (25%)
- Market Trend (20%)
- Volume Momentum (15%)
- Whale Activity (10%)
"""

from typing import Dict, Any, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger


class AIMarketMoodService:
    """Service to calculate AI Market Mood indicator."""
    
    WEIGHTS = {
        "fear_greed": 0.30,
        "asi_average": 0.25,
        "market_trend": 0.20,
        "volume_momentum": 0.15,
        "whale_activity": 0.10,
    }
    
    LABELS = [
        (20, "Extreme Fear"),
        (40, "Fear"),
        (60, "Neutral"),
        (80, "Greed"),
        (100, "Extreme Greed"),
    ]
    
    def __init__(self, engine=None):
        self.engine = engine
    
    async def calculate_mood(self) -> Dict[str, Any]:
        """Calculate the AI Market Mood score."""
        try:
            # Fetch all components
            fear_greed = await self._get_fear_greed()
            asi_average = await self._get_asi_average()
            market_trend = await self._get_market_trend()
            volume_momentum = await self._get_volume_momentum()
            whale_activity = await self._get_whale_activity()
            
            # Calculate weighted score
            score = (
                self.WEIGHTS["fear_greed"] * fear_greed +
                self.WEIGHTS["asi_average"] * asi_average +
                self.WEIGHTS["market_trend"] * market_trend +
                self.WEIGHTS["volume_momentum"] * volume_momentum +
                self.WEIGHTS["whale_activity"] * whale_activity
            )
            
            score = max(0, min(100, round(score)))  # Clamp to 0-100
            
            return {
                "score": score,
                "label": self._get_label(score),
                "components": {
                    "fear_greed": round(fear_greed),
                    "asi_average": round(asi_average),
                    "market_trend": round(market_trend),
                    "volume_momentum": round(volume_momentum),
                    "whale_activity": round(whale_activity),
                },
                "weights": self.WEIGHTS,
            }
        except Exception as e:
            logger.error(f"Error calculating AI Market Mood: {e}")
            return {
                "score": 50,
                "label": "Neutral",
                "components": {},
                "error": str(e),
            }
    
    def _get_label(self, score: int) -> str:
        """Get mood label based on score."""
        for threshold, label in self.LABELS:
            if score <= threshold:
                return label
        return "Extreme Greed"
    
    async def _get_fear_greed(self) -> float:
        """Fetch Fear & Greed Index from Alternative.me API."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.alternative.me/fng/")
                if response.status_code == 200:
                    data = response.json()
                    return float(data.get("data", [{}])[0].get("value", 50))
        except Exception as e:
            logger.warning(f"Failed to fetch Fear & Greed: {e}")
        return 50.0  # Default neutral
    
    async def _get_asi_average(self) -> float:
        """Calculate average ASI score from sentiment data."""
        try:
            from sqlalchemy import text
            
            if self.engine:
                with self.engine.connect() as conn:
                    result = conn.execute(
                        text("SELECT AVG(sentiment_score * 100) as avg_asi FROM aihub_sentiment WHERE sentiment_score IS NOT NULL")
                    )
                    row = result.fetchone()
                    if row and row.avg_asi:
                        return float(row.avg_asi)
        except Exception as e:
            logger.warning(f"Failed to get ASI average: {e}")
        return 50.0
    
    async def _get_market_trend(self) -> float:
        """Calculate market trend based on gainers vs losers ratio."""
        try:
            from sqlalchemy import text
            
            if self.engine:
                with self.engine.connect() as conn:
                    # Count gainers (positive 24h change) vs losers
                    result = conn.execute(
                        text("""
                            SELECT 
                                SUM(CASE WHEN change_24h > 0 THEN 1 ELSE 0 END) as gainers,
                                SUM(CASE WHEN change_24h < 0 THEN 1 ELSE 0 END) as losers,
                                COUNT(*) as total
                            FROM aihub_coins 
                            WHERE change_24h IS NOT NULL
                        """)
                    )
                    row = result.fetchone()
                    if row and row.total > 0:
                        # Convert ratio to 0-100 scale
                        gainers = row.gainers or 0
                        total = row.total
                        trend = (gainers / total) * 100
                        return trend
        except Exception as e:
            logger.warning(f"Failed to get market trend: {e}")
        return 50.0
    
    async def _get_volume_momentum(self) -> float:
        """Calculate volume momentum (24h volume change)."""
        try:
            from sqlalchemy import text
            
            if self.engine:
                with self.engine.connect() as conn:
                    # Get average volume change
                    result = conn.execute(
                        text("""
                            SELECT AVG(
                                CASE 
                                    WHEN volume_24h > 0 AND market_cap > 0 
                                    THEN LEAST(GREATEST((volume_24h / market_cap) * 1000, 0), 100)
                                    ELSE 50
                                END
                            ) as avg_volume_ratio
                            FROM aihub_coins
                        """)
                    )
                    row = result.fetchone()
                    if row and row.avg_volume_ratio:
                        return float(row.avg_volume_ratio)
        except Exception as e:
            logger.warning(f"Failed to get volume momentum: {e}")
        return 50.0
    
    async def _get_whale_activity(self) -> float:
        """Calculate whale activity score based on recent transactions."""
        try:
            from sqlalchemy import text
            
            if self.engine:
                with self.engine.connect() as conn:
                    # Check for accumulation vs distribution signals from onchain_signals
                    result = conn.execute(
                        text("""
                            SELECT 
                                SUM(CASE WHEN whale_signal = 'bullish' THEN 1 ELSE 0 END) as bullish,
                                SUM(CASE WHEN whale_signal = 'bearish' THEN 1 ELSE 0 END) as bearish,
                                COUNT(*) as total
                            FROM onchain_signals
                            WHERE updated_at > NOW() - INTERVAL '24 hours'
                        """)
                    )
                    row = result.fetchone()
                    if row and row.total > 0:
                        bullish = row.bullish or 0
                        total = row.total
                        # More bullish = higher score
                        score = (bullish / total) * 100
                        return score
        except Exception as e:
            logger.warning(f"Failed to get whale activity: {e}")
        return 50.0  # Default neutral


# Singleton instance
_ai_mood_service: Optional[AIMarketMoodService] = None


def get_ai_mood_service(db_session=None) -> AIMarketMoodService:
    """Get or create AI Mood service instance."""
    global _ai_mood_service
    if _ai_mood_service is None or db_session is not None:
        _ai_mood_service = AIMarketMoodService(db_session)
    return _ai_mood_service
