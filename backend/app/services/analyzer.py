"""
Technical Analyzer Service
Ported from python-service/services/analyzer.py
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import pandas as pd
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, ADXIndicator, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange

from app.services.database import DatabaseService

logger = logging.getLogger(__name__)


class AnalyzerService:
    """Technical analysis service using TA library"""
    
    def __init__(self, db: DatabaseService):
        self.db = db
    
    async def analyze_coins(self, coin_ids: List[str], force_refresh: bool = False) -> Dict[str, Any]:
        """Analyze multiple coins"""
        results = {"success_count": 0, "failed_count": 0, "results": []}
        
        for coin_id in coin_ids:
            try:
                analysis = await self.analyze_single_coin(coin_id)
                
                if analysis:
                    saved = self.db.save_sentiment(
                        coin_id=coin_id,
                        asi_score=analysis["asi_score"],
                        signal=analysis["signal"],
                        reason=analysis["reasoning"],
                        provider="technical",
                    )
                    
                    if saved:
                        results["success_count"] += 1
                        results["results"].append({
                            "coin_id": coin_id,
                            "asi_score": analysis["asi_score"],
                            "signal": analysis["signal"],
                        })
                    else:
                        results["failed_count"] += 1
                else:
                    results["failed_count"] += 1
                    
            except Exception as e:
                logger.error(f"Failed to analyze {coin_id}: {e}")
                results["failed_count"] += 1
        
        return results
    
    async def analyze_single_coin(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Perform technical analysis on a single coin"""
        MIN_CANDLES = 30
        
        ohlcv_data = self.db.get_ohlcv_data(coin_id, interval="1h", limit=100)
        
        if len(ohlcv_data) < MIN_CANDLES:
            logger.warning(f"Insufficient OHLCV for {coin_id}: {len(ohlcv_data)} candles")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(ohlcv_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.drop_duplicates(subset=["timestamp"], keep="last")
        df = df.set_index("timestamp").sort_index()
        
        # Rename columns for TA library
        df = df.rename(columns={
            "open": "Open", "high": "High", "low": "Low",
            "close": "Close", "volume": "Volume",
        })
        
        # Calculate indicators
        indicators = self.calculate_indicators(df)
        
        # Calculate ASI score
        asi_score, signal = self.calculate_asi_score(indicators)
        
        # Generate reasoning
        reasoning = self.generate_reasoning(indicators, asi_score, signal)
        
        return {
            "coin_id": coin_id,
            "asi_score": asi_score,
            "signal": signal,
            "reasoning": reasoning,
            "indicators": indicators,
            "analyzed_at": datetime.now().isoformat(),
        }
    
    def calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators"""
        indicators = {}
        
        try:
            # RSI (14)
            rsi = RSIIndicator(close=df["Close"], window=14)
            rsi_value = rsi.rsi().iloc[-1]
            indicators["rsi_14"] = round(float(rsi_value), 2) if pd.notna(rsi_value) else 50
            
            # MACD (12, 26, 9)
            macd = MACD(close=df["Close"], window_slow=26, window_fast=12, window_sign=9)
            indicators["macd_histogram"] = round(float(macd.macd_diff().iloc[-1]), 4) if pd.notna(macd.macd_diff().iloc[-1]) else 0
            indicators["macd_line"] = round(float(macd.macd().iloc[-1]), 4) if pd.notna(macd.macd().iloc[-1]) else 0
            indicators["macd_signal"] = round(float(macd.macd_signal().iloc[-1]), 4) if pd.notna(macd.macd_signal().iloc[-1]) else 0
            
            # Bollinger Bands (20, 2)
            bb = BollingerBands(close=df["Close"], window=20, window_dev=2)
            bb_upper = bb.bollinger_hband().iloc[-1]
            bb_lower = bb.bollinger_lband().iloc[-1]
            current_price = float(df["Close"].iloc[-1])
            
            bb_width = float(bb_upper - bb_lower) if pd.notna(bb_upper) and pd.notna(bb_lower) else 1
            indicators["bb_percent_b"] = round((current_price - float(bb_lower)) / bb_width, 4) if bb_width > 0 else 0.5
            
            # Stochastic (14, 3)
            stoch = StochasticOscillator(high=df["High"], low=df["Low"], close=df["Close"], window=14, smooth_window=3)
            indicators["stoch_k"] = round(float(stoch.stoch().iloc[-1]), 2) if pd.notna(stoch.stoch().iloc[-1]) else 50
            indicators["stoch_d"] = round(float(stoch.stoch_signal().iloc[-1]), 2) if pd.notna(stoch.stoch_signal().iloc[-1]) else 50
            
            # ADX (14)
            adx = ADXIndicator(high=df["High"], low=df["Low"], close=df["Close"], window=14)
            indicators["adx"] = round(float(adx.adx().iloc[-1]), 2) if pd.notna(adx.adx().iloc[-1]) else 0
            
            # EMA
            ema_9 = EMAIndicator(close=df["Close"], window=9).ema_indicator().iloc[-1]
            ema_21 = EMAIndicator(close=df["Close"], window=21).ema_indicator().iloc[-1]
            indicators["ema_9"] = round(float(ema_9), 4) if pd.notna(ema_9) else 0
            indicators["ema_21"] = round(float(ema_21), 4) if pd.notna(ema_21) else 0
            
            # Price info
            indicators["current_price"] = round(current_price, 8)
            if len(df) > 24:
                price_24h_ago = float(df["Close"].iloc[-25])
                indicators["price_change_24h"] = round(((current_price - price_24h_ago) / price_24h_ago) * 100, 2)
            else:
                indicators["price_change_24h"] = 0
                
        except Exception as e:
            logger.error(f"Failed to calculate indicators: {e}")
            indicators = {"rsi_14": 50, "macd_histogram": 0, "bb_percent_b": 0.5, "stoch_k": 50, "adx": 0}
        
        return indicators
    
    def calculate_asi_score(self, indicators: Dict[str, Any]) -> tuple:
        """Calculate AI Sentiment Index (0-100)"""
        score = 50
        
        # RSI (25 points)
        rsi = indicators.get("rsi_14", 50)
        if rsi < 30:
            score += 15
        elif rsi < 40:
            score += 8
        elif rsi > 70:
            score -= 15
        elif rsi > 60:
            score -= 8
        
        # MACD (25 points)
        macd_hist = indicators.get("macd_histogram", 0)
        if macd_hist > 0:
            score += min(12, abs(macd_hist) * 100)
        else:
            score -= min(12, abs(macd_hist) * 100)
        
        if indicators.get("macd_line", 0) > indicators.get("macd_signal", 0):
            score += 5
        else:
            score -= 5
        
        # Bollinger Bands (20 points)
        bb_pct = indicators.get("bb_percent_b", 0.5)
        if bb_pct < 0.2:
            score += 10
        elif bb_pct > 0.8:
            score -= 10
        
        # Stochastic (15 points)
        stoch_k = indicators.get("stoch_k", 50)
        if stoch_k < 20:
            score += 8
        elif stoch_k > 80:
            score -= 8
        
        # ADX trend (15 points)
        adx = indicators.get("adx", 0)
        if adx > 25:
            if indicators.get("price_change_24h", 0) > 0:
                score += 8
            else:
                score -= 8
        
        score = max(0, min(100, score))
        
        if score >= 75:
            signal = "STRONG_BUY"
        elif score >= 60:
            signal = "BUY"
        elif score >= 40:
            signal = "NEUTRAL"
        elif score >= 25:
            signal = "SELL"
        else:
            signal = "STRONG_SELL"
        
        return int(score), signal
    
    def generate_reasoning(self, indicators: Dict[str, Any], asi_score: int, signal: str) -> str:
        """Generate human-readable reasoning"""
        reasons = []
        
        rsi = indicators.get("rsi_14", 50)
        if rsi < 30:
            reasons.append(f"RSI({rsi:.1f}) oversold")
        elif rsi > 70:
            reasons.append(f"RSI({rsi:.1f}) overbought")
        
        if indicators.get("macd_histogram", 0) > 0:
            reasons.append("MACD bullish")
        else:
            reasons.append("MACD bearish")
        
        bb_pct = indicators.get("bb_percent_b", 0.5)
        if bb_pct < 0.2:
            reasons.append("Near lower BB")
        elif bb_pct > 0.8:
            reasons.append("Near upper BB")
        
        adx = indicators.get("adx", 0)
        if adx > 25:
            reasons.append(f"Strong trend (ADX:{adx:.0f})")
        
        return f"ASI:{asi_score}/100 ({signal}). " + ", ".join(reasons)
