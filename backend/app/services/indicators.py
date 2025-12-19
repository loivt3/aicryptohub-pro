"""
Enhanced Technical Indicators Module
Additional indicators for Multi-Horizon ASI calculation
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def calculate_obv(df: pd.DataFrame) -> pd.Series:
    """
    Calculate On-Balance Volume (OBV)
    
    OBV measures buying/selling pressure based on volume flow.
    Rising OBV = buyers in control, Falling OBV = sellers in control
    
    Args:
        df: DataFrame with 'Close' and 'Volume' columns
        
    Returns:
        Series with OBV values
    """
    close = df["Close"]
    volume = df["Volume"]
    
    # Calculate price direction
    direction = np.where(close > close.shift(1), 1,
                        np.where(close < close.shift(1), -1, 0))
    
    # OBV = cumulative sum of signed volume
    obv = (volume * direction).cumsum()
    
    return obv


def calculate_obv_signal(df: pd.DataFrame, window: int = 20) -> Dict[str, Any]:
    """
    Calculate OBV signal for ASI scoring
    
    Args:
        df: OHLCV DataFrame
        window: Period for OBV trend analysis
        
    Returns:
        Dict with obv, obv_sma, obv_trend, score (0-10)
    """
    obv = calculate_obv(df)
    obv_sma = obv.rolling(window=window).mean()
    
    current_obv = obv.iloc[-1]
    current_sma = obv_sma.iloc[-1]
    
    # Trend: OBV above/below its SMA
    obv_trend = "bullish" if current_obv > current_sma else "bearish"
    
    # Calculate momentum (rate of change)
    obv_roc = ((obv.iloc[-1] - obv.iloc[-5]) / abs(obv.iloc[-5])) * 100 if obv.iloc[-5] != 0 else 0
    
    # Score 0-10
    score = 5  # Neutral
    if obv_trend == "bullish":
        score += min(3, abs(obv_roc) / 5)  # Max +3 for strong bullish
    else:
        score -= min(3, abs(obv_roc) / 5)  # Max -3 for strong bearish
    
    # Divergence detection: Price up but OBV down = bearish divergence
    price_up = df["Close"].iloc[-1] > df["Close"].iloc[-5]
    obv_up = current_obv > obv.iloc[-5]
    
    if price_up and not obv_up:
        score -= 2  # Bearish divergence
    elif not price_up and obv_up:
        score += 2  # Bullish divergence
    
    score = max(0, min(10, score))
    
    return {
        "obv": float(current_obv),
        "obv_sma": float(current_sma) if pd.notna(current_sma) else 0,
        "obv_trend": obv_trend,
        "obv_roc": round(obv_roc, 2),
        "obv_score": round(score, 2),
    }


def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """
    Calculate Volume Weighted Average Price (VWAP)
    
    VWAP = Cumulative(Typical Price * Volume) / Cumulative(Volume)
    Typical Price = (High + Low + Close) / 3
    
    Args:
        df: DataFrame with OHLCV columns
        
    Returns:
        Series with VWAP values
    """
    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
    vwap = (typical_price * df["Volume"]).cumsum() / df["Volume"].cumsum()
    
    return vwap


def calculate_vwap_signal(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate VWAP signal for ASI scoring
    
    Price above VWAP = bullish (institutional buying)
    Price below VWAP = bearish (institutional selling)
    
    Args:
        df: OHLCV DataFrame
        
    Returns:
        Dict with vwap, price_vs_vwap, score (0-5)
    """
    vwap = calculate_vwap(df)
    current_vwap = vwap.iloc[-1]
    current_price = df["Close"].iloc[-1]
    
    # Distance from VWAP as percentage
    distance_pct = ((current_price - current_vwap) / current_vwap) * 100
    
    # Score 0-5
    score = 2.5  # Neutral
    if distance_pct > 0:
        score += min(2.5, distance_pct / 2)  # Above VWAP = bullish
    else:
        score -= min(2.5, abs(distance_pct) / 2)  # Below VWAP = bearish
    
    score = max(0, min(5, score))
    
    position = "above" if current_price > current_vwap else "below"
    
    return {
        "vwap": round(float(current_vwap), 8),
        "price_vs_vwap": position,
        "vwap_distance_pct": round(distance_pct, 2),
        "vwap_score": round(score, 2),
    }


def calculate_cci(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """
    Calculate Commodity Channel Index (CCI)
    
    CCI = (Typical Price - SMA) / (0.015 * Mean Deviation)
    
    Readings:
    - CCI > 100: Overbought
    - CCI < -100: Oversold
    - CCI > 200 or < -200: Extreme
    
    Args:
        df: DataFrame with OHLCV columns
        window: Period for calculation
        
    Returns:
        Series with CCI values
    """
    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
    sma = typical_price.rolling(window=window).mean()
    mean_deviation = typical_price.rolling(window=window).apply(
        lambda x: np.abs(x - x.mean()).mean(), raw=True
    )
    
    cci = (typical_price - sma) / (0.015 * mean_deviation)
    
    return cci


def calculate_cci_signal(df: pd.DataFrame, window: int = 20) -> Dict[str, Any]:
    """
    Calculate CCI signal for ASI scoring
    
    Args:
        df: OHLCV DataFrame
        window: CCI period
        
    Returns:
        Dict with cci, cci_zone, score (0-5)
    """
    cci = calculate_cci(df, window)
    current_cci = cci.iloc[-1]
    
    # Determine zone
    if current_cci > 200:
        zone = "extreme_overbought"
        score = 0  # Very bearish signal
    elif current_cci > 100:
        zone = "overbought"
        score = 1.5
    elif current_cci < -200:
        zone = "extreme_oversold"
        score = 5  # Very bullish signal (reversal expected)
    elif current_cci < -100:
        zone = "oversold"
        score = 4
    else:
        zone = "neutral"
        # Score based on position within neutral range
        score = 2.5 + (current_cci / 100) * 1.5  # -100 to 100 maps to 1 to 4
    
    score = max(0, min(5, score))
    
    return {
        "cci": round(float(current_cci), 2) if pd.notna(current_cci) else 0,
        "cci_zone": zone,
        "cci_score": round(score, 2),
    }


def calculate_all_enhanced_indicators(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate all enhanced indicators for ASI
    
    Args:
        df: OHLCV DataFrame with columns: Open, High, Low, Close, Volume
        
    Returns:
        Combined dict of all indicator signals
    """
    try:
        obv_signal = calculate_obv_signal(df)
        vwap_signal = calculate_vwap_signal(df)
        cci_signal = calculate_cci_signal(df)
        
        # Combined score (out of 20 total points)
        total_score = obv_signal["obv_score"] + vwap_signal["vwap_score"] + cci_signal["cci_score"]
        
        return {
            **obv_signal,
            **vwap_signal,
            **cci_signal,
            "enhanced_score": round(total_score, 2),
            "enhanced_max": 20,  # OBV(10) + VWAP(5) + CCI(5)
        }
        
    except Exception as e:
        logger.error(f"Error calculating enhanced indicators: {e}")
        return {
            "obv_score": 5,
            "vwap_score": 2.5,
            "cci_score": 2.5,
            "enhanced_score": 10,
            "enhanced_max": 20,
            "error": str(e),
        }
