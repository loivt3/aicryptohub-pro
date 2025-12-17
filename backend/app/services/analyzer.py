"""
AI Crypto Hub Pro - Analyzer Service
Technical Analysis using TA library
"""

import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

import pandas as pd
import ta
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, ADXIndicator, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange

from app.core.config import Settings
from app.services.database import DatabaseService

logger = logging.getLogger(__name__)



class AnalyzerService:
    """Technical analysis service using Pandas-TA"""
    
    def __init__(self, db: DatabaseService, settings: Settings):
        self.db = db
        self.settings = settings
    
    async def analyze_coins(
        self,
        coin_ids: List[str],
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze multiple coins
        
        Args:
            coin_ids: List of coin IDs to analyze
            force_refresh: Force refresh even if recent analysis exists
            
        Returns:
            Analysis results summary
        """
        # Import monitoring
        from app.services.monitoring import increment_counter, record_duration, set_gauge
        
        start_time = time.time()
        
        results = {
            "success_count": 0,
            "failed_count": 0,
            "results": [],
        }
        
        for coin_id in coin_ids:
            try:
                analysis = await self.analyze_single_coin(coin_id)
                
                if analysis:
                    # Save to database
                    saved = self.db.save_ai_sentiment(
                        coin_id=coin_id,
                        asi_score=analysis["asi_score"],
                        signal=analysis["signal"],
                        reasoning=analysis["reasoning"],
                        indicators=analysis["indicators"],
                        provider="python_ta",
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
        
        # Record metrics
        duration = time.time() - start_time
        increment_counter("analysis_total")
        increment_counter("analysis_success", results["success_count"])
        increment_counter("analysis_failed", results["failed_count"])
        record_duration("analysis", duration)
        set_gauge("coins_analyzed", results["success_count"])
        set_gauge("last_analysis_time", datetime.now().isoformat())
        
        return results
    
    async def _fetch_ohlcv_for_coin(self, coin_id: str) -> bool:
        """
        Fetch OHLCV data from Binance for a single coin and save to database.
        Called automatically when analyze_single_coin finds insufficient data.
        
        Args:
            coin_id: CoinGecko coin ID (e.g., 'bitcoin')
            
        Returns:
            True if fetched and saved successfully
        """
        try:
            from app.services.data_fetcher import get_data_fetcher
            fetcher = get_data_fetcher()
            
            # Get symbol from coin_id
            symbol = self.db._get_symbol_for_coin(coin_id)
            if not symbol:
                logger.warning(f"No symbol found for {coin_id}, cannot fetch OHLCV")
                return False
            
            # Fetch from Binance
            klines = await fetcher.binance.fetch_klines(f"{symbol}USDT", "1h", limit=100)
            
            if not klines or len(klines) < 30:
                logger.warning(f"Binance returned insufficient data for {symbol}: {len(klines) if klines else 0}")
                return False
            
            # Save to database
            from sqlalchemy import text
            query = text("""
                INSERT INTO aihub_ohlcv (symbol, timeframe, open_time, open, high, low, close, volume, trades_count)
                VALUES (:symbol, :timeframe, :open_time, :open, :high, :low, :close, :volume, :trades_count)
                ON CONFLICT DO NOTHING
            """)
            
            with self.db.engine.begin() as conn:
                for kline in klines:
                    conn.execute(query, {
                        "symbol": symbol.upper(),
                        "timeframe": 60,  # 1h = 60 minutes
                        "open_time": datetime.fromtimestamp(kline["timestamp"] / 1000),
                        "open": kline["open"],
                        "high": kline["high"],
                        "low": kline["low"],
                        "close": kline["close"],
                        "volume": kline["volume"],
                        "trades_count": kline.get("trades", 0),
                    })
            
            logger.info(f"Auto-fetched {len(klines)} OHLCV candles for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to auto-fetch OHLCV for {coin_id}: {e}")
            return False
    
    async def analyze_single_coin(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """
        Perform technical analysis on a single coin.
        Auto-fetches OHLCV data from Binance if insufficient data exists.
        
        Args:
            coin_id: Coin identifier
            
        Returns:
            Analysis result dict or None
        """
        MIN_CANDLES = 30
        
        # Fetch OHLCV data from database
        ohlcv_data = self.db.get_ohlcv_data(coin_id, timeframe="1h", limit=100)
        
        # Auto-fetch if insufficient data
        if len(ohlcv_data) < MIN_CANDLES:
            logger.info(f"Insufficient OHLCV for {coin_id}: {len(ohlcv_data)} candles. Auto-fetching...")
            fetched = await self._fetch_ohlcv_for_coin(coin_id)
            if fetched:
                # Re-read from database after fetch
                ohlcv_data = self.db.get_ohlcv_data(coin_id, timeframe="1h", limit=100)
        
        if len(ohlcv_data) < MIN_CANDLES:
            logger.warning(f"Still insufficient OHLCV for {coin_id}: {len(ohlcv_data)} candles (need {MIN_CANDLES})")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(ohlcv_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Remove duplicate timestamps (keep last)
        df = df.drop_duplicates(subset=["timestamp"], keep="last")
        df = df.set_index("timestamp")
        df = df.sort_index()  # Ensure chronological order
        
        # Ensure proper column names for TA library
        df = df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
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
        """
        Calculate technical indicators using TA library
        
        Args:
            df: OHLCV DataFrame
            
        Returns:
            Dictionary of indicator values
        """
        indicators = {}
        
        try:
            # RSI (14)
            rsi_indicator = RSIIndicator(close=df["Close"], window=14)
            rsi_value = rsi_indicator.rsi().iloc[-1]
            indicators["rsi_14"] = round(float(rsi_value), 2) if pd.notna(rsi_value) else 50
            
            # MACD (12, 26, 9)
            macd_indicator = MACD(close=df["Close"], window_slow=26, window_fast=12, window_sign=9)
            macd_line = macd_indicator.macd().iloc[-1]
            macd_signal = macd_indicator.macd_signal().iloc[-1]
            macd_hist = macd_indicator.macd_diff().iloc[-1]
            
            indicators["macd_line"] = round(float(macd_line), 4) if pd.notna(macd_line) else 0
            indicators["macd_signal"] = round(float(macd_signal), 4) if pd.notna(macd_signal) else 0
            indicators["macd_histogram"] = round(float(macd_hist), 4) if pd.notna(macd_hist) else 0
            
            # Bollinger Bands (20, 2)
            bb_indicator = BollingerBands(close=df["Close"], window=20, window_dev=2)
            bb_upper = bb_indicator.bollinger_hband().iloc[-1]
            bb_middle = bb_indicator.bollinger_mavg().iloc[-1]
            bb_lower = bb_indicator.bollinger_lband().iloc[-1]
            
            indicators["bb_upper"] = round(float(bb_upper), 4) if pd.notna(bb_upper) else 0
            indicators["bb_middle"] = round(float(bb_middle), 4) if pd.notna(bb_middle) else 0
            indicators["bb_lower"] = round(float(bb_lower), 4) if pd.notna(bb_lower) else 0
            
            # BB %B (price position within bands)
            current_price = float(df["Close"].iloc[-1])
            bb_width = indicators["bb_upper"] - indicators["bb_lower"]
            if bb_width > 0:
                indicators["bb_percent_b"] = round((current_price - indicators["bb_lower"]) / bb_width, 4)
            else:
                indicators["bb_percent_b"] = 0.5
            
            # EMA (9, 21, 50)
            ema_9 = EMAIndicator(close=df["Close"], window=9).ema_indicator().iloc[-1]
            ema_21 = EMAIndicator(close=df["Close"], window=21).ema_indicator().iloc[-1]
            ema_50 = EMAIndicator(close=df["Close"], window=50).ema_indicator().iloc[-1]
            
            indicators["ema_9"] = round(float(ema_9), 4) if pd.notna(ema_9) else 0
            indicators["ema_21"] = round(float(ema_21), 4) if pd.notna(ema_21) else 0
            indicators["ema_50"] = round(float(ema_50), 4) if pd.notna(ema_50) else 0
            
            # Stochastic (14, 3)
            stoch_indicator = StochasticOscillator(
                high=df["High"], low=df["Low"], close=df["Close"],
                window=14, smooth_window=3
            )
            stoch_k = stoch_indicator.stoch().iloc[-1]
            stoch_d = stoch_indicator.stoch_signal().iloc[-1]
            
            indicators["stoch_k"] = round(float(stoch_k), 2) if pd.notna(stoch_k) else 50
            indicators["stoch_d"] = round(float(stoch_d), 2) if pd.notna(stoch_d) else 50
            
            # ADX (14)
            adx_indicator = ADXIndicator(high=df["High"], low=df["Low"], close=df["Close"], window=14)
            adx_value = adx_indicator.adx().iloc[-1]
            indicators["adx"] = round(float(adx_value), 2) if pd.notna(adx_value) else 0
            
            # ATR (14)
            atr_indicator = AverageTrueRange(high=df["High"], low=df["Low"], close=df["Close"], window=14)
            atr_value = atr_indicator.average_true_range().iloc[-1]
            indicators["atr_14"] = round(float(atr_value), 4) if pd.notna(atr_value) else 0
            
            # Current price and change
            indicators["current_price"] = round(float(df["Close"].iloc[-1]), 8)
            if len(df) > 24:
                price_24h_ago = float(df["Close"].iloc[-25])
                indicators["price_change_24h"] = round(
                    ((indicators["current_price"] - price_24h_ago) / price_24h_ago) * 100, 2
                )
            else:
                indicators["price_change_24h"] = 0
            
        except Exception as e:
            logger.error(f"Failed to calculate indicators: {e}")
            # Return defaults
            indicators = {
                "rsi_14": 50,
                "macd_line": 0,
                "macd_signal": 0,
                "macd_histogram": 0,
                "bb_percent_b": 0.5,
                "stoch_k": 50,
                "stoch_d": 50,
                "adx": 0,
                "current_price": 0,
                "price_change_24h": 0,
            }
        
        return indicators
    
    def calculate_asi_score(self, indicators: Dict[str, Any]) -> tuple[int, str]:
        """
        Calculate AI Sentiment Index (0-100) from indicators
        
        Scoring breakdown:
        - RSI: 25 points
        - MACD: 25 points
        - Bollinger: 20 points
        - Stochastic: 15 points
        - Trend strength: 15 points
        
        Returns:
            (asi_score, signal)
        """
        score = 50  # Start neutral
        
        # RSI contribution (25 points)
        rsi = indicators.get("rsi_14", 50)
        if rsi < 30:
            score += 15  # Oversold = bullish
        elif rsi < 40:
            score += 8
        elif rsi > 70:
            score -= 15  # Overbought = bearish
        elif rsi > 60:
            score -= 8
        
        # MACD contribution (25 points)
        macd_hist = indicators.get("macd_histogram", 0)
        macd_line = indicators.get("macd_line", 0)
        macd_signal = indicators.get("macd_signal", 0)
        
        if macd_hist > 0:
            score += min(12, abs(macd_hist) * 100)  # Positive histogram
        else:
            score -= min(12, abs(macd_hist) * 100)
        
        if macd_line > macd_signal:
            score += 5  # Bullish crossover
        else:
            score -= 5
        
        # Bollinger Bands contribution (20 points)
        bb_pct = indicators.get("bb_percent_b", 0.5)
        if bb_pct < 0.2:
            score += 10  # Near lower band = buy signal
        elif bb_pct > 0.8:
            score -= 10  # Near upper band = sell signal
        
        # Stochastic contribution (15 points)
        stoch_k = indicators.get("stoch_k", 50)
        stoch_d = indicators.get("stoch_d", 50)
        
        if stoch_k < 20:
            score += 8  # Oversold
        elif stoch_k > 80:
            score -= 8  # Overbought
        
        if stoch_k > stoch_d:
            score += 3  # Bullish crossover
        else:
            score -= 3
        
        # Trend strength (ADX) contribution (15 points)
        adx = indicators.get("adx", 0)
        price_change = indicators.get("price_change_24h", 0)
        
        if adx > 25:  # Strong trend
            if price_change > 0:
                score += 8  # Strong uptrend
            else:
                score -= 8  # Strong downtrend
        
        # Clamp to 0-100
        score = max(0, min(100, score))
        
        # Determine signal
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
    
    def generate_reasoning(
        self,
        indicators: Dict[str, Any],
        asi_score: int,
        signal: str
    ) -> str:
        """Generate human-readable reasoning for the analysis"""
        
        reasons = []
        
        # RSI analysis
        rsi = indicators.get("rsi_14", 50)
        if rsi < 30:
            reasons.append(f"RSI({rsi:.1f}) indicates oversold conditions")
        elif rsi > 70:
            reasons.append(f"RSI({rsi:.1f}) indicates overbought conditions")
        else:
            reasons.append(f"RSI({rsi:.1f}) is in neutral territory")
        
        # MACD analysis
        macd_hist = indicators.get("macd_histogram", 0)
        if macd_hist > 0:
            reasons.append("MACD histogram is positive (bullish momentum)")
        else:
            reasons.append("MACD histogram is negative (bearish momentum)")
        
        # Bollinger Bands
        bb_pct = indicators.get("bb_percent_b", 0.5)
        if bb_pct < 0.2:
            reasons.append("Price near lower Bollinger Band (potential bounce)")
        elif bb_pct > 0.8:
            reasons.append("Price near upper Bollinger Band (potential pullback)")
        
        # Price change
        price_change = indicators.get("price_change_24h", 0)
        if abs(price_change) > 5:
            direction = "up" if price_change > 0 else "down"
            reasons.append(f"24h price {direction} {abs(price_change):.1f}%")
        
        # ADX trend
        adx = indicators.get("adx", 0)
        if adx > 25:
            reasons.append(f"ADX({adx:.1f}) indicates strong trend")
        
        reasoning = f"ASI Score: {asi_score}/100 ({signal}). " + ". ".join(reasons) + "."
        
        return reasoning
    
    def calculate_intent_divergence(
        self,
        whale_action: str,
        crowd_sentiment: int,
        crowd_action: str,
        whale_volume_usd: float = 0,
    ) -> Dict[str, Any]:
        """
        Calculate divergence between whale intent and crowd behavior.
        
        High divergence = Whale acting AGAINST crowd (strong signal)
        Low divergence = Whale acting WITH crowd (confirmation)
        
        Args:
            whale_action: "accumulate", "distribute", "neutral"
            crowd_sentiment: 0-100 sentiment score
            crowd_action: "Sell-off", "Buy-dip", "Hold", "FOMO-buy", etc.
            whale_volume_usd: Volume of whale transaction
            
        Returns:
            Dict with:
            - divergence_score: -100 to +100 
              (negative = whale selling while crowd buying, positive = whale buying while crowd selling)
            - alignment: "with_crowd", "against_crowd", "neutral"
            - signal_strength: "weak", "moderate", "strong"
            - interpretation: Human-readable explanation
        """
        # Map crowd actions to sentiment direction
        CROWD_ACTION_SCORES = {
            "Sell-off": -80,
            "Panic-sell": -100,
            "Buy-dip": 60,
            "FOMO-buy": 80,
            "Hold": 0,
            "Accumulate": 70,
        }
        
        # Map whale actions
        WHALE_ACTION_SCORES = {
            "accumulate": 100,
            "distribute": -100,
            "neutral": 0,
        }
        
        # Get scores
        crowd_direction = CROWD_ACTION_SCORES.get(crowd_action, 0)
        whale_direction = WHALE_ACTION_SCORES.get(whale_action.lower(), 0)
        
        # Adjust crowd direction by sentiment score
        # crowd_sentiment 0-100: 0=fear, 100=greed
        sentiment_factor = (crowd_sentiment - 50) / 50  # -1 to +1
        adjusted_crowd = crowd_direction * (0.5 + abs(sentiment_factor) * 0.5)
        
        # Calculate divergence
        # Positive = whale bullish when crowd bearish (contrarian buy)
        # Negative = whale bearish when crowd bullish (contrarian sell)
        divergence_score = whale_direction - adjusted_crowd
        
        # Normalize to -100 to +100
        divergence_score = max(-100, min(100, divergence_score))
        
        # Determine alignment
        if abs(divergence_score) < 20:
            alignment = "neutral"
        elif (whale_direction > 0 and adjusted_crowd > 0) or (whale_direction < 0 and adjusted_crowd < 0):
            alignment = "with_crowd"
        else:
            alignment = "against_crowd"
        
        # Signal strength based on divergence magnitude and volume
        volume_factor = 1.0
        if whale_volume_usd > 10_000_000:
            volume_factor = 1.5
        elif whale_volume_usd > 1_000_000:
            volume_factor = 1.2
        
        weighted_divergence = abs(divergence_score) * volume_factor
        
        if weighted_divergence < 30:
            signal_strength = "weak"
        elif weighted_divergence < 60:
            signal_strength = "moderate"
        else:
            signal_strength = "strong"
        
        # Generate interpretation
        if alignment == "against_crowd":
            if whale_direction > 0:
                interpretation = f"Whale accumulating while crowd is {crowd_action.lower()}. "
                interpretation += "This contrarian buy suggests smart money sees value others are missing."
            else:
                interpretation = f"Whale distributing while crowd is {crowd_action.lower()}. "
                interpretation += "This contrarian sell suggests smart money is de-risking ahead of potential correction."
        elif alignment == "with_crowd":
            if whale_direction > 0:
                interpretation = f"Whale accumulating along with crowd ({crowd_action}). "
                interpretation += "Alignment between smart money and retail suggests sustained momentum."
            else:
                interpretation = f"Whale distributing along with crowd ({crowd_action}). "
                interpretation += "Both smart money and retail exiting may indicate significant downside."
        else:
            interpretation = "No clear directional signal from whale activity relative to crowd sentiment."
        
        return {
            "divergence_score": round(divergence_score, 2),
            "alignment": alignment,
            "signal_strength": signal_strength,
            "interpretation": interpretation,
            "whale_action": whale_action,
            "crowd_action": crowd_action,
            "crowd_sentiment": crowd_sentiment,
        }
    
    async def calculate_intent_divergence_v2(
        self,
        coin_id: str,
        include_ai_insight: bool = True,
    ) -> Dict[str, Any]:
        """
        Enhanced Intent Divergence with whale profiling and AI insights.
        
        Scenarios:
        - Shadow Accumulation: Sentiment < 40, Whale Outflow from exchanges (bullish)
        - Bull Trap: Sentiment > 70, Whale Inflow to exchanges (bearish)
        - Confirmation: Whale and crowd aligned
        - Neutral: No clear signal
        
        Args:
            coin_id: Coin ID to analyze
            include_ai_insight: Whether to generate AI shadow insight
            
        Returns:
            Complete intent divergence package for frontend
        """
        from sqlalchemy import text
        
        result = {
            "coin_id": coin_id,
            "intent_score": 50,
            "divergence_type": "neutral",
            "divergence_label": "No Clear Signal",
            "sentiment_score": 50,
            "whale_score": 50,
            "whale_net_flow_usd": 0,
            "active_whale_profiles": [],
            "dominant_whale_behavior": "unknown",
            "avg_reaction_latency": 0,
            "shadow_insight": "",
            "signal_strength": "weak",
            "is_golden_shadow": False,
        }
        
        try:
            # 1. Get latest sentiment from behavioral_sentiment or aihub_sentiment
            sentiment_query = text("""
                SELECT 
                    sentiment_score,
                    emotional_tone,
                    expected_crowd_action
                FROM behavioral_sentiment
                WHERE coin_id = :coin_id
                ORDER BY analyzed_at DESC
                LIMIT 1
            """)
            
            with self.db.engine.connect() as conn:
                row = conn.execute(sentiment_query, {"coin_id": coin_id}).fetchone()
                
                if row:
                    result["sentiment_score"] = row[0] or 50
                    result["emotional_tone"] = row[1] or "Neutral"
                    result["crowd_action"] = row[2] or "Hold"
                else:
                    # Fallback to aihub_sentiment
                    fallback_query = text("""
                        SELECT sentiment_score * 100
                        FROM aihub_sentiment s
                        JOIN aihub_coins c ON UPPER(c.symbol) = UPPER(s.symbol)
                        WHERE c.coin_id = :coin_id
                        LIMIT 1
                    """)
                    fb_row = conn.execute(fallback_query, {"coin_id": coin_id}).fetchone()
                    if fb_row:
                        result["sentiment_score"] = int(fb_row[0] or 50)
            
            # 2. Get whale net flow from onchain_signals
            whale_query = text("""
                SELECT 
                    whale_net_flow_usd,
                    whale_signal,
                    bullish_probability
                FROM onchain_signals
                WHERE coin_id = :coin_id
                ORDER BY updated_at DESC
                LIMIT 1
            """)
            
            with self.db.engine.connect() as conn:
                row = conn.execute(whale_query, {"coin_id": coin_id}).fetchone()
                
                if row:
                    result["whale_net_flow_usd"] = float(row[0] or 0)
                    result["whale_signal"] = row[1] or "NEUTRAL"
                    result["whale_score"] = int(row[2] or 50)
            
            # 3. Determine divergence type
            sentiment = result["sentiment_score"]
            whale_flow = result["whale_net_flow_usd"]
            
            # Shadow Accumulation: Fear + Whale Outflow (buying from exchanges)
            if sentiment < 40 and whale_flow < -50000:  # Negative = outflow = accumulation
                result["divergence_type"] = "shadow_accumulation"
                result["divergence_label"] = "Shadow Accumulation"
                result["intent_score"] = min(100, 60 + abs(40 - sentiment) + abs(whale_flow) / 100000)
                result["signal_strength"] = "strong" if result["intent_score"] > 75 else "moderate"
                result["is_golden_shadow"] = result["intent_score"] > 80
            
            # Bull Trap: Greed + Whale Inflow (selling to exchanges)
            elif sentiment > 70 and whale_flow > 50000:  # Positive = inflow = distribution
                result["divergence_type"] = "bull_trap"
                result["divergence_label"] = "Bull Trap Warning"
                result["intent_score"] = min(100, 60 + (sentiment - 70) + whale_flow / 100000)
                result["signal_strength"] = "strong" if result["intent_score"] > 75 else "moderate"
                result["is_golden_shadow"] = result["intent_score"] > 80
            
            # Confirmation: Both aligned
            elif (sentiment > 60 and whale_flow < -30000) or (sentiment < 40 and whale_flow > 30000):
                result["divergence_type"] = "confirmation"
                result["divergence_label"] = "Trend Confirmation"
                result["intent_score"] = 50 + abs(sentiment - 50) / 2
                result["signal_strength"] = "moderate"
            
            else:
                result["divergence_type"] = "neutral"
                result["divergence_label"] = "No Clear Signal"
                result["intent_score"] = 50
                result["signal_strength"] = "weak"
            
            # 4. Get active whale profiles
            profile_query = text("""
                SELECT 
                    behavior_label,
                    behavior_confidence,
                    success_rate,
                    COUNT(*) as count
                FROM whale_behavioral_profiles
                WHERE last_active > NOW() - INTERVAL '24 hours'
                GROUP BY behavior_label, behavior_confidence, success_rate
                ORDER BY count DESC
                LIMIT 5
            """)
            
            try:
                with self.db.engine.connect() as conn:
                    rows = conn.execute(profile_query).fetchall()
                    if rows:
                        result["active_whale_profiles"] = [
                            {"behavior": r[0], "confidence": r[1], "success_rate": r[2], "count": r[3]}
                            for r in rows
                        ]
                        result["dominant_whale_behavior"] = rows[0][0] if rows else "unknown"
            except Exception:
                pass
            
            # 5. Generate AI Shadow Insight
            if include_ai_insight and result["divergence_type"] != "neutral":
                try:
                    from app.services.gemini import get_gemini_service
                    gemini = get_gemini_service()
                    
                    insight = await gemini.analyze_behavioral_intent({
                        "coin_id": coin_id,
                        "sentiment_score": result["sentiment_score"],
                        "whale_net_flow_usd": result["whale_net_flow_usd"],
                        "divergence_type": result["divergence_type"],
                        "intent_score": result["intent_score"],
                        "dominant_whale_behavior": result["dominant_whale_behavior"],
                    })
                    
                    if insight:
                        result["shadow_insight"] = insight.get("shadow_insight", "")
                        
                except Exception as e:
                    logger.warning(f"Failed to generate shadow insight: {e}")
            
            # 6. Save to intent_divergence_logs
            await self._save_intent_divergence_log(coin_id, result)
            
        except Exception as e:
            logger.error(f"Failed to calculate intent divergence v2: {e}")
        
        return result
    
    async def _save_intent_divergence_log(
        self,
        coin_id: str,
        divergence_data: Dict[str, Any],
    ) -> bool:
        """Save intent divergence to logs table"""
        from sqlalchemy import text
        
        query = text("""
            INSERT INTO intent_divergence_logs (
                coin_id, sentiment_score, whale_score, divergence_type,
                intent_score, whale_net_flow_usd, dominant_whale_behavior,
                shadow_insight
            ) VALUES (
                :coin_id, :sentiment_score, :whale_score, :divergence_type,
                :intent_score, :whale_net_flow_usd, :dominant_whale_behavior,
                :shadow_insight
            )
        """)
        
        try:
            with self.db.engine.begin() as conn:
                conn.execute(query, {
                    "coin_id": coin_id,
                    "sentiment_score": divergence_data.get("sentiment_score", 50),
                    "whale_score": divergence_data.get("whale_score", 50),
                    "divergence_type": divergence_data.get("divergence_type", "neutral"),
                    "intent_score": divergence_data.get("intent_score", 50),
                    "whale_net_flow_usd": divergence_data.get("whale_net_flow_usd", 0),
                    "dominant_whale_behavior": divergence_data.get("dominant_whale_behavior", "unknown"),
                    "shadow_insight": divergence_data.get("shadow_insight", ""),
                })
            return True
        except Exception as e:
            logger.warning(f"Failed to save intent divergence log: {e}")
            return False
    
    def get_radar_data(
        self,
        sentiment_score: int,
        whale_score: int,
        exchange_pressure: float,
        network_growth: float,
        intent_score: int,
    ) -> Dict[str, Any]:
        """
        Prepare data for ShadowRadar component (5 axes).
        
        Args:
            sentiment_score: Crowd sentiment 0-100
            whale_score: Whale momentum 0-100
            exchange_pressure: Net exchange flow normalized 0-100
            network_growth: DAU change % normalized 0-100
            intent_score: Intent divergence strength 0-100
            
        Returns:
            Radar chart data for ApexCharts
        """
        return {
            "labels": [
                "Crowd Sentiment",
                "Whale Momentum",
                "Exchange Pressure",
                "Network Growth",
                "Intent Strength",
            ],
            "values": [
                max(0, min(100, sentiment_score)),
                max(0, min(100, whale_score)),
                max(0, min(100, exchange_pressure)),
                max(0, min(100, network_growth)),
                max(0, min(100, intent_score)),
            ],
            "colors": {
                "fill": "rgba(0, 212, 255, 0.3)",
                "stroke": "#00d4ff",
            }
        }


