"""
News Aggregator Service
Fetches, categorizes, and pre-processes crypto news for behavioral analysis
"""
import asyncio
import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

import httpx

logger = logging.getLogger(__name__)


class NewsCategory(str, Enum):
    """News categories for behavioral analysis"""
    REGULATORY = "regulatory"
    TECHNICAL = "technical"
    WHALE_MOVEMENT = "whale_movement"
    SOCIAL_HYPE = "social_hype"
    MARKET = "market"
    UNKNOWN = "unknown"


class EmotionalTone(str, Enum):
    """Emotional tones detected in news"""
    FEAR = "Fear"
    FUD = "FUD"
    FOMO = "FOMO"
    EUPHORIA = "Euphoria"
    NEUTRAL = "Neutral"
    UNCERTAINTY = "Uncertainty"


class CrowdAction(str, Enum):
    """Expected crowd actions based on sentiment"""
    SELL_OFF = "Sell-off"
    PANIC_SELL = "Panic-sell"
    BUY_DIP = "Buy-dip"
    FOMO_BUY = "FOMO-buy"
    HOLD = "Hold"
    ACCUMULATE = "Accumulate"


@dataclass
class NewsItem:
    """Structured news item with metadata"""
    event_id: str
    coin_id: str
    symbol: str
    title: str
    summary: str = ""
    source: str = ""
    source_url: str = ""
    category: NewsCategory = NewsCategory.UNKNOWN
    publish_time: datetime = field(default_factory=datetime.now)
    event_time: Optional[datetime] = None  # Actual event time (may differ)
    sentiment_score: int = 50  # 0-100
    emotional_tone: EmotionalTone = EmotionalTone.NEUTRAL
    news_intensity: int = 5  # 1-10
    is_front_running: bool = False  # True if event happened before publish
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "coin_id": self.coin_id,
            "symbol": self.symbol,
            "title": self.title,
            "summary": self.summary,
            "source": self.source,
            "source_url": self.source_url,
            "category": self.category.value,
            "publish_time": self.publish_time.isoformat() if self.publish_time else None,
            "event_time": self.event_time.isoformat() if self.event_time else None,
            "sentiment_score": self.sentiment_score,
            "emotional_tone": self.emotional_tone.value,
            "news_intensity": self.news_intensity,
            "is_front_running": self.is_front_running,
        }


@dataclass
class BehavioralSentiment:
    """High-granularity behavioral sentiment result"""
    coin_id: str
    symbol: str
    sentiment_score: int  # 0-100
    emotional_tone: EmotionalTone
    expected_crowd_action: CrowdAction
    news_intensity: int  # 1-10
    dominant_category: NewsCategory
    impact_duration: str  # "hours", "days", "weeks"
    related_event_ids: List[str] = field(default_factory=list)
    confidence_score: float = 0.5
    raw_ai_response: str = ""
    analyzed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "coin_id": self.coin_id,
            "symbol": self.symbol,
            "sentiment_score": self.sentiment_score,
            "emotional_tone": self.emotional_tone.value,
            "expected_crowd_action": self.expected_crowd_action.value,
            "news_intensity": self.news_intensity,
            "dominant_category": self.dominant_category.value,
            "impact_duration": self.impact_duration,
            "related_event_ids": self.related_event_ids,
            "confidence_score": self.confidence_score,
            "analyzed_at": self.analyzed_at.isoformat(),
        }


@dataclass
class SentimentContext:
    """Sentiment context at a specific moment (for whale correlation)"""
    coin_id: str
    timestamp: datetime
    dominant_emotion: EmotionalTone
    crowd_action: CrowdAction
    sentiment_score: int
    news_intensity: int
    event_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "coin_id": self.coin_id,
            "timestamp": self.timestamp.isoformat(),
            "dominant_emotion": self.dominant_emotion.value,
            "crowd_action": self.crowd_action.value,
            "sentiment_score": self.sentiment_score,
            "news_intensity": self.news_intensity,
            "event_ids": self.event_ids,
        }


