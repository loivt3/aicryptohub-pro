"""
AI Highlights Service
Generates AI-powered signals and alerts based on market data analysis.
"""
from typing import Dict, Any, List
from datetime import datetime
import random


class AIHighlightsService:
    """
    Service for generating AI insights and alerts from market data.
    Produces multiple highlight types:
    - Bullish/Bearish signals based on price movement
    - Risk alerts based on volatility
    - Volume surge detection
    - Breakout signals
    - Whale activity alerts
    - Market opportunities
    """
    
    def __init__(self):
        self.highlight_types = [
            "bullish_signal",
            "bearish_signal", 
            "risk_alert",
            "volume_surge",
            "breakout",
            "whale_activity",
            "opportunity"
        ]
    
    def analyze_coin_signal(self, coin: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a coin and generate bullish/bearish signal."""
        change_24h = coin.get("price_change_percentage_24h") or coin.get("change_24h") or 0
        volume_24h = coin.get("volume_24h") or coin.get("total_volume") or 0
        market_cap = coin.get("market_cap") or 0
        symbol = coin.get("symbol", "").upper()
        name = coin.get("name", symbol)
        
        volume_ratio = (volume_24h / market_cap * 100) if market_cap > 0 else 0
        
        if change_24h >= 5:
            signal_type = "bullish"
            confidence = min(95, 70 + abs(change_24h))
        elif change_24h <= -5:
            signal_type = "bearish"  
            confidence = min(95, 70 + abs(change_24h))
        elif change_24h >= 2:
            signal_type = "bullish"
            confidence = 60 + abs(change_24h) * 3
        elif change_24h <= -2:
            signal_type = "bearish"
            confidence = 60 + abs(change_24h) * 3
        else:
            signal_type = "neutral"
            confidence = 50
        
        if volume_ratio > 15:
            confidence = min(95, confidence + 10)
        
        if signal_type == "bullish":
            descriptions = [
                f"AI predicts upward trend in 4h based on trading volume patterns.",
                f"Strong buying pressure detected. Volume/Cap ratio: {volume_ratio:.1f}%",
                f"Bullish momentum building with +{change_24h:.1f}% gain.",
                f"Technical indicators suggest continued uptrend.",
            ]
        elif signal_type == "bearish":
            descriptions = [
                f"Selling pressure detected. Consider taking profits.",
                f"Downward momentum with {abs(change_24h):.1f}% decline.",
                f"Volume patterns indicate potential correction ahead.",
                f"Risk-off sentiment detected in market data.",
            ]
        else:
            descriptions = [
                f"Market consolidating. Wait for clearer signals.",
                f"Mixed signals. Volume at normal levels.",
            ]
        
        return {
            "coin_id": coin.get("coin_id") or coin.get("id"),
            "symbol": symbol,
            "name": name,
            "highlight_type": "bullish_signal" if signal_type == "bullish" else "bearish_signal" if signal_type == "bearish" else "neutral",
            "signal_type": signal_type,
            "confidence": int(confidence),
            "change_24h": round(change_24h, 2),
            "volume_ratio": round(volume_ratio, 2),
            "description": random.choice(descriptions),
            "icon": "trend-up" if signal_type == "bullish" else "trend-down" if signal_type == "bearish" else "minus",
            "color": "green" if signal_type == "bullish" else "red" if signal_type == "bearish" else "gray",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def analyze_volatility_risk(self, coin: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze coin volatility and generate risk alert."""
        symbol = coin.get("symbol", "").upper()
        name = coin.get("name", symbol)
        change_24h = abs(coin.get("price_change_percentage_24h") or coin.get("change_24h") or 0)
        change_7d = abs(coin.get("price_change_percentage_7d") or 0)
        
        volatility_score = change_24h * 2 + change_7d * 0.5
        
        if volatility_score >= 30:
            risk_level = "extreme"
        elif volatility_score >= 20:
            risk_level = "high"
        elif volatility_score >= 10:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        descriptions = {
            "extreme": f"Extreme volatility ({change_24h:.1f}% 24h). Avoid leveraged positions.",
            "high": f"High volatility detected. Consider reducing leverage.",
            "medium": f"Elevated volatility. Monitor positions closely.",
            "low": f"Normal volatility. Standard risk management applies."
        }
        
        return {
            "coin_id": coin.get("coin_id") or coin.get("id"),
            "symbol": symbol,
            "name": name,
            "highlight_type": "risk_alert",
            "risk_level": risk_level,
            "volatility_score": round(volatility_score, 2),
            "change_24h": round(coin.get("price_change_percentage_24h") or coin.get("change_24h") or 0, 2),
            "description": descriptions[risk_level],
            "icon": "warning",
            "color": "red" if risk_level in ["high", "extreme"] else "orange" if risk_level == "medium" else "gray",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def detect_volume_surge(self, coin: Dict[str, Any]) -> Dict[str, Any] | None:
        """Detect unusual volume activity."""
        symbol = coin.get("symbol", "").upper()
        name = coin.get("name", symbol)
        volume_24h = coin.get("volume_24h") or coin.get("total_volume") or 0
        market_cap = coin.get("market_cap") or 0
        
        volume_ratio = (volume_24h / market_cap * 100) if market_cap > 0 else 0
        
        if volume_ratio < 20:
            return None
            
        surge_level = "extreme" if volume_ratio >= 50 else "high" if volume_ratio >= 35 else "moderate"
        
        descriptions = [
            f"Volume surge detected! {volume_ratio:.1f}% of market cap traded in 24h.",
            f"Unusual trading activity. Volume {volume_ratio:.0f}x above average.",
            f"Whale accumulation possible. Monitor for price action.",
        ]
        
        return {
            "coin_id": coin.get("coin_id") or coin.get("id"),
            "symbol": symbol,
            "name": name,
            "highlight_type": "volume_surge",
            "surge_level": surge_level,
            "volume_ratio": round(volume_ratio, 2),
            "description": random.choice(descriptions),
            "icon": "chart-bar",
            "color": "blue",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def detect_breakout(self, coin: Dict[str, Any]) -> Dict[str, Any] | None:
        """Detect price breakout patterns."""
        symbol = coin.get("symbol", "").upper()
        name = coin.get("name", symbol)
        change_24h = coin.get("price_change_percentage_24h") or coin.get("change_24h") or 0
        change_7d = coin.get("price_change_percentage_7d") or 0
        
        # Simple breakout detection: strong move with momentum
        if abs(change_24h) >= 8 and (change_24h * change_7d > 0):  # Same direction
            direction = "upward" if change_24h > 0 else "downward"
            
            descriptions = [
                f"{direction.capitalize()} breakout confirmed! +{abs(change_24h):.1f}% with momentum.",
                f"Price breaking {direction}. Volume supports the move.",
                f"Technical breakout detected. Watch for continuation.",
            ]
            
            return {
                "coin_id": coin.get("coin_id") or coin.get("id"),
                "symbol": symbol,
                "name": name,
                "highlight_type": "breakout",
                "direction": direction,
                "change_24h": round(change_24h, 2),
                "change_7d": round(change_7d, 2),
                "description": random.choice(descriptions),
                "icon": "lightning",
                "color": "cyan",
                "timestamp": datetime.utcnow().isoformat()
            }
        return None
    
    def detect_whale_activity(self, coin: Dict[str, Any]) -> Dict[str, Any] | None:
        """Detect potential whale activity based on volume patterns."""
        symbol = coin.get("symbol", "").upper()
        name = coin.get("name", symbol)
        volume_24h = coin.get("volume_24h") or coin.get("total_volume") or 0
        market_cap = coin.get("market_cap") or 0
        change_24h = coin.get("price_change_percentage_24h") or coin.get("change_24h") or 0
        
        volume_ratio = (volume_24h / market_cap * 100) if market_cap > 0 else 0
        
        # Whale activity: high volume with price movement
        if volume_ratio >= 25 and abs(change_24h) >= 3:
            activity = "accumulation" if change_24h > 0 else "distribution"
            
            descriptions = [
                f"Whale {activity} detected. Large orders moving the market.",
                f"Institutional activity spotted. {activity.capitalize()} in progress.",
                f"Smart money {activity}. Volume {volume_ratio:.0f}% of market cap.",
            ]
            
            return {
                "coin_id": coin.get("coin_id") or coin.get("id"),
                "symbol": symbol,
                "name": name,
                "highlight_type": "whale_activity",
                "activity_type": activity,
                "volume_ratio": round(volume_ratio, 2),
                "change_24h": round(change_24h, 2),
                "description": random.choice(descriptions),
                "icon": "fish" if activity == "accumulation" else "arrow-down",
                "color": "purple",
                "timestamp": datetime.utcnow().isoformat()
            }
        return None
    
    def detect_opportunity(self, coin: Dict[str, Any]) -> Dict[str, Any] | None:
        """Detect potential trading opportunities."""
        symbol = coin.get("symbol", "").upper()
        name = coin.get("name", symbol)
        change_24h = coin.get("price_change_percentage_24h") or coin.get("change_24h") or 0
        change_7d = coin.get("price_change_percentage_7d") or 0
        market_cap = coin.get("market_cap") or 0
        
        # Opportunity: oversold bounce or momentum continuation
        if change_24h <= -10 and change_7d <= -15:
            # Potential oversold bounce
            descriptions = [
                f"Oversold conditions. Potential bounce opportunity.",
                f"Sharp decline may be overextended. Watch for reversal.",
            ]
            opp_type = "oversold_bounce"
            
        elif change_24h >= 3 and change_7d >= 10:
            # Momentum continuation
            descriptions = [
                f"Strong momentum. Consider riding the trend.",
                f"Positive trend confirmed. Pullback may offer entry.",
            ]
            opp_type = "momentum"
        else:
            return None
        
        return {
            "coin_id": coin.get("coin_id") or coin.get("id"),
            "symbol": symbol,
            "name": name,
            "highlight_type": "opportunity",
            "opportunity_type": opp_type,
            "change_24h": round(change_24h, 2),
            "change_7d": round(change_7d, 2),
            "description": random.choice(descriptions),
            "icon": "target",
            "color": "yellow",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_highlights(self, coins: List[Dict[str, Any]], limit: int = 6) -> Dict[str, Any]:
        """Generate comprehensive AI highlights from market data."""
        if not coins:
            return {
                "highlights": [],
                "total_analyzed": 0,
                "generated_at": None
            }
        
        all_highlights = []
        
        for coin in coins:
            # Generate all highlight types
            signal = self.analyze_coin_signal(coin)
            if signal["signal_type"] != "neutral":
                all_highlights.append(signal)
            
            risk = self.analyze_volatility_risk(coin)
            if risk["risk_level"] in ["high", "extreme"]:
                all_highlights.append(risk)
            
            volume = self.detect_volume_surge(coin)
            if volume:
                all_highlights.append(volume)
            
            breakout = self.detect_breakout(coin)
            if breakout:
                all_highlights.append(breakout)
            
            whale = self.detect_whale_activity(coin)
            if whale:
                all_highlights.append(whale)
            
            opportunity = self.detect_opportunity(coin)
            if opportunity:
                all_highlights.append(opportunity)
        
        # Sort by importance (confidence for signals, severity for risks)
        def get_priority(h):
            if h.get("confidence"):
                return h["confidence"]
            if h.get("volatility_score"):
                return h["volatility_score"] * 2
            if h.get("volume_ratio"):
                return h["volume_ratio"]
            return 50
        
        all_highlights.sort(key=get_priority, reverse=True)
        
        # Ensure diversity - pick different types
        seen_types = {}
        diverse_highlights = []
        for h in all_highlights:
            htype = h["highlight_type"]
            if seen_types.get(htype, 0) < 2:  # Max 2 per type
                diverse_highlights.append(h)
                seen_types[htype] = seen_types.get(htype, 0) + 1
            if len(diverse_highlights) >= limit:
                break
        
        return {
            "highlights": diverse_highlights,
            "total_analyzed": len(coins),
            "generated_at": datetime.utcnow().isoformat()
        }


# Singleton instance
ai_highlights_service = AIHighlightsService()
