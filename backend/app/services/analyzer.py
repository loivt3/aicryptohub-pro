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
                # Use composite ASI for better accuracy (multi-timeframe + sentiment + onchain)
                analysis = await self.calculate_composite_asi(coin_id)
                
                if analysis:
                    # Save to database - use composite_asi as the main score
                    saved = self.db.save_ai_sentiment(
                        coin_id=coin_id,
                        asi_score=analysis["composite_asi"],
                        signal=analysis["signal"],
                        reasoning=analysis["reasoning"],
                        indicators=analysis.get("components", {}),
                        provider="python_ta_composite",
                    )
                    
                    if saved:
                        results["success_count"] += 1
                        results["results"].append({
                            "coin_id": coin_id,
                            "asi_score": analysis["composite_asi"],
                            "signal": analysis["signal"],
                            "components": analysis.get("components"),
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
    
    async def _fetch_ohlcv_for_coin(
        self, 
        coin_id: str, 
        timeframe: str = "1h"
    ) -> bool:
        """
        On-demand OHLCV fetch from multiple exchanges with fallback.
        Fetches from 5 sources in PARALLEL: Binance, OKX, Bybit, KuCoin, Gate.io
        
        Args:
            coin_id: CoinGecko coin ID (e.g., 'bitcoin')
            timeframe: '1m', '1h', '4h', '1d', '1w', '1M'
            
        Returns:
            True if fetched and saved successfully from any source
        """
        import asyncio
        import httpx
        
        # Timeframe config - mapping to each exchange format
        TIMEFRAME_CONFIG = {
            "1h": {"binance": "1h", "okx": "1H", "bybit": "60", "kucoin": "1hour", "gate": "1h", "db_code": 1, "limit": 100},
            "4h": {"binance": "4h", "okx": "4H", "bybit": "240", "kucoin": "4hour", "gate": "4h", "db_code": 4, "limit": 100},
            "1d": {"binance": "1d", "okx": "1D", "bybit": "D", "kucoin": "1day", "gate": "1d", "db_code": 24, "limit": 100},
            "1w": {"binance": "1w", "okx": "1W", "bybit": "W", "kucoin": "1week", "gate": "1w", "db_code": 168, "limit": 52},
            "1M": {"binance": "1M", "okx": "1M", "bybit": "M", "kucoin": "1month", "gate": "1M", "db_code": 720, "limit": 60},
        }
        
        config = TIMEFRAME_CONFIG.get(timeframe, TIMEFRAME_CONFIG["1h"])
        
        # Get symbol from coin_id
        symbol = self.db._get_symbol_for_coin(coin_id)
        if not symbol:
            logger.warning(f"No symbol found for {coin_id}, cannot fetch OHLCV")
            return False
        
        symbol = symbol.upper()
        
        async def fetch_binance():
            """Binance klines"""
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://api.binance.com/api/v3/klines",
                    params={"symbol": f"{symbol}USDT", "interval": config["binance"], "limit": config["limit"]}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return [{"timestamp": k[0], "open": float(k[1]), "high": float(k[2]), 
                             "low": float(k[3]), "close": float(k[4]), "volume": float(k[5]),
                             "source": "binance"} for k in data]
            return None
        
        async def fetch_okx():
            """OKX klines"""
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://www.okx.com/api/v5/market/candles",
                    params={"instId": f"{symbol}-USDT", "bar": config["okx"], "limit": str(config["limit"])}
                )
                if resp.status_code == 200:
                    result = resp.json()
                    data = result.get("data", [])
                    return [{"timestamp": int(k[0]), "open": float(k[1]), "high": float(k[2]),
                             "low": float(k[3]), "close": float(k[4]), "volume": float(k[5]),
                             "source": "okx"} for k in data]
            return None
        
        async def fetch_bybit():
            """Bybit klines"""
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://api.bybit.com/v5/market/kline",
                    params={"category": "spot", "symbol": f"{symbol}USDT", "interval": config["bybit"], "limit": config["limit"]}
                )
                if resp.status_code == 200:
                    result = resp.json()
                    data = result.get("result", {}).get("list", [])
                    return [{"timestamp": int(k[0]), "open": float(k[1]), "high": float(k[2]),
                             "low": float(k[3]), "close": float(k[4]), "volume": float(k[5]),
                             "source": "bybit"} for k in data]
            return None
        
        async def fetch_kucoin():
            """KuCoin klines"""
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://api.kucoin.com/api/v1/market/candles",
                    params={"symbol": f"{symbol}-USDT", "type": config["kucoin"]}
                )
                if resp.status_code == 200:
                    result = resp.json()
                    data = result.get("data", [])
                    # KuCoin format: [timestamp, open, close, high, low, volume, turnover]
                    return [{"timestamp": int(k[0]) * 1000, "open": float(k[1]), "high": float(k[3]),
                             "low": float(k[4]), "close": float(k[2]), "volume": float(k[5]),
                             "source": "kucoin"} for k in data[-config["limit"]:]]
            return None
        
        async def fetch_gate():
            """Gate.io klines"""
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"https://api.gateio.ws/api/v4/spot/candlesticks",
                    params={"currency_pair": f"{symbol}_USDT", "interval": config["gate"], "limit": config["limit"]}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    # Gate format: [timestamp, volume, close, high, low, open]
                    return [{"timestamp": int(k[0]) * 1000, "open": float(k[5]), "high": float(k[3]),
                             "low": float(k[4]), "close": float(k[2]), "volume": float(k[1]),
                             "source": "gate"} for k in data]
            return None
        
        try:
            # Fetch from ALL 5 sources in PARALLEL
            results = await asyncio.gather(
                fetch_binance(),
                fetch_okx(),
                fetch_bybit(),
                fetch_kucoin(),
                fetch_gate(),
                return_exceptions=True,
            )
            
            # Find first successful result with enough data
            klines = None
            source_used = None
            sources = ["binance", "okx", "bybit", "kucoin", "gate"]
            
            for i, result in enumerate(results):
                if isinstance(result, list) and len(result) >= 30:
                    klines = result
                    source_used = sources[i]
                    break
                elif isinstance(result, Exception):
                    logger.debug(f"{sources[i]} OHLCV failed for {symbol}: {result}")
            
            if not klines:
                logger.warning(f"All sources returned insufficient {timeframe} data for {symbol}")
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
                        "timeframe": config["db_code"],
                        "open_time": datetime.fromtimestamp(kline["timestamp"] / 1000),
                        "open": kline["open"],
                        "high": kline["high"],
                        "low": kline["low"],
                        "close": kline["close"],
                        "volume": kline["volume"],
                        "trades_count": 0,
                    })
            
            logger.info(f"On-demand fetched {len(klines)} {timeframe} candles for {symbol} from {source_used}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to on-demand fetch OHLCV for {coin_id} ({timeframe}): {e}")
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
    
    # ==================== MULTI-HORIZON ASI ====================
    
    async def calculate_asi_for_timeframe(
        self,
        coin_id: str,
        timeframe: str = "1h",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Calculate ASI score for a specific timeframe.
        
        Args:
            coin_id: Coin identifier
            timeframe: '1m', '1h', '4h', '1d', '1w'
            limit: Number of candles to fetch
            
        Returns:
            Dict with asi_score, signal, indicators for that timeframe
        """
        # Fetch OHLCV for specific timeframe
        ohlcv_data = self.db.get_ohlcv_data(coin_id, timeframe=timeframe, limit=limit)
        
        # Skip on-demand fetch to avoid blocking - return defaults instead
        # Background scheduler will populate data over time
        if len(ohlcv_data) < 30:
            logger.debug(f"Insufficient {timeframe} data for {coin_id} ({len(ohlcv_data)} candles). Returning defaults.")
            return {
                "timeframe": timeframe,
                "asi_score": 50,  # Neutral default
                "signal": "HOLD",
                "data_available": False,
                "data_status": "Awaiting data",
                "candles_found": len(ohlcv_data),
                "candles_required": 30,
            }
        
        # Create DataFrame
        df = pd.DataFrame(ohlcv_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.drop_duplicates(subset=["timestamp"], keep="last")
        df = df.set_index("timestamp").sort_index()
        df = df.rename(columns={
            "open": "Open", "high": "High", "low": "Low",
            "close": "Close", "volume": "Volume",
        })
        
        # Calculate base indicators
        indicators = self.calculate_indicators(df)
        
        # Add enhanced indicators (OBV, VWAP, CCI)
        from app.services.indicators import calculate_all_enhanced_indicators
        enhanced = calculate_all_enhanced_indicators(df)
        indicators.update(enhanced)
        
        # Calculate ASI with enhanced scoring
        asi_score, signal = self.calculate_enhanced_asi_score(indicators)
        
        # === NEW: Candlestick Pattern Recognition ===
        pattern_result = {}
        pattern_adjustment = 0
        try:
            from app.services.pattern_recognizer import get_pattern_recognizer
            pattern_recognizer = get_pattern_recognizer()
            
            # Need lowercase columns for pattern recognizer
            df_lower = df.rename(columns={
                "Open": "open", "High": "high", "Low": "low",
                "Close": "close", "Volume": "volume",
            })
            
            pattern_result = pattern_recognizer.recognize_patterns(df_lower)
            
            if pattern_result.get("pattern"):
                # Get ASI adjustment from pattern
                pattern_adjustment = pattern_recognizer.get_pattern_score_adjustment(pattern_result)
                
                # Apply pattern adjustment to ASI score
                asi_score = max(0, min(100, asi_score + pattern_adjustment))
                
                # Update signal if pattern is strong
                if pattern_adjustment >= 10:
                    signal = "STRONG_BUY" if asi_score >= 65 else "BUY"
                elif pattern_adjustment <= -10:
                    signal = "STRONG_SELL" if asi_score <= 35 else "SELL"
                
                logger.debug(f"{coin_id} [{timeframe}]: Pattern {pattern_result['pattern']} ({pattern_result['reliability']}) -> ASI adjustment {pattern_adjustment:+d}")
                
                # Save pattern to database for backtesting
                try:
                    current_price = df['Close'].iloc[-1] if len(df) > 0 else None
                    candle_time = df.index[-1] if len(df) > 0 else None
                    
                    self.db.save_pattern(
                        coin_id=coin_id,
                        timeframe=timeframe,
                        pattern=pattern_result['pattern'],
                        direction=pattern_result['direction'],
                        reliability=pattern_result['reliability'],
                        priority=pattern_recognizer.PATTERN_PRIORITY.get(pattern_result['pattern'], 5),
                        volume_ratio=pattern_result.get('volume_ratio'),
                        price_at_detection=float(current_price) if current_price else None,
                        candle_timestamp=candle_time,
                    )
                except Exception as save_err:
                    logger.debug(f"Failed to save pattern to DB: {save_err}")
        except Exception as e:
            logger.debug(f"Pattern recognition failed for {coin_id}: {e}")
        
        return {
            "timeframe": timeframe,
            "asi_score": asi_score,
            "signal": signal,
            "indicators": indicators,
            "data_available": True,
            # Pattern info
            "pattern": pattern_result.get("pattern"),
            "pattern_direction": pattern_result.get("direction"),
            "pattern_reliability": pattern_result.get("reliability"),
            "pattern_adjustment": pattern_adjustment,
        }

    
    def calculate_enhanced_asi_score(self, indicators: Dict[str, Any]) -> tuple[int, str]:
        """
        Enhanced ASI calculation including OBV, VWAP, CCI.
        
        Scoring breakdown (100 points total):
        - RSI: 20 points
        - MACD: 15 points
        - Bollinger: 15 points
        - Stochastic: 10 points
        - ADX: 10 points
        - EMA Trend: 10 points
        - OBV: 10 points (enhanced)
        - VWAP: 5 points (enhanced)
        - CCI: 5 points (enhanced)
        """
        score = 50  # Start neutral
        
        # RSI contribution (20 points)
        rsi = indicators.get("rsi_14", 50)
        if rsi < 30:
            score += 12  # Oversold = bullish
        elif rsi < 40:
            score += 6
        elif rsi > 70:
            score -= 12  # Overbought = bearish
        elif rsi > 60:
            score -= 6
        
        # MACD contribution (15 points)
        macd_hist = indicators.get("macd_histogram", 0)
        macd_line = indicators.get("macd_line", 0)
        macd_signal = indicators.get("macd_signal", 0)
        
        if macd_hist > 0:
            score += min(8, abs(macd_hist) * 80)
        else:
            score -= min(8, abs(macd_hist) * 80)
        
        if macd_line > macd_signal:
            score += 4
        else:
            score -= 4
        
        # Bollinger Bands contribution (15 points)
        bb_pct = indicators.get("bb_percent_b", 0.5)
        if bb_pct < 0.2:
            score += 8
        elif bb_pct > 0.8:
            score -= 8
        
        # Stochastic contribution (10 points)
        stoch_k = indicators.get("stoch_k", 50)
        stoch_d = indicators.get("stoch_d", 50)
        
        if stoch_k < 20:
            score += 5
        elif stoch_k > 80:
            score -= 5
        
        if stoch_k > stoch_d:
            score += 2
        else:
            score -= 2
        
        # ADX contribution (10 points)
        adx = indicators.get("adx", 0)
        price_change = indicators.get("price_change_24h", 0)
        
        if adx > 25:
            if price_change > 0:
                score += 6
            else:
                score -= 6
        
        # EMA Trend (10 points)
        ema_9 = indicators.get("ema_9", 0)
        ema_21 = indicators.get("ema_21", 0)
        ema_50 = indicators.get("ema_50", 0)
        
        if ema_9 > ema_21 > ema_50:
            score += 6  # Strong uptrend
        elif ema_9 < ema_21 < ema_50:
            score -= 6  # Strong downtrend
        
        # Enhanced: OBV contribution (10 points) - maps 0-10 to +/-5
        obv_score = indicators.get("obv_score", 5)
        score += (obv_score - 5)  # -5 to +5
        
        # Enhanced: VWAP contribution (5 points) - maps 0-5 to +/-2.5
        vwap_score = indicators.get("vwap_score", 2.5)
        score += (vwap_score - 2.5)  # -2.5 to +2.5
        
        # Enhanced: CCI contribution (5 points) - maps 0-5 to +/-2.5
        cci_score = indicators.get("cci_score", 2.5)
        score += (cci_score - 2.5)  # -2.5 to +2.5
        
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
    
    async def calculate_multi_horizon_asi(
        self, 
        coin_id: str,
        use_cache: bool = True,
        cache_max_age: int = 5
    ) -> Dict[str, Any]:
        """
        Calculate ASI for all horizons: Short, Medium, Long-term.
        
        Horizons:
        - Short: 1h (Scalp/Day trade)
        - Medium: 4h * 0.4 + 1d * 0.6 (Swing trade)
        - Long: 1w * 0.4 + 1M * 0.6 (Position/HODL) - 1M = 1 month
        
        Args:
            coin_id: Coin identifier
            use_cache: Whether to check cache first (default True)
            cache_max_age: Maximum cache age in minutes (default 5)
        
        Returns:
            Dict with asi_short, asi_medium, asi_long, asi_combined
        """
        import asyncio
        
        # Check cache first (if enabled)
        if use_cache:
            cached = self.db.get_multi_horizon_cache([coin_id], cache_max_age)
            if coin_id in cached and cached[coin_id]:
                logger.debug(f"Using cached multi-horizon for {coin_id}")
                return cached[coin_id]
        
        
        # Fetch ASI for ALL timeframes in PARALLEL (much faster!)
        tf_results = await asyncio.gather(
            self.calculate_asi_for_timeframe(coin_id, "1h", 100),
            self.calculate_asi_for_timeframe(coin_id, "4h", 100),
            self.calculate_asi_for_timeframe(coin_id, "1d", 100),
            self.calculate_asi_for_timeframe(coin_id, "1w", 100),
            self.calculate_asi_for_timeframe(coin_id, "1M", 60),  # 1M = 1 month
            return_exceptions=True,  # Don't fail if one timeframe fails
        )
        
        # Unpack results (handle exceptions gracefully)
        def safe_result(r, default_tf):
            if isinstance(r, Exception):
                logger.warning(f"Timeframe {default_tf} failed: {r}")
                return {"data_available": False, "timeframe": default_tf}
            return r
        
        tf_1h = safe_result(tf_results[0], "1h")
        tf_4h = safe_result(tf_results[1], "4h")
        tf_1d = safe_result(tf_results[2], "1d")
        tf_1w = safe_result(tf_results[3], "1w")
        tf_1M = safe_result(tf_results[4], "1M")
        
        # Calculate horizon scores
        # Short-term: 1h only
        asi_short = None
        signal_short = None
        short_status = "Insufficient data"
        
        if tf_1h["data_available"]:
            asi_short = tf_1h["asi_score"]
            short_status = "OK"
        
        # Medium-term: 4h + 1d
        asi_medium = None
        signal_medium = None
        medium_status = "Insufficient data"
        
        if tf_1d["data_available"]:
            if tf_4h["data_available"]:
                asi_medium = tf_4h["asi_score"] * 0.4 + tf_1d["asi_score"] * 0.6
            else:
                asi_medium = tf_1d["asi_score"]
            medium_status = "OK"
        
        # Long-term: 1w + 1M (month)
        asi_long = None
        signal_long = None
        long_status = "Insufficient data"
        
        if tf_1w["data_available"]:
            if tf_1M["data_available"]:
                asi_long = tf_1w["asi_score"] * 0.4 + tf_1M["asi_score"] * 0.6
            else:
                asi_long = tf_1w["asi_score"]
            long_status = "OK"
        
        # Get on-chain score
        onchain_score = await self._get_onchain_score(coin_id)
        
        # Calculate combined ASI - only if we have at least short-term data
        asi_combined = None
        combined_status = "Insufficient data"
        
        # Count available horizons for averaging
        available_scores = [s for s in [asi_short, asi_medium, asi_long] if s is not None]
        
        if available_scores:
            technical_avg = sum(available_scores) / len(available_scores)
            
            # Combined = Technical (60%) + OnChain (40%)
            if onchain_score["available"]:
                asi_combined = technical_avg * 0.6 + onchain_score["score"] * 0.4
            else:
                asi_combined = technical_avg
            combined_status = "OK"
        
        # Determine signals - handle None
        def get_signal(score):
            if score is None:
                return None
            if score >= 75: return "STRONG_BUY"
            elif score >= 60: return "BUY"
            elif score >= 40: return "NEUTRAL"
            elif score >= 25: return "SELL"
            else: return "STRONG_SELL"
        
        result = {
            "coin_id": coin_id,
            "asi_short": round(asi_short) if asi_short is not None else None,
            "asi_medium": round(asi_medium) if asi_medium is not None else None,
            "asi_long": round(asi_long) if asi_long is not None else None,
            "asi_combined": round(asi_combined) if asi_combined is not None else None,
            "signal_short": get_signal(asi_short),
            "signal_medium": get_signal(asi_medium),
            "signal_long": get_signal(asi_long),
            "signal_combined": get_signal(asi_combined),
            "data_status": {
                "short": short_status,
                "medium": medium_status,
                "long": long_status,
                "combined": combined_status,
            },
            "onchain_score": onchain_score,
            "timeframes": {
                "1h": tf_1h,
                "4h": tf_4h,
                "1d": tf_1d,
                "1w": tf_1w,
                "1M": tf_1M,
            },
            "analyzed_at": datetime.now().isoformat(),
        }
        
        # Save to cache for future requests
        self.db.save_multi_horizon_cache(coin_id, result)
        
        return result
    
    async def _get_onchain_score(self, coin_id: str) -> Dict[str, Any]:
        """
        Get on-chain score from existing on-chain signals.
        
        Components:
        - Whale score: 40%
        - Network score: 30%
        - Holder score: 30%
        """
        onchain_data = self.db.get_onchain_signals(coin_id)
        
        if not onchain_data:
            return {
                "available": False, 
                "score": None,
                "data_status": "Insufficient data",
            }
        
        # Get individual scores
        whale_prob = onchain_data.get("bullish_probability", 50) or 50
        
        # Map whale_signal to score
        whale_signal = onchain_data.get("whale_signal", "NEUTRAL")
        whale_score = 50
        if whale_signal == "BULLISH":
            whale_score = 70
        elif whale_signal == "STRONG_BULLISH":
            whale_score = 85
        elif whale_signal == "BEARISH":
            whale_score = 30
        elif whale_signal == "STRONG_BEARISH":
            whale_score = 15
        
        # Network signal
        network_signal = onchain_data.get("network_signal", "NEUTRAL")
        network_score = 50
        if network_signal == "BULLISH":
            network_score = 70
        elif network_signal == "BEARISH":
            network_score = 30
        
        # DAU change
        dau_change = onchain_data.get("dau_change_1d_pct", 0) or 0
        dau_score = 50 + min(25, max(-25, dau_change))  # ±25 from neutral
        
        # Calculate combined on-chain score
        combined = whale_score * 0.4 + network_score * 0.3 + dau_score * 0.3
        
        return {
            "available": True,
            "score": round(combined),
            "whale_score": whale_score,
            "network_score": network_score,
            "dau_score": round(dau_score),
            "whale_signal": whale_signal,
            "network_signal": network_signal,
        }
    
    async def calculate_composite_asi(
        self,
        coin_id: str,
        use_multi_timeframe: bool = True,
    ) -> Dict[str, Any]:
        """
        Calculate Composite ASI combining multiple data sources:
        
        Components:
        - Multi-timeframe Technical Analysis: 60%
        - Behavioral Sentiment (news/social): 25%
        - On-chain Signals: 15%
        
        This provides a more robust sentiment score than single-source analysis.
        
        Args:
            coin_id: Coin identifier
            use_multi_timeframe: Use multi-horizon analysis vs simple 1h
            
        Returns:
            Dict with composite_asi, tech_asi, sentiment_asi, onchain_asi, and components
        """
        # 1. Get Multi-Timeframe Technical ASI
        tech_result = None
        tech_asi = 50  # Default neutral
        
        if use_multi_timeframe:
            try:
                tech_result = await self.calculate_multi_horizon_asi(coin_id)
                # Use combined score or fallback to short-term
                tech_asi = tech_result.get("asi_combined") or tech_result.get("asi_short") or 50
            except Exception as e:
                logger.warning(f"Multi-horizon failed for {coin_id}: {e}")
                # Fallback to simple analysis
                simple = await self.analyze_single_coin(coin_id)
                tech_asi = simple["asi_score"] if simple else 50
        else:
            simple = await self.analyze_single_coin(coin_id)
            tech_asi = simple["asi_score"] if simple else 50
        
        # 2. Get Behavioral Sentiment (from AI news analysis)
        sentiment_asi = 50  # Default neutral
        sentiment_available = False
        sentiment_tone = None
        crowd_action = None
        
        behavior = self.db.get_latest_behavioral_sentiment(coin_id)
        if behavior:
            # sentiment_score is 0-100 in behavioral table
            raw_score = behavior.get("sentiment_score", 50)
            # Ensure it's in 0-100 range
            sentiment_asi = int(raw_score) if raw_score else 50
            sentiment_available = True
            sentiment_tone = behavior.get("emotional_tone", "neutral")
            crowd_action = behavior.get("expected_crowd_action", "hold")
        
        # 3. On-chain signals (already integrated in multi_horizon, but get separately for weighting)
        onchain_result = await self._get_onchain_score(coin_id)
        onchain_asi = onchain_result.get("score") or 50
        onchain_available = onchain_result.get("available", False)
        
        # Calculate Composite ASI
        # Weights: Technical 60%, Sentiment 25%, On-chain 15%
        if sentiment_available and onchain_available:
            composite_asi = (
                tech_asi * 0.60 +
                sentiment_asi * 0.25 +
                onchain_asi * 0.15
            )
        elif sentiment_available:
            # No on-chain, use: Technical 70%, Sentiment 30%
            composite_asi = tech_asi * 0.70 + sentiment_asi * 0.30
        elif onchain_available:
            # No sentiment, use: Technical 80%, On-chain 20%
            composite_asi = tech_asi * 0.80 + onchain_asi * 0.20
        else:
            # Technical only
            composite_asi = tech_asi
        
        # Clamp to 0-100
        composite_asi = max(0, min(100, round(composite_asi)))
        
        # Determine signal
        if composite_asi >= 75:
            signal = "STRONG_BUY"
        elif composite_asi >= 60:
            signal = "BUY"
        elif composite_asi >= 40:
            signal = "NEUTRAL"
        elif composite_asi >= 25:
            signal = "SELL"
        else:
            signal = "STRONG_SELL"
        
        # Generate enhanced reasoning
        reasons = []
        if tech_result:
            reasons.append(f"Multi-timeframe tech score: {tech_asi}")
        if sentiment_available:
            reasons.append(f"News sentiment: {sentiment_tone or 'neutral'} ({crowd_action or 'hold'})")
        if onchain_available:
            whale_signal = onchain_result.get("whale_signal", "neutral")
            reasons.append(f"On-chain: whale {whale_signal}")
        
        reasoning = f"Composite ASI: {composite_asi}/100 ({signal}). " + ". ".join(reasons) + "."
        
        return {
            "coin_id": coin_id,
            "composite_asi": composite_asi,
            "signal": signal,
            "reasoning": reasoning,
            "components": {
                "tech_asi": round(tech_asi),
                "tech_weight": 0.60 if (sentiment_available and onchain_available) else (0.70 if sentiment_available else 0.80),
                "sentiment_asi": sentiment_asi if sentiment_available else None,
                "sentiment_available": sentiment_available,
                "sentiment_tone": sentiment_tone,
                "crowd_action": crowd_action,
                "onchain_asi": onchain_asi if onchain_available else None,
                "onchain_available": onchain_available,
            },
            "multi_horizon": tech_result,
            "analyzed_at": datetime.now().isoformat(),
        }


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
        Enhanced Intent Divergence with real data from existing modules.
        
        Uses:
        - AI Sentiment from aihub_sentiment table (existing module)
        - On-chain signals from get_onchain_signals (existing module)
        - Fear & Greed Index from Alternative.me API as fallback
        
        Scenarios:
        - Shadow Accumulation: Sentiment < 40, Whale Outflow (bullish)
        - Bull Trap: Sentiment > 70, Whale Inflow (bearish)
        - Confirmation: Whale and crowd aligned
        - Neutral: No clear signal
        """
        from app.services.shadow_data import get_shadow_service
        
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
        
        shadow_svc = get_shadow_service()
        
        try:
            # 1. Get sentiment from existing AI sentiment module
            sentiment_data = self.db.get_coin_sentiment(coin_id)
            
            if sentiment_data:
                # Use ASI score as sentiment (0-100)
                asi_score = sentiment_data.get("asi_score", 50)
                result["sentiment_score"] = int(asi_score) if asi_score else 50
                result["ai_signal"] = sentiment_data.get("signal", "NEUTRAL")
                logger.info(f"[Shadow] Got AI sentiment for {coin_id}: ASI={result['sentiment_score']}")
            else:
                # Fallback to Fear & Greed Index
                fng = await shadow_svc.fetch_fear_greed_index()
                result["sentiment_score"] = fng.get("value", 50)
                result["fear_greed_classification"] = fng.get("classification", "Neutral")
                logger.info(f"[Shadow] Using Fear & Greed fallback: {result['sentiment_score']}")
            
            # 2. Get on-chain signals from existing module
            onchain_data = self.db.get_onchain_signals(coin_id)
            
            if onchain_data:
                result["whale_net_flow_usd"] = float(onchain_data.get("whale_net_flow_usd") or 0)
                result["whale_signal"] = onchain_data.get("whale_signal") or "NEUTRAL"
                result["whale_score"] = int(onchain_data.get("bullish_probability") or 50)
                
                # Add whale activity details
                result["whale_tx_count"] = onchain_data.get("whale_tx_count_24h", 0)
                result["network_signal"] = onchain_data.get("network_signal", "NEUTRAL")
                logger.info(f"[Shadow] Got on-chain for {coin_id}: flow={result['whale_net_flow_usd']}, signal={result['whale_signal']}")
            else:
                # Try to get market data for whale approximation
                market_data = self.db.get_coin_by_id(coin_id)
                if market_data:
                    volume_24h = market_data.get("volume_24h", 0)
                    avg_volume = volume_24h * 0.8  # Approximate 7d average
                    price_change = market_data.get("price_change_24h", 0)
                    market_cap = market_data.get("market_cap", 0)
                    
                    # Calculate whale metrics from volume
                    whale_metrics = shadow_svc.calculate_whale_metrics(
                        volume_24h=volume_24h,
                        avg_volume_7d=avg_volume,
                        price_change_24h=price_change,
                        market_cap=market_cap,
                    )
                    
                    result["whale_score"] = whale_metrics["whale_score"]
                    result["whale_net_flow_usd"] = whale_metrics["whale_net_flow_usd"]
                    result["dominant_whale_behavior"] = whale_metrics["dominant_whale_behavior"]
                    result["active_whale_profiles"] = whale_metrics["active_whale_profiles"]
                    logger.info(f"[Shadow] Calculated whale metrics from volume for {coin_id}")
            
            # 3. Calculate intent divergence
            sentiment = result["sentiment_score"]
            whale_flow = result["whale_net_flow_usd"]
            whale_score = result["whale_score"]
            
            # Get price change for direction
            market_data = self.db.get_coin_by_id(coin_id)
            price_change = market_data.get("change_24h", 0) if market_data else 0
            
            # Use ShadowDataService for intent calculation
            intent_result = shadow_svc.calculate_intent_score(
                fear_greed=sentiment,
                whale_score=whale_score,
                price_change_24h=price_change,
            )
            
            result.update(intent_result)
            
            # 4. Build whale profiles if not already set
            if not result["active_whale_profiles"] and whale_score > 55:
                result["active_whale_profiles"] = [{
                    "behavior": result.get("dominant_whale_behavior", "mixed"),
                    "confidence": 0.6 + (whale_score - 50) * 0.008,
                    "success_rate": 0.65,
                    "count": max(1, int((whale_score - 50) / 10)),
                }]
            
            # 5. Generate AI Shadow Insight if divergence detected
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
            
            # Generate default insight if none
            if not result["shadow_insight"]:
                result["shadow_insight"] = self._generate_default_insight(result)
            
            # 6. Save to intent_divergence_logs
            await self._save_intent_divergence_log(coin_id, result)
            
        except Exception as e:
            logger.error(f"Failed to calculate intent divergence v2: {e}")
        
        return result
    
    def _generate_default_insight(self, data: Dict[str, Any]) -> str:
        """Generate default shadow insight based on divergence type"""
        div_type = data.get("divergence_type", "neutral")
        sentiment = data.get("sentiment_score", 50)
        whale_score = data.get("whale_score", 50)
        
        if div_type == "shadow_accumulation":
            return f"Whales are accumulating while crowd sentiment is fearful ({sentiment}/100). This divergence suggests smart money sees value others are missing."
        elif div_type == "bull_trap":
            return f"Warning: High crowd greed ({sentiment}/100) but whale activity suggests distribution. Consider taking profits or reducing exposure."
        elif div_type == "confirmation":
            return f"Whale behavior aligns with crowd sentiment. Current trend likely to continue."
        else:
            return f"No significant divergence detected. Sentiment: {sentiment}/100, Whale activity: {whale_score}/100."
    
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


