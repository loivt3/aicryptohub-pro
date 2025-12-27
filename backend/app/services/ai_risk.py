"""
AI Risk Assessment Service

Evaluates cryptocurrency risk levels based on multiple factors:
- Volatility (price movements)
- Volume/Market Cap ratio
- Market cap ranking
- Known regulatory issues
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk level classifications matching UI mockup"""
    NO_RISK = "NO_RISK"         # Score 0-10: Stablecoins
    SAFE = "SAFE"               # Score 11-25: Very stable
    LOW_RISK = "LOW_RISK"       # Score 26-40: Low volatility
    MED_RISK = "MED_RISK"       # Score 41-60: Moderate
    VOLATILE = "VOLATILE"       # Score 61-75: High volatility
    EXTREME = "EXTREME"         # Score 76-90: Very high risk
    LAWSUIT = "LAWSUIT"         # Score 91-100: Regulatory/legal issues


# Known stablecoins (very low risk)
STABLECOINS = {
    "tether", "usdt", "usd-coin", "usdc", "dai", "trueusd", "tusd",
    "binance-usd", "busd", "paxos-standard", "usdp", "frax", "usdd",
    "first-digital-usd", "fdusd", "paypal-usd", "pyusd"
}

# Coins with known regulatory/legal issues
LAWSUIT_COINS = {
    "ripple", "xrp",           # SEC lawsuit
    "binancecoin", "bnb",      # Regulatory issues
    "solana", "sol",           # SEC classification
    "cardano", "ada",          # SEC classification
    "polygon", "matic",        # SEC classification
}

# Risk level color mapping (matching mockup)
RISK_COLORS = {
    RiskLevel.NO_RISK: "#6b7280",      # Gray
    RiskLevel.SAFE: "#38efeb",         # Cyan
    RiskLevel.LOW_RISK: "#10b981",     # Green
    RiskLevel.MED_RISK: "#eab308",     # Yellow
    RiskLevel.VOLATILE: "gradient",    # Multi-color
    RiskLevel.EXTREME: "#ef4444",      # Red
    RiskLevel.LAWSUIT: "#ec4899",      # Pink/Magenta
}


