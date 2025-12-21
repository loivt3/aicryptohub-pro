"""
Candlestick Pattern Recognizer
Detects high-probability reversal patterns using TA-Lib with volume confirmation.
"""

import logging
from typing import Dict, Optional, List, Tuple
import pandas as pd
import numpy as np

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    logging.warning("TA-Lib not available. Candlestick pattern recognition disabled.")

logger = logging.getLogger(__name__)


class CandlestickPatternRecognizer:
    """
    Recognizes candlestick patterns with volume confirmation.
    
    Supports:
    - Bullish: Hammer, Inverted Hammer, Bullish Engulfing, Morning Star
    - Bearish: Shooting Star, Hanging Man, Bearish Engulfing, Evening Star
    - Indecision: Doji, Dragonfly Doji
    """
    
    # Pattern priority (higher = more reliable, prioritize multi-candle patterns)
    PATTERN_PRIORITY = {
        # Multi-candle patterns (highest priority)
        'Morning Star': 10,
        'Evening Star': 10,
        'Bullish Engulfing': 9,
        'Bearish Engulfing': 9,
        # Single-candle patterns (medium priority)
        'Hammer': 7,
        'Inverted Hammer': 7,
        'Shooting Star': 7,
        'Hanging Man': 7,
        # Indecision patterns (lower priority)
        'Dragonfly Doji': 5,
        'Doji': 4,
    }
    
    # Pattern direction mapping
    PATTERN_DIRECTION = {
        'Hammer': 'BULLISH',
        'Inverted Hammer': 'BULLISH',
        'Bullish Engulfing': 'BULLISH',
        'Morning Star': 'BULLISH',
        'Shooting Star': 'BEARISH',
        'Hanging Man': 'BEARISH',
        'Bearish Engulfing': 'BEARISH',
        'Evening Star': 'BEARISH',
        'Doji': 'NEUTRAL',
        'Dragonfly Doji': 'NEUTRAL',
    }
    
    # TA-Lib function mapping
    TALIB_FUNCTIONS = {
        'Hammer': 'CDLHAMMER',
        'Inverted Hammer': 'CDLINVERTEDHAMMER',
        'Bullish Engulfing': 'CDLENGULFING',
        'Bearish Engulfing': 'CDLENGULFING',  # Same function, different sign
        'Morning Star': 'CDLMORNINGSTAR',
        'Evening Star': 'CDLEVENINGSTAR',
        'Shooting Star': 'CDLSHOOTINGSTAR',
        'Hanging Man': 'CDLHANGINGMAN',
        'Doji': 'CDLDOJI',
        'Dragonfly Doji': 'CDLDRAGONFLYDOJI',
    }
    
    # Volume multiplier threshold for HIGH reliability
    VOLUME_CONFIRMATION_THRESHOLD = 1.2
    VOLUME_SMA_PERIOD = 20
    
    def __init__(self):
        """Initialize the pattern recognizer."""
        if not TALIB_AVAILABLE:
            logger.warning("CandlestickPatternRecognizer initialized without TA-Lib")
    
    def recognize_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Analyze OHLCV data and return detected patterns for the latest candle.
        
        Args:
            df: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
                Must have at least 20 rows for volume SMA calculation.
        
        Returns:
            Dict with pattern info:
            {
                'pattern': 'Bullish Engulfing',
                'direction': 'BULLISH',
                'reliability': 'HIGH',
                'all_patterns': [...]
            }
        """
        if not TALIB_AVAILABLE:
            return self._empty_result()
        
        if df is None or len(df) < self.VOLUME_SMA_PERIOD:
            logger.debug(f"Insufficient data for pattern recognition: {len(df) if df is not None else 0} rows")
            return self._empty_result()
        
        # Ensure column names are lowercase
        df = df.copy()
        df.columns = [c.lower() for c in df.columns]
        
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            logger.warning(f"Missing required columns. Have: {df.columns.tolist()}")
            return self._empty_result()
        
        # Convert to numpy arrays for TA-Lib
        open_prices = df['open'].values.astype(float)
        high_prices = df['high'].values.astype(float)
        low_prices = df['low'].values.astype(float)
        close_prices = df['close'].values.astype(float)
        volumes = df['volume'].values.astype(float)
        
        # Calculate Volume SMA for confirmation
        volume_sma = self._calculate_sma(volumes, self.VOLUME_SMA_PERIOD)
        
        # Detect all patterns
        detected_patterns = []
        
        for pattern_name, talib_func_name in self.TALIB_FUNCTIONS.items():
            try:
                talib_func = getattr(talib, talib_func_name)
                
                # Call TA-Lib function
                if pattern_name in ['Morning Star', 'Evening Star']:
                    # These need penetration parameter
                    result = talib_func(open_prices, high_prices, low_prices, close_prices, penetration=0.3)
                else:
                    result = talib_func(open_prices, high_prices, low_prices, close_prices)
                
                # Check latest candle for pattern
                latest_signal = result[-1] if len(result) > 0 else 0
                
                # Handle Engulfing pattern (positive = bullish, negative = bearish)
                if pattern_name == 'Bullish Engulfing' and latest_signal <= 0:
                    continue
                if pattern_name == 'Bearish Engulfing' and latest_signal >= 0:
                    continue
                
                if latest_signal != 0:
                    # Pattern detected! Check volume confirmation
                    latest_volume = volumes[-1]
                    latest_volume_sma = volume_sma[-1] if len(volume_sma) > 0 else latest_volume
                    
                    volume_ratio = latest_volume / latest_volume_sma if latest_volume_sma > 0 else 1.0
                    reliability = 'HIGH' if volume_ratio >= self.VOLUME_CONFIRMATION_THRESHOLD else 'WEAK'
                    
                    detected_patterns.append({
                        'pattern': pattern_name,
                        'direction': self.PATTERN_DIRECTION[pattern_name],
                        'reliability': reliability,
                        'priority': self.PATTERN_PRIORITY[pattern_name],
                        'signal_strength': abs(latest_signal),
                        'volume_ratio': round(volume_ratio, 2),
                    })
                    
            except Exception as e:
                logger.debug(f"Error detecting {pattern_name}: {e}")
                continue
        
        # Sort by priority (descending) then by reliability
        detected_patterns.sort(
            key=lambda x: (x['priority'], 1 if x['reliability'] == 'HIGH' else 0),
            reverse=True
        )
        
        # Return the strongest pattern
        if detected_patterns:
            strongest = detected_patterns[0]
            return {
                'pattern': strongest['pattern'],
                'direction': strongest['direction'],
                'reliability': strongest['reliability'],
                'volume_ratio': strongest['volume_ratio'],
                'all_patterns': detected_patterns,
            }
        
        return self._empty_result()
    
    def _calculate_sma(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculate Simple Moving Average."""
        if len(data) < period:
            return np.array([np.mean(data)] * len(data))
        
        sma = np.convolve(data, np.ones(period) / period, mode='valid')
        # Pad the beginning to match original length
        padding = np.array([sma[0]] * (period - 1))
        return np.concatenate([padding, sma])
    
    def _empty_result(self) -> Dict:
        """Return empty result when no pattern detected."""
        return {
            'pattern': None,
            'direction': 'NEUTRAL',
            'reliability': None,
            'volume_ratio': None,
            'all_patterns': [],
        }
    
    def get_pattern_score_adjustment(self, pattern_result: Dict) -> int:
        """
        Calculate ASI score adjustment based on detected pattern.
        
        Returns value between -15 and +15 to add to ASI score.
        """
        if not pattern_result or not pattern_result.get('pattern'):
            return 0
        
        direction = pattern_result.get('direction', 'NEUTRAL')
        reliability = pattern_result.get('reliability', 'WEAK')
        pattern = pattern_result.get('pattern', '')
        
        # Base adjustment based on pattern type
        priority = self.PATTERN_PRIORITY.get(pattern, 5)
        
        # Scale: priority 10 = 15 points, priority 4 = 6 points
        base_adjustment = int(priority * 1.5)
        
        # Apply direction
        if direction == 'BULLISH':
            adjustment = base_adjustment
        elif direction == 'BEARISH':
            adjustment = -base_adjustment
        else:  # NEUTRAL
            adjustment = 0
        
        # Apply reliability modifier
        if reliability == 'WEAK':
            adjustment = int(adjustment * 0.6)  # 60% weight for weak signals
        
        # Clamp to [-15, +15]
        return max(-15, min(15, adjustment))


# Singleton instance for easy access
_pattern_recognizer = None

def get_pattern_recognizer() -> CandlestickPatternRecognizer:
    """Get singleton instance of CandlestickPatternRecognizer."""
    global _pattern_recognizer
    if _pattern_recognizer is None:
        _pattern_recognizer = CandlestickPatternRecognizer()
    return _pattern_recognizer