class NewsAggregator:
    """
    Aggregates and categorizes crypto news from multiple sources.
    Supports behavioral analysis for AI Sentiment module.
    """
    
    # CryptoPanic API (free tier)
    CRYPTOPANIC_API = "https://cryptopanic.com/api/v1/posts/"
    
    # Keywords for category classification
    CATEGORY_KEYWORDS = {
        NewsCategory.REGULATORY: [
            "sec", "regulation", "lawsuit", "ban", "legal", "compliance",
            "government", "law", "court", "fine", "penalty", "license",
            "etf", "approval", "reject", "policy", "tax", "sanctions"
        ],
        NewsCategory.TECHNICAL: [
            "upgrade", "fork", "update", "patch", "bug", "vulnerability",
            "smart contract", "protocol", "mainnet", "testnet", "development",
            "roadmap", "release", "version", "merge", "hardfork", "softfork"
        ],
        NewsCategory.WHALE_MOVEMENT: [
            "whale", "large transfer", "moved", "wallet", "exchange inflow",
            "exchange outflow", "dormant", "accumulation", "distribution",
            "million", "billion", "massive", "huge transfer", "unknown wallet"
        ],
        NewsCategory.SOCIAL_HYPE: [
            "elon", "musk", "celebrity", "viral", "trending", "meme",
            "twitter", "x.com", "social media", "influencer", "pump",
            "moon", "rocket", "ape", "degen", "community", "fomo"
        ],
    }
    
    # Keywords for emotional tone detection
    EMOTION_KEYWORDS = {
        EmotionalTone.FEAR: [
            "crash", "collapse", "plunge", "dump", "sell-off", "panic",
            "crisis", "warning", "danger", "risk", "bearish", "downtrend"
        ],
        EmotionalTone.FUD: [
            "scam", "fraud", "hack", "exploit", "rug", "ponzi",
            "fake", "suspicious", "investigation", "concern", "doubt"
        ],
        EmotionalTone.FOMO: [
            "surge", "soar", "rally", "breakout", "all-time high", "ath",
            "bull run", "moon", "rocket", "explosive", "parabolic"
        ],
        EmotionalTone.EUPHORIA: [
            "historic", "milestone", "breakthrough", "revolutionary",
            "game-changer", "massive adoption", "institutional", "mainstream"
        ],
    }
    
    def __init__(self, cryptopanic_token: str = "", gemini_service=None):
        self.cryptopanic_token = cryptopanic_token
        self.gemini = gemini_service
        self._cache: Dict[str, List[NewsItem]] = {}
        self._cache_time: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=15)
    
    def _generate_event_id(self, title: str, source: str, publish_time: datetime) -> str:
        """Generate unique event ID from news properties"""
        content = f"{title}|{source}|{publish_time.isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _classify_category(self, title: str, summary: str) -> NewsCategory:
        """Classify news category based on keywords"""
        text = (title + " " + summary).lower()
        
        scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[category] = score
        
        if not scores:
            return NewsCategory.MARKET
        
        return max(scores, key=scores.get)
    
    def _detect_emotion(self, title: str, summary: str) -> EmotionalTone:
        """Detect emotional tone from news text"""
        text = (title + " " + summary).lower()
        
        scores = {}
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[emotion] = score
        
        if not scores:
            return EmotionalTone.NEUTRAL
        
        return max(scores, key=scores.get)
    
    def _estimate_intensity(self, title: str, summary: str, category: NewsCategory) -> int:
        """Estimate news intensity (1-10)"""
        text = (title + " " + summary).lower()
        
        intensity = 5  # Default
        
        # High-impact keywords
        high_impact = ["breaking", "urgent", "major", "massive", "historic", "unprecedented"]
        if any(kw in text for kw in high_impact):
            intensity += 2
        
        # Regulatory news tends to be high impact
        if category == NewsCategory.REGULATORY:
            intensity += 1
        
        # Whale movements are significant
        if category == NewsCategory.WHALE_MOVEMENT:
            intensity += 1
        
        # Numbers indicate specificity
        if any(char.isdigit() for char in text):
            intensity += 1
        
        return min(max(intensity, 1), 10)
    
    def _extract_event_time(self, title: str, summary: str, publish_time: datetime) -> Optional[datetime]:
        """
        Extract actual event time from news text.
        Detects front-running behavior when event happened before publish.
        """
        text = (title + " " + summary).lower()
        
        # Time indicators suggesting past event
        past_indicators = ["yesterday", "last week", "earlier today", "hours ago", "days ago"]
        
        for indicator in past_indicators:
            if indicator in text:
                if "yesterday" in text:
                    return publish_time - timedelta(days=1)
                elif "last week" in text:
                    return publish_time - timedelta(days=7)
                elif "hours ago" in text:
                    return publish_time - timedelta(hours=6)  # Estimate
                elif "days ago" in text:
                    return publish_time - timedelta(days=3)  # Estimate
        
        # Default: event time = publish time
        return publish_time
    
    async def fetch_news(
        self,
        coin_id: str,
        symbol: str = "",
        limit: int = 20,
        use_cache: bool = True,
    ) -> List[NewsItem]:
        """
        Fetch news for a specific coin.
        
        Args:
            coin_id: CoinGecko coin ID
            symbol: Coin symbol (e.g., 'BTC')
            limit: Max news items to fetch
            use_cache: Use cached results if available
            
        Returns:
            List of NewsItem objects
        """
        cache_key = f"{coin_id}:{symbol}"
        
        # Check cache
        if use_cache and cache_key in self._cache:
            if datetime.now() - self._cache_time.get(cache_key, datetime.min) < self._cache_ttl:
                return self._cache[cache_key][:limit]
        
        news_items = []
        
        # Try CryptoPanic API
        if self.cryptopanic_token:
            try:
                news_items = await self._fetch_from_cryptopanic(symbol or coin_id, limit)
            except Exception as e:
                logger.warning(f"CryptoPanic fetch failed: {e}")
        
        # Fallback: Generate mock data for testing (remove in production)
        if not news_items:
            news_items = self._generate_mock_news(coin_id, symbol, limit=5)
        
        # Cache results
        self._cache[cache_key] = news_items
        self._cache_time[cache_key] = datetime.now()
        
        return news_items[:limit]
    
    async def _fetch_from_cryptopanic(self, currency: str, limit: int) -> List[NewsItem]:
        """Fetch news from CryptoPanic API"""
        news_items = []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    "auth_token": self.cryptopanic_token,
                    "currencies": currency.upper(),
                    "kind": "news",
                    "public": "true",
                }
                
                response = await client.get(self.CRYPTOPANIC_API, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for post in data.get("results", [])[:limit]:
                        publish_time = datetime.fromisoformat(
                            post.get("published_at", "").replace("Z", "+00:00")
                        ) if post.get("published_at") else datetime.now()
                        
                        title = post.get("title", "")
                        summary = post.get("body", "") or ""
                        source = post.get("source", {}).get("title", "Unknown")
                        
                        category = self._classify_category(title, summary)
                        emotion = self._detect_emotion(title, summary)
                        intensity = self._estimate_intensity(title, summary, category)
                        event_time = self._extract_event_time(title, summary, publish_time)
                        
                        news_items.append(NewsItem(
                            event_id=self._generate_event_id(title, source, publish_time),
                            coin_id=currency.lower(),
                            symbol=currency.upper(),
                            title=title,
                            summary=summary,
                            source=source,
                            source_url=post.get("url", ""),
                            category=category,
                            publish_time=publish_time,
                            event_time=event_time,
                            sentiment_score=50,  # Will be updated by AI
                            emotional_tone=emotion,
                            news_intensity=intensity,
                            is_front_running=(event_time and event_time < publish_time - timedelta(hours=1)),
                        ))
                        
        except Exception as e:
            logger.error(f"CryptoPanic API error: {e}")
        
        return news_items
    
    def _generate_mock_news(self, coin_id: str, symbol: str, limit: int = 5) -> List[NewsItem]:
        """Generate mock news for testing (remove in production)"""
        symbol = symbol or coin_id.upper()[:4]
        now = datetime.now()
        
        mock_items = [
            NewsItem(
                event_id=self._generate_event_id(f"Mock Regulatory {symbol}", "MockSource", now),
                coin_id=coin_id,
                symbol=symbol,
                title=f"SEC Reviews {symbol} ETF Application",
                summary="Regulatory body is reviewing the latest spot ETF application.",
                source="MockNews",
                category=NewsCategory.REGULATORY,
                publish_time=now - timedelta(hours=2),
                event_time=now - timedelta(hours=2),
                emotional_tone=EmotionalTone.UNCERTAINTY,
                news_intensity=7,
            ),
            NewsItem(
                event_id=self._generate_event_id(f"Mock Whale {symbol}", "MockSource", now),
                coin_id=coin_id,
                symbol=symbol,
                title=f"Whale Moves 10,000 {symbol} to Exchange",
                summary="Large holder transferred significant amount to Binance.",
                source="WhaleAlert",
                category=NewsCategory.WHALE_MOVEMENT,
                publish_time=now - timedelta(hours=1),
                event_time=now - timedelta(hours=3),  # Event before publish (front-running)
                emotional_tone=EmotionalTone.FEAR,
                news_intensity=6,
                is_front_running=True,
            ),
            NewsItem(
                event_id=self._generate_event_id(f"Mock Technical {symbol}", "MockSource", now),
                coin_id=coin_id,
                symbol=symbol,
                title=f"{symbol} Network Upgrade Successful",
                summary="Latest protocol upgrade deployed without issues.",
                source="CryptoNews",
                category=NewsCategory.TECHNICAL,
                publish_time=now - timedelta(hours=4),
                event_time=now - timedelta(hours=4),
                emotional_tone=EmotionalTone.NEUTRAL,
                news_intensity=5,
            ),
        ]
        
        return mock_items[:limit]
    
    async def get_categorized_news(
        self,
        coin_id: str,
        symbol: str = "",
    ) -> Dict[str, List[NewsItem]]:
        """
        Get news organized by category.
        
        Returns:
            Dict with category names as keys and lists of NewsItem as values
        """
        all_news = await self.fetch_news(coin_id, symbol)
        
        categorized = {cat.value: [] for cat in NewsCategory}
        
        for item in all_news:
            categorized[item.category.value].append(item)
        
        return categorized
    
    async def analyze_news_with_ai(
        self,
        news_items: List[NewsItem],
        coin_id: str,
        symbol: str,
        price_context: Dict[str, Any] = None,
    ) -> Optional[BehavioralSentiment]:
        """
        Use Gemini AI to analyze news and generate behavioral sentiment.
        
        Args:
            news_items: List of news items to analyze
            coin_id: Coin ID
            symbol: Coin symbol
            price_context: Optional price/market data for context
            
        Returns:
            BehavioralSentiment result or None
        """
        if not self.gemini or not news_items:
            return None
        
        # Delegate to Gemini's advanced_sentiment_analysis
        return await self.gemini.advanced_sentiment_analysis(
            coin_id=coin_id,
            symbol=symbol,
            news_data=[item.to_dict() for item in news_items],
            price_context=price_context or {},
        )


# Singleton
_news_aggregator: Optional[NewsAggregator] = None


def get_news_aggregator() -> NewsAggregator:
    """Get news aggregator singleton"""
    global _news_aggregator
    if _news_aggregator is None:
        from app.core.config import get_settings
        from app.services.gemini import get_gemini_service
        
        settings = get_settings()
        cryptopanic_token = getattr(settings, 'CRYPTOPANIC_TOKEN', '')
        
        _news_aggregator = NewsAggregator(
            cryptopanic_token=cryptopanic_token,
            gemini_service=get_gemini_service(),
        )
    return _news_aggregator