class AIRiskService:
    """
    AI-powered risk assessment for cryptocurrencies.
    Calculates risk scores based on multiple weighted factors.
    """
    
    def __init__(self):
        # Factor weights (must sum to 1.0)
        self.weights = {
            "volatility": 0.35,      # Price volatility
            "volume_ratio": 0.20,    # Volume to market cap
            "market_cap": 0.20,      # Market cap ranking
            "regulatory": 0.15,      # Known legal issues
            "age": 0.10,             # Coin maturity
        }
    
    def calculate_risk_score(self, coin: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score for a coin.
        
        Args:
            coin: Coin data with price changes, volume, market cap
            
        Returns:
            Risk assessment with score, level, factors breakdown
        """
        coin_id = (coin.get("coin_id") or coin.get("id") or "").lower()
        symbol = (coin.get("symbol") or "").lower()
        
        # Special case: Stablecoins
        if coin_id in STABLECOINS or symbol in ["usdt", "usdc", "dai", "tusd", "busd", "fdusd"]:
            return self._create_stablecoin_risk(coin)
        
        # Special case: Coins with legal issues
        if coin_id in LAWSUIT_COINS or symbol in ["xrp", "bnb", "sol", "ada", "matic"]:
            return self._create_lawsuit_risk(coin)
        
        # Calculate individual factor scores
        factors = {
            "volatility": self._calculate_volatility_score(coin),
            "volume_ratio": self._calculate_volume_score(coin),
            "market_cap": self._calculate_market_cap_score(coin),
            "regulatory": self._calculate_regulatory_score(coin),
            "age": self._calculate_age_score(coin),
        }
        
        # Weighted average
        total_score = sum(
            factors[factor]["score"] * self.weights[factor]
            for factor in factors
        )
        
        # Clamp to 0-100
        total_score = max(0, min(100, total_score))
        
        # Get risk level
        risk_level = self._score_to_level(total_score)
        
        return {
            "coin_id": coin_id,
            "symbol": coin.get("symbol", "").upper(),
            "name": coin.get("name", ""),
            "risk_score": round(total_score, 1),
            "risk_level": risk_level.value,
            "risk_label": self._level_to_label(risk_level),
            "risk_color": RISK_COLORS[risk_level],
            "factors": factors,
            "summary": self._generate_summary(risk_level, factors),
            "calculated_at": datetime.utcnow().isoformat(),
        }
    
    def _calculate_volatility_score(self, coin: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate volatility risk (0-100).
        Higher volatility = higher risk score.
        """
        change_24h = abs(coin.get("price_change_percentage_24h") or coin.get("change_24h") or 0)
        change_7d = abs(coin.get("price_change_percentage_7d") or 0)
        
        # Normalize: 0-2% = low, 2-5% = medium, 5-10% = high, >10% = extreme
        if change_24h < 2 and change_7d < 5:
            score = 10 + change_24h * 5
        elif change_24h < 5 and change_7d < 10:
            score = 30 + change_24h * 4
        elif change_24h < 10 and change_7d < 20:
            score = 50 + change_24h * 3
        else:
            score = min(100, 70 + change_24h)
        
        return {
            "score": round(score, 1),
            "change_24h": round(change_24h, 2),
            "change_7d": round(change_7d, 2),
            "description": self._volatility_description(score),
        }
    
    def _calculate_volume_score(self, coin: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate volume/market cap ratio risk.
        Abnormally high or low volume indicates risk.
        """
        volume = coin.get("total_volume") or coin.get("volume_24h") or 0
        market_cap = coin.get("market_cap") or 1
        
        ratio = (volume / market_cap) * 100 if market_cap > 0 else 0
        
        # Normal ratio is 2-10%, below or above is risky
        if 2 <= ratio <= 10:
            score = 20 + (ratio - 2) * 2
        elif ratio < 2:
            score = 50 + (2 - ratio) * 15  # Low liquidity risk
        else:
            score = 40 + min(60, ratio * 2)  # High pump/dump risk
        
        return {
            "score": round(min(100, score), 1),
            "volume_ratio": round(ratio, 2),
            "description": "Normal volume" if 2 <= ratio <= 10 else "Unusual volume activity",
        }
    
    def _calculate_market_cap_score(self, coin: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate market cap ranking risk.
        Lower market cap = higher risk.
        """
        rank = coin.get("market_cap_rank") or 1000
        market_cap = coin.get("market_cap") or 0
        
        # Top 10 = very safe, Top 50 = safe, Top 100 = moderate
        if rank <= 10:
            score = 10
        elif rank <= 50:
            score = 20 + (rank - 10) * 0.5
        elif rank <= 100:
            score = 40 + (rank - 50) * 0.4
        elif rank <= 500:
            score = 60 + (rank - 100) * 0.05
        else:
            score = 80 + min(20, (rank - 500) * 0.02)
        
        return {
            "score": round(min(100, score), 1),
            "rank": rank,
            "market_cap": market_cap,
            "description": f"Rank #{rank}",
        }
    
    def _calculate_regulatory_score(self, coin: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate regulatory/legal risk.
        Known issues = high score.
        """
        coin_id = (coin.get("coin_id") or coin.get("id") or "").lower()
        symbol = (coin.get("symbol") or "").lower()
        
        # Check for known issues
        if coin_id in LAWSUIT_COINS or symbol in ["xrp", "bnb", "sol", "ada", "matic"]:
            return {
                "score": 85,
                "has_issues": True,
                "description": "Known regulatory concerns",
            }
        
        # Default: no known issues
        return {
            "score": 20,
            "has_issues": False,
            "description": "No known regulatory issues",
        }
    
    def _calculate_age_score(self, coin: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate age/maturity risk.
        Newer coins = higher risk (simplified - use ATH date as proxy).
        """
        # Use market cap rank as proxy for maturity
        rank = coin.get("market_cap_rank") or 1000
        
        if rank <= 20:
            score = 15  # Established
        elif rank <= 100:
            score = 30
        elif rank <= 500:
            score = 50
        else:
            score = 70  # Likely newer/riskier
        
        return {
            "score": score,
            "description": "Established" if rank <= 50 else "Less established",
        }
    
    def _create_stablecoin_risk(self, coin: Dict[str, Any]) -> Dict[str, Any]:
        """Create risk assessment for stablecoins."""
        return {
            "coin_id": coin.get("coin_id") or coin.get("id") or "",
            "symbol": coin.get("symbol", "").upper(),
            "name": coin.get("name", ""),
            "risk_score": 5,
            "risk_level": RiskLevel.NO_RISK.value,
            "risk_label": "No Risk",
            "risk_color": RISK_COLORS[RiskLevel.NO_RISK],
            "factors": {
                "volatility": {"score": 5, "description": "Pegged to fiat"},
                "volume_ratio": {"score": 10, "description": "High liquidity"},
                "market_cap": {"score": 5, "description": "Large market cap"},
                "regulatory": {"score": 10, "description": "Regulated stablecoin"},
                "age": {"score": 5, "description": "Established"},
            },
            "summary": "Stablecoin pegged to fiat currency. Minimal price volatility.",
            "calculated_at": datetime.utcnow().isoformat(),
        }
    
    def _create_lawsuit_risk(self, coin: Dict[str, Any]) -> Dict[str, Any]:
        """Create risk assessment for coins with legal issues."""
        coin_id = coin.get("coin_id") or coin.get("id") or ""
        
        # Still calculate base score
        base_factors = {
            "volatility": self._calculate_volatility_score(coin),
            "volume_ratio": self._calculate_volume_score(coin),
            "market_cap": self._calculate_market_cap_score(coin),
            "regulatory": {"score": 95, "has_issues": True, "description": "Active legal/regulatory concerns"},
            "age": self._calculate_age_score(coin),
        }
        
        # Override with lawsuit emphasis
        base_score = sum(
            base_factors[f]["score"] * self.weights[f]
            for f in base_factors
        )
        
        # Lawsuit adds significant risk
        final_score = min(100, max(91, base_score + 20))
        
        return {
            "coin_id": coin_id,
            "symbol": coin.get("symbol", "").upper(),
            "name": coin.get("name", ""),
            "risk_score": round(final_score, 1),
            "risk_level": RiskLevel.LAWSUIT.value,
            "risk_label": "Lawsuit",
            "risk_color": RISK_COLORS[RiskLevel.LAWSUIT],
            "factors": base_factors,
            "summary": "This asset has known regulatory or legal concerns. Exercise caution.",
            "calculated_at": datetime.utcnow().isoformat(),
        }
    
    def _score_to_level(self, score: float) -> RiskLevel:
        """Map score to risk level."""
        if score <= 10:
            return RiskLevel.NO_RISK
        elif score <= 25:
            return RiskLevel.SAFE
        elif score <= 40:
            return RiskLevel.LOW_RISK
        elif score <= 60:
            return RiskLevel.MED_RISK
        elif score <= 75:
            return RiskLevel.VOLATILE
        elif score <= 90:
            return RiskLevel.EXTREME
        else:
            return RiskLevel.LAWSUIT
    
    def _level_to_label(self, level: RiskLevel) -> str:
        """Get display label for risk level."""
        labels = {
            RiskLevel.NO_RISK: "No Risk",
            RiskLevel.SAFE: "Safe",
            RiskLevel.LOW_RISK: "Low Risk",
            RiskLevel.MED_RISK: "Med Risk",
            RiskLevel.VOLATILE: "Volatile",
            RiskLevel.EXTREME: "Extreme",
            RiskLevel.LAWSUIT: "Lawsuit",
        }
        return labels.get(level, "Unknown")
    
    def _volatility_description(self, score: float) -> str:
        """Generate volatility description."""
        if score < 30:
            return "Low volatility"
        elif score < 50:
            return "Moderate volatility"
        elif score < 70:
            return "High volatility"
        else:
            return "Extreme volatility"
    
    def _generate_summary(self, level: RiskLevel, factors: Dict[str, Any]) -> str:
        """Generate summary text for risk assessment."""
        summaries = {
            RiskLevel.NO_RISK: "Extremely stable asset with minimal price fluctuation.",
            RiskLevel.SAFE: "Low-risk asset with proven stability and liquidity.",
            RiskLevel.LOW_RISK: "Generally stable with occasional minor fluctuations.",
            RiskLevel.MED_RISK: "Moderate volatility. Standard risk management recommended.",
            RiskLevel.VOLATILE: "High volatility. Significant price swings expected.",
            RiskLevel.EXTREME: "Very high risk. Only for experienced traders.",
            RiskLevel.LAWSUIT: "Legal/regulatory concerns. Exercise extreme caution.",
        }
        return summaries.get(level, "Risk level undetermined.")
    
    def get_top_risky_coins(self, coins: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top riskiest coins from a list.
        
        Args:
            coins: List of coin data
            limit: Max number to return
            
        Returns:
            List of risk assessments sorted by score descending
        """
        assessments = [self.calculate_risk_score(coin) for coin in coins]
        
        # Sort by risk score descending
        assessments.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return assessments[:limit]
    
    def get_market_risk_overview(self, coins: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall market risk summary.
        
        Args:
            coins: List of coin data
            
        Returns:
            Market-wide risk metrics
        """
        if not coins:
            return {
                "average_risk": 50,
                "risk_level": RiskLevel.MED_RISK.value,
                "distribution": {},
                "top_risks": [],
            }
        
        assessments = [self.calculate_risk_score(coin) for coin in coins[:100]]
        
        # Calculate average
        avg_score = sum(a["risk_score"] for a in assessments) / len(assessments)
        
        # Count distribution
        distribution = {}
        for level in RiskLevel:
            distribution[level.value] = len([
                a for a in assessments if a["risk_level"] == level.value
            ])
        
        # Top 5 riskiest
        top_risks = sorted(assessments, key=lambda x: x["risk_score"], reverse=True)[:5]
        
        return {
            "average_risk": round(avg_score, 1),
            "risk_level": self._score_to_level(avg_score).value,
            "risk_label": self._level_to_label(self._score_to_level(avg_score)),
            "distribution": distribution,
            "top_risks": top_risks,
            "calculated_at": datetime.utcnow().isoformat(),
        }


# Singleton
ai_risk_service = AIRiskService()
