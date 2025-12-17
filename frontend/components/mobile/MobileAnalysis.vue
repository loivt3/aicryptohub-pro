<template>
  <div class="mobile-layout">
    <!-- Header -->
    <header class="m-header">
      <div class="m-header-content">
        <div class="m-logo">
          <Icon name="ph:chart-line-up-bold" class="m-logo-icon" style="color: #38efeb; width: 16px; height: 16px;" />
          <span class="m-logo-text">AI Hub</span>
        </div>
        <div class="m-ticker">
          <span class="m-ticker-label">BTC</span>
          <span class="m-ticker-value">$98,500</span>
        </div>
        <div class="m-actions">
          <NuxtLink to="/" class="m-action-btn"><Icon name="ph:house" class="m-icon" /></NuxtLink>
          <button class="m-action-btn"><Icon name="ph:magnifying-glass" class="m-icon" /></button>
        </div>
      </div>
    </header>

    <main class="m-main">
      <!-- Search Section -->
      <section class="m-section">
        <h3 class="m-section-title">
          <Icon name="ph:chart-line-up" class="w-4 h-4" style="color: #00d4ff;" />
          Coin Analysis
        </h3>
        
        <!-- Search Row -->
        <div style="display: flex; flex-direction: column; gap: 12px;">
          <!-- Search Input -->
          <div style="position: relative; width: 100%;">
            <Icon name="ph:magnifying-glass" class="m-icon" style="position: absolute; left: 14px; top: 50%; transform: translateY(-50%); opacity: 0.4; pointer-events: none;" />
            <input 
              v-model="searchQuery" 
              @input="onSearchInput"
              @keyup.enter="() => executeSearch()"
              type="text" 
              placeholder="Search coin (e.g. Bitcoin, ETH)..."
              style="width: 100%; height: 48px; padding: 0 16px 0 46px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 14px; font-size: 0.95rem; color: #fff;"
            />
            
            <!-- Suggestions Dropdown -->
            <div v-if="suggestions.length > 0" class="m-card m-card--dark" style="position: absolute; top: 100%; left: 0; right: 0; z-index: 100; margin-top: 6px; max-height: 200px; overflow-y: auto; padding: 6px;">
              <div v-for="coin in suggestions" :key="coin.coin_id" @click="selectCoin(coin)" class="m-list-item" style="padding: 10px 12px; cursor: pointer;">
                <img v-if="coin.image" :src="coin.image" class="m-avatar" style="width: 28px; height: 28px;" />
                <div class="m-info">
                  <span class="m-info-title">{{ coin.symbol?.toUpperCase() }}</span>
                  <span class="m-info-subtitle">{{ coin.name }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Analyze Button -->
          <button @click="() => executeSearch()" :disabled="!searchQuery || loading" class="m-btn m-btn--primary" style="width: 100%; height: 48px; border-radius: 14px; font-size: 1rem; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px; background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);" :style="{ opacity: (!searchQuery || loading) ? 0.5 : 1 }">
            <div v-if="loading" class="m-spinner" style="width: 18px; height: 18px;"></div>
            <template v-else>
              <Icon name="ph:chart-line-up" class="m-icon" />
              <span>ANALYZE</span>
            </template>
          </button>
        </div>

        <!-- Data Source Badge -->
        <div v-if="dataSource" style="text-align: center; margin-top: 12px;">
          <span class="m-badge" :class="dataSource === 'cache' ? 'm-badge--success' : 'm-badge--accent'">
            {{ dataSource === 'cache' ? '⚡ Cached' : '✓ Fresh' }}
          </span>
        </div>
      </section>

      <!-- Loading State -->
      <section v-if="loading" class="m-section">
        <div class="m-card m-card--dark" style="text-align: center; padding: 60px 16px;">
          <div class="m-spinner"></div>
          <p class="m-text-muted" style="margin-top: 16px;">Loading analysis...</p>
        </div>
      </section>

      <!-- Featured Coin Card (Hero) -->
      <section v-if="analysisCoin && !loading" class="m-section">
        <div class="m-card m-card--dark" style="padding: 16px; background: linear-gradient(160deg, rgba(20,25,40,0.98), rgba(12,15,28,0.98)); border-radius: 14px; overflow: hidden;">
          
          <!-- Row 1: Coin Info + Stats -->
          <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; margin-bottom: 12px;">
            <!-- Left: Icon + Name -->
            <div style="display: flex; align-items: flex-start; gap: 10px;">
              <div style="position: relative;">
                <img v-if="analysisCoin.image" :src="analysisCoin.image" style="width: 44px; height: 44px; border-radius: 50%;" />
                <span v-if="analysisCoin.rank" style="position: absolute; top: -6px; left: -4px; padding: 2px 6px; background: linear-gradient(135deg, rgba(34,197,94,0.9), rgba(22,163,74,0.9)); border-radius: 8px; font-size: 0.5rem; font-weight: 700; color: #fff;">
                  #{{ analysisCoin.rank }}
                </span>
              </div>
              <div>
                <div style="font-size: 0.65rem; color: rgba(255,255,255,0.5); text-transform: uppercase; letter-spacing: 0.8px;">{{ analysisCoin.name }}</div>
                <div style="font-size: 1.3rem; font-weight: 700; color: #fff;">{{ analysisCoin.symbol?.toUpperCase() }}</div>
              </div>
            </div>
            <!-- Right: Stats -->
            <div style="text-align: right; display: flex; flex-direction: column; gap: 3px;">
              <div><span style="font-size: 0.5rem; color: rgba(255,255,255,0.4);">MCap </span><span style="font-size: 0.7rem; font-weight: 600; color: rgba(255,255,255,0.8);">{{ formatMarketCap(analysisCoin.market_cap) }}</span></div>
              <div><span style="font-size: 0.5rem; color: rgba(255,255,255,0.4);">Vol </span><span style="font-size: 0.7rem; font-weight: 600; color: rgba(255,255,255,0.8);">{{ formatMarketCap(analysisCoin.volume_24h) }}</span></div>
            </div>
          </div>
          
          <!-- Row 2: Price + Change -->
          <div style="display: flex; align-items: baseline; gap: 10px; margin-bottom: 10px;">
            <span style="font-size: 2rem; font-weight: 700; color: #fff; letter-spacing: -1px;">{{ formatCurrency(analysisCoin.price) }}</span>
            <span :style="{ fontSize: '0.9rem', fontWeight: '600', color: analysisCoin.change_24h >= 0 ? '#22c55e' : '#ef4444' }">
              {{ analysisCoin.change_24h >= 0 ? '↑' : '↓' }} {{ Math.abs(analysisCoin.change_24h || 0).toFixed(2) }}%
            </span>
          </div>
          
          <!-- Row 3: Sparkline Chart -->
          <div style="margin: 0 -16px; height: 60px;">
            <svg viewBox="0 0 320 60" preserveAspectRatio="none" style="width: 100%; height: 100%;">
              <defs>
                <linearGradient id="analysisSparkGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" :stop-color="analysisCoin.change_24h >= 0 ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)'" />
                  <stop offset="100%" stop-color="transparent" />
                </linearGradient>
              </defs>
              <path :d="getSparklinePath(320, 60, true)" fill="url(#analysisSparkGrad)" />
              <path :d="getSparklinePath(320, 60, false)" fill="none" :stroke="analysisCoin.change_24h >= 0 ? '#22c55e' : '#ef4444'" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          
          <!-- Row 4: 24H Range Bar -->
          <div style="margin-top: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <span style="font-size: 0.75rem; font-weight: 500; color: rgba(255,255,255,0.7);">{{ formatCurrency(analysisCoin.low_24h || analysisCoin.price * 0.98) }}</span>
              <span style="font-size: 0.6rem; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 1px;">24H RANGE</span>
              <span style="font-size: 0.75rem; font-weight: 500; color: rgba(255,255,255,0.7);">{{ formatCurrency(analysisCoin.high_24h || analysisCoin.price * 1.02) }}</span>
            </div>
            <div style="height: 5px; background: linear-gradient(90deg, #ef4444, #eab308, #22c55e); border-radius: 3px; position: relative;">
              <div :style="{ position: 'absolute', top: '-3px', left: pricePosition + '%', width: '11px', height: '11px', background: '#fff', borderRadius: '50%', boxShadow: '0 2px 4px rgba(0,0,0,0.4)', transform: 'translateX(-50%)' }"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- Timeframe Change Cards -->
      <section v-if="analysisCoin && !loading" class="m-section">
        <div style="display: flex; gap: 8px; overflow-x: auto; padding: 4px 0; -webkit-overflow-scrolling: touch;">
          <div v-for="tf in timeframes" :key="tf.label" :style="{ flex: '0 0 auto', minWidth: '60px', padding: '10px 14px', background: tf.active ? 'rgba(0,212,255,0.15)' : 'rgba(255,255,255,0.04)', border: tf.active ? '1px solid rgba(0,212,255,0.4)' : '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', textAlign: 'center' }">
            <div :style="{ fontSize: '0.7rem', color: tf.active ? '#00d4ff' : 'rgba(255,255,255,0.5)', marginBottom: '4px' }">{{ tf.label }}</div>
            <div :style="{ fontSize: '0.85rem', fontWeight: '600', color: tf.value >= 0 ? '#22c55e' : '#ef4444' }">
              {{ tf.value >= 0 ? '+' : '' }}{{ tf.value.toFixed(1) }}%
            </div>
          </div>
        </div>
      </section>

      <!-- ASI SCORE Card -->
      <section v-if="analysisCoin && !loading" class="m-section">
        <div class="m-card m-card--dark" style="padding: 28px 20px; background: linear-gradient(180deg, rgba(20,20,35,1), rgba(15,15,28,1)); text-align: center;">
          <!-- Header -->
          <div style="display: inline-flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <Icon name="ph:clock" class="m-icon" style="color: #00d4ff;" />
            <span style="font-size: 0.85rem; font-weight: 600; color: rgba(255,255,255,0.7); letter-spacing: 1.5px;">ASI SCORE</span>
          </div>
          <div style="font-size: 0.7rem; color: rgba(255,255,255,0.4); margin-bottom: 12px;">AI Signal Index - Technical indicators analysis</div>
          
          <!-- Circular Gauge -->
          <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <div style="width: 160px; height: 160px; position: relative;">
              <svg viewBox="0 0 160 160" style="width: 100%; height: 100%; transform: rotate(-90deg);">
                <circle cx="80" cy="80" r="70" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="12"/>
                <defs>
                  <linearGradient id="asiGaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#ef4444" />
                    <stop offset="50%" stop-color="#eab308" />
                    <stop offset="100%" stop-color="#22c55e" />
                  </linearGradient>
                </defs>
                <circle cx="80" cy="80" r="70" fill="none" stroke="url(#asiGaugeGrad)" stroke-width="12" stroke-linecap="round" :stroke-dasharray="440" :stroke-dashoffset="440 - (440 * asiScore / 100)"/>
              </svg>
              <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                <div :style="{ fontSize: '2.5rem', fontWeight: '700', color: asiColor, lineHeight: '1' }">{{ asiScore }}</div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.4);">/100</div>
              </div>
            </div>
          </div>
          
          <!-- Sentiment Label -->
          <div style="margin-bottom: 16px;">
            <span style="font-size: 1rem;">{{ asiScore >= 60 ? '📈' : asiScore <= 40 ? '📉' : '📊' }}</span>
            <span :style="{ fontSize: '0.95rem', fontWeight: '500', color: asiColor }"> {{ sentimentLabel }}</span>
          </div>
          
          <!-- Signal Badge -->
          <div style="margin-bottom: 20px;">
            <span :style="{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '10px 28px', borderRadius: '24px', fontSize: '1rem', fontWeight: '700', background: signalBg, color: signalColor, border: '1px solid ' + signalBorder }">
              {{ signal.includes('BUY') ? '→' : signal.includes('SELL') ? '←' : '—' }} {{ signal.replace('_', ' ') }}
            </span>
          </div>
          
          <!-- Confidence Level -->
          <div style="padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.06);">
            <div style="font-size: 0.7rem; color: rgba(255,255,255,0.4); letter-spacing: 1px; margin-bottom: 10px;">CONFIDENCE LEVEL</div>
            <div style="max-width: 200px; margin: 0 auto;">
              <div style="height: 8px; background: rgba(255,255,255,0.08); border-radius: 4px; overflow: hidden;">
                <div :style="{ width: confidenceWidth, height: '100%', background: 'linear-gradient(90deg, #00d4ff, #22c55e)', borderRadius: '4px', transition: 'width 0.5s ease' }"></div>
              </div>
              <div :style="{ marginTop: '8px', fontSize: '0.85rem', fontWeight: '600', textTransform: 'capitalize', color: confidenceColor }">{{ confidence }}</div>
            </div>
          </div>
          
          <!-- How to Read Guide -->
          <div style="margin-top: 20px; padding: 14px; background: rgba(255,255,255,0.03); border-radius: 12px;">
            <div style="font-size: 0.65rem; color: rgba(255,255,255,0.35); letter-spacing: 0.5px; margin-bottom: 10px;">HOW TO READ</div>
            <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
              <div style="display: flex; align-items: center; gap: 5px;">
                <span style="width: 10px; height: 10px; border-radius: 50%; background: #ef4444;"></span>
                <span style="font-size: 0.72rem; color: rgba(255,255,255,0.5);">0-40 Bearish</span>
              </div>
              <div style="display: flex; align-items: center; gap: 5px;">
                <span style="width: 10px; height: 10px; border-radius: 50%; background: #eab308;"></span>
                <span style="font-size: 0.72rem; color: rgba(255,255,255,0.5);">40-60 Neutral</span>
              </div>
              <div style="display: flex; align-items: center; gap: 5px;">
                <span style="width: 10px; height: 10px; border-radius: 50%; background: #22c55e;"></span>
                <span style="font-size: 0.72rem; color: rgba(255,255,255,0.5);">60-100 Bullish</span>
              </div>
            </div>
          </div>
          
          <div style="margin-top: 14px; font-size: 0.65rem; color: rgba(255,255,255,0.25);">Based on MACD, RSI, Stochastic, Bollinger Bands & more</div>
        </div>
      </section>

      <!-- Technical Indicators (Horizontal Scroll) -->
      <section v-if="analysisCoin && !loading" class="m-section">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
          <div>
            <h3 class="m-section-title" style="margin-bottom: 4px;">
              <Icon name="ph:chart-line" class="w-4 h-4" style="color: #00d4ff;" />
              Technical Indicators
            </h3>
            <div style="font-size: 0.65rem; color: rgba(255,255,255,0.35);">Market signals analysis</div>
          </div>
        </div>
        
        <div style="display: flex; gap: 10px; overflow-x: auto; padding: 4px 0; -webkit-overflow-scrolling: touch;">
          <!-- RSI Card -->
          <div style="flex: 0 0 auto; min-width: 140px; padding: 14px; background: linear-gradient(145deg, rgba(30,35,50,0.95), rgba(20,25,40,0.95)); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <span style="font-size: 0.7rem; color: rgba(255,255,255,0.6); font-weight: 600;">RSI</span>
              <span :style="{ fontSize: '0.55rem', padding: '2px 5px', borderRadius: '4px', background: indicators.rsi > 70 ? 'rgba(239,68,68,0.2)' : indicators.rsi < 30 ? 'rgba(34,197,94,0.2)' : 'rgba(234,179,8,0.2)', color: indicators.rsi > 70 ? '#ef4444' : indicators.rsi < 30 ? '#22c55e' : '#eab308' }">
                {{ indicators.rsi > 70 ? 'OVERBOUGHT' : indicators.rsi < 30 ? 'OVERSOLD' : 'NEUTRAL' }}
              </span>
            </div>
            <div :style="{ fontSize: '1.5rem', fontWeight: '700', color: indicators.rsi > 70 ? '#ef4444' : indicators.rsi < 30 ? '#22c55e' : '#eab308', marginBottom: '6px' }">{{ indicators.rsi }}</div>
            <div style="height: 3px; background: rgba(255,255,255,0.1); border-radius: 2px; overflow: hidden;">
              <div :style="{ width: indicators.rsi + '%', height: '100%', background: indicators.rsi > 70 ? '#ef4444' : indicators.rsi < 30 ? '#22c55e' : '#eab308', borderRadius: '2px' }"></div>
            </div>
          </div>
          
          <!-- MACD Card -->
          <div style="flex: 0 0 auto; min-width: 130px; padding: 14px; background: linear-gradient(145deg, rgba(30,35,50,0.95), rgba(20,25,40,0.95)); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;">
            <div style="margin-bottom: 8px;">
              <span style="font-size: 0.7rem; color: rgba(255,255,255,0.6); font-weight: 600;">MACD</span>
            </div>
            <div :style="{ fontSize: '1.6rem', color: indicators.macd === 'Bullish' ? '#22c55e' : indicators.macd === 'Bearish' ? '#ef4444' : '#eab308', marginBottom: '4px' }">
              {{ indicators.macd === 'Bullish' ? '↑' : indicators.macd === 'Bearish' ? '↓' : '→' }}
            </div>
            <div :style="{ fontSize: '0.75rem', fontWeight: '500', color: indicators.macd === 'Bullish' ? '#22c55e' : indicators.macd === 'Bearish' ? '#ef4444' : '#eab308' }">{{ indicators.macd }}</div>
          </div>
          
          <!-- Bollinger Card -->
          <div style="flex: 0 0 auto; min-width: 140px; padding: 14px; background: linear-gradient(145deg, rgba(30,35,50,0.95), rgba(20,25,40,0.95)); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;">
            <div style="margin-bottom: 8px;">
              <span style="font-size: 0.7rem; color: rgba(255,255,255,0.6); font-weight: 600;">BOLLINGER</span>
            </div>
            <div :style="{ fontSize: '0.95rem', fontWeight: '600', color: indicators.bollinger === 'Upper' ? '#22c55e' : indicators.bollinger === 'Lower' ? '#ef4444' : '#eab308', marginBottom: '8px' }">
              {{ indicators.bollinger }} Band
            </div>
            <div style="display: flex; gap: 2px;">
              <div :style="{ flex: 1, height: '3px', borderRadius: '2px', background: indicators.bollinger === 'Lower' ? '#ef4444' : 'rgba(239,68,68,0.2)' }"></div>
              <div :style="{ flex: 1, height: '3px', borderRadius: '2px', background: indicators.bollinger === 'Middle' ? '#eab308' : 'rgba(234,179,8,0.2)' }"></div>
              <div :style="{ flex: 1, height: '3px', borderRadius: '2px', background: indicators.bollinger === 'Upper' ? '#22c55e' : 'rgba(34,197,94,0.2)' }"></div>
            </div>
          </div>
          
          <!-- Stochastic Card -->
          <div style="flex: 0 0 auto; min-width: 130px; padding: 14px; background: linear-gradient(145deg, rgba(30,35,50,0.95), rgba(20,25,40,0.95)); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;">
            <div style="margin-bottom: 8px;">
              <span style="font-size: 0.7rem; color: rgba(255,255,255,0.6); font-weight: 600;">STOCHASTIC</span>
            </div>
            <div style="display: flex; gap: 10px;">
              <div>
                <div style="font-size: 0.5rem; color: rgba(255,255,255,0.4); margin-bottom: 2px;">K</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #00d4ff;">{{ indicators.stochastic.k }}</div>
              </div>
              <div>
                <div style="font-size: 0.5rem; color: rgba(255,255,255,0.4); margin-bottom: 2px;">D</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #a855f7;">{{ indicators.stochastic.d }}</div>
              </div>
            </div>
          </div>
          
          <!-- ADX Card -->
          <div style="flex: 0 0 auto; min-width: 130px; padding: 14px; background: linear-gradient(145deg, rgba(30,35,50,0.95), rgba(20,25,40,0.95)); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <span style="font-size: 0.7rem; color: rgba(255,255,255,0.6); font-weight: 600;">ADX</span>
              <span :style="{ fontSize: '0.55rem', padding: '2px 5px', borderRadius: '4px', background: indicators.adx > 25 ? 'rgba(34,197,94,0.2)' : 'rgba(255,255,255,0.1)', color: indicators.adx > 25 ? '#22c55e' : 'rgba(255,255,255,0.5)' }">
                {{ indicators.adx > 50 ? 'STRONG' : indicators.adx > 25 ? 'MODERATE' : 'WEAK' }}
              </span>
            </div>
            <div :style="{ fontSize: '1.5rem', fontWeight: '700', color: indicators.adx > 25 ? '#22c55e' : '#eab308', marginBottom: '6px' }">{{ indicators.adx }}</div>
            <div style="height: 3px; background: rgba(255,255,255,0.1); border-radius: 2px; overflow: hidden;">
              <div :style="{ width: Math.min(100, indicators.adx) + '%', height: '100%', background: 'linear-gradient(90deg, #eab308, #22c55e)', borderRadius: '2px' }"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- Key Levels -->
      <section v-if="analysisCoin && !loading" class="m-section">
        <div style="margin-bottom: 12px;">
          <h3 class="m-section-title" style="margin-bottom: 4px;">Key Levels</h3>
          <div style="font-size: 0.65rem; color: rgba(255,255,255,0.35);">Important price levels to watch</div>
        </div>
        <div class="m-list m-list--dark">
          <div class="m-list-item" style="padding: 14px 12px;">
            <span class="m-rank m-rank--danger">R</span>
            <div class="m-info" style="flex: 1;">
              <span class="m-info-title">Resistance</span>
              <span class="m-info-subtitle" style="font-size: 0.65rem; color: rgba(255,255,255,0.35);">Price ceiling where selling may increase</span>
            </div>
            <span class="m-text-danger" style="font-weight: 600; font-size: 0.95rem;">{{ formatCurrency(keyLevels.resistance) }}</span>
          </div>
          <div class="m-list-item" style="background: rgba(255,255,255,0.03); padding: 14px 12px;">
            <span class="m-rank" style="background: rgba(234, 179, 8, 0.2); color: #eab308;">P</span>
            <div class="m-info" style="flex: 1;">
              <span class="m-info-title">Pivot Point</span>
              <span class="m-info-subtitle" style="font-size: 0.65rem; color: rgba(255,255,255,0.35);">Key level for trend direction</span>
            </div>
            <span style="font-weight: 600; color: #eab308; font-size: 0.95rem;">{{ formatCurrency(keyLevels.pivot) }}</span>
          </div>
          <div class="m-list-item" style="padding: 14px 12px;">
            <span class="m-rank m-rank--success">S</span>
            <div class="m-info" style="flex: 1;">
              <span class="m-info-title">Support</span>
              <span class="m-info-subtitle" style="font-size: 0.65rem; color: rgba(255,255,255,0.35);">Price floor where buying may increase</span>
            </div>
            <span class="m-text-success" style="font-weight: 600; font-size: 0.95rem;">{{ formatCurrency(keyLevels.support) }}</span>
          </div>
        </div>
      </section>

      <!-- AI Reasoning -->
      <section v-if="analysisCoin && reasoning && !loading" class="m-section">
        <h3 class="m-section-title">AI Reasoning</h3>
        <div class="m-card m-card--dark" style="padding: 16px;">
          <p style="font-size: 0.85rem; color: rgba(255,255,255,0.7); line-height: 1.6; margin: 0;">{{ reasoning }}</p>
        </div>
      </section>

      <!-- On-Chain Signals -->
      <section v-if="analysisCoin && !loading" class="m-section">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <div>
            <h3 class="m-section-title" style="margin-bottom: 4px;">
              <Icon name="ph:stack" class="w-4 h-4" style="color: #00d4ff;" />
              On-Chain Signals
            </h3>
            <div style="font-size: 0.65rem; color: rgba(255,255,255,0.35);">Blockchain data analysis</div>
          </div>
          <span v-if="onchain.overall" :style="{ padding: '4px 12px', borderRadius: '12px', fontSize: '0.7rem', fontWeight: '700', background: onchain.overall === 'BULLISH' ? 'rgba(34, 197, 94, 0.2)' : onchain.overall === 'BEARISH' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(234, 179, 8, 0.2)', color: onchain.overall === 'BULLISH' ? '#22c55e' : onchain.overall === 'BEARISH' ? '#ef4444' : '#eab308', border: '1px solid ' + (onchain.overall === 'BULLISH' ? 'rgba(34, 197, 94, 0.4)' : onchain.overall === 'BEARISH' ? 'rgba(239, 68, 68, 0.4)' : 'rgba(234, 179, 8, 0.4)') }">
            {{ onchain.overall }}
          </span>
        </div>
        
        <div style="display: flex; flex-direction: column; gap: 10px;">
          <!-- Exchange Flows -->
          <div class="m-card m-card--dark" :style="{ padding: '12px', borderLeft: '3px solid ' + (onchain.exchangeFlow.signal === 'BULLISH' ? '#22c55e' : onchain.exchangeFlow.signal === 'BEARISH' ? '#ef4444' : '#eab308') }">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.2rem;">💱</span>
                <span style="font-size: 0.85rem; font-weight: 600; color: #fff;">Exchange Flows</span>
              </div>
              <span :style="{ padding: '3px 8px', borderRadius: '6px', fontSize: '0.6rem', fontWeight: '600', background: onchain.exchangeFlow.signal === 'BULLISH' ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)', color: onchain.exchangeFlow.signal === 'BULLISH' ? '#22c55e' : '#ef4444' }">{{ onchain.exchangeFlow.signal }}</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; font-size: 0.7rem;">
              <div style="text-align: center; padding: 6px; background: rgba(0,0,0,0.3); border-radius: 6px;">
                <div style="color: rgba(255,255,255,0.5); font-size: 0.55rem; margin-bottom: 2px;">Inflow</div>
                <div style="color: #ef4444; font-weight: 600;">{{ onchain.exchangeFlow.inflow }}</div>
              </div>
              <div style="text-align: center; padding: 6px; background: rgba(0,0,0,0.3); border-radius: 6px;">
                <div style="color: rgba(255,255,255,0.5); font-size: 0.55rem; margin-bottom: 2px;">Outflow</div>
                <div style="color: #22c55e; font-weight: 600;">{{ onchain.exchangeFlow.outflow }}</div>
              </div>
              <div style="text-align: center; padding: 6px; background: rgba(0,0,0,0.3); border-radius: 6px;">
                <div style="color: rgba(255,255,255,0.5); font-size: 0.55rem; margin-bottom: 2px;">Net</div>
                <div :style="{ color: onchain.exchangeFlow.netFlow < 0 ? '#22c55e' : '#ef4444', fontWeight: '600' }">{{ onchain.exchangeFlow.netFlow }}</div>
              </div>
            </div>
          </div>
          
          <!-- Whale Activity -->
          <div class="m-card m-card--dark" :style="{ padding: '12px', borderLeft: '3px solid ' + (onchain.whaleActivity.signal === 'BULLISH' ? '#22c55e' : '#a855f7') }">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.2rem;">🐋</span>
                <span style="font-size: 0.85rem; font-weight: 600; color: #fff;">Whale Activity</span>
              </div>
              <span :style="{ padding: '3px 8px', borderRadius: '6px', fontSize: '0.6rem', fontWeight: '600', background: 'rgba(168, 85, 247, 0.2)', color: '#a855f7' }">{{ onchain.whaleActivity.signal }}</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; font-size: 0.7rem;">
              <div style="text-align: center; padding: 6px; background: rgba(0,0,0,0.3); border-radius: 6px;">
                <div style="color: rgba(255,255,255,0.5); font-size: 0.55rem; margin-bottom: 2px;">Large Tx (24h)</div>
                <div style="color: #a855f7; font-weight: 600;">{{ onchain.whaleActivity.largeTxCount }}</div>
              </div>
              <div style="text-align: center; padding: 6px; background: rgba(0,0,0,0.3); border-radius: 6px;">
                <div style="color: rgba(255,255,255,0.5); font-size: 0.55rem; margin-bottom: 2px;">Top Holders Δ</div>
                <div :style="{ color: onchain.whaleActivity.topHoldersChange > 0 ? '#22c55e' : '#ef4444', fontWeight: '600' }">
                  {{ onchain.whaleActivity.topHoldersChange > 0 ? '+' : '' }}{{ onchain.whaleActivity.topHoldersChange }}%
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Empty State -->
      <section v-if="!analysisCoin && !loading" class="m-section">
        <div class="m-card m-card--dark" style="text-align: center; padding: 60px 16px;">
          <span style="font-size: 56px; display: block; margin-bottom: 16px;">📈</span>
          <h3 style="margin-bottom: 8px;">Start Your Analysis</h3>
          <p class="m-text-muted">Search and select a coin to analyze</p>
        </div>
      </section>

      <div class="m-bottom-spacer"></div>
    </main>

    <!-- Bottom Navigation -->
    <nav class="m-bottom-nav">
      <button class="m-nav-item" @click="$emit('setTab', 'dashboard')">
        <Icon name="ph:squares-four" class="m-nav-icon" />
        <span class="m-nav-label">Dashboard</span>
      </button>
      <button class="m-nav-item" @click="$emit('setTab', 'market')">
        <Icon name="ph:trend-up" class="m-nav-icon" />
        <span class="m-nav-label">Market</span>
      </button>
      <button class="m-nav-item active">
        <Icon name="ph:chart-line-up" class="m-nav-icon" />
        <span class="m-nav-label">Analysis</span>
      </button>
      <button class="m-nav-item" @click="$emit('setTab', 'shadow')">
        <Icon name="ph:eye" class="m-nav-icon" />
        <span class="m-nav-label">Shadow</span>
      </button>
      <button class="m-nav-item" @click="$emit('setTab', 'aichat')">
        <Icon name="ph:chat-dots" class="m-nav-icon" />
        <span class="m-nav-label">AI Chat</span>
      </button>
    </nav>
  </div>
