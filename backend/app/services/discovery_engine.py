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
            
            # Step 5: Detect sudden pumps/dumps
            df = self._detect_pumps_dumps_advanced(df)
            
            # Step 6: Merge with sentiment data
            df = self._merge_sentiment(df)
            
            # Step 7: Calculate discovery score
            df = self._calculate_discovery_score(df)
            
            # Step 8: Upsert to snapshot table
            upsert_count = self._upsert_snapshot(df)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            high_momentum = int((df['momentum_score'] >= 70).sum()) if 'momentum_score' in df.columns else 0
            strong_trends = int((df['trend_score'].abs() >= 3).sum()) if 'trend_score' in df.columns else 0
            anomalies = int((df['is_anomaly'] == True).sum()) if 'is_anomaly' in df.columns else 0
            
            stats = {
                "success": True,
                "coins_processed": len(df),
                "coins_upserted": upsert_count,
                "pumps_detected": int(df['is_sudden_pump'].sum()) if 'is_sudden_pump' in df.columns else 0,
                "dumps_detected": int(df['is_sudden_dump'].sum()) if 'is_sudden_dump' in df.columns else 0,
                "high_momentum_coins": high_momentum,
                "strong_trends": strong_trends,
                "anomalies_detected": anomalies,
                "elapsed_seconds": round(elapsed, 2),
                "updated_at": datetime.now().isoformat(),
            }
            
            logger.info(f"Discovery snapshot updated: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Discovery update failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_market_data(self) -> pd.DataFrame:
        """Get current market data from coins table."""
        query = text("""
            SELECT coin_id, symbol, name, image, price, 
                   change_1h, change_24h, change_7d,
                   volume_24h, market_cap, market_cap_rank
            FROM coins
            WHERE price IS NOT NULL AND price > 0
            ORDER BY market_cap DESC NULLS LAST
            LIMIT 1000
        """)
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query)
                rows = result.fetchall()
                
                if not rows:
                    return pd.DataFrame()
                
                columns = ['coin_id', 'symbol', 'name', 'image', 'price',
                          'change_1h', 'change_24h', 'change_7d',
                          'volume_24h', 'market_cap', 'market_cap_rank']
                
                df = pd.DataFrame(rows, columns=columns)
                
                numeric_cols = ['price', 'change_1h', 'change_24h', 'change_7d', 
                               'volume_24h', 'market_cap', 'market_cap_rank']
                for col in numeric_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                btc_row = df[df['coin_id'] == 'bitcoin']
                if not btc_row.empty:
                    self._btc_change_24h = btc_row['change_24h'].values[0] or 0.0
                
                return df
                
        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            return pd.DataFrame()
    
    async def _calculate_changes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate % changes from OHLCV data."""
        now = datetime.now()
        
        query = text("""
            WITH latest_prices AS (
                SELECT DISTINCT ON (coin_id) 
                    coin_id, close as current_close
                FROM aihub_ohlcv
                WHERE interval = '1h'
                  AND timestamp > :recent_time
                ORDER BY coin_id, timestamp DESC
            ),
            prices_4h AS (
                SELECT DISTINCT ON (coin_id)
                    coin_id, close as close_4h
                FROM aihub_ohlcv
                WHERE interval = '1h'
                  AND timestamp <= :time_4h
                  AND timestamp > :time_4h - INTERVAL '2 hours'
                ORDER BY coin_id, timestamp DESC
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
                
                if rows:
                    ohlcv_df = pd.DataFrame(rows, columns=['coin_id', 'calc_change_4h'])
                    df = df.merge(ohlcv_df, on='coin_id', how='left')
                    df['change_4h'] = df['calc_change_4h'].fillna(df['change_24h'] * 4 / 24)
                else:
                    df['change_4h'] = df['change_24h'] * 4 / 24
                    
        except Exception as e:
            logger.warning(f"OHLCV change calculation failed: {e}")
            df['change_4h'] = df['change_24h'] * 4 / 24
        
        return df
    
    async def _calculate_volume_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate advanced volume metrics."""
        query = text("""
            WITH volume_stats AS (
                SELECT 
                    coin_id,
                    SUM(CASE WHEN timestamp > NOW() - INTERVAL '1 hour' THEN volume ELSE 0 END) as volume_1h,
                    AVG(volume) as avg_volume_1h
                FROM aihub_ohlcv
                WHERE interval = '1h'
                  AND timestamp > NOW() - INTERVAL '24 hours'
                GROUP BY coin_id
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
        """Calculate Discovery Score for hidden gem detection."""
        df['discovery_score'] = (
            df['momentum_score'] * 0.4 +
            df['rs_score'] * 0.3 +
            np.where(df['market_cap_rank'] > 100, 10, 0) +
            np.where(df['is_outperformer'], 10, 0) +
            np.where(df['trend_score'] > 2, 10, 0)
        ).round(0).astype(int)
        df['discovery_score'] = np.clip(df['discovery_score'], 0, 100)
        
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
                updated_at
            ) VALUES (
                :coin_id, :symbol, :name, :image, :price,
                :change_1h, :change_4h, :change_24h, :change_7d,
                :volume_24h, :volume_1h, :avg_volume_1h, :volume_change_pct,
                :market_cap, :market_cap_rank,
                :is_sudden_pump, :is_sudden_dump,
                :asi_score, :signal,
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
                updated_at = NOW()
        """)
        
        count = 0
        try:
            with self.db.engine.begin() as conn:
                for _, row in df.iterrows():
                    conn.execute(query, {
                        'coin_id': row['coin_id'],
                        'symbol': row.get('symbol'),
                        'name': row.get('name'),
                        'image': row.get('image'),
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
                        'signal': row.get('signal'),
                    })
                    count += 1
        except Exception as e:
            logger.error(f"Upsert failed: {e}")
        
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
