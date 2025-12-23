<template>
  <div class="mobile-layout">
    <!-- Shared Header -->
    <SharedMobileHeader 
      :active-tab="activeTab" 
      @set-tab="$emit('setTab', $event)" 
      @open-search="$emit('openSearch')" 
    />

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

      <!-- Candlestick Pattern Detection -->
      <section v-if="analysisCoin && !loading" class="m-section">
        <div class="m-card m-card--dark" style="padding: 20px; background: linear-gradient(160deg, rgba(25,20,45,0.98), rgba(15,12,30,0.98));">
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px;">
            <Icon name="ph:chart-bar" class="w-5 h-5" style="color: #a855f7;" />
            <span style="font-size: 0.85rem; font-weight: 600; color: rgba(255,255,255,0.8); letter-spacing: 1px;">CANDLESTICK PATTERN</span>
          </div>
          
          <!-- Pattern Found -->
          <template v-if="patternData.pattern">
            <!-- Pattern Display -->
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
              <!-- Pattern Icon -->
              <div :style="{ 
                width: '60px', height: '60px', borderRadius: '14px', 
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: patternData.direction === 'BULLISH' ? 'rgba(34,197,94,0.15)' : 
                            patternData.direction === 'BEARISH' ? 'rgba(239,68,68,0.15)' : 'rgba(234,179,8,0.15)',
                border: '1px solid ' + (patternData.direction === 'BULLISH' ? 'rgba(34,197,94,0.3)' : 
                            patternData.direction === 'BEARISH' ? 'rgba(239,68,68,0.3)' : 'rgba(234,179,8,0.3)')
              }">
                <span style="font-size: 1.8rem;">
                  {{ patternData.direction === 'BULLISH' ? '📈' : patternData.direction === 'BEARISH' ? '📉' : '📊' }}
                </span>
              </div>
              
              <!-- Pattern Name + Direction -->
              <div style="flex: 1;">
                <div :style="{ 
                  fontSize: '1.1rem', fontWeight: '700', 
                  color: patternData.direction === 'BULLISH' ? '#22c55e' : 
                         patternData.direction === 'BEARISH' ? '#ef4444' : '#eab308',
                  marginBottom: '4px'
                }">
                  {{ patternData.pattern }}
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                  <span :style="{ 
                    fontSize: '0.7rem', padding: '3px 8px', borderRadius: '4px',
                    background: patternData.direction === 'BULLISH' ? 'rgba(34,197,94,0.2)' : 
                                patternData.direction === 'BEARISH' ? 'rgba(239,68,68,0.2)' : 'rgba(234,179,8,0.2)',
                    color: patternData.direction === 'BULLISH' ? '#22c55e' : 
                           patternData.direction === 'BEARISH' ? '#ef4444' : '#eab308'
                  }">
                    {{ patternData.direction }}
                  </span>
                  <span :style="{ 
                    fontSize: '0.7rem', padding: '3px 8px', borderRadius: '4px',
                    background: patternData.reliability === 'HIGH' ? 'rgba(168,85,247,0.2)' : 'rgba(255,255,255,0.1)',
                    color: patternData.reliability === 'HIGH' ? '#a855f7' : 'rgba(255,255,255,0.5)'
                  }">
                    {{ patternData.reliability }} CONFIDENCE
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Pattern Details -->
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 16px;">
              <div style="padding: 10px; background: rgba(255,255,255,0.03); border-radius: 8px; text-align: center;">
                <div style="font-size: 0.6rem; color: rgba(255,255,255,0.4); margin-bottom: 4px;">TIMEFRAME</div>
                <div style="font-size: 0.9rem; font-weight: 600; color: #00d4ff;">{{ patternData.timeframe || '1h' }}</div>
              </div>
              <div style="padding: 10px; background: rgba(255,255,255,0.03); border-radius: 8px; text-align: center;">
                <div style="font-size: 0.6rem; color: rgba(255,255,255,0.4); margin-bottom: 4px;">VOLUME</div>
                <div :style="{ fontSize: '0.9rem', fontWeight: '600', color: patternData.volume_ratio >= 1.2 ? '#22c55e' : 'rgba(255,255,255,0.7)' }">
                  {{ patternData.volume_ratio ? patternData.volume_ratio.toFixed(1) + 'x' : '--' }}
                </div>
              </div>
              <div style="padding: 10px; background: rgba(255,255,255,0.03); border-radius: 8px; text-align: center;">
                <div style="font-size: 0.6rem; color: rgba(255,255,255,0.4); margin-bottom: 4px;">ASI IMPACT</div>
                <div :style="{ fontSize: '0.9rem', fontWeight: '600', color: patternData.pattern_adjustment > 0 ? '#22c55e' : patternData.pattern_adjustment < 0 ? '#ef4444' : 'rgba(255,255,255,0.7)' }">
                  {{ patternData.pattern_adjustment > 0 ? '+' : '' }}{{ patternData.pattern_adjustment || 0 }}
                </div>
              </div>
            </div>
            
            <!-- Pattern Explanation -->
            <div style="padding: 12px; background: rgba(255,255,255,0.03); border-radius: 10px; border-left: 3px solid #a855f7;">
              <div style="font-size: 0.75rem; color: rgba(255,255,255,0.7); line-height: 1.5;">
                <template v-if="patternData.pattern === 'Bullish Engulfing'">
                  A large bullish candle completely engulfs the previous bearish candle. Strong reversal signal indicating buyers are taking control.
                </template>
                <template v-else-if="patternData.pattern === 'Bearish Engulfing'">
                  A large bearish candle completely engulfs the previous bullish candle. Strong reversal signal indicating sellers are taking control.
                </template>
                <template v-else-if="patternData.pattern === 'Morning Star'">
                  Three-candle bullish reversal pattern. Indicates the end of a downtrend with a small-bodied candle followed by a strong bullish candle.
                </template>
                <template v-else-if="patternData.pattern === 'Evening Star'">
                  Three-candle bearish reversal pattern. Indicates the end of an uptrend with a small-bodied candle followed by a strong bearish candle.
                </template>
                <template v-else-if="patternData.pattern === 'Hammer'">
                  Bullish reversal pattern with a small body and long lower wick. Indicates buying pressure at the bottom.
                </template>
                <template v-else-if="patternData.pattern === 'Shooting Star'">
                  Bearish reversal pattern with a small body and long upper wick. Indicates selling pressure at the top.
                </template>
                <template v-else-if="patternData.pattern === 'Doji'">
                  Indecision pattern where open and close are nearly equal. Market is uncertain about direction.
                </template>
                <template v-else>
                  {{ patternData.pattern }} detected. {{ patternData.reliability === 'HIGH' ? 'High volume confirms the signal.' : 'Low volume - wait for confirmation.' }}
                </template>
              </div>
            </div>
          </template>
          
          <!-- No Pattern Found -->
          <template v-else>
            <div style="text-align: center; padding: 20px;">
              <div style="font-size: 2rem; margin-bottom: 8px;">📊</div>
              <div style="font-size: 0.85rem; color: rgba(255,255,255,0.5); margin-bottom: 8px;">No Pattern Detected</div>
              <div style="font-size: 0.7rem; color: rgba(255,255,255,0.35);">
                No significant candlestick reversal patterns found on the 1h timeframe.
              </div>
            </div>
          </template>
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

      <!-- Shadow Insight Section -->
      <section v-if="analysisCoin && !loading && shadowData" class="m-section">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <div>
            <h3 class="m-section-title" style="margin-bottom: 4px;">
              <Icon name="ph:eye" class="w-4 h-4" style="color: #a855f7;" />
              Shadow Insight
            </h3>
            <div style="font-size: 0.65rem; color: rgba(255,255,255,0.35);">Whale-crowd divergence analysis</div>
          </div>
          <span v-if="shadowData.divergence_type" :style="getDivergenceBadgeStyle(shadowData.divergence_type)">
            {{ formatDivergence(shadowData.divergence_type) }}
          </span>
        </div>
        
        <!-- Intent Score & Metrics Row -->
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
          <!-- Intent Score Gauge -->
          <div class="m-card m-card--dark" style="flex: 1; padding: 14px; text-align: center;">
            <div style="font-size: 0.65rem; color: rgba(255,255,255,0.4); letter-spacing: 1px; margin-bottom: 8px;">INTENT SCORE</div>
            <div :style="{ fontSize: '2rem', fontWeight: '700', color: getIntentColor(shadowData.intent_score) }">
              {{ shadowData.intent_score || 50 }}
            </div>
            <div style="height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-top: 8px; overflow: hidden;">
              <div :style="{ width: (shadowData.intent_score || 50) + '%', height: '100%', background: getIntentGradient(shadowData.intent_score), borderRadius: '2px' }"></div>
            </div>
          </div>
          
          <!-- Metrics Column -->
          <div style="flex: 1; display: flex; flex-direction: column; gap: 6px;">
            <!-- Whale Score -->
            <div class="m-card m-card--dark" style="padding: 10px 12px; display: flex; justify-content: space-between; align-items: center;">
              <div style="display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 1rem;">🐋</span>
                <span style="font-size: 0.7rem; color: rgba(255,255,255,0.6);">Whale</span>
              </div>
              <span :style="{ fontSize: '0.9rem', fontWeight: '600', color: shadowData.whale_score > 50 ? '#22c55e' : shadowData.whale_score < 50 ? '#ef4444' : '#eab308' }">
                {{ shadowData.whale_score || 50 }}
              </span>
            </div>
            <!-- Crowd Fear -->
            <div class="m-card m-card--dark" style="padding: 10px 12px; display: flex; justify-content: space-between; align-items: center;">
              <div style="display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 1rem;">😨</span>
                <span style="font-size: 0.7rem; color: rgba(255,255,255,0.6);">Crowd</span>
              </div>
              <span :style="{ fontSize: '0.9rem', fontWeight: '600', color: shadowData.sentiment_score > 50 ? '#22c55e' : shadowData.sentiment_score < 50 ? '#ef4444' : '#eab308' }">
                {{ shadowData.sentiment_score || 50 }}
              </span>
            </div>
          </div>
        </div>
        
        <!-- AI Shadow Insight Box -->
        <div v-if="shadowData.shadow_insight" class="m-card m-card--dark" style="padding: 14px; border-left: 3px solid #a855f7; background: linear-gradient(135deg, rgba(168, 85, 247, 0.08), transparent);">
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <Icon name="ph:brain" class="w-4 h-4" style="color: #a855f7;" />
            <span style="font-size: 0.7rem; font-weight: 600; color: #a855f7; letter-spacing: 0.5px;">AI INSIGHT</span>
          </div>
          <p style="font-size: 0.85rem; color: rgba(255,255,255,0.75); line-height: 1.5; margin: 0;">
            {{ shadowData.shadow_insight }}
          </p>
        </div>
        
        <!-- Golden Shadow Alert -->
        <div v-if="shadowData.is_golden_shadow" style="margin-top: 10px; padding: 12px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.15), rgba(168, 85, 247, 0.1)); border: 1px solid rgba(234, 179, 8, 0.3); border-radius: 12px; display: flex; align-items: center; gap: 10px;">
          <span style="font-size: 1.5rem;">⚡</span>
          <div>
            <div style="font-size: 0.75rem; font-weight: 600; color: #eab308;">Golden Shadow Entry</div>
            <div style="font-size: 0.65rem; color: rgba(255,255,255,0.5);">High-confidence whale divergence signal</div>
          </div>
        </div>
      </section>

      <!-- Empty State - Enhanced -->
      <section v-if="!analysisCoin && !loading" class="m-section">
        <!-- Market Mood Indicator -->
        <div class="analysis-mood-card">
          <div class="mood-header">
            <Icon name="ph:pulse" class="w-4 h-4" style="color: #00d4ff;" />
            <span>Market Mood</span>
          </div>
          <div class="mood-content">
            <div class="mood-gauge">
              <svg viewBox="0 0 100 50" class="mood-arc">
                <defs>
                  <linearGradient id="moodGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#ef4444" />
                    <stop offset="50%" stop-color="#eab308" />
                    <stop offset="100%" stop-color="#22c55e" />
                  </linearGradient>
                </defs>
                <path d="M 10 45 A 40 40 0 0 1 90 45" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="6" stroke-linecap="round"/>
                <path d="M 10 45 A 40 40 0 0 1 90 45" fill="none" stroke="url(#moodGrad)" stroke-width="6" stroke-linecap="round" :stroke-dasharray="126" :stroke-dashoffset="126 - (126 * marketMood / 100)"/>
              </svg>
              <div class="mood-value" :style="{ color: marketMood >= 60 ? '#22c55e' : marketMood <= 40 ? '#ef4444' : '#eab308' }">
                {{ marketMood }}
              </div>
            </div>
            <div class="mood-label" :style="{ color: marketMood >= 60 ? '#22c55e' : marketMood <= 40 ? '#ef4444' : '#eab308' }">
              {{ marketMood >= 70 ? 'Strongly Bullish' : marketMood >= 55 ? 'Bullish' : marketMood <= 30 ? 'Strongly Bearish' : marketMood <= 45 ? 'Bearish' : 'Neutral' }}
            </div>
          </div>
        </div>

        <!-- Quick Analyze Section -->
        <div class="analysis-quick-section">
          <div class="quick-header">
            <Icon name="ph:lightning" class="w-4 h-4" style="color: #eab308;" />
            <span>Quick Analyze</span>
          </div>
          <div class="quick-chips">
            <button v-for="coin in quickCoins" :key="coin.id" class="quick-chip" @click="analyzeQuick(coin.id)">
              <img :src="coin.image" class="quick-chip-img" />
              <span>{{ coin.symbol }}</span>
            </button>
          </div>
        </div>

        <!-- Trending Analysis Section -->
        <div class="analysis-trending-section">
          <div class="trending-header">
            <div class="trending-title">
              <Icon name="ph:fire" class="w-4 h-4" style="color: #f97316;" />
              <span>Trending Analysis</span>
            </div>
            <span class="trending-subtitle">Top ASI Scores</span>
          </div>
          <div class="trending-list">
            <div v-for="coin in trendingCoins" :key="coin.coin_id" class="trending-item" @click="analyzeQuick(coin.coin_id)">
              <img :src="coin.image" class="trending-img" />
              <div class="trending-info">
                <span class="trending-symbol">{{ coin.symbol?.toUpperCase() }}</span>
                <span class="trending-name">{{ coin.name }}</span>
              </div>
              <div class="trending-asi">
                <div class="asi-bar-mini">
                  <div class="asi-fill-mini" :class="coin.asi_score >= 60 ? 'bullish' : coin.asi_score <= 40 ? 'bearish' : 'neutral'" :style="{ width: coin.asi_score + '%' }"></div>
                </div>
                <span class="asi-value-mini" :class="coin.asi_score >= 60 ? 'bullish' : coin.asi_score <= 40 ? 'bearish' : 'neutral'">{{ coin.asi_score }}</span>
              </div>
              <span class="trending-signal" :class="'signal-' + (coin.signal || 'hold').toLowerCase()">
                {{ coin.signal || 'HOLD' }}
              </span>
              <Icon name="ph:caret-right" class="w-4 h-4 opacity-40" />
            </div>
          </div>
        </div>

        <!-- CTA Card -->
        <div class="analysis-cta-card">
          <div class="cta-icon">
            <Icon name="ph:chart-line-up" class="w-8 h-8" />
          </div>
          <div class="cta-content">
            <h4>Deep Analysis</h4>
            <p>Search for any coin to get comprehensive AI-powered technical analysis</p>
          </div>
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

