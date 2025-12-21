"""
Market Discovery Engine - Advanced Edition
Computes and caches market metrics for fast discovery API.

Features:
- Momentum Score (Multi-factor scoring)
- Trend Strength Detection (Consecutive gains/losses)
- Relative Strength vs BTC/Market
- Anomaly Detection (Z-score based)
- Smart Money Signals (ASI + Volume + Whale integration)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from sqlalchemy import text

from app.services.database import DatabaseService

logger = logging.getLogger(__name__)


class DiscoveryEngine:
    """
    Advanced Engine for computing market discovery metrics.
    
    Scoring System:
    - Momentum Score: 0-100 based on price action + volume confirmation
    - Trend Score: Strength and consistency of trend
    - Relative Strength: Performance vs BTC and market
    - Discovery Score: Combined score for "hidden gems"
    """
    
    # Minimum volume to include in results (filter scam coins)
    MIN_VOLUME_24H = 100_000  # $100k
    
    # Pump/Dump detection thresholds
    PUMP_THRESHOLD_1H = 3.0    # +3% in 1h
    DUMP_THRESHOLD_1H = -3.0   # -3% in 1h
    VOLUME_SPIKE_MULTIPLIER = 2.0  # Volume > 2x average
    
    # Momentum scoring weights
    MOMENTUM_WEIGHTS = {
        'price_action': 0.35,
        'volume_confirmation': 0.25,
        'trend_consistency': 0.20,
        'asi_alignment': 0.20,
    }
    
    # Trend detection
    STRONG_TREND_THRESHOLD = 2.0
    WEAK_TREND_THRESHOLD = 0.5
    
    def __init__(self, db: DatabaseService):
        """Initialize discovery engine."""
        self.db = db
        self._btc_change_24h = 0.0
    
    async def update_snapshot(self) -> Dict[str, Any]:
        """Main method to update market_discovery_snapshot table."""
        start_time = datetime.now()
        
        try:
            # Step 1: Get current market data
            market_data = self._get_market_data()
            
            if market_data.empty:
                logger.warning("No market data found for discovery")
                return {"success": False, "error": "No market data"}
            
            # Step 2: Calculate historical price changes
            df = await self._calculate_changes(market_data)
            
            # Step 3: Calculate volume metrics
            df = await self._calculate_volume_metrics(df)
            
            # Step 4: Calculate advanced metrics
            df = self._calculate_momentum_score(df)
            df = self._calculate_trend_score(df)
            df = self._calculate_relative_strength(df)
            df = self._detect_anomalies(df)
            
            # Step 5: Detect candlestick patterns
            df = await self._detect_candlestick_patterns(df)
            
            # Step 6: Detect RSI divergence
            df = await self._detect_rsi_divergence(df)
            
            # Step 7: Calculate confirmation scores (NEW - for accuracy)
            df = await self._calculate_confirmation_score(df)
            
            # Step 8: Detect sudden pumps/dumps
            df = self._detect_pumps_dumps_advanced(df)
            
            # Step 9: Merge with sentiment data
            df = self._merge_sentiment(df)
            
            # Step 10: Calculate discovery score (includes pattern + confirmation bonus)
            df = self._calculate_discovery_score(df)
            
            # Step 10: Upsert to snapshot table
            upsert_count = self._upsert_snapshot(df)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            high_momentum = int((df['momentum_score'] >= 70).sum()) if 'momentum_score' in df.columns else 0
            strong_trends = int((df['trend_score'].abs() >= 3).sum()) if 'trend_score' in df.columns else 0
            anomalies = int((df['is_anomaly'] == True).sum()) if 'is_anomaly' in df.columns else 0
            bullish_patterns = int((df['pattern_direction'] == 'BULLISH').sum()) if 'pattern_direction' in df.columns else 0
            bearish_patterns = int((df['pattern_direction'] == 'BEARISH').sum()) if 'pattern_direction' in df.columns else 0
            divergences = int((df['has_divergence'] == True).sum()) if 'has_divergence' in df.columns else 0
            
            stats = {
                "success": True,
                "coins_processed": len(df),
                "coins_upserted": upsert_count,
                "pumps_detected": int(df['is_sudden_pump'].sum()) if 'is_sudden_pump' in df.columns else 0,
                "dumps_detected": int(df['is_sudden_dump'].sum()) if 'is_sudden_dump' in df.columns else 0,
                "high_momentum_coins": high_momentum,
                "strong_trends": strong_trends,
                "anomalies_detected": anomalies,
                "bullish_patterns": bullish_patterns,
                "bearish_patterns": bearish_patterns,
                "divergences_detected": divergences,
                "elapsed_seconds": round(elapsed, 2),
                "updated_at": datetime.now().isoformat(),
            }
            
            logger.info(f"Discovery snapshot updated: {stats}")
            return stats
            
        except Exception as e:
            import traceback
            logger.error(f"Discovery update failed: {e}\n{traceback.format_exc()}")
            return {"success": False, "error": str(e)}

    
    def _get_market_data(self) -> pd.DataFrame:
        """Get current market data from aihub_coins table."""
        query = text("""
            SELECT coin_id, symbol, name, image_url as image, price, 
                   price_change_1h as change_1h, change_24h, price_change_7d as change_7d,
                   volume_24h, market_cap, rank as market_cap_rank
            FROM aihub_coins
            WHERE price IS NOT NULL AND price > 0
              AND coin_id IS NOT NULL
            ORDER BY market_cap DESC NULLS LAST
            LIMIT 1000
        """)
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query)
                rows = result.fetchall()
                
                if not rows:
                    logger.warning("No coins found in aihub_coins table")
                    return pd.DataFrame()
                
                columns = ['coin_id', 'symbol', 'name', 'image', 'price',
                          'change_1h', 'change_24h', 'change_7d',
                          'volume_24h', 'market_cap', 'market_cap_rank']
                
                df = pd.DataFrame(rows, columns=columns)
                
                # Force convert all numeric columns from Decimal to float
                numeric_cols = ['price', 'change_1h', 'change_24h', 'change_7d', 
                               'volume_24h', 'market_cap', 'market_cap_rank']
                for col in numeric_cols:
                    df[col] = df[col].apply(lambda x: float(x) if x is not None else 0.0)
                
                btc_row = df[df['coin_id'] == 'bitcoin']
                if not btc_row.empty:
                    self._btc_change_24h = float(btc_row['change_24h'].values[0] or 0.0)
                
                return df

                
        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            return pd.DataFrame()
    
    async def _calculate_changes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate % changes from OHLCV data."""
        now = datetime.now()
        
        # Fixed query using correct OHLCV schema:
        # - symbol (not coin_id)
        # - open_time (not timestamp)
        # - timeframe = 1 for 1h (not interval = '1h')
        query = text("""
            WITH latest_prices AS (
                SELECT DISTINCT ON (o.symbol) 
                    c.coin_id, o.close as current_close
                FROM aihub_ohlcv o
                JOIN aihub_coins c ON UPPER(o.symbol) = UPPER(c.symbol)
                WHERE o.timeframe = 1
                  AND o.open_time > :recent_time
                ORDER BY o.symbol, o.open_time DESC
            ),
            prices_4h AS (
                SELECT DISTINCT ON (o.symbol)
                    c.coin_id, o.close as close_4h
                FROM aihub_ohlcv o
                JOIN aihub_coins c ON UPPER(o.symbol) = UPPER(c.symbol)
                WHERE o.timeframe = 1
                  AND o.open_time <= :time_4h
                  AND o.open_time > :time_4h - INTERVAL '2 hours'
                ORDER BY o.symbol, o.open_time DESC
            )
            SELECT 
                lp.coin_id,
                CASE WHEN p4.close_4h > 0 THEN 
                    ((lp.current_close - p4.close_4h) / p4.close_4h * 100)
                ELSE NULL END as calc_change_4h
            FROM latest_prices lp
            LEFT JOIN prices_4h p4 ON lp.coin_id = p4.coin_id
        """)
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query, {
                    "recent_time": now - timedelta(hours=2),
                    "time_4h": now - timedelta(hours=4),
                })
                rows = result.fetchall()
                
                # Ensure change_24h is float for arithmetic
                if 'change_24h' in df.columns:
                    df['change_24h'] = pd.to_numeric(df['change_24h'], errors='coerce').astype(float)
                
                if rows:
                    ohlcv_df = pd.DataFrame(rows, columns=['coin_id', 'calc_change_4h'])
                    ohlcv_df['calc_change_4h'] = pd.to_numeric(ohlcv_df['calc_change_4h'], errors='coerce').astype(float)
                    df = df.merge(ohlcv_df, on='coin_id', how='left')
                    df['change_4h'] = df['calc_change_4h'].fillna(df['change_24h'] * 4.0 / 24.0)
                else:
                    df['change_4h'] = df['change_24h'] * 4.0 / 24.0
                    
        except Exception as e:
            logger.warning(f"OHLCV change calculation failed: {e}")
            if 'change_24h' in df.columns:
                df['change_24h'] = pd.to_numeric(df['change_24h'], errors='coerce').astype(float)
            df['change_4h'] = df['change_24h'] * 4.0 / 24.0
        
        return df


    
    async def _calculate_volume_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate advanced volume metrics."""
        # Fixed query using correct OHLCV schema:
        query = text("""
            WITH volume_stats AS (
                SELECT 
                    c.coin_id,
                    SUM(CASE WHEN o.open_time > NOW() - INTERVAL '1 hour' THEN o.volume ELSE 0 END) as volume_1h,
                    AVG(o.volume) as avg_volume_1h
                FROM aihub_ohlcv o
                JOIN aihub_coins c ON UPPER(o.symbol) = UPPER(c.symbol)
                WHERE o.timeframe = 1
                  AND o.open_time > NOW() - INTERVAL '24 hours'
                GROUP BY c.coin_id
            )
            SELECT 
                coin_id,
                volume_1h,
                avg_volume_1h,
                CASE WHEN avg_volume_1h > 0 THEN volume_1h / avg_volume_1h ELSE 1 END as volume_ratio
            FROM volume_stats
        """)
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query)
                rows = result.fetchall()
                
                if rows:
                    vol_df = pd.DataFrame(rows, columns=['coin_id', 'volume_1h', 'avg_volume_1h', 'volume_ratio'])
                    vol_df['volume_change_pct'] = (vol_df['volume_ratio'] - 1) * 100
                    df = df.merge(vol_df, on='coin_id', how='left')
                else:
                    df['volume_1h'] = None
                    df['avg_volume_1h'] = None
                    df['volume_change_pct'] = 0
                    df['volume_ratio'] = 1
                    
        except Exception as e:
            logger.warning(f"Volume metrics calculation failed: {e}")
            df['volume_1h'] = None
            df['volume_change_pct'] = 0
            df['volume_ratio'] = 1
        
        return df
    
    def _calculate_momentum_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Momentum Score (0-100)."""
        # Ensure all numeric columns are float to avoid Decimal issues
        for col in ['change_1h', 'change_4h', 'change_24h', 'volume_ratio']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: float(x) if x is not None else 0.0)
        
        # Price action score
        df['price_action_raw'] = (
            df['change_1h'].fillna(0) * 0.5 +
            df['change_4h'].fillna(0) * 0.3 +
            df['change_24h'].fillna(0) * 0.2
        )
        df['price_action_score'] = 50 + np.clip(df['price_action_raw'] * 5, -50, 50)
        
        # Volume score
        volume_ratio = df['volume_ratio'].fillna(1)

        df['volume_score'] = np.clip(50 + (volume_ratio - 1) * 25, 0, 100)
        
        # Trend consistency
        df['trend_consistency_score'] = 50.0
        bullish = (df['change_1h'].fillna(0) > 0) & (df['change_4h'].fillna(0) > 0) & (df['change_24h'].fillna(0) > 0)
        bearish = (df['change_1h'].fillna(0) < 0) & (df['change_4h'].fillna(0) < 0) & (df['change_24h'].fillna(0) < 0)
        df.loc[bullish, 'trend_consistency_score'] = 85
        df.loc[bearish, 'trend_consistency_score'] = 15
        
        # ASI placeholder
        df['asi_alignment_score'] = 50
        
        # Final score
        df['momentum_score'] = (
            df['price_action_score'] * 0.35 +
            df['volume_score'] * 0.25 +
            df['trend_consistency_score'] * 0.20 +
            df['asi_alignment_score'] * 0.20
        ).round(0).astype(int)
        df['momentum_score'] = np.clip(df['momentum_score'], 0, 100)
        
        return df
    
    def _calculate_trend_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Trend Score (-5 to +5)."""
        # Ensure numeric columns are float to avoid Decimal issues
        for col in ['change_1h', 'change_4h', 'change_24h']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: float(x) if x is not None else 0.0)
        
        df['trend_1h'] = np.where(df['change_1h'].abs() > 2, np.sign(df['change_1h']) * 2, np.sign(df['change_1h']))
        df['trend_4h'] = np.where(df['change_4h'].abs() > 4, np.sign(df['change_4h']) * 1.5, np.sign(df['change_4h']) * 0.75)
        df['trend_24h'] = np.where(df['change_24h'].abs() > 8, np.sign(df['change_24h']) * 1.5, np.sign(df['change_24h']) * 0.75)

        
        df['trend_score'] = np.clip(df['trend_1h'] + df['trend_4h'] + df['trend_24h'], -5, 5).round(1)
        
        df['trend_label'] = np.select(
            [df['trend_score'] >= 4, df['trend_score'] >= 2, df['trend_score'] <= -4, df['trend_score'] <= -2],
            ['STRONG_UP', 'UP', 'STRONG_DOWN', 'DOWN'],
            default='NEUTRAL'
        )
        
        return df
    
    def _calculate_relative_strength(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Relative Strength vs BTC and Market."""
        btc_change = self._btc_change_24h or 0
        
        df['rs_vs_btc'] = (df['change_24h'].fillna(0) - btc_change).round(2)
        
        top_100 = df[df['market_cap_rank'] <= 100]
        market_avg = top_100['change_24h'].mean() if not top_100.empty else df['change_24h'].mean()
        
        df['rs_vs_market'] = (df['change_24h'].fillna(0) - market_avg).round(2)
        df['rs_score'] = np.clip(50 + (df['rs_vs_btc'] + df['rs_vs_market']) / 2 * 5, 0, 100).round(0).astype(int)
        df['is_outperformer'] = (df['rs_vs_btc'] > 0) & (df['rs_vs_market'] > 0)
        
        return df
    
    def _detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect statistical anomalies using Z-score."""
        price_mean = df['change_24h'].mean()
        price_std = df['change_24h'].std()
        
        df['price_zscore'] = (df['change_24h'] - price_mean) / price_std if price_std > 0 else 0
        df['is_anomaly'] = (df['price_zscore'].abs() > 2.5).fillna(False)
        df['anomaly_type'] = None
        df.loc[df['price_zscore'] > 2.5, 'anomaly_type'] = 'PRICE_SPIKE'
        df.loc[df['price_zscore'] < -2.5, 'anomaly_type'] = 'PRICE_CRASH'
        
        return df
    
    async def _detect_candlestick_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect candlestick reversal patterns from OHLCV data.
        
        Patterns detected:
        - Bullish Engulfing, Hammer, Morning Star, Piercing Line
        - Bearish Engulfing, Shooting Star, Evening Star, Dark Cloud
        - Doji (indecision)
        """
        # Initialize pattern columns
        df['pattern_name'] = None
        df['pattern_direction'] = None  # BULLISH, BEARISH, NEUTRAL
        df['pattern_reliability'] = None  # HIGH, MEDIUM, LOW
        df['pattern_score'] = 0  # Impact on discovery score
        
        # Try to get patterns from aihub_patterns table (cached)
        query = text("""
            SELECT DISTINCT ON (coin_id) coin_id, pattern, direction, reliability
            FROM aihub_patterns
            WHERE detected_at > NOW() - INTERVAL '2 hours'
            ORDER BY coin_id, detected_at DESC
        """)
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query)
                rows = result.fetchall()
                
                if rows:
                    pattern_df = pd.DataFrame(rows, columns=['coin_id', 'pattern_name', 'pattern_direction', 'pattern_reliability'])
                    
                    df = df.merge(pattern_df, on='coin_id', how='left', suffixes=('', '_db'))
                    df['pattern_name'] = df['pattern_name_db'].fillna(df['pattern_name'])
                    df['pattern_direction'] = df['pattern_direction_db'].fillna(df['pattern_direction'])
                    df['pattern_reliability'] = df['pattern_reliability_db'].fillna(df['pattern_reliability'])
                    df.drop(columns=[c for c in df.columns if c.endswith('_db')], errors='ignore', inplace=True)
                    
                    logger.debug(f"Merged {len(rows)} patterns from database")
                    
        except Exception as e:
            logger.debug(f"Pattern table query failed (table may not exist): {e}")
        
        # Fallback: Calculate patterns from OHLCV for coins without patterns
        no_pattern_coins = df[df['pattern_name'].isna()]['coin_id'].tolist()[:50]
        if no_pattern_coins:
            ohlcv_patterns = await self._calculate_patterns_from_ohlcv(no_pattern_coins)
            for pattern_data in ohlcv_patterns:
                idx = df[df['coin_id'] == pattern_data['coin_id']].index
                if len(idx) > 0:
                    df.loc[idx[0], 'pattern_name'] = pattern_data['pattern']
                    df.loc[idx[0], 'pattern_direction'] = pattern_data['direction']
                    df.loc[idx[0], 'pattern_reliability'] = pattern_data['reliability']
        
        # Calculate pattern score
        # Bullish patterns with HIGH reliability = +15, MEDIUM = +10, LOW = +5
        # Bearish patterns = -15, -10, -5
        df['pattern_score'] = np.where(
            df['pattern_direction'] == 'BULLISH',
            np.where(df['pattern_reliability'] == 'HIGH', 15, np.where(df['pattern_reliability'] == 'MEDIUM', 10, 5)),
            np.where(
                df['pattern_direction'] == 'BEARISH',
                np.where(df['pattern_reliability'] == 'HIGH', -15, np.where(df['pattern_reliability'] == 'MEDIUM', -10, -5)),
                0
            )
        )
        
        return df
    
    async def _calculate_patterns_from_ohlcv(self, coin_ids: List[str]) -> List[Dict]:
        """Calculate candlestick patterns from OHLCV data for specific coins."""
        patterns = []
        
        # Fixed query using correct OHLCV schema
        query = text("""
            SELECT c.coin_id, o.open, o.high, o.low, o.close, o.volume, o.open_time
            FROM aihub_ohlcv o
            JOIN aihub_coins c ON UPPER(o.symbol) = UPPER(c.symbol)
            WHERE o.timeframe = 1
              AND c.coin_id = ANY(:coin_ids)
              AND o.open_time > NOW() - INTERVAL '24 hours'
            ORDER BY c.coin_id, o.open_time DESC
        """)
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query, {"coin_ids": coin_ids})
                rows = result.fetchall()
                
                if not rows:
                    return patterns
                
                ohlcv_df = pd.DataFrame(rows, columns=['coin_id', 'open', 'high', 'low', 'close', 'volume', 'open_time'])

                
                for coin_id in coin_ids:
                    coin_data = ohlcv_df[ohlcv_df['coin_id'] == coin_id].sort_values('open_time', ascending=False)
                    
                    if len(coin_data) < 3:
                        continue
                    
                    # Get last 3 candles
                    c1 = coin_data.iloc[0]  # Most recent
                    c2 = coin_data.iloc[1]  # Previous
                    c3 = coin_data.iloc[2] if len(coin_data) >= 3 else None  # 2 candles ago
                    
                    # Calculate candle properties
                    body_1 = float(c1['close'] - c1['open'])
                    body_2 = float(c2['close'] - c2['open'])
                    range_1 = float(c1['high'] - c1['low'])
                    range_2 = float(c2['high'] - c2['low'])
                    
                    pattern = None
                    direction = None
                    reliability = "MEDIUM"
                    
                    # === BULLISH PATTERNS ===
                    
                    # Bullish Engulfing: Big green candle engulfs previous red
                    if body_1 > 0 and body_2 < 0 and abs(body_1) > abs(body_2) * 1.5:
                        pattern = "Bullish Engulfing"
                        direction = "BULLISH"
                        reliability = "HIGH"
                    
                    # Hammer: Small body at top, long lower wick (at bottom of trend)
                    elif range_1 > 0:
                        lower_wick_1 = float(min(c1['open'], c1['close']) - c1['low'])
                        upper_wick_1 = float(c1['high'] - max(c1['open'], c1['close']))
                        
                        if lower_wick_1 > abs(body_1) * 2 and upper_wick_1 < abs(body_1) * 0.5:
                            # Confirm downtrend before hammer
                            if body_2 < 0:
                                pattern = "Hammer"
                                direction = "BULLISH"
                                reliability = "MEDIUM"
                    
                    # Piercing Line: Red followed by green that closes above 50% of red
                    if not pattern and body_1 > 0 and body_2 < 0:
                        midpoint = float(c2['close']) + abs(body_2) / 2
                        if float(c1['close']) > midpoint and float(c1['open']) < float(c2['close']):
                            pattern = "Piercing Line"
                            direction = "BULLISH"
                            reliability = "MEDIUM"
                    
                    # === BEARISH PATTERNS ===
                    
                    # Bearish Engulfing: Big red candle engulfs previous green
                    if not pattern and body_1 < 0 and body_2 > 0 and abs(body_1) > abs(body_2) * 1.5:
                        pattern = "Bearish Engulfing"
                        direction = "BEARISH"
                        reliability = "HIGH"
                    
                    # Shooting Star: Small body at bottom, long upper wick (at top of trend)
                    elif not pattern and range_1 > 0:
                        lower_wick_1 = float(min(c1['open'], c1['close']) - c1['low'])
                        upper_wick_1 = float(c1['high'] - max(c1['open'], c1['close']))
                        
                        if upper_wick_1 > abs(body_1) * 2 and lower_wick_1 < abs(body_1) * 0.5:
                            if body_2 > 0:  # Confirm uptrend
                                pattern = "Shooting Star"
                                direction = "BEARISH"
                                reliability = "MEDIUM"
                    
                    # Dark Cloud Cover: Green followed by red that closes below 50%
                    if not pattern and body_1 < 0 and body_2 > 0:
                        midpoint = float(c2['open']) + body_2 / 2
                        if float(c1['close']) < midpoint and float(c1['open']) > float(c2['close']):
                            pattern = "Dark Cloud Cover"
                            direction = "BEARISH"
                            reliability = "MEDIUM"
                    
                    # === NEUTRAL ===
                    
                    # Doji: Very small body (indecision)
                    if not pattern and range_1 > 0 and abs(body_1) / range_1 < 0.1:
                        pattern = "Doji"
                        direction = "NEUTRAL"
                        reliability = "LOW"
                    
                    if pattern:
                        patterns.append({
                            "coin_id": coin_id,
                            "pattern": pattern,
                            "direction": direction,
                            "reliability": reliability,
                        })
                        
        except Exception as e:
            logger.warning(f"OHLCV pattern calculation failed: {e}")
        
        return patterns
    
    async def _detect_rsi_divergence(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect RSI divergence from OHLCV data.
        
        Bullish Divergence: Price makes lower low, RSI makes higher low
        Bearish Divergence: Price makes higher high, RSI makes lower high
        """
        # Initialize divergence columns
        df['has_divergence'] = False
        df['divergence_type'] = None  # BULLISH_DIV, BEARISH_DIV
        df['rsi_14'] = None
        df['divergence_score'] = 0
        
        # Fixed query using correct OHLCV schema
        query = text("""
            WITH price_data AS (
                SELECT 
                    c.coin_id,
                    o.close,
                    o.high,
                    o.low,
                    o.open_time,
                    LAG(o.close) OVER (PARTITION BY o.symbol ORDER BY o.open_time) as prev_close,
                    ROW_NUMBER() OVER (PARTITION BY o.symbol ORDER BY o.open_time DESC) as rn
                FROM aihub_ohlcv o
                JOIN aihub_coins c ON UPPER(o.symbol) = UPPER(c.symbol)
                WHERE o.timeframe = 1
                  AND o.open_time > NOW() - INTERVAL '48 hours'
            ),
            gains_losses AS (
                SELECT 
                    coin_id,
                    open_time,
                    close,
                    high,
                    low,
                    rn,
                    CASE WHEN close > prev_close THEN close - prev_close ELSE 0 END as gain,
                    CASE WHEN close < prev_close THEN prev_close - close ELSE 0 END as loss
                FROM price_data
                WHERE prev_close IS NOT NULL
            ),
            rsi_calc AS (
                SELECT 
                    coin_id,
                    open_time,
                    close,
                    high,
                    low,
                    rn,
                    AVG(gain) OVER (PARTITION BY coin_id ORDER BY open_time ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) as avg_gain,
                    AVG(loss) OVER (PARTITION BY coin_id ORDER BY open_time ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) as avg_loss
                FROM gains_losses
            )

            SELECT 
                coin_id,
                rn,
                close,
                high,
                low,
                CASE WHEN avg_loss = 0 THEN 100 
                     ELSE 100 - (100 / (1 + avg_gain / NULLIF(avg_loss, 0))) 
                END as rsi_14
            FROM rsi_calc
            WHERE rn <= 10  -- Last 10 hourly candles
            ORDER BY coin_id, rn
        """)
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query)
                rows = result.fetchall()
                
                if not rows:
                    return df
                
                rsi_df = pd.DataFrame(rows, columns=['coin_id', 'rn', 'close', 'high', 'low', 'rsi_14'])
                
                # For each coin, detect divergence
                for coin_id in rsi_df['coin_id'].unique():
                    coin_rsi = rsi_df[rsi_df['coin_id'] == coin_id].sort_values('rn')
                    
                    if len(coin_rsi) < 6:
                        continue
                    
                    # Get current (rn=1) and previous period (rn=4-6)
                    current = coin_rsi.iloc[0]
                    previous = coin_rsi.iloc[4:6].mean() if len(coin_rsi) >= 6 else None
                    
                    if previous is None:
                        continue
                    
                    idx = df[df['coin_id'] == coin_id].index
                    if len(idx) == 0:
                        continue
                    
                    # Store current RSI
                    df.loc[idx[0], 'rsi_14'] = round(float(current['rsi_14']), 1)
                    
                    # Detect Bullish Divergence: Lower low in price, higher low in RSI
                    if float(current['low']) < float(previous['low']) and float(current['rsi_14']) > float(previous['rsi_14']):
                        # Also check RSI is oversold (<40)
                        if float(current['rsi_14']) < 40:
                            df.loc[idx[0], 'has_divergence'] = True
                            df.loc[idx[0], 'divergence_type'] = 'BULLISH_DIV'
                            df.loc[idx[0], 'divergence_score'] = 15
                            
                    # Detect Bearish Divergence: Higher high in price, lower high in RSI
                    elif float(current['high']) > float(previous['high']) and float(current['rsi_14']) < float(previous['rsi_14']):
                        # Also check RSI is overbought (>60)
                        if float(current['rsi_14']) > 60:
                            df.loc[idx[0], 'has_divergence'] = True
                            df.loc[idx[0], 'divergence_type'] = 'BEARISH_DIV'
                            df.loc[idx[0], 'divergence_score'] = -15
                            
        except Exception as e:
            logger.warning(f"RSI divergence detection failed: {e}")
        
        return df
    
    async def _calculate_confirmation_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate multi-factor confirmation score for pattern accuracy.
        
        Confirmations (each adds points if met):
        1. Volume Confirmation: Volume > 1.5x average during pattern
        2. MA Trend Context: Pattern direction aligned with 20-MA trend
        3. RSI Extremes: RSI in oversold (<30) or overbought (>70) zone
        4. Support/Resistance: Pattern near key S/R level
        5. Multi-TF Alignment: Same direction on multiple timeframes
        """
        # Initialize confirmation columns
        df['volume_confirmed'] = False
        df['ma_confirmed'] = False
        df['rsi_extreme'] = False
        df['near_sr'] = False
        df['confirmation_count'] = 0
        df['confirmation_score'] = 0
        
        # 1. Volume Confirmation
        df['volume_confirmed'] = df['volume_ratio'].fillna(1) > 1.5
        
        # 2. RSI Extremes (from _detect_rsi_divergence we have rsi_14)
        rsi = df['rsi_14'].fillna(50)
        df['rsi_extreme'] = (rsi < 30) | (rsi > 70)
        
        # 3. MA Trend and S/R levels from OHLCV
        coin_ids = df['coin_id'].tolist()[:100]  # Limit for performance
        
        query = text("""
            WITH recent_prices AS (
                SELECT 
                    coin_id,
                    close,
                    high,
                    low,
                    timestamp,
                    AVG(close) OVER (PARTITION BY coin_id ORDER BY timestamp ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as ma_20,
                    MAX(high) OVER (PARTITION BY coin_id ORDER BY timestamp ROWS BETWEEN 23 PRECEDING AND CURRENT ROW) as resistance_24h,
                    MIN(low) OVER (PARTITION BY coin_id ORDER BY timestamp ROWS BETWEEN 23 PRECEDING AND CURRENT ROW) as support_24h,
                    ROW_NUMBER() OVER (PARTITION BY coin_id ORDER BY timestamp DESC) as rn
                FROM aihub_ohlcv
                WHERE interval = '1h'
                  AND timestamp > NOW() - INTERVAL '48 hours'
            )
            SELECT 
                coin_id,
                close as current_price,
                ma_20,
                resistance_24h,
                support_24h,
                CASE WHEN close > ma_20 THEN 'ABOVE' ELSE 'BELOW' END as price_vs_ma
            FROM recent_prices
            WHERE rn = 1
        """)
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query)
                rows = result.fetchall()
                
                if rows:
                    ma_df = pd.DataFrame(rows, columns=[
                        'coin_id', 'current_price', 'ma_20', 'resistance_24h', 'support_24h', 'price_vs_ma'
                    ])
                    
                    # Merge with main df
                    df = df.merge(ma_df, on='coin_id', how='left', suffixes=('', '_ma'))
                    
                    # MA Confirmation: Bullish pattern + price above MA, or Bearish pattern + price below MA
                    df['ma_confirmed'] = (
                        ((df['pattern_direction'] == 'BULLISH') & (df['price_vs_ma'] == 'ABOVE')) |
                        ((df['pattern_direction'] == 'BEARISH') & (df['price_vs_ma'] == 'BELOW')) |
                        ((df['divergence_type'] == 'BULLISH_DIV') & (df['price_vs_ma'] == 'ABOVE')) |
                        ((df['divergence_type'] == 'BEARISH_DIV') & (df['price_vs_ma'] == 'BELOW'))
                    ).fillna(False)
                    
                    # Near S/R level (within 2% of support or resistance)
                    price = df['price'].fillna(0)
                    support = df['support_24h'].fillna(0)
                    resistance = df['resistance_24h'].fillna(0)
                    
                    df['near_support'] = (price > 0) & (support > 0) & (abs(price - support) / support < 0.02)
                    df['near_resistance'] = (price > 0) & (resistance > 0) & (abs(price - resistance) / resistance < 0.02)
                    
                    # Bullish pattern near support = strong, Bearish near resistance = strong
                    df['near_sr'] = (
                        ((df['pattern_direction'] == 'BULLISH') & df['near_support']) |
                        ((df['pattern_direction'] == 'BEARISH') & df['near_resistance']) |
                        ((df['divergence_type'] == 'BULLISH_DIV') & df['near_support']) |
                        ((df['divergence_type'] == 'BEARISH_DIV') & df['near_resistance'])
                    ).fillna(False)
                    
                    # Cleanup merge columns
                    df.drop(columns=[c for c in df.columns if c.endswith('_ma')], errors='ignore', inplace=True)
                    
        except Exception as e:
            logger.warning(f"MA/SR calculation failed: {e}")
        
        # 4. Multi-timeframe alignment (already have this in trend consistency)
        df['mtf_aligned'] = df['trend_consistency_score'].fillna(50) >= 80
        
        # Count confirmations
        df['confirmation_count'] = (
            df['volume_confirmed'].astype(int) +
            df['ma_confirmed'].astype(int) +
            df['rsi_extreme'].astype(int) +
            df['near_sr'].astype(int) +
            df['mtf_aligned'].astype(int)
        )
        
        # 6. MACD Confirmation
        df = await self._calculate_macd_signals(df)
        
        # 7. Bollinger Bands Squeeze Detection
        df = await self._calculate_bollinger_signals(df)
        
        # Update confirmation count with new factors
        df['confirmation_count'] = (
            df['volume_confirmed'].astype(int) +
            df['ma_confirmed'].astype(int) +
            df['rsi_extreme'].astype(int) +
            df['near_sr'].astype(int) +
            df['mtf_aligned'].astype(int) +
            df['macd_confirmed'].fillna(False).astype(int) +
            df['bb_signal'].fillna(False).astype(int)
        )
        
        # Confirmation score: Extended bonus table (now 7 factors)
        # 0=0, 1=+2, 2=+4, 3=+7, 4=+10, 5=+14, 6=+18, 7=+22
        confirmation_bonuses = {0: 0, 1: 2, 2: 4, 3: 7, 4: 10, 5: 14, 6: 18, 7: 22}
        df['confirmation_score'] = df['confirmation_count'].map(
            lambda x: confirmation_bonuses.get(min(x, 7), 22)
        )
        
        # Upgrade pattern reliability based on confirmations
        # 4+ confirmations = HIGH, 2-3 = MEDIUM, 0-1 = LOW
        df['pattern_reliability_adj'] = np.where(
            df['confirmation_count'] >= 4,
            'HIGH',
            np.where(
                df['confirmation_count'] >= 2,
                df['pattern_reliability'],
                np.where(
                    df['pattern_reliability'].notna(),
                    'LOW',
                    None
                )
            )
        )
        
        # Recalculate pattern score with adjusted reliability
        df['pattern_score'] = np.where(
            df['pattern_direction'] == 'BULLISH',
            np.where(df['pattern_reliability_adj'] == 'HIGH', 15, 
                     np.where(df['pattern_reliability_adj'] == 'MEDIUM', 10, 5)),
            np.where(
                df['pattern_direction'] == 'BEARISH',
                np.where(df['pattern_reliability_adj'] == 'HIGH', -15, 
                         np.where(df['pattern_reliability_adj'] == 'MEDIUM', -10, -5)),
                0
            )
        )

        
        return df
    
    async def _calculate_macd_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MACD signals for confirmation.
        
        MACD = EMA(12) - EMA(26)
        Signal = EMA(9) of MACD
        Histogram = MACD - Signal
        
        Bullish: MACD crosses above Signal (histogram turns positive)
        Bearish: MACD crosses below Signal (histogram turns negative)
        """
        df['macd_confirmed'] = False
        df['macd_histogram'] = None
        df['macd_signal_type'] = None
        
        # Fixed query using correct OHLCV schema
        query = text("""
            WITH price_series AS (
                SELECT 
                    c.coin_id,
                    o.close,
                    o.open_time,
                    ROW_NUMBER() OVER (PARTITION BY o.symbol ORDER BY o.open_time DESC) as rn
                FROM aihub_ohlcv o
                JOIN aihub_coins c ON UPPER(o.symbol) = UPPER(c.symbol)
                WHERE o.timeframe = 1
                  AND o.open_time > NOW() - INTERVAL '48 hours'
            ),
            ema_calc AS (
                SELECT 
                    coin_id,
                    close,
                    rn,
                    AVG(close) OVER (PARTITION BY coin_id ORDER BY rn DESC ROWS BETWEEN CURRENT ROW AND 11 FOLLOWING) as ema_12,
                    AVG(close) OVER (PARTITION BY coin_id ORDER BY rn DESC ROWS BETWEEN CURRENT ROW AND 25 FOLLOWING) as ema_26
                FROM price_series
                WHERE rn <= 30
            ),
            macd_line AS (
                SELECT 
                    coin_id,
                    rn,
                    (ema_12 - ema_26) as macd,
                    LAG(ema_12 - ema_26) OVER (PARTITION BY coin_id ORDER BY rn DESC) as prev_macd
                FROM ema_calc
            )

            SELECT 
                coin_id,
                macd,
                prev_macd,
                AVG(macd) OVER (PARTITION BY coin_id ORDER BY rn DESC ROWS BETWEEN CURRENT ROW AND 8 FOLLOWING) as signal_line,
                CASE 
                    WHEN macd > prev_macd AND macd > 0 THEN 'BULLISH_CROSS'
                    WHEN macd < prev_macd AND macd < 0 THEN 'BEARISH_CROSS'
                    WHEN macd > 0 THEN 'BULLISH'
                    ELSE 'BEARISH'
                END as macd_signal
            FROM macd_line
            WHERE rn = 1
        """)
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query)
                rows = result.fetchall()
                
                if rows:
                    macd_df = pd.DataFrame(rows, columns=[
                        'coin_id', 'macd', 'prev_macd', 'signal_line', 'macd_signal'
                    ])
                    
                    macd_df['macd_histogram'] = macd_df['macd'] - macd_df['signal_line']
                    
                    df = df.merge(
                        macd_df[['coin_id', 'macd_histogram', 'macd_signal']], 
                        on='coin_id', 
                        how='left', 
                        suffixes=('', '_macd')
                    )
                    
                    df['macd_signal_type'] = df['macd_signal']
                    
                    # MACD confirms pattern if directions align
                    df['macd_confirmed'] = (
                        ((df['pattern_direction'] == 'BULLISH') & (df['macd_signal'].isin(['BULLISH', 'BULLISH_CROSS']))) |
                        ((df['pattern_direction'] == 'BEARISH') & (df['macd_signal'].isin(['BEARISH', 'BEARISH_CROSS']))) |
                        ((df['divergence_type'] == 'BULLISH_DIV') & (df['macd_signal'].isin(['BULLISH', 'BULLISH_CROSS']))) |
                        ((df['divergence_type'] == 'BEARISH_DIV') & (df['macd_signal'].isin(['BEARISH', 'BEARISH_CROSS'])))
                    ).fillna(False)
                    
                    df.drop(columns=['macd_signal'], errors='ignore', inplace=True)
                    
        except Exception as e:
            logger.warning(f"MACD calculation failed: {e}")
        
        return df
    
    async def _calculate_bollinger_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Bollinger Bands signals.
        
        BB Middle = SMA(20)
        BB Upper = SMA(20) + 2 * StdDev(20)
        BB Lower = SMA(20) - 2 * StdDev(20)
        
        Squeeze: Bands are narrow (low volatility, breakout imminent)
        Price at Lower + Bullish pattern = Strong buy
        Price at Upper + Bearish pattern = Strong sell
        """
        df['bb_signal'] = False
        df['bb_position'] = None  # UPPER, MIDDLE, LOWER
        df['bb_squeeze'] = False
        df['bb_width'] = None
        
        # Fixed query using correct OHLCV schema
        query = text("""
            WITH price_series AS (
                SELECT 
                    c.coin_id,
                    o.close,
                    o.high,
                    o.low,
                    o.open_time,
                    ROW_NUMBER() OVER (PARTITION BY o.symbol ORDER BY o.open_time DESC) as rn
                FROM aihub_ohlcv o
                JOIN aihub_coins c ON UPPER(o.symbol) = UPPER(c.symbol)
                WHERE o.timeframe = 1
                  AND o.open_time > NOW() - INTERVAL '48 hours'
            ),
            bb_calc AS (
                SELECT 
                    coin_id,
                    close,
                    AVG(close) OVER (PARTITION BY coin_id ORDER BY rn DESC ROWS BETWEEN CURRENT ROW AND 19 FOLLOWING) as sma_20,
                    STDDEV(close) OVER (PARTITION BY coin_id ORDER BY rn DESC ROWS BETWEEN CURRENT ROW AND 19 FOLLOWING) as stddev_20
                FROM price_series
                WHERE rn <= 25
            )

            SELECT 
                coin_id,
                close as current_price,
                sma_20,
                sma_20 + 2 * stddev_20 as bb_upper,
                sma_20 - 2 * stddev_20 as bb_lower,
                CASE WHEN sma_20 > 0 THEN (4 * stddev_20) / sma_20 * 100 ELSE 0 END as bb_width_pct,
                CASE 
                    WHEN close >= sma_20 + 1.5 * stddev_20 THEN 'UPPER'
                    WHEN close <= sma_20 - 1.5 * stddev_20 THEN 'LOWER'
                    ELSE 'MIDDLE'
                END as bb_position
            FROM bb_calc
            WHERE sma_20 IS NOT NULL
            ORDER BY coin_id
            LIMIT 1000
        """)
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query)
                rows = result.fetchall()
                
                if rows:
                    bb_df = pd.DataFrame(rows, columns=[
                        'coin_id', 'current_price', 'sma_20', 'bb_upper', 'bb_lower', 'bb_width_pct', 'bb_position'
                    ])
                    
                    # BB Squeeze: Width < 4% (low volatility)
                    bb_df['bb_squeeze'] = bb_df['bb_width_pct'] < 4
                    
                    df = df.merge(
                        bb_df[['coin_id', 'bb_position', 'bb_squeeze', 'bb_width_pct']], 
                        on='coin_id', 
                        how='left',
                        suffixes=('', '_bb')
                    )
                    
                    df['bb_width'] = df['bb_width_pct']
                    
                    # BB confirms pattern:
                    # - Bullish pattern + price at LOWER band = strong buy signal
                    # - Bearish pattern + price at UPPER band = strong sell signal
                    # - BB Squeeze + any pattern = potential breakout
                    df['bb_signal'] = (
                        ((df['pattern_direction'] == 'BULLISH') & (df['bb_position'] == 'LOWER')) |
                        ((df['pattern_direction'] == 'BEARISH') & (df['bb_position'] == 'UPPER')) |
                        ((df['divergence_type'] == 'BULLISH_DIV') & (df['bb_position'] == 'LOWER')) |
                        ((df['divergence_type'] == 'BEARISH_DIV') & (df['bb_position'] == 'UPPER')) |
                        (df['bb_squeeze'].fillna(False) & df['pattern_direction'].notna())
                    ).fillna(False)
                    
                    df.drop(columns=['bb_width_pct'], errors='ignore', inplace=True)
                    
        except Exception as e:
            logger.warning(f"Bollinger Bands calculation failed: {e}")
        
        return df

    def _detect_pumps_dumps_advanced(self, df: pd.DataFrame) -> pd.DataFrame:



        """Advanced pump/dump detection."""
        is_pump = (
            (df['change_1h'] > self.PUMP_THRESHOLD_1H) &
            (df['volume_ratio'].fillna(1) > self.VOLUME_SPIKE_MULTIPLIER) &
            (df['volume_24h'] > self.MIN_VOLUME_24H)
        )
        df['is_sudden_pump'] = (is_pump | ((df['is_anomaly']) & (df['price_zscore'] > 2))).fillna(False)
        
        is_dump = (
            (df['change_1h'] < self.DUMP_THRESHOLD_1H) &
            (df['volume_ratio'].fillna(1) > self.VOLUME_SPIKE_MULTIPLIER) &
            (df['volume_24h'] > self.MIN_VOLUME_24H)
        )
        df['is_sudden_dump'] = (is_dump | ((df['is_anomaly']) & (df['price_zscore'] < -2))).fillna(False)
        
        return df
    
    def _merge_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Merge with sentiment/ASI data."""
        query = text("""
            SELECT symbol, 
                   CAST(sentiment_score * 100 AS INT) as asi_score,
                   ai_signal as signal
            FROM aihub_sentiment
        """)
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query)
                rows = result.fetchall()
                
                if rows:
                    sent_df = pd.DataFrame(rows, columns=['symbol', 'asi_score', 'signal'])
                    sent_df['symbol'] = sent_df['symbol'].str.upper()
                    df['symbol_upper'] = df['symbol'].str.upper()
                    
                    df = df.merge(sent_df, left_on='symbol_upper', right_on='symbol', 
                                 how='left', suffixes=('', '_sent'))
                    df.drop(columns=['symbol_upper', 'symbol_sent'], errors='ignore', inplace=True)
                else:
                    df['asi_score'] = None
                    df['signal'] = None
                    
        except Exception as e:
            logger.warning(f"Sentiment merge failed: {e}")
            df['asi_score'] = None
            df['signal'] = None
        
        return df
    
    def _calculate_discovery_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Discovery Score for hidden gem detection.
        
        Includes:
        - Momentum Score (40%)
        - Relative Strength Score (30%)
        - Pattern Bonus (candlestick patterns)
        - Divergence Bonus (RSI divergence)
        - Confirmation Bonus (multi-factor validation)
        - Trend/Outperformer bonuses
        """
        # Base score from momentum and RS
        base_score = df['momentum_score'] * 0.4 + df['rs_score'] * 0.3
        
        # Pattern bonus (from candlestick patterns: -15 to +15)
        pattern_bonus = df['pattern_score'].fillna(0)
        
        # Divergence bonus (from RSI divergence: -15 to +15)
        divergence_bonus = df['divergence_score'].fillna(0)
        
        # Confirmation bonus (0 to +20 based on confirmation count)
        confirmation_bonus = df['confirmation_score'].fillna(0)
        
        # Other bonuses
        rank_bonus = np.where(df['market_cap_rank'] > 100, 10, 0)  # Small cap bonus
        outperformer_bonus = np.where(df['is_outperformer'], 10, 0)
        trend_bonus = np.where(df['trend_score'] > 2, 10, 0)
        
        # Combined score
        df['discovery_score'] = (
            base_score + 
            pattern_bonus + 
            divergence_bonus + 
            confirmation_bonus +
            rank_bonus + 
            outperformer_bonus + 
            trend_bonus
        ).round(0).astype(int)
        
        df['discovery_score'] = np.clip(df['discovery_score'], 0, 100)
        
        # Create signal strength label based on technical signals + confirmations
        high_confirmation = df['confirmation_count'].fillna(0) >= 3
        
        df['signal_strength'] = np.select(
            [
                # VERY_STRONG: Pattern + Divergence + 3+ confirmations
                (df['pattern_direction'] == 'BULLISH') & (df['divergence_type'] == 'BULLISH_DIV') & high_confirmation,
                (df['pattern_direction'] == 'BEARISH') & (df['divergence_type'] == 'BEARISH_DIV') & high_confirmation,
                # STRONG: Pattern + Divergence (without high confirmation)
                (df['pattern_direction'] == 'BULLISH') & (df['divergence_type'] == 'BULLISH_DIV'),
                (df['pattern_direction'] == 'BEARISH') & (df['divergence_type'] == 'BEARISH_DIV'),
                # CONFIRMED: Pattern or Divergence + 3+ confirmations
                ((df['pattern_direction'] == 'BULLISH') | (df['divergence_type'] == 'BULLISH_DIV')) & high_confirmation,
                ((df['pattern_direction'] == 'BEARISH') | (df['divergence_type'] == 'BEARISH_DIV')) & high_confirmation,
                # MODERATE: Pattern or Divergence only
                (df['pattern_direction'] == 'BULLISH') | (df['divergence_type'] == 'BULLISH_DIV'),
                (df['pattern_direction'] == 'BEARISH') | (df['divergence_type'] == 'BEARISH_DIV'),
            ],
            ['VERY_STRONG_BULL', 'VERY_STRONG_BEAR', 'STRONG_BULLISH', 'STRONG_BEARISH', 
             'CONFIRMED_BULL', 'CONFIRMED_BEAR', 'BULLISH', 'BEARISH'],
            default=None
        )
        
        return df


    
    def _upsert_snapshot(self, df: pd.DataFrame) -> int:
        """Upsert data into market_discovery_snapshot table."""
        if df.empty:
            return 0
        
        df = df.replace({np.nan: None})
        
        query = text("""
            INSERT INTO market_discovery_snapshot (
                coin_id, symbol, name, image, price,
                change_1h, change_4h, change_24h, change_7d,
                volume_24h, volume_1h, avg_volume_1h, volume_change_pct,
                market_cap, market_cap_rank,
                is_sudden_pump, is_sudden_dump,
                asi_score, signal,
                momentum_score, trend_score, trend_label,
                rs_vs_btc, rs_vs_market, rs_score, is_outperformer, is_anomaly, anomaly_type,
                pattern_name, pattern_direction, pattern_reliability, pattern_score,
                rsi_14, has_divergence, divergence_type, divergence_score,
                macd_histogram, macd_signal_type, macd_confirmed,
                bb_position, bb_squeeze, bb_width, bb_signal,
                volume_confirmed, ma_confirmed, rsi_extreme, near_sr, mtf_aligned,
                confirmation_count, confirmation_score, discovery_score, signal_strength,
                updated_at
            ) VALUES (
                :coin_id, :symbol, :name, :image, :price,
                :change_1h, :change_4h, :change_24h, :change_7d,
                :volume_24h, :volume_1h, :avg_volume_1h, :volume_change_pct,
                :market_cap, :market_cap_rank,
                :is_sudden_pump, :is_sudden_dump,
                :asi_score, :signal,
                :momentum_score, :trend_score, :trend_label,
                :rs_vs_btc, :rs_vs_market, :rs_score, :is_outperformer, :is_anomaly, :anomaly_type,
                :pattern_name, :pattern_direction, :pattern_reliability, :pattern_score,
                :rsi_14, :has_divergence, :divergence_type, :divergence_score,
                :macd_histogram, :macd_signal_type, :macd_confirmed,
                :bb_position, :bb_squeeze, :bb_width, :bb_signal,
                :volume_confirmed, :ma_confirmed, :rsi_extreme, :near_sr, :mtf_aligned,
                :confirmation_count, :confirmation_score, :discovery_score, :signal_strength,
                NOW()
            )
            ON CONFLICT (coin_id) DO UPDATE SET
                symbol = EXCLUDED.symbol, name = EXCLUDED.name, image = EXCLUDED.image,
                price = EXCLUDED.price, change_1h = EXCLUDED.change_1h, change_4h = EXCLUDED.change_4h,
                change_24h = EXCLUDED.change_24h, change_7d = EXCLUDED.change_7d,
                volume_24h = EXCLUDED.volume_24h, volume_1h = EXCLUDED.volume_1h,
                avg_volume_1h = EXCLUDED.avg_volume_1h, volume_change_pct = EXCLUDED.volume_change_pct,
                market_cap = EXCLUDED.market_cap, market_cap_rank = EXCLUDED.market_cap_rank,
                is_sudden_pump = EXCLUDED.is_sudden_pump, is_sudden_dump = EXCLUDED.is_sudden_dump,
                asi_score = EXCLUDED.asi_score, signal = EXCLUDED.signal,
                momentum_score = EXCLUDED.momentum_score, trend_score = EXCLUDED.trend_score, 
                trend_label = EXCLUDED.trend_label,
                rs_vs_btc = EXCLUDED.rs_vs_btc, rs_vs_market = EXCLUDED.rs_vs_market, 
                rs_score = EXCLUDED.rs_score, is_outperformer = EXCLUDED.is_outperformer,
                is_anomaly = EXCLUDED.is_anomaly, anomaly_type = EXCLUDED.anomaly_type,
                pattern_name = EXCLUDED.pattern_name, pattern_direction = EXCLUDED.pattern_direction,
                pattern_reliability = EXCLUDED.pattern_reliability, pattern_score = EXCLUDED.pattern_score,
                rsi_14 = EXCLUDED.rsi_14, has_divergence = EXCLUDED.has_divergence,
                divergence_type = EXCLUDED.divergence_type, divergence_score = EXCLUDED.divergence_score,
                macd_histogram = EXCLUDED.macd_histogram, macd_signal_type = EXCLUDED.macd_signal_type,
                macd_confirmed = EXCLUDED.macd_confirmed,
                bb_position = EXCLUDED.bb_position, bb_squeeze = EXCLUDED.bb_squeeze,
                bb_width = EXCLUDED.bb_width, bb_signal = EXCLUDED.bb_signal,
                volume_confirmed = EXCLUDED.volume_confirmed, ma_confirmed = EXCLUDED.ma_confirmed,
                rsi_extreme = EXCLUDED.rsi_extreme, near_sr = EXCLUDED.near_sr, mtf_aligned = EXCLUDED.mtf_aligned,
                confirmation_count = EXCLUDED.confirmation_count, confirmation_score = EXCLUDED.confirmation_score,
                discovery_score = EXCLUDED.discovery_score, signal_strength = EXCLUDED.signal_strength,
                updated_at = NOW()
        """)

        
        count = 0
        try:
            with self.db.engine.begin() as conn:
                for _, row in df.iterrows():
                    try:
                        # Truncate strings to fit column sizes
                        coin_id = str(row['coin_id'])[:50] if row.get('coin_id') else None
                        symbol = str(row.get('symbol', ''))[:20] if row.get('symbol') else None
                        name = str(row.get('name', ''))[:100] if row.get('name') else None
                        image = str(row.get('image', ''))[:500] if row.get('image') else None
                        
                        if not coin_id:
                            continue
                            
                        conn.execute(query, {
                            'coin_id': coin_id,
                            'symbol': symbol,
                            'name': name,
                            'image': image,
                            'price': row.get('price'),
                            'change_1h': row.get('change_1h'),
                            'change_4h': row.get('change_4h'),
                            'change_24h': row.get('change_24h'),
                            'change_7d': row.get('change_7d'),
                            'volume_24h': row.get('volume_24h'),
                            'volume_1h': row.get('volume_1h'),
                            'avg_volume_1h': row.get('avg_volume_1h'),
                            'volume_change_pct': row.get('volume_change_pct'),
                            'market_cap': row.get('market_cap'),
                            'market_cap_rank': row.get('market_cap_rank'),
                            'is_sudden_pump': bool(row.get('is_sudden_pump', False)),
                            'is_sudden_dump': bool(row.get('is_sudden_dump', False)),
                            'asi_score': row.get('asi_score'),
                            'signal': str(row.get('signal', ''))[:20] if row.get('signal') else None,
                            # Technical metrics
                            'momentum_score': int(row.get('momentum_score', 0)) if row.get('momentum_score') is not None else None,
                            'trend_score': float(row.get('trend_score', 0)) if row.get('trend_score') is not None else None,
                            'trend_label': str(row.get('trend_label', ''))[:20] if row.get('trend_label') else None,
                            # Relative strength
                            'rs_vs_btc': float(row.get('rs_vs_btc', 0)) if row.get('rs_vs_btc') is not None else None,
                            'rs_vs_market': float(row.get('rs_vs_market', 0)) if row.get('rs_vs_market') is not None else None,
                            'rs_score': int(row.get('rs_score', 0)) if row.get('rs_score') is not None else None,
                            'is_outperformer': bool(row.get('is_outperformer', False)),
                            'is_anomaly': bool(row.get('is_anomaly', False)),
                            'anomaly_type': str(row.get('anomaly_type', ''))[:50] if row.get('anomaly_type') else None,
                            # Pattern detection
                            'pattern_name': str(row.get('pattern_name', ''))[:50] if row.get('pattern_name') else None,
                            'pattern_direction': str(row.get('pattern_direction', ''))[:20] if row.get('pattern_direction') else None,
                            'pattern_reliability': str(row.get('pattern_reliability', ''))[:20] if row.get('pattern_reliability') else None,
                            'pattern_score': int(row.get('pattern_score', 0)) if row.get('pattern_score') is not None else None,
                            # RSI divergence
                            'rsi_14': float(row.get('rsi_14', 0)) if row.get('rsi_14') is not None else None,
                            'has_divergence': bool(row.get('has_divergence', False)),
                            'divergence_type': str(row.get('divergence_type', ''))[:20] if row.get('divergence_type') else None,
                            'divergence_score': int(row.get('divergence_score', 0)) if row.get('divergence_score') is not None else None,
                            # MACD
                            'macd_histogram': float(row.get('macd_histogram', 0)) if row.get('macd_histogram') is not None else None,
                            'macd_signal_type': str(row.get('macd_signal_type', ''))[:20] if row.get('macd_signal_type') else None,
                            'macd_confirmed': bool(row.get('macd_confirmed', False)),
                            # Bollinger Bands
                            'bb_position': str(row.get('bb_position', ''))[:20] if row.get('bb_position') else None,
                            'bb_squeeze': bool(row.get('bb_squeeze', False)),
                            'bb_width': float(row.get('bb_width', 0)) if row.get('bb_width') is not None else None,
                            'bb_signal': str(row.get('bb_signal', ''))[:20] if row.get('bb_signal') else None,
                            # Confirmations
                            'volume_confirmed': bool(row.get('volume_confirmed', False)),
                            'ma_confirmed': bool(row.get('ma_confirmed', False)),
                            'rsi_extreme': bool(row.get('rsi_extreme', False)),
                            'near_sr': bool(row.get('near_sr', False)),
                            'mtf_aligned': bool(row.get('mtf_aligned', False)),
                            'confirmation_count': int(row.get('confirmation_count', 0)) if row.get('confirmation_count') is not None else 0,
                            'confirmation_score': int(row.get('confirmation_score', 0)) if row.get('confirmation_score') is not None else 0,
                            # Final scores
                            'discovery_score': int(row.get('discovery_score', 0)) if row.get('discovery_score') is not None else 0,
                            'signal_strength': str(row.get('signal_strength', ''))[:20] if row.get('signal_strength') else None,
                        })

                        count += 1
                    except Exception as e:
                        logger.warning(f"Upsert row failed for {row.get('coin_id', 'unknown')}: {e}")
                        continue
        except Exception as e:
            logger.error(f"Upsert transaction failed: {e}")
        
        return count

    
    # ============ Query Methods ============
    
    def get_top_gainers(self, timeframe: str = "1h", limit: int = 10) -> List[Dict]:
        """Get top gaining coins."""
        change_col = f"change_{timeframe}" if timeframe in ["1h", "4h", "24h", "7d"] else "change_24h"
        
        query = text(f"""
            SELECT coin_id, symbol, name, image, price, 
                   {change_col} as change_pct, 
                   volume_24h, market_cap, market_cap_rank, asi_score, signal
            FROM market_discovery_snapshot
            WHERE volume_24h > :min_volume AND {change_col} IS NOT NULL
            ORDER BY {change_col} DESC
            LIMIT :limit
        """)
        
        return self._execute_query(query, {"min_volume": self.MIN_VOLUME_24H, "limit": limit})
    
    def get_top_losers(self, timeframe: str = "1h", limit: int = 10) -> List[Dict]:
        """Get top losing coins."""
        change_col = f"change_{timeframe}" if timeframe in ["1h", "4h", "24h", "7d"] else "change_24h"
        
        query = text(f"""
            SELECT coin_id, symbol, name, image, price, 
                   {change_col} as change_pct, 
                   volume_24h, market_cap, market_cap_rank, asi_score, signal
            FROM market_discovery_snapshot
            WHERE volume_24h > :min_volume AND {change_col} IS NOT NULL
            ORDER BY {change_col} ASC
            LIMIT :limit
        """)
        
        return self._execute_query(query, {"min_volume": self.MIN_VOLUME_24H, "limit": limit})
    
    def get_sudden_pumps(self, limit: int = 10) -> List[Dict]:
        """Get coins with sudden pump signals."""
        query = text("""
            SELECT coin_id, symbol, name, image, price, change_1h, 
                   volume_1h, avg_volume_1h, volume_change_pct,
                   market_cap, asi_score, signal, updated_at
            FROM market_discovery_snapshot
            WHERE is_sudden_pump = TRUE AND volume_24h > :min_volume
            ORDER BY change_1h DESC
            LIMIT :limit
        """)
        
        return self._execute_query(query, {"min_volume": self.MIN_VOLUME_24H, "limit": limit})
    
    def get_sudden_dumps(self, limit: int = 10) -> List[Dict]:
        """Get coins with sudden dump signals."""
        query = text("""
            SELECT coin_id, symbol, name, image, price, change_1h, 
                   volume_1h, avg_volume_1h, volume_change_pct,
                   market_cap, asi_score, signal, updated_at
            FROM market_discovery_snapshot
            WHERE is_sudden_dump = TRUE AND volume_24h > :min_volume
            ORDER BY change_1h ASC
            LIMIT :limit
        """)
        
        return self._execute_query(query, {"min_volume": self.MIN_VOLUME_24H, "limit": limit})
    
    def get_most_traded(self, limit: int = 10) -> List[Dict]:
        """Get most traded coins by volume."""
        query = text("""
            SELECT coin_id, symbol, name, image, price, change_24h, 
                   volume_24h, market_cap, market_cap_rank, asi_score, signal
            FROM market_discovery_snapshot
            WHERE volume_24h > :min_volume
            ORDER BY volume_24h DESC
            LIMIT :limit
        """)
        
        return self._execute_query(query, {"min_volume": self.MIN_VOLUME_24H, "limit": limit})
    
    def _execute_query(self, query, params: dict) -> List[Dict]:
        """Execute query and return list of dicts."""
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query, params)
                rows = result.fetchall()
                columns = result.keys()
                
                return [
                    {col: self._serialize(row[i]) for i, col in enumerate(columns)}
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []
    
    def _serialize(self, val):
        """Convert value to JSON-serializable type."""
        if val is None:
            return None
        if isinstance(val, (datetime,)):
            return val.isoformat()
        if isinstance(val, (float, np.floating)):
            return round(float(val), 6)
        if isinstance(val, (int, np.integer)):
            return int(val)
        if isinstance(val, (bool, np.bool_)):
            return bool(val)
        return val


# Singleton instance
_discovery_engine: Optional[DiscoveryEngine] = None


def get_discovery_engine() -> DiscoveryEngine:
    """Get singleton instance of DiscoveryEngine."""
    global _discovery_engine
    if _discovery_engine is None:
        from app.services.database import get_db_service
        _discovery_engine = DiscoveryEngine(get_db_service())
    return _discovery_engine
