"""
AI Market Mood Service

Calculates a proprietary AI Market Mood score by combining multiple market signals:
- Fear & Greed Index (30%)
- Average ASI of top coins (25%)
- Market Trend (20%)
- Volume Momentum (15%)
- Whale Activity (10%)
"""

import logging
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


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
            label = self._get_label(score)
            
            # Generate AI-powered analysis
            components = {
                "fear_greed": round(fear_greed),
                "asi_average": round(asi_average),
                "market_trend": round(market_trend),
                "volume_momentum": round(volume_momentum),
                "whale_activity": round(whale_activity),
            }
            
            analysis, source = await self._generate_ai_analysis(score, label, components)
            
            return {
                "score": score,
                "label": label,
                "analysis": analysis,
                "source": source,
                "components": components,
                "weights": self.WEIGHTS,
            }
        except Exception as e:
            logger.error(f"Error calculating AI Market Mood: {e}")
            return {
                "score": 50,
                "label": "Neutral",
                "analysis": "Markets are neutral. Wait for clearer signals.",
                "source": "fallback",
                "components": {},
                "error": str(e),
            }
    
    def _get_label(self, score: int) -> str:
        """Get mood label based on score."""
        for threshold, label in self.LABELS:
            if score <= threshold:
                return label
        return "Extreme Greed"
    
    async def _generate_ai_analysis(self, score: int, label: str, components: dict) -> tuple[str, str]:
        """
        Generate AI-powered market analysis using Gemini/DeepSeek.
        Returns (analysis_text, source).
        """
        import os
        
        prompt = self._build_analysis_prompt(score, label, components)
        
        # Try Gemini first
        analysis = await self._try_gemini(prompt)
        if analysis:
            return analysis, "gemini"
        
        # Try DeepSeek as fallback
        analysis = await self._try_deepseek(prompt)
        if analysis:
            return analysis, "deepseek"
        
        # Algorithmic fallback
        return self._get_fallback_analysis(score, label), "algorithmic"
    
    def _build_analysis_prompt(self, score: int, label: str, components: dict) -> str:
        """Build prompt for AI analysis."""
        trend_pct = components.get("market_trend", 50)
        fg = components.get("fear_greed", 50)
        
        return f"""You are a professional crypto market analyst. Based on the following market data, generate a brief 1-2 sentence analysis for crypto traders.

Market Data:
- AI Mood Score: {score}/100 ({label})
- Fear & Greed Index: {fg}
- ASI Average: {components.get("asi_average", 50)}
- Market Trend: {trend_pct}% coins are gaining
- Volume Momentum: {components.get("volume_momentum", 50)}/100
- Whale Activity: {components.get("whale_activity", 50)}/100

Generate a professional, actionable insight in 1-2 sentences. Be specific about what traders should consider. Do not use markdown, just plain text."""

    async def _try_gemini(self, prompt: str) -> str | None:
        """Try to get analysis from Gemini API."""
        import os
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "maxOutputTokens": 100,
                            "temperature": 0.7,
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    if text:
                        return text.strip()
        except Exception as e:
            logger.warning(f"Gemini API failed for mood analysis: {e}")
        
        return None
    
    async def _try_deepseek(self, prompt: str) -> str | None:
        """Try to get analysis from DeepSeek API."""
        import os
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    "https://api.deepseek.com/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 100,
                        "temperature": 0.7,
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if text:
                        return text.strip()
        except Exception as e:
            logger.warning(f"DeepSeek API failed for mood analysis: {e}")
        
        return None
    
    def _get_fallback_analysis(self, score: int, label: str) -> str:
        """Get algorithmic fallback analysis based on score."""
        if score <= 20:
            return "Extreme fear in the market. Historically, such levels have presented buying opportunities for long-term investors."
        elif score <= 40:
            return "Market sentiment is fearful. Consider accumulating quality assets cautiously while monitoring support levels."
        elif score <= 60:
            return "Markets are neutral with mixed signals. Wait for clearer directional confirmation before taking significant positions."
        elif score <= 80:
            return "Greed is building in the market. Consider taking partial profits and setting stop-losses on leveraged positions."
        else:
            return "Extreme greed detected. Exercise caution as markets may be overextended. Consider reducing exposure."

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
