"""
Market Discovery Engine
Computes and caches market metrics for fast discovery API.
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
    Engine for computing market discovery metrics.
    
    Features:
    - Top Gainers/Losers (1h, 4h, 24h)
    - Sudden Pump/Dump detection
    - Volume spike detection
    """
    
    # Minimum volume to include in results (filter scam coins)
    MIN_VOLUME_24H = 100_000  # $100k
    
    # Pump/Dump detection thresholds
    PUMP_THRESHOLD_1H = 3.0    # +3% in 1h
    DUMP_THRESHOLD_1H = -3.0   # -3% in 1h
    VOLUME_SPIKE_MULTIPLIER = 2.0  # Volume > 2x average
    
    def __init__(self, db: DatabaseService):
        """Initialize discovery engine."""
        self.db = db
    
    async def update_snapshot(self) -> Dict[str, Any]:
        """
        Main method to update market_discovery_snapshot table.
        Called by scheduler every 5 minutes.
        
        Returns:
            Dict with update stats
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Get current market data from coins table
            market_data = self._get_market_data()
            
            if market_data.empty:
                logger.warning("No market data found for discovery")
                return {"success": False, "error": "No market data"}
            
            # Step 2: Calculate historical price changes from OHLCV
            df = await self._calculate_changes(market_data)
            
            # Step 3: Calculate volume metrics
            df = await self._calculate_volume_metrics(df)
            
            # Step 4: Detect sudden pumps/dumps
            df = self._detect_pumps_dumps(df)
            
            # Step 5: Merge with sentiment data
            df = self._merge_sentiment(df)
            
            # Step 6: Upsert to snapshot table
            upsert_count = self._upsert_snapshot(df)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            stats = {
                "success": True,
                "coins_processed": len(df),
                "coins_upserted": upsert_count,
                "pumps_detected": int(df['is_sudden_pump'].sum()) if 'is_sudden_pump' in df.columns else 0,
                "dumps_detected": int(df['is_sudden_dump'].sum()) if 'is_sudden_dump' in df.columns else 0,
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
                
                # Convert to numeric
                numeric_cols = ['price', 'change_1h', 'change_24h', 'change_7d', 
                               'volume_24h', 'market_cap', 'market_cap_rank']
                for col in numeric_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                return df
                
        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            return pd.DataFrame()
    
    async def _calculate_changes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate % changes from OHLCV data.
        Uses vectorized operations for speed.
        """
        # Get OHLCV data for calculating 4h changes
        coin_ids = df['coin_id'].tolist()
        
        # Query historical closes (4h and 24h ago)
        now = datetime.now()
        time_4h_ago = now - timedelta(hours=4)
        time_24h_ago = now - timedelta(hours=24)
        
        query = text("""
            WITH latest_prices AS (
                SELECT DISTINCT ON (coin_id) 
                    coin_id, close as current_close, timestamp
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
            ),
            prices_24h AS (
                SELECT DISTINCT ON (coin_id)
                    coin_id, close as close_24h
                FROM aihub_ohlcv
                WHERE interval = '1h'
                  AND timestamp <= :time_24h
                  AND timestamp > :time_24h - INTERVAL '2 hours'
                ORDER BY coin_id, timestamp DESC
            )
            SELECT 
                lp.coin_id,
                lp.current_close,
                p4.close_4h,
                p24.close_24h,
                CASE WHEN p4.close_4h > 0 THEN 
                    ((lp.current_close - p4.close_4h) / p4.close_4h * 100)
                ELSE NULL END as calc_change_4h,
                CASE WHEN p24.close_24h > 0 THEN 
                    ((lp.current_close - p24.close_24h) / p24.close_24h * 100)
                ELSE NULL END as calc_change_24h
            FROM latest_prices lp
            LEFT JOIN prices_4h p4 ON lp.coin_id = p4.coin_id
            LEFT JOIN prices_24h p24 ON lp.coin_id = p24.coin_id
        """)
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query, {
                    "recent_time": now - timedelta(hours=2),
                    "time_4h": time_4h_ago,
                    "time_24h": time_24h_ago,
                })
                rows = result.fetchall()
                
                if rows:
                    ohlcv_df = pd.DataFrame(rows, columns=[
                        'coin_id', 'current_close', 'close_4h', 'close_24h',
                        'calc_change_4h', 'calc_change_24h'
                    ])
                    
                    # Merge with main dataframe
                    df = df.merge(
                        ohlcv_df[['coin_id', 'calc_change_4h', 'calc_change_24h']],
                        on='coin_id',
                        how='left'
                    )
                    
                    # Use calculated 4h change if available
                    df['change_4h'] = df['calc_change_4h'].fillna(
                        df['change_24h'] * 4 / 24  # Estimate from 24h
                    )
                    
                    # Override 24h if calculated is available
                    df['change_24h'] = df['calc_change_24h'].fillna(df['change_24h'])
                else:
                    # Fallback: estimate 4h from 24h
                    df['change_4h'] = df['change_24h'] * 4 / 24
                    
        except Exception as e:
            logger.warning(f"OHLCV change calculation failed, using estimates: {e}")
            df['change_4h'] = df['change_24h'] * 4 / 24
        
        return df
    
    async def _calculate_volume_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate volume metrics for pump/dump detection.
        """
        # Query recent volume data
        query = text("""
            WITH recent_volume AS (
                SELECT 
                    coin_id,
                    SUM(volume) as volume_1h
                FROM aihub_ohlcv
                WHERE interval = '1h'
                  AND timestamp > NOW() - INTERVAL '1 hour'
                GROUP BY coin_id
            ),
            avg_volume AS (
                SELECT 
                    coin_id,
                    AVG(volume) as avg_volume_1h
                FROM aihub_ohlcv
                WHERE interval = '1h'
                  AND timestamp > NOW() - INTERVAL '20 hours'
                GROUP BY coin_id
            )
            SELECT 
                rv.coin_id,
                rv.volume_1h,
                av.avg_volume_1h
            FROM recent_volume rv
            LEFT JOIN avg_volume av ON rv.coin_id = av.coin_id
        """)
        
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(query)
                rows = result.fetchall()
                
                if rows:
                    vol_df = pd.DataFrame(rows, columns=['coin_id', 'volume_1h', 'avg_volume_1h'])
                    
                    # Calculate volume change percentage
                    vol_df['volume_change_pct'] = np.where(
                        vol_df['avg_volume_1h'] > 0,
                        (vol_df['volume_1h'] / vol_df['avg_volume_1h']) * 100,
                        None
                    )
                    
                    df = df.merge(vol_df, on='coin_id', how='left')
                else:
                    df['volume_1h'] = None
                    df['avg_volume_1h'] = None
                    df['volume_change_pct'] = None
                    
        except Exception as e:
            logger.warning(f"Volume metrics calculation failed: {e}")
            df['volume_1h'] = None
            df['avg_volume_1h'] = None
            df['volume_change_pct'] = None
        
        return df
    
    def _detect_pumps_dumps(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect sudden pump/dump events.
        
        Pump: change_1h > 3% AND volume > 2x average
        Dump: change_1h < -3% AND volume > 2x average
        """
        df['is_sudden_pump'] = (
            (df['change_1h'] > self.PUMP_THRESHOLD_1H) &
            (df['volume_change_pct'] > self.VOLUME_SPIKE_MULTIPLIER * 100) &
            (df['volume_24h'] > self.MIN_VOLUME_24H)
        ).fillna(False)
        
        df['is_sudden_dump'] = (
            (df['change_1h'] < self.DUMP_THRESHOLD_1H) &
            (df['volume_change_pct'] > self.VOLUME_SPIKE_MULTIPLIER * 100) &
            (df['volume_24h'] > self.MIN_VOLUME_24H)
        ).fillna(False)
        
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
    
    def _upsert_snapshot(self, df: pd.DataFrame) -> int:
        """
        Upsert data into market_discovery_snapshot table.
        Uses batch insert with ON CONFLICT.
        """
        if df.empty:
            return 0
        
        # Prepare columns
        columns = [
            'coin_id', 'symbol', 'name', 'image', 'price',
            'change_1h', 'change_4h', 'change_24h', 'change_7d',
            'volume_24h', 'volume_1h', 'avg_volume_1h', 'volume_change_pct',
            'market_cap', 'market_cap_rank', 
            'is_sudden_pump', 'is_sudden_dump',
            'asi_score', 'signal'
        ]
        
        # Fill missing columns
        for col in columns:
            if col not in df.columns:
                df[col] = None
        
        # Replace NaN with None
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
                symbol = EXCLUDED.symbol,
                name = EXCLUDED.name,
                image = EXCLUDED.image,
                price = EXCLUDED.price,
                change_1h = EXCLUDED.change_1h,
                change_4h = EXCLUDED.change_4h,
                change_24h = EXCLUDED.change_24h,
                change_7d = EXCLUDED.change_7d,
                volume_24h = EXCLUDED.volume_24h,
                volume_1h = EXCLUDED.volume_1h,
                avg_volume_1h = EXCLUDED.avg_volume_1h,
                volume_change_pct = EXCLUDED.volume_change_pct,
                market_cap = EXCLUDED.market_cap,
                market_cap_rank = EXCLUDED.market_cap_rank,
                is_sudden_pump = EXCLUDED.is_sudden_pump,
                is_sudden_dump = EXCLUDED.is_sudden_dump,
                asi_score = EXCLUDED.asi_score,
                signal = EXCLUDED.signal,
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
    
    # ============ Query Methods for API ============
    
    def get_top_gainers(self, timeframe: str = "1h", limit: int = 10) -> List[Dict]:
        """Get top gaining coins."""
        change_col = f"change_{timeframe}" if timeframe in ["1h", "4h", "24h", "7d"] else "change_24h"
        
        query = text(f"""
            SELECT coin_id, symbol, name, image, price, 
                   {change_col} as change_pct, 
                   volume_24h, market_cap, market_cap_rank, asi_score, signal
            FROM market_discovery_snapshot
            WHERE volume_24h > :min_volume
              AND {change_col} IS NOT NULL
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
            WHERE volume_24h > :min_volume
              AND {change_col} IS NOT NULL
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
            WHERE is_sudden_pump = TRUE
              AND volume_24h > :min_volume
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
            WHERE is_sudden_dump = TRUE
              AND volume_24h > :min_volume
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
