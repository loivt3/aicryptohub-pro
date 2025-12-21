# AI Crypto Hub Pro - Project Report

**Generated:** 2025-12-21  
**Version:** 2.0.0

---

## 1. Project Overview

**AI Crypto Hub Pro** is a real-time cryptocurrency analytics platform with AI-powered sentiment analysis, technical indicators, and on-chain signal tracking.

### Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Nuxt 3, Vue 3, TypeScript |
| **Backend** | FastAPI, Python 3.11 |
| **Database** | PostgreSQL (Supabase + Proxmox) |
| **Real-time** | Socket.IO, WebSocket |
| **AI** | Google Gemini, DeepSeek |
| **Infrastructure** | Docker, Proxmox |

---

## 2. Architecture

```mermaid
graph TB
    subgraph Frontend
        A[Nuxt 3 App] --> B[Mobile Dashboard]
        A --> C[Desktop Dashboard]
        A --> D[Analysis Module]
    end
    
    subgraph Backend
        E[FastAPI] --> F[Price Aggregator]
        E --> G[Technical Analyzer]
        E --> H[AI Service]
        E --> I[On-chain Collector]
    end
    
    subgraph Data
        J[(PostgreSQL)]
        K[Redis Cache]
    end
    
    A -.Socket.IO.-> E
    F --> J
    G --> J
    I --> J
```

---

## 3. Backend Services (21 files, ~350KB)

| Service | Size | Purpose |
|---------|------|---------|
| `analyzer.py` | 59KB | Technical analysis, ASI calculation, multi-timeframe |
| `onchain_collector.py` | 60KB | Whale tracking, DAU, holder analysis |
| `database.py` | 47KB | PostgreSQL operations, all DB functions |
| `data_fetcher.py` | 37KB | CoinGecko, Binance, OKX price fetching |
| `gemini.py` | 30KB | Google Gemini AI integration |
| `scheduler.py` | 25KB | Background jobs (fetcher, analyzer, OHLCV) |
| `price_aggregator.py` | 18KB | Multi-source price aggregation |
| `ai_service.py` | 16KB | AI provider abstraction (Gemini/DeepSeek) |

---

## 4. API Endpoints (15 files)

| Endpoint | Purpose |
|----------|---------|
| `/api/market` | Market data, top coins |
| `/api/sentiment` | ASI scores, signals |
| `/api/onchain` | Whale activity, network metrics |
| `/api/portfolio` | User portfolios |
| `/api/auth` | Authentication |
| `/api/admin/*` | Admin panel APIs |

---

## 5. Frontend Components

### Mobile (11 components)
- `MobileDashboard.vue` - Main dashboard with treemap, gainers/losers
- `MobileMarket.vue` - Market overview
- `MobileAnalysis.vue` - Coin analysis with AI insights
- `MobileShadow.vue` - Whale-crowd divergence
- `MobileAIChat.vue` - AI chat assistant

### Desktop (6 components)
- `DesktopDashboard.vue` - Desktop dashboard
- `DesktopAnalysis.vue` - Full analysis view
- `DesktopMarket.vue` - Market tables

### Shared
- `SharedMobileHeader.vue` - Synchronized mobile header
- `SharedBottomNav.vue` - Bottom navigation

---

## 6. Key Features

### ASI Score (Composite)
```
composite_asi = tech_asi × 0.60 + sentiment_asi × 0.25 + onchain_asi × 0.15
```

| Component | Weight | Source |
|-----------|--------|--------|
| Technical | 60% | Multi-timeframe (1h, 4h, 1d, 1w, 1M) |
| Sentiment | 25% | AI news analysis |
| On-chain | 15% | Whale activity, DAU |

### Multi-Horizon Analysis
- **Short (1h):** Scalp/Day trade
- **Medium (4h+1d):** Swing trade
- **Long (1w+1M):** Position/HODL

### On-chain Signals
- Whale transaction tracking (>$100K)
- Daily Active Users (DAU)
- Top holder changes
- Exchange inflow/outflow

---

## 7. Database Schema

### Core Tables
| Table | Purpose |
|-------|---------|
| `aihub_coins` | Coin data, prices, sparklines |
| `aihub_sentiment` | AI sentiment scores |
| `onchain_signals` | Whale/DAU/holder metrics |
| `behavioral_sentiment` | News sentiment from AI |
| `ohlcv_1h`, `ohlcv_4h`, `ohlcv_1d`, `ohlcv_1w` | Candle data |

---

## 8. Scheduler Jobs

| Job | Interval | Purpose |
|-----|----------|---------|
| `fetcher` | 3 min | Fetch market data |
| `ai_workers` | 30 min | AI sentiment analysis |
| `onchain_collector` | 30 min | Whale/DAU collection |
| `multi_horizon` | 5 min | Pre-compute ASI (top 50) |
| `ohlcv_4h` | 4 hours | Fetch 4h candles |
| `ohlcv_1d` | 24 hours | Fetch daily candles |

---

## 9. Recent Changes (2025-12-21)

1. **Composite ASI Implementation**
   - Multi-timeframe + sentiment + on-chain blend
   - Dynamic weight adjustment

2. **Analysis Module Redesign**
   - Market Mood gauge
   - Quick Analyze chips
   - Trending coins section

3. **Real Sparklines**
   - Using `sparkline_7d` from CoinGecko
   - `useSparkline` composable

4. **Migration v8**
   - Added `contract_address` to `aihub_coins`
   - Sync on-chain tables to Supabase

---

## 10. Deployment

### Production (Proxmox)
```bash
cd /opt/aicryptohub-pro && git pull
docker compose -f infrastructure/docker-compose.yml build
docker compose -f infrastructure/docker-compose.yml up -d
```

### Run Migrations
```bash
psql -U aihub_pro -d aihub_pro -f backend/sql/migration_v8_onchain_supabase.sql
```

---

## 11. Git Commits (Recent)

| Commit | Message |
|--------|---------|
| `e2a3adec` | feat: add migration v8 for on-chain tables |
| `8738b7b0` | feat: implement composite ASI |
| `e932e610` | feat: redesign Analysis module |
| `182501cc` | feat: implement real sparkline data |

---

## 12. Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# AI Providers
GEMINI_API_KEY=...
DEEPSEEK_API_KEY=...

# Data Sources
COINGECKO_API_KEY=...
ETHERSCAN_API_KEY=...

# Real-time
BINANCE_WS_URL=wss://stream.binance.com:9443/ws
```

---

**End of Report**