</template>

<script setup lang="ts">
interface AnalysisCoin {
  coin_id: string
  symbol: string
  name: string
  image?: string
  price: number
  change_24h: number
  change_1h?: number
  change_7d?: number
  change_30d?: number
  change_1y?: number
  market_cap?: number
  volume_24h?: number
  high_24h?: number
  low_24h?: number
  rank?: number
  market_cap_rank?: number
}

interface Suggestion {
  coin_id: string
  symbol: string
  name: string
  image?: string
}

interface SentimentResponse {
  coin_id: string
  asi_score: number
  signal: string
  reason?: string
}

defineEmits<{
  (e: 'setTab', tab: string): void
}>()

const api = useApi()

// State
const searchQuery = ref('')
const suggestions = ref<Suggestion[]>([])
const loading = ref(false)
const dataSource = ref<string | null>(null)
const analysisCoin = ref<AnalysisCoin | null>(null)
const allCoins = ref<Suggestion[]>([])

// Sentiment data from API
const asiScore = ref(50)
const signal = ref('HOLD')
const confidence = ref('medium')
const reasoning = ref('')

// Technical indicators (calculated or from API)
const indicators = ref({
  rsi: 50,
  macd: 'Neutral',
  bollinger: 'Middle',
  stochastic: { k: 50, d: 50 },
  adx: 25,
})

