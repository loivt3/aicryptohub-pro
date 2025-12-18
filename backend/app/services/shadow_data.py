"""
Shadow Radar Data Service
Fetches real-time sentiment and calculates whale activity metrics
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class ShadowDataService:
    """Service for fetching Shadow Radar specific data"""
    
    FEAR_GREED_API = "https://api.alternative.me/fng/"
    
    def __init__(self):
        self._fear_greed_cache = None
        self._cache_time = None
        self._cache_ttl = 300  # 5 minutes
    
    async def fetch_fear_greed_index(self) -> Dict[str, Any]:
        """
        Fetch Fear & Greed Index from Alternative.me
        
        Returns:
            Dict with value (0-100), classification, and timestamp
        """
        # Return cached if fresh
        if self._fear_greed_cache and self._cache_time:
            elapsed = (datetime.now() - self._cache_time).seconds
            if elapsed < self._cache_ttl:
                return self._fear_greed_cache
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.FEAR_GREED_API)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("data") and len(data["data"]) > 0:
                        fng = data["data"][0]
                        result = {
                            "value": int(fng.get("value", 50)),
                            "classification": fng.get("value_classification", "Neutral"),
                            "timestamp": fng.get("timestamp"),
                            "time_until_update": fng.get("time_until_update"),
                        }
                        
                        # Cache it
                        self._fear_greed_cache = result
                        self._cache_time = datetime.now()
                        
                        logger.info(f"[Shadow] Fear & Greed: {result['value']} ({result['classification']})")
                        return result
                        
        except Exception as e:
            logger.warning(f"Failed to fetch Fear & Greed Index: {e}")
        
        # Default fallback
        return {
            "value": 50,
            "classification": "Neutral",
            "timestamp": None,
            "time_until_update": None,
        }
    
    def calculate_whale_metrics(
        self,
        volume_24h: float,
        avg_volume_7d: float,
        price_change_24h: float,
        market_cap: float = 0,
    ) -> Dict[str, Any]:
        """
        Calculate whale activity metrics from volume and price data.
        
        Approximation logic:
        - Volume spike > 2x = potential whale activity
        - Price ⬆️ + Volume ⬆️ = Buying (accumulation)
        - Price ⬇️ + Volume ⬆️ = Selling (distribution)
        
        Args:
            volume_24h: Current 24h volume
            avg_volume_7d: Average 7-day volume
            price_change_24h: 24h price change percentage
            market_cap: Market cap for whale flow calculation
            
        Returns:
            Dict with whale_score, whale_net_flow, dominant_behavior
        """
        # Calculate volume spike ratio
        volume_ratio = 1.0
        if avg_volume_7d > 0:
            volume_ratio = volume_24h / avg_volume_7d
        
        # Determine whale activity level (0-100)
        whale_activity = 50  # Baseline
        
        if volume_ratio > 3.0:
            whale_activity = 90  # Extreme activity
        elif volume_ratio > 2.0:
            whale_activity = 75  # High activity
        elif volume_ratio > 1.5:
            whale_activity = 65  # Above average
        elif volume_ratio > 1.0:
            whale_activity = 55  # Slightly elevated
        elif volume_ratio < 0.5:
            whale_activity = 30  # Low activity
        else:
            whale_activity = 45  # Below average
        
        # Determine direction from price action
        # Positive flow = accumulation, Negative flow = distribution
        direction_factor = 1 if price_change_24h > 0 else -1
        
        # Calculate simulated whale net flow based on volume * market_cap ratio
        # This is an approximation - real whale flow requires on-chain data
        if market_cap > 0:
            flow_magnitude = (volume_ratio - 1) * market_cap * 0.001  # 0.1% of market cap per unit of spike
            whale_net_flow = direction_factor * flow_magnitude
        else:
            whale_net_flow = direction_factor * volume_24h * (volume_ratio - 1) * 0.01
        
        # Determine dominant behavior
        if volume_ratio > 1.5 and price_change_24h > 3:
            behavior = "accumulator"
        elif volume_ratio > 1.5 and price_change_24h < -3:
            behavior = "distributor"
        elif volume_ratio > 2.0:
            behavior = "value_hunter" if price_change_24h < 0 else "momentum_trader"
        else:
            behavior = "mixed"
        
        # Create whale profiles
        active_profiles = []
        if volume_ratio > 1.3:
            profile_count = min(int(volume_ratio * 2), 10)
            active_profiles.append({
                "behavior": behavior,
                "confidence": min(0.9, 0.5 + (volume_ratio - 1) * 0.2),
                "success_rate": 0.65 + (price_change_24h / 100) * 0.1,
                "count": profile_count,
            })
        
        return {
            "whale_score": int(whale_activity),
            "whale_net_flow_usd": round(whale_net_flow, 2),
            "volume_ratio": round(volume_ratio, 2),
            "dominant_whale_behavior": behavior,
            "active_whale_profiles": active_profiles,
        }
    
    def calculate_intent_score(
        self,
        fear_greed: int,
        whale_score: int,
        price_change_24h: float,
    ) -> Dict[str, Any]:
        """
        Calculate overall intent divergence score.
        
        Divergence scenarios:
        - Shadow Accumulation: Fear (FG < 40) + Whale buying (high activity + price up)
        - Bull Trap: Greed (FG > 70) + Whale selling (high activity + price down)
        - Confirmation: Sentiment and whales aligned
        - Neutral: No clear signal
        
        Args:
            fear_greed: Fear & Greed value (0-100)
            whale_score: Whale activity score (0-100)
            price_change_24h: 24h price change %
            
        Returns:
            Dict with intent_score, divergence_type, signal_strength
        """
        # Calculate divergence
        intent_score = 50
        divergence_type = "neutral"
        signal_strength = "weak"
        is_golden_shadow = False
        
        # Map Fear & Greed: Low = Fear, High = Greed
        sentiment_direction = (fear_greed - 50) / 50  # -1 (extreme fear) to +1 (extreme greed)
        
        # Whale direction from activity + price
        whale_direction = 1 if price_change_24h > 0 else -1
        whale_intensity = (whale_score - 50) / 50  # -1 to +1
        
        # Check for Shadow Accumulation: Fear + Whale Buying
        if fear_greed < 40 and price_change_24h > 0 and whale_score > 60:
            divergence_type = "shadow_accumulation"
            # Score increases with more fear and more whale activity
            fear_bonus = (40 - fear_greed) * 0.5  # 0-20 points
            whale_bonus = (whale_score - 60) * 0.3  # 0-12 points
            intent_score = min(100, 60 + fear_bonus + whale_bonus)
            signal_strength = "strong" if intent_score > 75 else "moderate"
            is_golden_shadow = intent_score > 80
        
        # Check for Bull Trap: Greed + Whale Selling
        elif fear_greed > 70 and price_change_24h < 0 and whale_score > 60:
            divergence_type = "bull_trap"
            # Score increases with more greed and more selling pressure
            greed_bonus = (fear_greed - 70) * 0.5  # 0-15 points
            whale_bonus = (whale_score - 60) * 0.3
            intent_score = min(100, 60 + greed_bonus + whale_bonus)
            signal_strength = "strong" if intent_score > 75 else "moderate"
            is_golden_shadow = intent_score > 80
        
        # Trend Confirmation
        elif (fear_greed > 60 and price_change_24h > 0) or (fear_greed < 40 and price_change_24h < 0):
            divergence_type = "confirmation"
            intent_score = 50 + abs(fear_greed - 50) * 0.3
            signal_strength = "moderate"
        
        # Neutral
        else:
            divergence_type = "neutral"
            intent_score = 50 + (whale_score - 50) * 0.2 + (fear_greed - 50) * 0.1
            signal_strength = "weak"
        
        # Ensure bounds
        intent_score = max(0, min(100, int(intent_score)))
        
        # Generate label
        labels = {
            "shadow_accumulation": "Shadow Accumulation",
            "bull_trap": "Bull Trap Warning",
            "confirmation": "Trend Confirmation",
            "neutral": "No Clear Signal",
        }
        
        return {
            "intent_score": intent_score,
            "divergence_type": divergence_type,
            "divergence_label": labels.get(divergence_type, divergence_type),
            "signal_strength": signal_strength,
            "is_golden_shadow": is_golden_shadow,
        }


# Singleton instance
_shadow_service: Optional[ShadowDataService] = None


def get_shadow_service() -> ShadowDataService:
    """Get singleton ShadowDataService instance"""
    global _shadow_service
    if _shadow_service is None:
        _shadow_service = ShadowDataService()
    return _shadow_service
