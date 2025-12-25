
from typing import List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AIHedgeFundService:
    """
    AI Hedge Fund Manager Service
    Handles Portfolio Auditing, Risk Analysis, and Stress Simulation
    """
    
    def __init__(self):
        # Base betas for stress testing (volatility relative to BTC)
        # In a real app, these would be calculated dynamically from historical data
        self.default_betas = {
            "bitcoin": 1.0,
            "ethereum": 1.1,
            "solana": 1.4,
            "binancecoin": 0.9,
            "ripple": 0.8,
            "cardano": 1.1,
            "dogecoin": 1.6,
            "avalanche-2": 1.4,
            "polkadot": 1.2,
            "matic-network": 1.3,
            "shiba-inu": 1.8,
            "chainlink": 1.2,
            "uniswap": 1.3,
            "litecoin": 0.9
        }
        self.default_beta_alts = 1.5

    def audit_portfolio(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Audit the portfolio and calculate a health score (0-100)
        Analysis covers: Diversification, Stablecoin Ratio, High-Risk concentration
        """
        if not holdings:
            return {
                "score": 0, 
                "health": "Empty", 
                "warnings": ["Portfolio is empty"],
                "breakdown": {}
            }

        total_value = sum(h.get('value', 0) or (h.get('amount', 0) * h.get('current_price', 0)) for h in holdings)
        
        if total_value == 0:
            return {"score": 0, "health": "Empty", "warnings": [], "breakdown": {}}

        # Analysis Variables
        score = 100
        warnings = []
        breakdown = {
            "diversification_score": 100,
            "risk_score": 100,
            "stablecoin_ratio": 0
        }
        
        # 1. Concentration Risk (Diversification)
        # Penalty if any single asset > 40% (except Stablecoins - simplified check)
        max_allocation = 0
        concentrated_asset = None
        
        for h in holdings:
            value = h.get('value', 0) or (h.get('amount', 0) * h.get('current_price', 0))
            allocation = value / total_value
            
            if allocation > max_allocation:
                max_allocation = allocation
                concentrated_asset = h.get('symbol', 'Unknown')

        if max_allocation > 0.60:
            penalty = 25
            score -= penalty
            breakdown["diversification_score"] -= penalty
            warnings.append(f"High concentration risk: {concentrated_asset} makes up {int(max_allocation*100)}% of portfolio.")
        elif max_allocation > 0.40:
            penalty = 10
            score -= penalty
            breakdown["diversification_score"] -= penalty
            warnings.append(f"Moderate concentration: {concentrated_asset} is {int(max_allocation*100)}% of portfolio.")

        # 2. Holdings Count Risk
        # Penalty if < 3 assets (too concentrated) or > 20 (over-diversified/hard to manage)
        count = len(holdings)
        if count < 3:
            penalty = 10
            score -= penalty
            breakdown["diversification_score"] -= penalty
            warnings.append("Low diversification: Consider holding at least 3-5 assets.")
        elif count > 20:
             # Small penalty for over-diversification
            score -= 5
            warnings.append("High fragmentation: Managing >20 assets may reduce effective returns.")

        # 3. Volatility/Beta Risk (Simplified)
        # Check weighted average beta
        weighted_beta = 0
        for h in holdings:
            value = h.get('value', 0) or (h.get('amount', 0) * h.get('current_price', 0))
            weight = value / total_value
            coin_id = h.get('coin_id', '').lower()
            beta = self.default_betas.get(coin_id, self.default_beta_alts)
            weighted_beta += beta * weight

        if weighted_beta > 1.4:
            penalty = 15
            score -= penalty
            breakdown["risk_score"] -= penalty
            warnings.append("High Portfolio Volatility: Your portfolio is significantly more volatile than Bitcoin.")
        
        # Final Score Normalization
        score = max(0, min(100, score))
        
        # Health Label
        health_label = "Excellent"
        if score < 60: health_label = "Critical"
        elif score < 75: health_label = "Fair"
        elif score < 90: health_label = "Good"

        return {
            "score": score,
            "health": health_label,
            "metric_beta": round(weighted_beta, 2),
            "warnings": warnings,
            "breakdown": breakdown
        }

    def simulate_stress(self, holdings: List[Dict[str, Any]], scenario_btc_change: float) -> Dict[str, Any]:
        """
        Simulate portfolio performance based on a BTC price change scenario.
        scenario_btc_change: Percentage change of BTC (e.g., -10 for -10% drop)
        """
        if not holdings:
            return {"current_value": 0, "projected_value": 0, "change_amount": 0, "change_percent": 0, "details": []}

        total_current_value = 0
        total_projected_value = 0
        details = []

        scenario_factor = scenario_btc_change / 100.0

        for h in holdings:
            coin_id = h.get('coin_id', '').lower()
            symbol = h.get('symbol', 'UNK')
            amount = float(h.get('amount', 0))
            current_price = float(h.get('current_price', 0) or h.get('buy_price', 0)) # Fallback if current_price missing
            
            current_value = amount * current_price
            total_current_value += current_value

            # Get Beta
            beta = self.default_betas.get(coin_id, self.default_beta_alts)
            
            # Stablecoins (USDT, USDC, DAI) ideally have 0 beta
            if symbol.upper() in ['USDT', 'USDC', 'DAI', 'FDUSD']:
                beta = 0.01 # Very low correlation
            
            # Calculate expected change for this asset
            # If BTC moves X%, Asset moves X% * Beta
            asset_change_pct = scenario_factor * beta
            
            # Calculate projected price
            projected_price = current_price * (1 + asset_change_pct)
            projected_value = amount * projected_price
            
            total_projected_value += projected_value
            
            details.append({
                "symbol": symbol,
                "beta": beta,
                "projected_change_pct": round(asset_change_pct * 100, 2),
                "pnl_amount": projected_value - current_value
            })

        change_amount = total_projected_value - total_current_value
        change_percent = (change_amount / total_current_value * 100) if total_current_value > 0 else 0

        return {
            "scenario": f"BTC {scenario_btc_change}%",
            "current_value": total_current_value,
            "projected_value": total_projected_value,
            "change_amount": change_amount,
            "change_percent": change_percent,
            "details": sorted(details, key=lambda x: x['pnl_amount']) # Sort by biggest losers/gainers
        }

# Singleton instance
ai_hedge_fund_service = AIHedgeFundService()