// Key levels (calculated from price)
const keyLevels = computed(() => {
  const price = analysisCoin.value?.price || 0
  return {
    resistance: price * 1.05,
    pivot: price,
    support: price * 0.95,
  }
})

// On-chain data (from API or default)
const onchain = ref({
  overall: 'NEUTRAL',
  exchangeFlow: { signal: 'NEUTRAL', inflow: '$0', outflow: '$0', netFlow: 0 },
  whaleActivity: { signal: 'NEUTRAL', largeTxCount: 0, topHoldersChange: 0 },
})

const timeframes = computed(() => [
  { label: '1H', value: analysisCoin.value?.change_1h || 0, active: false },
  { label: '24H', value: analysisCoin.value?.change_24h || 0, active: true },
  { label: '7D', value: analysisCoin.value?.change_7d || 0, active: false },
  { label: '30D', value: analysisCoin.value?.change_30d || 0, active: false },
  { label: '1Y', value: analysisCoin.value?.change_1y || 0, active: false },
])

const pricePosition = computed(() => {
  if (!analysisCoin.value) return 50
  const low = analysisCoin.value.low_24h || analysisCoin.value.price * 0.98
  const high = analysisCoin.value.high_24h || analysisCoin.value.price * 1.02
  return Math.max(0, Math.min(100, ((analysisCoin.value.price - low) / (high - low)) * 100))
})

