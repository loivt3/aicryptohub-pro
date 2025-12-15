"""
Gemini AI service for enhanced reasoning
Uses Google Gemini API for intelligent market analysis
"""
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import httpx

logger = logging.getLogger(__name__)


class GeminiService:
    """Google Gemini AI integration for market analysis"""
    
    # Gemini API endpoint
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    
    # Rate limiting (15 RPM for free tier)
    MAX_REQUESTS_PER_MINUTE = 15
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.enabled = bool(api_key)
        self._request_times = []
        
        if not self.enabled:
            logger.warning("Gemini API key not configured - AI reasoning disabled")
    
    async def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        now = datetime.now().timestamp()
        
        # Remove requests older than 1 minute
        self._request_times = [t for t in self._request_times if now - t < 60]
        
        if len(self._request_times) >= self.MAX_REQUESTS_PER_MINUTE:
            wait_time = 60 - (now - self._request_times[0])
            if wait_time > 0:
                logger.info(f"Rate limited, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        self._request_times.append(now)
    
    async def generate_reasoning(
        self,
        symbol: str,
        indicators: Dict[str, Any],
        price_change: float,
        signal: str,
    ) -> Optional[str]:
        """
        Generate AI-enhanced reasoning for a coin analysis
        
        Args:
            symbol: Coin symbol (e.g., 'BTC')
            indicators: Technical indicators dict
            price_change: 24h price change percentage
            signal: Current signal (BUY, SELL, NEUTRAL)
            
        Returns:
            AI-generated reasoning text or None
        """
        if not self.enabled:
            return None
        
        await self._rate_limit()
        
        prompt = self._build_prompt(symbol, indicators, price_change, signal)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.API_URL}?key={self.api_key}",
                    json={
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "temperature": 0.7,
                            "maxOutputTokens": 200,
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return text.strip()
                else:
                    logger.warning(f"Gemini API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Gemini request failed: {e}")
            return None
    
    def _build_prompt(
        self,
        symbol: str,
        indicators: Dict[str, Any],
        price_change: float,
        signal: str,
    ) -> str:
        """Build prompt for Gemini"""
        return f"""You are a professional crypto analyst. Analyze this technical data for {symbol} and provide a brief, actionable insight in 2-3 sentences.

Technical Indicators:
- RSI: {indicators.get('rsi', 'N/A')}
- MACD Histogram: {indicators.get('macd_histogram', 'N/A')}
- Bollinger Band Position: {indicators.get('bb_position', 'N/A')}
- ADX (Trend Strength): {indicators.get('adx', 'N/A')}
- Stochastic K: {indicators.get('stoch_k', 'N/A')}

Price Change (24h): {price_change:+.2f}%
Current Signal: {signal}

Provide a concise market insight focusing on:
1. Current market condition
2. Key risk/opportunity
3. Brief outlook

Keep response under 50 words. Be specific and actionable."""
    
    async def generate_batch_summary(
        self,
        analyses: list,
    ) -> Optional[str]:
        """
        Generate summary for multiple coin analyses
        
        Args:
            analyses: List of analysis dicts
            
        Returns:
            AI-generated market summary
        """
        if not self.enabled or not analyses:
            return None
        
        await self._rate_limit()
        
        # Build summary of signals
        buy_coins = [a["symbol"] for a in analyses if "BUY" in a.get("signal", "")]
        sell_coins = [a["symbol"] for a in analyses if "SELL" in a.get("signal", "")]
        
        prompt = f"""Summarize the crypto market sentiment based on these signals:

BUY signals: {', '.join(buy_coins[:10]) if buy_coins else 'None'}
SELL signals: {', '.join(sell_coins[:10]) if sell_coins else 'None'}

Total coins analyzed: {len(analyses)}
Buy signals: {len(buy_coins)}
Sell signals: {len(sell_coins)}

Provide a brief 2-sentence market summary. Be concise."""
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.API_URL}?key={self.api_key}",
                    json={
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "temperature": 0.5,
                            "maxOutputTokens": 100,
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    
        except Exception as e:
            logger.error(f"Gemini batch summary failed: {e}")
        
        return None
    
    async def analyze_onchain_signals(
        self,
        symbol: str,
        price_usd: float,
        price_change_24h: float,
        rsi: float,
        onchain_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze on-chain data and generate AI prediction with probability
        
        Args:
            symbol: Coin symbol (e.g., 'ETH')
            price_usd: Current price in USD
            price_change_24h: 24h price change %
            rsi: Current RSI value
            onchain_data: On-chain metrics from collector
            
        Returns:
            Dict with ai_prediction, ai_summary, bullish_probability
        """
        if not self.enabled:
            return {
                "ai_prediction": "AI analysis unavailable",
                "ai_summary": "Configure Gemini API for AI predictions",
                "bullish_probability": 50.0,
            }
        
        await self._rate_limit()
        
        # Extract on-chain metrics
        whale = onchain_data.get("whale_signals", {})
        dau = onchain_data.get("dau_signals", {})
        holder = onchain_data.get("holder_signals", {})
        overall = onchain_data.get("overall", {})
        
        prompt = f"""You are an expert crypto on-chain analyst. Analyze this data for {symbol} and provide a trading prediction.

=== PRICE DATA ===
Current Price: ${price_usd:,.2f}
24h Change: {price_change_24h:+.2f}%
RSI: {rsi:.1f} ({'Oversold' if rsi < 30 else 'Overbought' if rsi > 70 else 'Neutral'})

=== ON-CHAIN DATA ===

🐋 WHALE ACTIVITY (24h):
- Large Transactions (>$100K): {whale.get('whale_tx_count_24h', 0)} tx
- Change vs Previous 24h: {whale.get('whale_tx_change_pct', 0):+.1f}%
- Exchange Inflow: ${whale.get('whale_inflow_usd', 0):,.0f}
- Exchange Outflow: ${whale.get('whale_outflow_usd', 0):,.0f}
- Net Flow: ${whale.get('whale_net_flow_usd', 0):+,.0f} ({'Bearish' if whale.get('whale_net_flow_usd', 0) > 0 else 'Bullish'})
- Whale Signal: {whale.get('whale_signal', 'NEUTRAL')}

📊 NETWORK HEALTH:
- Daily Active Addresses (DAU): {dau.get('dau_current', 0):,}
- 1-Day Change: {dau.get('dau_change_1d_pct', 0):+.1f}%
- 3-Day Trend: {dau.get('dau_change_3d_pct', 0):+.1f}%
- 7-Day Trend: {dau.get('dau_change_7d_pct', 0):+.1f}%
- Network Signal: {dau.get('network_signal', 'NEUTRAL')}

👥 TOP HOLDERS:
- Top 10 Balance Change (7d): {holder.get('top10_change_pct', 0):+.1f}%
- Accumulation Score: {holder.get('accumulation_score', 50)}/100
- Holder Signal: {holder.get('holder_signal', 'NEUTRAL')}

=== TASK ===
Based on the on-chain data (NOT just price action), predict:
1. Short-term trend (1-7 days)
2. Key observations from on-chain metrics
3. Trading recommendation

OUTPUT FORMAT (JSON):
{{
    "prediction": "BULLISH/BEARISH/NEUTRAL",
    "probability": 0-100,
    "summary": "One sentence key insight",
    "reasoning": "2-3 sentences explaining WHY based on on-chain data",
    "risk_level": "LOW/MEDIUM/HIGH"
}}

IMPORTANT: Base your analysis primarily on ON-CHAIN DATA (whale activity, DAU trends, holder accumulation) rather than just price movement. These are leading indicators.
"""

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    f"{self.API_URL}?key={self.api_key}",
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.4,
                            "maxOutputTokens": 500,
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    
                    # Try to parse JSON from response
                    try:
                        # Extract JSON from response (may be wrapped in ```json)
                        json_str = text
                        if "```json" in text:
                            json_str = text.split("```json")[1].split("```")[0]
                        elif "```" in text:
                            json_str = text.split("```")[1].split("```")[0]
                        
                        result = json.loads(json_str.strip())
                        
                        return {
                            "ai_prediction": result.get("reasoning", text),
                            "ai_summary": result.get("summary", ""),
                            "bullish_probability": float(result.get("probability", 50)),
                            "risk_level": result.get("risk_level", "MEDIUM"),
                            "overall_signal": result.get("prediction", "NEUTRAL"),
                        }
                        
                    except (json.JSONDecodeError, IndexError):
                        # Fallback: use raw text
                        logger.warning("Failed to parse Gemini JSON response")
                        return {
                            "ai_prediction": text,
                            "ai_summary": text[:100] + "..." if len(text) > 100 else text,
                            "bullish_probability": overall.get("bullish_probability", 50),
                        }
                else:
                    logger.warning(f"Gemini on-chain analysis error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Gemini on-chain analysis failed: {e}")
        
        # Fallback based on calculated signals
        return {
            "ai_prediction": "AI analysis unavailable - using calculated signals",
            "ai_summary": f"On-chain signal: {overall.get('overall_signal', 'NEUTRAL')}",
            "bullish_probability": overall.get("bullish_probability", 50),
        }


# Singleton
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get Gemini service singleton"""
    global _gemini_service
    if _gemini_service is None:
        from config import get_settings
        settings = get_settings()
        _gemini_service = GeminiService(settings.gemini_api_key)
    return _gemini_service
