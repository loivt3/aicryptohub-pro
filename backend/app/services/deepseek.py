"""
DeepSeek AI Service for On-Chain Signal Analysis
Uses DeepSeek API for AI-powered crypto analysis
"""
import logging
import httpx
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"


class DeepSeekService:
    """
    DeepSeek AI service for on-chain signal analysis.
    Uses DeepSeek chat API for generating predictions.
    """
    
    def __init__(self, api_key: str = ""):
        """Initialize DeepSeek service"""
        self.api_key = api_key
        self.enabled = bool(api_key)
        self._client = None
        
        if not self.enabled:
            logger.warning("DeepSeek API key not configured - AI analysis disabled")
        else:
            logger.info("DeepSeek service initialized")
            
    async def _get_client(self) -> httpx.AsyncClient:
        """Get HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client
        
    async def analyze_onchain_signals(
        self,
        symbol: str,
        price_usd: float,
        price_change_24h: float,
        rsi: float,
        onchain_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze on-chain signals using DeepSeek AI
        
        Args:
            symbol: Token symbol (e.g., 'ETH')
            price_usd: Current price in USD
            price_change_24h: 24h price change percentage
            rsi: RSI indicator value
            onchain_data: On-chain metrics from collector
            
        Returns:
            AI analysis with prediction, summary, reasoning
        """
        if not self.enabled:
            return {
                "prediction": "NEUTRAL",
                "probability": 50,
                "summary": "AI analysis unavailable",
                "reasoning": "Configure DeepSeek API key for AI predictions",
                "risk_level": "MEDIUM",
            }
            
        try:
            # Extract on-chain metrics
            whale = onchain_data.get("whale_signals", {})
            dau = onchain_data.get("dau_signals", {})
            holder = onchain_data.get("holder_signals", {})
            overall = onchain_data.get("overall", {})
            
            # Build analysis prompt
            prompt = f"""You are an expert crypto on-chain analyst. Analyze this data for {symbol} and provide a trading prediction.

=== PRICE DATA ===
Current Price: ${price_usd:,.2f}
24h Change: {price_change_24h:+.2f}%
RSI: {rsi:.1f} ({'Oversold' if rsi < 30 else 'Overbought' if rsi > 70 else 'Neutral'})

=== ON-CHAIN DATA ===
Whale Activity (24h):
- Transactions: {whale.get('whale_tx_count_24h', 0)}
- Change vs prev 24h: {whale.get('whale_tx_change_pct', 0):+.1f}%
- Net Flow USD: ${whale.get('whale_net_flow_usd', 0):,.0f}
- Signal: {whale.get('whale_signal', 'N/A')}

Network Health:
- DAU: {dau.get('dau_current', 0):,}
- 1d Change: {dau.get('dau_change_1d_pct', 0):+.1f}%
- 7d Trend: {dau.get('dau_trend', 'N/A')}
- Signal: {dau.get('network_signal', 'N/A')}

Top Holders:
- 7d Balance Change: {holder.get('top10_change_pct', 0):+.2f}%
- Accumulation Score: {holder.get('accumulation_score', 50)}/100
- Signal: {holder.get('holder_signal', 'N/A')}

Overall On-Chain:
- Signal: {overall.get('overall_signal', 'N/A')}
- Bullish Probability: {overall.get('bullish_probability', 50):.1f}%

=== TASK ===
Based on the on-chain data (NOT just price action), predict:
1. Short-term trend (1-7 days)
2. Key observations from on-chain metrics
3. Trading recommendation

Respond in JSON format only:
{{"prediction": "BULLISH/BEARISH/NEUTRAL", "probability": 0-100, "summary": "One sentence key insight", "reasoning": "2-3 sentences explaining WHY based on on-chain data", "risk_level": "LOW/MEDIUM/HIGH"}}
"""
            
            # Call DeepSeek API
            client = await self._get_client()
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a crypto analyst. Always respond with valid JSON only."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 500,
            }
            
            response = await client.post(
                f"{DEEPSEEK_API_BASE}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Parse JSON response
            try:
                # Extract JSON from response (handle markdown code blocks)
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                    
                result = json.loads(content.strip())
                
                logger.info(f"DeepSeek analysis for {symbol}: {result.get('prediction')}")
                
                return {
                    "prediction": result.get("prediction", "NEUTRAL"),
                    "probability": result.get("probability", 50),
                    "summary": result.get("summary", ""),
                    "reasoning": result.get("reasoning", ""),
                    "risk_level": result.get("risk_level", "MEDIUM"),
                }
                
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse DeepSeek response: {content[:200]}")
                return self._fallback_analysis(overall)
                
        except Exception as e:
            logger.error(f"DeepSeek analysis failed: {e}")
            return self._fallback_analysis(onchain_data.get("overall", {}))
            
    def _fallback_analysis(self, overall: Dict) -> Dict[str, Any]:
        """Fallback when AI fails"""
        signal = overall.get("overall_signal", "NEUTRAL")
        prob = overall.get("bullish_probability", 50)
        
        return {
            "prediction": signal,
            "probability": prob,
            "summary": f"On-chain signal: {signal} ({prob:.0f}% bullish)",
            "reasoning": "Based on whale activity and exchange flow analysis",
            "risk_level": "MEDIUM" if signal == "NEUTRAL" else "HIGH",
        }
        
    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None


# Singleton
_deepseek_service: Optional[DeepSeekService] = None


def get_deepseek_service() -> DeepSeekService:
    """Get DeepSeek service singleton"""
    global _deepseek_service
    if _deepseek_service is None:
        from config import get_settings
        settings = get_settings()
        _deepseek_service = DeepSeekService(settings.deepseek_api_key)
    return _deepseek_service