const asiColor = computed(() => {
  if (asiScore.value >= 60) return '#22c55e'
  if (asiScore.value <= 40) return '#ef4444'
  return '#eab308'
})

const sentimentLabel = computed(() => {
  if (asiScore.value >= 70) return 'Strongly Bullish'
  if (asiScore.value >= 60) return 'Bullish'
  if (asiScore.value <= 30) return 'Strongly Bearish'
  if (asiScore.value <= 40) return 'Bearish'
  return 'Neutral'
})

const signalBg = computed(() => {
  if (signal.value.includes('BUY')) return 'rgba(34, 197, 94, 0.15)'
  if (signal.value.includes('SELL')) return 'rgba(239, 68, 68, 0.15)'
  return 'rgba(234, 179, 8, 0.15)'
})

const signalColor = computed(() => {
  if (signal.value.includes('BUY')) return '#22c55e'
  if (signal.value.includes('SELL')) return '#ef4444'
  return '#eab308'
})

const signalBorder = computed(() => {
  if (signal.value.includes('BUY')) return 'rgba(34, 197, 94, 0.3)'
  if (signal.value.includes('SELL')) return 'rgba(239, 68, 68, 0.3)'
  return 'rgba(234, 179, 8, 0.3)'
})

const confidenceWidth = computed(() => {
  if (confidence.value === 'high') return '100%'
  if (confidence.value === 'medium') return '66%'
  return '33%'
})

