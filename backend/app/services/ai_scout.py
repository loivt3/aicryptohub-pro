
from typing import List, Dict, Any
import logging
import random

logger = logging.getLogger(__name__)

class AIScoutService:
    """
    AI Scout Service
    Handles 'Why is it moving?' explanations and Smart Alerts
    """
    
    def __init__(self):
        # Mock reasons for demonstration
        self.reasons_up = [
            "Strong on-chain accumulation by whales detected in the last 4 hours.",
            "Positive sentiment spike on social media regarding upcoming protocol upgrade.",
            "Correlation with Bitcoin's recent breakout.",
            "Rumors of a major partnership announcement.",
            "Technical breakout above key resistance level."
        ]
        self.reasons_down = [
            "Profit-taking after recent rally.",
            "Overall market correction led by Bitcoin.",
            "Large whale transfer to exchange detected (potential sell pressure).",
            "Regulatory FUD news circulating in major regions.",
            "Technical rejection at resistance level."
        ]

    def explain_volatility(self, coin_id: str, percent_change_24h: float) -> Dict[str, Any]:
        """
        Generate an AI explanation for a coin's volatility
        """
        # In a real implementation, this would query NewsAPI/Social Sentiment
        # and use an LLM to summarize the context.
        
        direction = "up" if percent_change_24h > 0 else "down"
        magnitude = abs(percent_change_24h)
        
        if magnitude < 2:
            return {
                "coin_id": coin_id,
                "explanation": "Price is relatively stable. No significant events detected.",
                "confidence": "High",
                "sources": []
            } # Not volatile enough

        reason = ""
        if direction == "up":
            reason = random.choice(self.reasons_up)
            if magnitude > 10:
                reason = f"🚀 SURGE: {reason}"
        else:
            reason = random.choice(self.reasons_down)
            if magnitude > 10:
                reason = f"⚠️ CRASH: {reason}"

        return {
            "coin_id": coin_id,
            "change": f"{percent_change_24h}%",
            "explanation": reason,
            "confidence": "Medium",
            "sources": ["On-chain Data", "Social Sentinel", "Market Stream"]
        }

# Singleton instance
ai_scout_service = AIScoutService()
