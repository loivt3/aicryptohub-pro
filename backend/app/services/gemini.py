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
    
    async def advanced_sentiment_analysis(
        self,
        coin_id: str,
        symbol: str,
        news_data: list,
        price_context: Dict[str, Any] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze news with behavioral lens for AI Behavioral Alpha.
        
        Args:
            coin_id: Coin identifier
            symbol: Coin symbol
            news_data: List of news item dicts
            price_context: Optional price/market data
            
        Returns:
            BehavioralSentiment dict with:
            - sentiment_score: 0-100
            - emotional_tone: Fear/FUD/FOMO/Euphoria/Neutral
            - expected_crowd_action: Sell-off/Buy-dip/Hold/etc.
            - news_intensity: 1-10
            - dominant_category: regulatory/technical/whale/social
            - impact_duration: hours/days/weeks
        """
        if not self.enabled:
            return None
        
        if not news_data:
            return {
                "coin_id": coin_id,
                "symbol": symbol,
                "sentiment_score": 50,
                "emotional_tone": "Neutral",
                "expected_crowd_action": "Hold",
                "news_intensity": 5,
                "dominant_category": "market",
                "impact_duration": "days",
                "confidence_score": 0.3,
            }
        
        await self._rate_limit()
        
        # Build news summary for prompt
        news_summary = ""
        categories = {}
        for i, item in enumerate(news_data[:10], 1):  # Limit to 10 items
            cat = item.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            
            front_run_flag = " [FRONT-RUNNING]" if item.get("is_front_running") else ""
            news_summary += f"""
{i}. [{item.get('source', 'Unknown')}] {item.get('title', 'No title')}{front_run_flag}
   Category: {cat} | Intensity: {item.get('news_intensity', 5)}/10
   Emotion: {item.get('emotional_tone', 'Neutral')}
"""
        
        # Determine dominant category
        dominant_cat = max(categories, key=categories.get) if categories else "market"
        
        # Price context
        price_info = ""
        if price_context:
            price_info = f"""
=== PRICE CONTEXT ===
Current Price: ${price_context.get('price', 0):,.2f}
24h Change: {price_context.get('change_24h', 0):+.2f}%
Volume: ${price_context.get('volume_24h', 0):,.0f}
"""
        
        prompt = f"""You are a BEHAVIORAL FINANCE expert specializing in crypto markets. Your task is to analyze news sentiment and predict CROWD BEHAVIOR.

=== COIN: {symbol} ({coin_id}) ===
{price_info}
=== NEWS ITEMS ({len(news_data)} total) ===
{news_summary}

=== ANALYSIS TASK ===
Based on these news items, predict:
1. Overall CROWD SENTIMENT (not just news sentiment)
2. EMOTIONAL STATE of the market
3. Most likely CROWD ACTION in next 24-48 hours
4. How STRONGLY will this affect price (intensity)
5. How LONG will this effect last

=== BEHAVIORAL FRAMEWORK ===
- Fear: Crowd is scared, may panic sell
- FUD: Deliberate uncertainty spreading, may cause sell-off
- FOMO: Fear of missing out, may cause irrational buying
- Euphoria: Extreme optimism, often precedes correction
- Neutral: No strong emotional driver

=== OUTPUT FORMAT (JSON ONLY) ===
{{
    "sentiment_score": 0-100 (0=extreme fear, 100=extreme greed),
    "emotional_tone": "Fear|FUD|FOMO|Euphoria|Neutral|Uncertainty",
    "expected_crowd_action": "Sell-off|Panic-sell|Buy-dip|FOMO-buy|Hold|Accumulate",
    "news_intensity": 1-10 (how strongly will this affect market),
    "dominant_category": "{dominant_cat}",
    "impact_duration": "hours|days|weeks",
    "confidence": 0.0-1.0,
    "reasoning": "One sentence explaining your prediction"
}}

RESPOND WITH JSON ONLY. No markdown, no explanation outside JSON."""

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    f"{self.API_URL}?key={self.api_key}",
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.3,
                            "maxOutputTokens": 500,
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    
                    # Parse JSON response
                    try:
                        json_str = text
                        if "```json" in text:
                            json_str = text.split("```json")[1].split("```")[0]
                        elif "```" in text:
                            json_str = text.split("```")[1].split("```")[0]
                        
                        result = json.loads(json_str.strip())
                        
                        return {
                            "coin_id": coin_id,
                            "symbol": symbol,
                            "sentiment_score": int(result.get("sentiment_score", 50)),
                            "emotional_tone": result.get("emotional_tone", "Neutral"),
                            "expected_crowd_action": result.get("expected_crowd_action", "Hold"),
                            "news_intensity": int(result.get("news_intensity", 5)),
                            "dominant_category": result.get("dominant_category", dominant_cat),
                            "impact_duration": result.get("impact_duration", "days"),
                            "confidence_score": float(result.get("confidence", 0.5)),
                            "reasoning": result.get("reasoning", ""),
                            "raw_ai_response": text,
                            "analyzed_at": datetime.now().isoformat(),
                            "related_event_ids": [n.get("event_id") for n in news_data if n.get("event_id")],
                        }
                        
                    except (json.JSONDecodeError, IndexError) as e:
                        logger.warning(f"Failed to parse behavioral sentiment JSON: {e}")
                        return {
                            "coin_id": coin_id,
                            "symbol": symbol,
                            "sentiment_score": 50,
                            "emotional_tone": "Neutral",
                            "expected_crowd_action": "Hold",
                            "news_intensity": 5,
                            "dominant_category": dominant_cat,
                            "impact_duration": "days",
                            "confidence_score": 0.3,
                            "raw_ai_response": text,
                            "analyzed_at": datetime.now().isoformat(),
                        }
                else:
                    logger.warning(f"Gemini behavioral analysis error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Gemini advanced sentiment failed: {e}")
        
        return None
    
    async def get_sentiment_context(
        self,
        timestamp: datetime,
        coin_id: str,
        db=None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get dominant sentiment at a specific moment.
        Used to determine if whale is acting WITH or AGAINST crowd.
        
        Args:
            timestamp: The moment to analyze
            coin_id: Coin identifier
            db: DatabaseService instance
            
        Returns:
            SentimentContext dict for whale intent analysis
        """
        if not db:
            logger.warning("No database provided for sentiment context")
            return None
        
        # Find sentiment data within ±2 hours of timestamp
        window_hours = 2
        
        try:
            query = f"""
                SELECT 
                    sentiment_score,
                    emotional_tone,
                    expected_crowd_action,
                    news_intensity,
                    dominant_category,
                    analyzed_at
                FROM behavioral_sentiment
                WHERE coin_id = $1
                AND analyzed_at BETWEEN $2 AND $3
                ORDER BY ABS(EXTRACT(EPOCH FROM (analyzed_at - $4)))
                LIMIT 1
            """
            
            from datetime import timedelta
            window_start = timestamp - timedelta(hours=window_hours)
            window_end = timestamp + timedelta(hours=window_hours)
            
            row = await db.fetch_one(query, coin_id, window_start, window_end, timestamp)
            
            if row:
                return {
                    "coin_id": coin_id,
                    "timestamp": timestamp.isoformat(),
                    "dominant_emotion": row.get("emotional_tone", "Neutral"),
                    "crowd_action": row.get("expected_crowd_action", "Hold"),
                    "sentiment_score": row.get("sentiment_score", 50),
                    "news_intensity": row.get("news_intensity", 5),
                    "dominant_category": row.get("dominant_category", "market"),
                }
            
            # Fallback: try aihub_sentiment table
            fallback_query = f"""
                SELECT 
                    sentiment_score * 100 as sentiment_score,
                    COALESCE(emotional_tone, 'Neutral') as emotional_tone,
                    COALESCE(expected_crowd_action, 'Hold') as expected_crowd_action,
                    COALESCE(news_intensity, 5) as news_intensity
                FROM aihub_sentiment
                WHERE symbol = (SELECT UPPER(symbol) FROM aihub_coins WHERE coin_id = $1 LIMIT 1)
                AND analyzed_at BETWEEN $2 AND $3
                ORDER BY ABS(EXTRACT(EPOCH FROM (analyzed_at - $4)))
                LIMIT 1
            """
            
            row = await db.fetch_one(fallback_query, coin_id, window_start, window_end, timestamp)
            
            if row:
                return {
                    "coin_id": coin_id,
                    "timestamp": timestamp.isoformat(),
                    "dominant_emotion": row.get("emotional_tone", "Neutral"),
                    "crowd_action": row.get("expected_crowd_action", "Hold"),
                    "sentiment_score": int(row.get("sentiment_score", 50)),
                    "news_intensity": int(row.get("news_intensity", 5)),
                }
                
        except Exception as e:
            logger.error(f"Failed to get sentiment context: {e}")
        
        # Default neutral context
        return {
            "coin_id": coin_id,
            "timestamp": timestamp.isoformat(),
            "dominant_emotion": "Neutral",
            "crowd_action": "Hold",
            "sentiment_score": 50,
            "news_intensity": 5,
        }


# Singleton
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get Gemini service singleton"""
    global _gemini_service
    if _gemini_service is None:
        from app.core.config import get_settings
        settings = get_settings()
        _gemini_service = GeminiService(settings.gemini_api_key)
    return _gemini_service