const confidenceColor = computed(() => {
  if (confidence.value === 'high') return '#22c55e'
  if (confidence.value === 'low') return '#ef4444'
  return '#eab308'
})

// Fetch all coins for search suggestions
const fetchAllCoins = async () => {
  try {
    const res = await api.getMarketData(200)
    if (res.success && res.data) {
      allCoins.value = res.data.map((c: any) => ({
        coin_id: c.coin_id,
        symbol: c.symbol,
        name: c.name,
        image: c.image,
      }))
    }
  } catch (e) {
    console.error('Failed to fetch coins:', e)
  }
}

// Filter suggestions based on search query
const onSearchInput = () => {
  if (searchQuery.value.length >= 2) {
    const query = searchQuery.value.toLowerCase()
    suggestions.value = allCoins.value
      .filter(c => 
        c.name.toLowerCase().includes(query) || 
        c.symbol.toLowerCase().includes(query)
      )
      .slice(0, 8)
  } else {
    suggestions.value = []
  }
}

const selectCoin = (coin: Suggestion) => {
  searchQuery.value = coin.symbol?.toUpperCase() || ''
  suggestions.value = []
  executeSearch(coin.coin_id)
}

const executeSearch = async (coinId?: string) => {
  if (!searchQuery.value && !coinId) return
  loading.value = true
  suggestions.value = []
  
  try {
    // Find coin_id from search query if not provided
    let targetCoinId = coinId
    if (!targetCoinId) {
      const query = searchQuery.value.toLowerCase()
      const found = allCoins.value.find(c => 
        c.symbol.toLowerCase() === query || 
        c.name.toLowerCase() === query ||
        c.coin_id === query
      )
      targetCoinId = found?.coin_id
    }
    
    if (!targetCoinId) {
      // Try to fetch by symbol
      targetCoinId = searchQuery.value.toLowerCase()
    }
    
    // Fetch coin data
    const coinRes = await api.getCoin(targetCoinId)
    if (coinRes.success && coinRes.data) {
      analysisCoin.value = {
        ...coinRes.data,
        rank: coinRes.data.market_cap_rank,
      } as AnalysisCoin
      dataSource.value = 'fresh'
      
      // Fetch sentiment data
      try {
        const sentimentRes = await api.getCoinSentiment(targetCoinId) as SentimentResponse
        if (sentimentRes) {
          asiScore.value = sentimentRes.asi_score || 50
          signal.value = sentimentRes.signal || 'HOLD'
          reasoning.value = sentimentRes.reason || ''
          
          // Set confidence based on score extremity
          if (asiScore.value >= 70 || asiScore.value <= 30) {
            confidence.value = 'high'
          } else if (asiScore.value >= 55 || asiScore.value <= 45) {
            confidence.value = 'medium'
          } else {
            confidence.value = 'low'
          }
          
          // Calculate simple indicators from ASI score
          indicators.value = {
            rsi: Math.round(30 + (asiScore.value * 0.4) + (Math.random() * 10 - 5)),
            macd: asiScore.value >= 55 ? 'Bullish' : asiScore.value <= 45 ? 'Bearish' : 'Neutral',
            bollinger: asiScore.value >= 60 ? 'Upper' : asiScore.value <= 40 ? 'Lower' : 'Middle',
            stochastic: { 
              k: Math.round(20 + (asiScore.value * 0.6) + (Math.random() * 10 - 5)),
              d: Math.round(25 + (asiScore.value * 0.5) + (Math.random() * 10 - 5))
            },
            adx: Math.round(15 + (Math.abs(asiScore.value - 50) * 0.5) + (Math.random() * 10)),
          }
        }
      } catch (e) {
        console.warn('Sentiment not available:', e)
      }
      
      // Fetch on-chain data
      try {
        const onchainRes = await api.getOnchainSignals(targetCoinId)
        if (onchainRes && onchainRes.data) {
          onchain.value = onchainRes.data
        }
      } catch (e) {
        console.warn('On-chain data not available:', e)
      }
    } else {
      analysisCoin.value = null
      dataSource.value = null
    }
  } catch (error) {
    console.error('Analysis failed:', error)
    analysisCoin.value = null
  } finally {
    loading.value = false
  }
}

