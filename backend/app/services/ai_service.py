"""
AI Service Abstract Interface
Unified interface for AI providers (Gemini, DeepSeek, OpenAI, etc.)
Supports behavioral sentiment analysis for AI Behavioral Alpha
"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional, Protocol
from enum import Enum

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """Supported AI providers"""
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    LOCAL = "local"


@dataclass
class BehavioralSentimentResult:
    """Result from behavioral sentiment analysis"""
    coin_id: str
    symbol: str
    sentiment_score: int  # 0-100
    emotional_tone: str  # Fear/FUD/FOMO/Euphoria/Neutral
    expected_crowd_action: str  # Sell-off/Buy-dip/Hold/etc.
    news_intensity: int  # 1-10
    dominant_category: str  # regulatory/technical/whale/social
    impact_duration: str  # hours/days/weeks
    confidence_score: float = 0.5
    reasoning: str = ""
    raw_ai_response: str = ""
    related_event_ids: List[str] = field(default_factory=list)
    analyzed_at: datetime = field(default_factory=datetime.now)
    provider: AIProvider = AIProvider.GEMINI
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "coin_id": self.coin_id,
            "symbol": self.symbol,
            "sentiment_score": self.sentiment_score,
            "emotional_tone": self.emotional_tone,
            "expected_crowd_action": self.expected_crowd_action,
            "news_intensity": self.news_intensity,
            "dominant_category": self.dominant_category,
            "impact_duration": self.impact_duration,
            "confidence_score": self.confidence_score,
            "reasoning": self.reasoning,
            "related_event_ids": self.related_event_ids,
            "analyzed_at": self.analyzed_at.isoformat(),
            "provider": self.provider.value,
        }


@dataclass 
class SentimentContextResult:
    """Sentiment context at a specific moment for whale correlation"""
    coin_id: str
    timestamp: datetime
    dominant_emotion: str
    crowd_action: str
    sentiment_score: int
    news_intensity: int
    event_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "coin_id": self.coin_id,
            "timestamp": self.timestamp.isoformat(),
            "dominant_emotion": self.dominant_emotion,
            "crowd_action": self.crowd_action,
            "sentiment_score": self.sentiment_score,
            "news_intensity": self.news_intensity,
            "event_ids": self.event_ids,
        }


@dataclass
class OnChainAnalysisResult:
    """Result from on-chain signal analysis"""
    prediction: str  # BULLISH/BEARISH/NEUTRAL
    probability: int  # 0-100
    summary: str
    reasoning: str
    risk_level: str  # LOW/MEDIUM/HIGH
    provider: AIProvider = AIProvider.GEMINI
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prediction": self.prediction,
            "probability": self.probability,
            "summary": self.summary,
            "reasoning": self.reasoning,
            "risk_level": self.risk_level,
            "provider": self.provider.value,
        }


class AIService(ABC):
    """Abstract base class for AI services"""
    
    @property
    @abstractmethod
    def provider(self) -> AIProvider:
        """Return the AI provider type"""
        pass
    
    @property
    @abstractmethod
    def enabled(self) -> bool:
        """Check if service is enabled"""
        pass
    
    @abstractmethod
    async def analyze_onchain_signals(
        self,
        symbol: str,
        price_usd: float,
        price_change_24h: float,
        rsi: float,
        onchain_data: Dict[str, Any],
    ) -> OnChainAnalysisResult:
        """Analyze on-chain signals and generate prediction"""
        pass
    
    @abstractmethod
    async def advanced_sentiment_analysis(
        self,
        coin_id: str,
        symbol: str,
        news_data: List[Dict[str, Any]],
        price_context: Optional[Dict[str, Any]] = None,
    ) -> Optional[BehavioralSentimentResult]:
        """Analyze news with behavioral lens"""
        pass
    
    @abstractmethod
    async def get_sentiment_context(
        self,
        timestamp: datetime,
        coin_id: str,
        db=None,
    ) -> Optional[SentimentContextResult]:
        """Get sentiment context at a specific moment"""
        pass


class AIServiceManager:
    """
    Manager for AI services with automatic fallback.
    Tries primary provider first, falls back to secondary on failure.
    """
    
    def __init__(self):
        self._services: Dict[AIProvider, AIService] = {}
        self._primary: Optional[AIProvider] = None
        self._fallback: Optional[AIProvider] = None
    
    def register(self, service: AIService, primary: bool = False):
        """Register an AI service"""
        provider = service.provider
        self._services[provider] = service
        
        if primary or self._primary is None:
            if service.enabled:
                self._primary = provider
                logger.info(f"Registered {provider.value} as primary AI service")
            else:
                logger.warning(f"{provider.value} registered but not enabled")
        
        # Set fallback if not primary
        if not primary and self._fallback is None and service.enabled:
            self._fallback = provider
            logger.info(f"Registered {provider.value} as fallback AI service")
    
    def get_service(self, provider: Optional[AIProvider] = None) -> Optional[AIService]:
        """Get specific service or primary service"""
        if provider:
            return self._services.get(provider)
        
        if self._primary:
            return self._services.get(self._primary)
        
        return None
    
    async def analyze_onchain_signals(
        self,
        symbol: str,
        price_usd: float,
        price_change_24h: float,
        rsi: float,
        onchain_data: Dict[str, Any],
    ) -> OnChainAnalysisResult:
        """Analyze with automatic fallback"""
        # Try primary
        if self._primary:
            service = self._services.get(self._primary)
            if service and service.enabled:
                try:
                    return await service.analyze_onchain_signals(
                        symbol, price_usd, price_change_24h, rsi, onchain_data
                    )
                except Exception as e:
                    logger.warning(f"Primary AI ({self._primary.value}) failed: {e}")
        
        # Try fallback
        if self._fallback:
            service = self._services.get(self._fallback)
            if service and service.enabled:
                try:
                    return await service.analyze_onchain_signals(
                        symbol, price_usd, price_change_24h, rsi, onchain_data
                    )
                except Exception as e:
                    logger.error(f"Fallback AI ({self._fallback.value}) also failed: {e}")
        
        # Return default
        return OnChainAnalysisResult(
            prediction="NEUTRAL",
            probability=50,
            summary="AI analysis unavailable",
            reasoning="No AI service available",
            risk_level="MEDIUM",
        )
    
    async def advanced_sentiment_analysis(
        self,
        coin_id: str,
        symbol: str,
        news_data: List[Dict[str, Any]],
        price_context: Optional[Dict[str, Any]] = None,
    ) -> Optional[BehavioralSentimentResult]:
        """Behavioral sentiment analysis with fallback"""
        for provider_key in [self._primary, self._fallback]:
            if provider_key:
                service = self._services.get(provider_key)
                if service and service.enabled:
                    try:
                        result = await service.advanced_sentiment_analysis(
                            coin_id, symbol, news_data, price_context
                        )
                        if result:
                            return result
                    except Exception as e:
                        logger.warning(f"AI sentiment ({provider_key.value}) failed: {e}")
        
        return None
    
    async def get_sentiment_context(
        self,
        timestamp: datetime,
        coin_id: str,
        db=None,
    ) -> Optional[SentimentContextResult]:
        """Get sentiment context with fallback"""
        for provider_key in [self._primary, self._fallback]:
            if provider_key:
                service = self._services.get(provider_key)
                if service and service.enabled:
                    try:
                        result = await service.get_sentiment_context(timestamp, coin_id, db)
                        if result:
                            return result
                    except Exception as e:
                        logger.warning(f"Sentiment context ({provider_key.value}) failed: {e}")
        
        return None


# Singleton manager
_ai_manager: Optional[AIServiceManager] = None


def get_ai_service_manager() -> AIServiceManager:
    """Get AI service manager singleton"""
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = AIServiceManager()
        
        # Register available services
        try:
            from app.services.gemini import get_gemini_service
            gemini = get_gemini_service()
            # Wrap GeminiService to implement AIService interface
            _ai_manager.register(_wrap_gemini_service(gemini), primary=True)
        except Exception as e:
            logger.warning(f"Failed to register Gemini: {e}")
        
        try:
            from app.services.deepseek import get_deepseek_service
            deepseek = get_deepseek_service()
            _ai_manager.register(_wrap_deepseek_service(deepseek), primary=False)
        except Exception as e:
            logger.warning(f"Failed to register DeepSeek: {e}")
    
    return _ai_manager


def _wrap_gemini_service(gemini) -> AIService:
    """Wrap GeminiService to implement AIService interface"""
    
    class GeminiAIService(AIService):
        def __init__(self, gemini_service):
            self._gemini = gemini_service
        
        @property
        def provider(self) -> AIProvider:
            return AIProvider.GEMINI
        
        @property
        def enabled(self) -> bool:
            return self._gemini.enabled
        
        async def analyze_onchain_signals(
            self,
            symbol: str,
            price_usd: float,
            price_change_24h: float,
            rsi: float,
            onchain_data: Dict[str, Any],
        ) -> OnChainAnalysisResult:
            result = await self._gemini.analyze_onchain_signals(
                symbol, price_usd, price_change_24h, rsi, onchain_data
            )
            return OnChainAnalysisResult(
                prediction=result.get("overall_signal", "NEUTRAL"),
                probability=int(result.get("bullish_probability", 50)),
                summary=result.get("ai_summary", ""),
                reasoning=result.get("ai_prediction", ""),
                risk_level=result.get("risk_level", "MEDIUM"),
                provider=AIProvider.GEMINI,
            )
        
        async def advanced_sentiment_analysis(
            self,
            coin_id: str,
            symbol: str,
            news_data: List[Dict[str, Any]],
            price_context: Optional[Dict[str, Any]] = None,
        ) -> Optional[BehavioralSentimentResult]:
            result = await self._gemini.advanced_sentiment_analysis(
                coin_id, symbol, news_data, price_context
            )
            if not result:
                return None
            
            return BehavioralSentimentResult(
                coin_id=result.get("coin_id", coin_id),
                symbol=result.get("symbol", symbol),
                sentiment_score=result.get("sentiment_score", 50),
                emotional_tone=result.get("emotional_tone", "Neutral"),
                expected_crowd_action=result.get("expected_crowd_action", "Hold"),
                news_intensity=result.get("news_intensity", 5),
                dominant_category=result.get("dominant_category", "market"),
                impact_duration=result.get("impact_duration", "days"),
                confidence_score=result.get("confidence_score", 0.5),
                reasoning=result.get("reasoning", ""),
                raw_ai_response=result.get("raw_ai_response", ""),
                related_event_ids=result.get("related_event_ids", []),
                provider=AIProvider.GEMINI,
            )
        
        async def get_sentiment_context(
            self,
            timestamp: datetime,
            coin_id: str,
            db=None,
        ) -> Optional[SentimentContextResult]:
            result = await self._gemini.get_sentiment_context(timestamp, coin_id, db)
            if not result:
                return None
            
            return SentimentContextResult(
                coin_id=result.get("coin_id", coin_id),
                timestamp=timestamp,
                dominant_emotion=result.get("dominant_emotion", "Neutral"),
                crowd_action=result.get("crowd_action", "Hold"),
                sentiment_score=result.get("sentiment_score", 50),
                news_intensity=result.get("news_intensity", 5),
            )
    
    return GeminiAIService(gemini)


def _wrap_deepseek_service(deepseek) -> AIService:
    """Wrap DeepSeekService to implement AIService interface"""
    
    class DeepSeekAIService(AIService):
        def __init__(self, deepseek_service):
            self._deepseek = deepseek_service
        
        @property
        def provider(self) -> AIProvider:
            return AIProvider.DEEPSEEK
        
        @property
        def enabled(self) -> bool:
            return self._deepseek.enabled
        
        async def analyze_onchain_signals(
            self,
            symbol: str,
            price_usd: float,
            price_change_24h: float,
            rsi: float,
            onchain_data: Dict[str, Any],
        ) -> OnChainAnalysisResult:
            result = await self._deepseek.analyze_onchain_signals(
                symbol, price_usd, price_change_24h, rsi, onchain_data
            )
            return OnChainAnalysisResult(
                prediction=result.get("prediction", "NEUTRAL"),
                probability=result.get("probability", 50),
                summary=result.get("summary", ""),
                reasoning=result.get("reasoning", ""),
                risk_level=result.get("risk_level", "MEDIUM"),
                provider=AIProvider.DEEPSEEK,
            )
        
        async def advanced_sentiment_analysis(
            self,
            coin_id: str,
            symbol: str,
            news_data: List[Dict[str, Any]],
            price_context: Optional[Dict[str, Any]] = None,
        ) -> Optional[BehavioralSentimentResult]:
            # DeepSeek doesn't have this yet - return None for fallback
            logger.debug("DeepSeek advanced_sentiment_analysis not implemented")
            return None
        
        async def get_sentiment_context(
            self,
            timestamp: datetime,
            coin_id: str,
            db=None,
        ) -> Optional[SentimentContextResult]:
            # DeepSeek doesn't have this yet - return None for fallback
            logger.debug("DeepSeek get_sentiment_context not implemented")
            return None
    
    return DeepSeekAIService(deepseek)