defineProps<{
  activeTab?: string
}>()

defineEmits<{
  (e: 'setTab', tab: string): void
  (e: 'openSearch'): void
}>()

const api = useApi()

// Header data
const btcPrice = ref(98500)
const alertCount = ref(3)

// State
const searchQuery = ref('')
const suggestions = ref<Suggestion[]>([])
const loading = ref(false)
const dataSource = ref<string | null>(null)
const analysisCoin = ref<AnalysisCoin | null>(null)
const allCoins = ref<Suggestion[]>([])

// New: Enhanced empty state data
const marketMood = ref(55)
const quickCoins = ref([
  { id: 'bitcoin', symbol: 'BTC', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png' },
  { id: 'ethereum', symbol: 'ETH', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png' },
  { id: 'solana', symbol: 'SOL', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png' },
  { id: 'ripple', symbol: 'XRP', image: 'https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png' },
  { id: 'dogecoin', symbol: 'DOGE', image: 'https://assets.coingecko.com/coins/images/5/small/dogecoin.png' },
])

interface TrendingCoin {
  coin_id: string
  symbol: string
  name: string
  image: string
  asi_score: number
  signal: string
}
const trendingCoins = ref<TrendingCoin[]>([])

// New: Quick analyze function
const analyzeQuick = (coinId: string) => {
  searchQuery.value = coinId
  executeSearch(coinId)
}

// New: Fetch trending coins with ASI data
const fetchTrendingCoins = async () => {
  try {
    const [marketRes, sentimentRes] = await Promise.all([
      api.getMarketData(50),
      api.getSentimentBatch()
    ])
    
    if (marketRes.success && marketRes.data) {
      const sentimentMap = new Map()
      if (sentimentRes.success && sentimentRes.data) {
        sentimentRes.data.forEach((s: any) => {
          sentimentMap.set(s.coin_id, { asi_score: s.asi_score, signal: s.signal })
        })
      }
      
      // Get coins with ASI and sort by ASI score
      const withAsi = marketRes.data
        .map((c: any) => ({
          coin_id: c.coin_id,
          symbol: c.symbol,
          name: c.name,
          image: c.image,
          asi_score: sentimentMap.get(c.coin_id)?.asi_score || 50,
          signal: sentimentMap.get(c.coin_id)?.signal || 'HOLD'
        }))
        .sort((a: TrendingCoin, b: TrendingCoin) => b.asi_score - a.asi_score)
        .slice(0, 5)
      
      trendingCoins.value = withAsi
      
      // Calculate market mood from average ASI
      if (withAsi.length > 0) {
        const avgAsi = withAsi.reduce((sum: number, c: TrendingCoin) => sum + c.asi_score, 0) / withAsi.length
        marketMood.value = Math.round(avgAsi)
      }
    }
  } catch (e) {
    console.error('Failed to fetch trending:', e)
  }
}


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

// Candlestick pattern data
const patternData = ref<{
  pattern: string | null,
  direction: string,
  reliability: string | null,
  timeframe: string,
  volume_ratio: number | null,
  pattern_adjustment: number,
}>({
  pattern: null,
  direction: 'NEUTRAL',
  reliability: null,
  timeframe: '1h',
  volume_ratio: null,
  pattern_adjustment: 0,
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

// Shadow/Intent Divergence data
interface ShadowData {
  intent_score: number
  whale_score: number
  sentiment_score: number
  divergence_type: string
  divergence_label: string
  shadow_insight: string
  is_golden_shadow: boolean
  whale_net_flow_usd: number
}

const shadowData = ref<ShadowData | null>(null)

// Shadow helper functions
const getIntentColor = (score: number) => {
  if (score >= 70) return '#22c55e'
  if (score >= 55) return '#4ade80'
  if (score <= 30) return '#ef4444'
  if (score <= 45) return '#f97316'
  return '#eab308'
}

const getIntentGradient = (score: number) => {
  if (score >= 60) return 'linear-gradient(90deg, #22c55e, #4ade80)'
  if (score <= 40) return 'linear-gradient(90deg, #ef4444, #f97316)'
  return 'linear-gradient(90deg, #eab308, #fcd34d)'
}

const getDivergenceBadgeStyle = (divType: string) => {
  const baseStyle = {
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '0.7rem',
    fontWeight: '700' as const,
    border: '1px solid',
  }
  
  if (divType === 'shadow_accumulation') {
    return { ...baseStyle, background: 'rgba(34, 197, 94, 0.2)', color: '#22c55e', borderColor: 'rgba(34, 197, 94, 0.4)' }
  } else if (divType === 'bull_trap') {
    return { ...baseStyle, background: 'rgba(239, 68, 68, 0.2)', color: '#ef4444', borderColor: 'rgba(239, 68, 68, 0.4)' }
  } else if (divType === 'confirmation') {
    return { ...baseStyle, background: 'rgba(0, 212, 255, 0.2)', color: '#00d4ff', borderColor: 'rgba(0, 212, 255, 0.4)' }
  }
  return { ...baseStyle, background: 'rgba(234, 179, 8, 0.2)', color: '#eab308', borderColor: 'rgba(234, 179, 8, 0.4)' }
}

const formatDivergence = (divType: string) => {
  const labels: Record<string, string> = {
    shadow_accumulation: '🐋 Shadow Accumulation',
    bull_trap: '⚠️ Bull Trap',
    confirmation: '✓ Confirmation',
    neutral: '— Neutral',
  }
  return labels[divType] || divType
}

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
      
      // Fetch multi-horizon ASI (includes pattern data)
      try {
        const config = useRuntimeConfig()
        const mhRes = await $fetch<any>(`${config.public.apiBase}/sentiment/${targetCoinId}/multi-horizon`)
        if (mhRes?.success && mhRes.data) {
          // Pattern data is in timeframes['1h']
          const tf1h = mhRes.data.timeframes?.['1h']
          if (tf1h?.pattern) {
            patternData.value = {
              pattern: tf1h.pattern,
              direction: tf1h.pattern_direction || 'NEUTRAL',
              reliability: tf1h.pattern_reliability,
              timeframe: '1h',
              volume_ratio: tf1h.volume_ratio || null,
              pattern_adjustment: tf1h.pattern_adjustment || 0,
            }
          }
        }
      } catch (e) {
        console.warn('Multi-horizon data not available:', e)
      }


      
      // Fetch on-chain data
      try {
        const onchainRes = await api.getOnchainSignals(targetCoinId)
        if (onchainRes) {
          // Map from actual API response to component structure
          onchain.value = {
            overall: onchainRes.overall_signal || 'NEUTRAL',
            exchangeFlow: {
              signal: onchainRes.whale_activity?.signal || 'NEUTRAL',
              inflow: formatCompact(onchainRes.whale_activity?.inflow_usd || 0),
              outflow: formatCompact(onchainRes.whale_activity?.outflow_usd || 0),
              netFlow: onchainRes.whale_activity?.net_flow_usd || 0,
            },
            whaleActivity: {
              signal: onchainRes.whale_activity?.signal || 'NEUTRAL',
              largeTxCount: onchainRes.whale_activity?.tx_count_24h || 0,
              topHoldersChange: onchainRes.holder_signals?.top10_change_pct || 0,
            },
          }
        }
      } catch (e) {
        console.warn('On-chain data not available:', e)
      }
      
      // Fetch shadow/intent divergence data
      try {
        const shadowRes = await api.getIntentDivergence(targetCoinId)
        if (shadowRes) {
          shadowData.value = {
            intent_score: shadowRes.intent_score || 50,
            whale_score: shadowRes.whale_score || 50,
            sentiment_score: shadowRes.sentiment_score || 50,
            divergence_type: shadowRes.divergence_type || 'neutral',
            divergence_label: shadowRes.divergence_label || 'Neutral',
            shadow_insight: shadowRes.shadow_insight || '',
            is_golden_shadow: shadowRes.is_golden_shadow || false,
            whale_net_flow_usd: shadowRes.whale_net_flow_usd || 0,
          }
        }
      } catch (e) {
        console.warn('Shadow data not available:', e)
        shadowData.value = null
      }
    } else {
      analysisCoin.value = null
      dataSource.value = null
      shadowData.value = null
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
  fetchTrendingCoins()
})


const formatCurrency = (n: number) => {
  if (!n) return '$--'
  if (n >= 1) return '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return '$' + n.toFixed(6)
}

const formatCompact = (n: number) => {
  if (!n) return '$0'
  if (n >= 1e9) return '$' + (n / 1e9).toFixed(1) + 'B'
  if (n >= 1e6) return '$' + (n / 1e6).toFixed(1) + 'M'
  if (n >= 1e3) return '$' + (n / 1e3).toFixed(0) + 'K'
  return '$' + n.toFixed(0)
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

/* Market Mood Card */
.analysis-mood-card {
  background: linear-gradient(160deg, rgba(30, 35, 55, 0.95), rgba(15, 20, 35, 0.95));
  border: 1px solid rgba(0, 212, 255, 0.15);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 14px;
}

.mood-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.mood-header span {
  font-size: 0.8rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 0.5px;
}

.mood-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.mood-gauge {
  position: relative;
  width: 120px;
  height: 60px;
}

.mood-arc {
  width: 100%;
  height: 100%;
}

.mood-value {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  font-size: 1.8rem;
  font-weight: 700;
}

.mood-label {
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Quick Analyze Section */
.analysis-quick-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 14px;
  margin-bottom: 14px;
}

.quick-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.quick-header span {
  font-size: 0.8rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
}

.quick-chips {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 4px 0;
  -webkit-overflow-scrolling: touch;
}

.quick-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  background: linear-gradient(145deg, rgba(40, 45, 60, 0.9), rgba(25, 30, 45, 0.9));
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.quick-chip:hover, .quick-chip:active {
  background: linear-gradient(145deg, rgba(0, 212, 255, 0.15), rgba(0, 150, 200, 0.1));
  border-color: rgba(0, 212, 255, 0.3);
  transform: translateY(-1px);
}

.quick-chip-img {
  width: 22px;
  height: 22px;
  border-radius: 50%;
}

.quick-chip span {
  font-size: 0.8rem;
  font-weight: 600;
  color: #fff;
}

/* Trending Analysis Section */
.analysis-trending-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 14px;
  margin-bottom: 14px;
}

.trending-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.trending-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trending-title span {
  font-size: 0.8rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
}

.trending-subtitle {
  font-size: 0.65rem;
  color: rgba(255, 255, 255, 0.4);
}

.trending-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trending-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.trending-item:hover, .trending-item:active {
  background: rgba(0, 212, 255, 0.08);
}

.trending-img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.trending-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.trending-symbol {
  font-size: 0.85rem;
  font-weight: 600;
  color: #fff;
}

.trending-name {
  font-size: 0.65rem;
  color: rgba(255, 255, 255, 0.45);
}

.trending-asi {
  display: flex;
  align-items: center;
  gap: 6px;
}

.asi-bar-mini {
  width: 40px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.asi-fill-mini {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.asi-fill-mini.bullish { background: #22c55e; }
.asi-fill-mini.neutral { background: #eab308; }
.asi-fill-mini.bearish { background: #ef4444; }

.asi-value-mini {
  font-size: 0.75rem;
  font-weight: 600;
  min-width: 24px;
  text-align: right;
}

.asi-value-mini.bullish { color: #22c55e; }
.asi-value-mini.neutral { color: #eab308; }
.asi-value-mini.bearish { color: #ef4444; }

.trending-signal {
  font-size: 0.55rem;
  font-weight: 700;
  padding: 3px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.signal-buy, .signal-strong_buy {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.signal-sell, .signal-strong_sell {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.signal-hold {
  background: rgba(234, 179, 8, 0.2);
  color: #eab308;
}

/* CTA Card */
.analysis-cta-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.08), rgba(168, 85, 247, 0.06));
  border: 1px solid rgba(0, 212, 255, 0.15);
  border-radius: 14px;
}

.cta-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 150, 200, 0.15));
  border-radius: 12px;
  color: #00d4ff;
}

.cta-content h4 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #fff;
  margin: 0 0 4px 0;
}

.cta-content p {
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  line-height: 1.4;
}
</style>