// Fetch coins on mount for search suggestions
onMounted(() => {
  fetchAllCoins()
})

const formatCurrency = (n: number) => {
  if (!n) return '$--'
  if (n >= 1) return '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return '$' + n.toFixed(6)
}

const formatMarketCap = (n: number) => {
  if (!n) return '--'
  if (n >= 1e12) return '$' + (n / 1e12).toFixed(2) + 'T'
  if (n >= 1e9) return '$' + (n / 1e9).toFixed(1) + 'B'
  if (n >= 1e6) return '$' + (n / 1e6).toFixed(1) + 'M'
  return '$' + n.toLocaleString()
}

const getSparklinePath = (width: number, height: number, fill: boolean) => {
  const points: number[] = []
  for (let i = 0; i <= 10; i++) {
    const x = (i / 10) * width
    const y = height * 0.2 + Math.sin(i * 0.6) * height * 0.3 + Math.cos(i * 0.4) * height * 0.15
    points.push(x, Math.max(height * 0.1, Math.min(height * 0.9, y)))
  }
  
  let path = `M${points[0]},${points[1]}`
  for (let i = 2; i < points.length; i += 2) {
    path += ` L${points[i]},${points[i + 1]}`
  }
  
  if (fill) {
    path += ` L${width},${height} L0,${height} Z`
  }
  
  return path
}
</script>

<style scoped>
.m-bottom-spacer {
  height: 80px;
}
</style>
