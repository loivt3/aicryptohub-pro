<template>
  <div class="mobile-layout">
    <!-- Shared Header -->
    <SharedMobileHeader 
      :active-tab="activeTab" 
      @set-tab="$emit('setTab', $event)" 
      @open-search="$emit('openSearch')" 
    />

    <!-- Main Content -->
    <main class="m-main">
      <!-- Stats Cards Scroll (from module-dashboard-mobile.php) -->
      <section class="m-section">
        <div class="m-stats-scroll">
          <div class="m-stats-container">
            <!-- Total Market Cap -->
            <div class="m-stat-card-pro">
              <div class="m-stat-header">
                <span class="m-stat-label">TOTAL MARKET CAP</span>
                <span class="m-stat-change" :class="avgChange >= 0 ? 'positive' : 'negative'">
                  {{ avgChange >= 0 ? '▲' : '▼' }} {{ Math.abs(avgChange).toFixed(2) }}%
                </span>
              </div>
              <div class="m-stat-value-large">{{ formatCurrency(totalMarketCap, 0) }}</div>
              <div class="m-stat-sparkline">
                <svg viewBox="0 0 120 40" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="mSparkGreen" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stop-color="rgba(34, 197, 94, 0.5)" />
                      <stop offset="100%" stop-color="rgba(34, 197, 94, 0)" />
                    </linearGradient>
                    <linearGradient id="mSparkRed" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stop-color="rgba(239, 68, 68, 0.5)" />
                      <stop offset="100%" stop-color="rgba(239, 68, 68, 0)" />
                    </linearGradient>
                  </defs>
                  <path d="M0,30 C10,28 20,22 30,20 C40,18 50,25 60,18 C70,12 80,16 90,10 C100,6 110,14 120,8 L120,40 L0,40 Z" 
                        :fill="avgChange >= 0 ? 'url(#mSparkGreen)' : 'url(#mSparkRed)'" />
                  <path d="M0,30 C10,28 20,22 30,20 C40,18 50,25 60,18 C70,12 80,16 90,10 C100,6 110,14 120,8" 
                        fill="none" :stroke="avgChange >= 0 ? '#22c55e' : '#ef4444'" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
            </div>

            <!-- BTC Dominance -->
            <div class="m-stat-card-pro">
              <div class="m-stat-header">
                <span class="m-stat-label">BTC DOMINANCE</span>
                <span class="m-stat-change" :class="btcDomChange >= 0 ? 'positive' : 'negative'">
                  {{ btcDomChange >= 0 ? '▲' : '▼' }} {{ Math.abs(btcDomChange).toFixed(2) }}%
                </span>
              </div>
              <div class="m-stat-value-large">{{ btcDominance.toFixed(1) }}%</div>
              <div class="m-stat-sparkline">
                <svg viewBox="0 0 120 40" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="mSparkOrange" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stop-color="rgba(249, 115, 22, 0.4)" />
                      <stop offset="100%" stop-color="rgba(249, 115, 22, 0)" />
                    </linearGradient>
                  </defs>
                  <path d="M0,20 C10,25 20,15 30,22 C40,29 50,18 60,24 C70,30 80,12 90,20 C100,28 110,8 120,15 L120,40 L0,40 Z" fill="url(#mSparkOrange)" />
                  <path d="M0,20 C10,25 20,15 30,22 C40,29 50,18 60,24 C70,30 80,12 90,20 C100,28 110,8 120,15" fill="none" stroke="#f97316" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
            </div>

            <!-- Fear & Greed Gauge -->
            <div class="m-stat-card-pro" style="min-width: 130px;">
              <div class="m-stat-header">
                <span class="m-stat-label">FEAR & GREED</span>
              </div>
              <div class="m-gauge-wrapper">
                <svg viewBox="0 0 100 50" class="m-gauge-svg">
                  <defs>
                    <linearGradient id="mGaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stop-color="#ef4444" />
                      <stop offset="25%" stop-color="#f97316" />
                      <stop offset="50%" stop-color="#eab308" />
                      <stop offset="75%" stop-color="#84cc16" />
                      <stop offset="100%" stop-color="#22c55e" />
                    </linearGradient>
                  </defs>
                  <path d="M 10 45 A 40 40 0 0 1 90 45" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="6" stroke-linecap="round"/>
                  <path d="M 10 45 A 40 40 0 0 1 90 45" fill="none" stroke="url(#mGaugeGrad)" stroke-width="6" stroke-linecap="round"/>
                  <line :x1="50" :y1="45" :x2="50 + 25 * Math.cos((180 - fearGreedValue * 1.8) * Math.PI / 180)" :y2="45 - 25 * Math.sin((180 - fearGreedValue * 1.8) * Math.PI / 180)" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
                  <circle cx="50" cy="45" r="3" fill="#1a1f2e" stroke="#fff" stroke-width="1"/>
                </svg>
              </div>
              <div class="m-gauge-value">
                <span class="m-gauge-number" :class="fearGreedClass">{{ Math.round(fearGreedValue) }}</span>
                <span class="m-gauge-label">{{ fearGreedLabel }}</span>
              </div>
            </div>

            <!-- 24H Volume -->
            <div class="m-stat-card-pro">
              <div class="m-stat-header">
                <span class="m-stat-label">24H VOLUME</span>
              </div>
              <div class="m-stat-value-large">{{ formatCurrency(total24hVolume, 0) }}</div>
              <div class="m-stat-sparkline">
                <svg viewBox="0 0 120 40" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="mSparkCyan" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stop-color="rgba(56, 189, 248, 0.4)" />
                      <stop offset="100%" stop-color="rgba(56, 189, 248, 0)" />
                    </linearGradient>
                  </defs>
                  <path d="M0,28 C10,22 20,30 30,18 C40,6 50,20 60,14 C70,8 80,25 90,15 C100,5 110,18 120,12 L120,40 L0,40 Z" fill="url(#mSparkCyan)" />
                  <path d="M0,28 C10,22 20,30 30,18 C40,6 50,20 60,14 C70,8 80,25 90,15 C100,5 110,18 120,12" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Multi-Horizon ASI Signals (REDESIGNED) -->
      <section class="m-section">
        <!-- Header with inline tabs -->
        <div style="display: flex; align-items: center; gap: 16px; padding-bottom: 8px; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">
          <h3 class="m-section-title" style="margin: 0;">
            <Icon name="ph:pulse" class="w-4 h-4" style="color: #8b5cf6;" />
            ASI
          </h3>
          <button 
            @click="activeHorizon = 'short'"
            :style="{
              background: 'none', border: 'none', padding: '6px 10px',
              fontSize: '13px', fontWeight: activeHorizon === 'short' ? '600' : '400',
              color: activeHorizon === 'short' ? '#a78bfa' : 'rgba(255,255,255,0.6)',
              borderBottom: activeHorizon === 'short' ? '2px solid #a78bfa' : '2px solid transparent',
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px'
            }"
          ><Icon name="lucide:gauge" class="w-3.5 h-3.5" />Short</button>
          <button 
            @click="activeHorizon = 'medium'"
            :style="{
              background: 'none', border: 'none', padding: '6px 10px',
              fontSize: '13px', fontWeight: activeHorizon === 'medium' ? '600' : '400',
              color: activeHorizon === 'medium' ? '#a78bfa' : 'rgba(255,255,255,0.6)',
              borderBottom: activeHorizon === 'medium' ? '2px solid #a78bfa' : '2px solid transparent',
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px'
            }"
          ><Icon name="lucide:timer" class="w-3.5 h-3.5" />Medium</button>
          <button 
            @click="activeHorizon = 'long'"
            :style="{
              background: 'none', border: 'none', padding: '6px 10px',
              fontSize: '13px', fontWeight: activeHorizon === 'long' ? '600' : '400',
              color: activeHorizon === 'long' ? '#a78bfa' : 'rgba(255,255,255,0.6)',
              borderBottom: activeHorizon === 'long' ? '2px solid #a78bfa' : '2px solid transparent',
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px'
            }"
          ><Icon name="lucide:target" class="w-3.5 h-3.5" />Long</button>
          <NuxtLink to="/analysis" class="m-section-link" style="margin-left: auto;">View All</NuxtLink>
        </div>
        
        <!-- Stats Bar -->
        <div class="m-horizon-stats">
          <div class="m-stat-mini">
            <span class="stat-value positive">{{ horizonStats.buyCount }}</span>
            <span class="stat-label">Buy</span>
          </div>
          <div class="m-stat-mini">
            <span class="stat-value neutral">{{ horizonStats.neutralCount }}</span>
            <span class="stat-label">Neutral</span>
          </div>
          <div class="m-stat-mini">
            <span class="stat-value negative">{{ horizonStats.sellCount }}</span>
            <span class="stat-label">Sell</span>
          </div>
          <div class="m-stat-mini">
            <span class="stat-value">{{ horizonStats.avgAsi }}</span>
            <span class="stat-label">Avg ASI</span>
          </div>
        </div>
        
        <!-- Coin List (matching Top Gainers style) -->
        <div class="m-list m-list--dark">
          <template v-for="(coin, idx) in horizonCoins" :key="coin.coin_id">
            <!-- Main Row + Meta combined -->
            <div class="m-coin-card-wrapper">
            <div class="m-list-item m-list-item--with-meta">
              <div class="m-list-item-main">
                <span class="m-rank" :class="getRankClass(idx)">{{ idx + 1 }}</span>
                <img :src="coin.image" class="m-avatar" />
                <div class="m-info">
                  <span class="m-info-title">{{ coin.symbol?.toUpperCase() }}</span>
                  <span class="m-info-subtitle">{{ coin.name }}</span>
                </div>
                <div class="m-price-col">
                  <span class="m-info-title" :class="getFlashClass(coin.symbol)">{{ formatCurrency(coin.price) }}</span>
                  <span class="m-info-subtitle" :class="coin.change_24h >= 0 ? 'm-text-success' : 'm-text-danger'">
                    {{ coin.change_24h >= 0 ? '+' : '' }}{{ coin.change_24h?.toFixed(2) }}%
                  </span>
                </div>
                <!-- Mini Sparkline (Real Data) -->
                <div class="m-mini-sparkline" style="width: 50px; height: 24px;">
                  <svg viewBox="0 0 50 24" preserveAspectRatio="none" style="width: 100%; height: 100%;">
                    <path :d="generateSparklineFill(coin, 50, 24)" :fill="coin.change_24h >= 0 ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'"/>
                    <path :d="generateSparkline(coin, 50, 24)" fill="none" :stroke="coin.change_24h >= 0 ? '#22c55e' : '#ef4444'" stroke-width="1.5"/>
                  </svg>
                </div>

                <!-- Signal Badge on main row -->
                <span class="m-signal-badge m-signal-badge--compact" :class="'m-signal-' + (coin.signal || 'hold').toLowerCase().replace('_', '-')">
                  {{ formatSignal(coin.signal) }}
                </span>
                <Icon name="ph:caret-right" class="w-4 h-4 opacity-30" />
              </div>
              <!-- ASI Meta Row - inside list-item -->
              <div class="m-list-item-meta">
                <span class="m-meta-mcap">MCap: {{ formatMarketCap(coin.market_cap) }}</span>
                <div class="m-meta-asi">
                  <span class="m-meta-asi-label">ASI</span>
                  <div class="m-meta-asi-bar">
                    <div class="m-meta-asi-fill" :class="getAsiClass(coin.asi_score)" :style="{ width: (coin.asi_score || 50) + '%' }"></div>
                  </div>
                  <span class="m-meta-asi-value" :class="getAsiClass(coin.asi_score)">{{ coin.asi_score ?? '--' }}</span>
                </div>
              </div>

            </div>
            </div>
          </template>
          
          <div v-if="horizonCoins.length === 0" class="m-horizon-empty">
            <Icon name="ph:chart-bar" class="w-8 h-8 opacity-30" />
            <span>No multi-horizon data yet</span>
          </div>
        </div>
      </section>

      <!-- Market Movers Section (Tabbed) -->
      <section class="m-section">
        <!-- Header with inline tabs -->
        <div style="display: flex; align-items: center; gap: 16px; padding-bottom: 8px; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">
          <h3 class="m-section-title" style="margin: 0;">
            <Icon name="ph:lightning" class="w-4 h-4" style="color: #f97316;" />
            Movers
          </h3>
          <button 
            @click="activeMoversTab = 'gainers'"
            :style="{
              background: 'none', border: 'none', padding: '6px 10px',
              fontSize: '13px', fontWeight: activeMoversTab === 'gainers' ? '600' : '400',
              color: activeMoversTab === 'gainers' ? '#4ade80' : 'rgba(255,255,255,0.6)',
              borderBottom: activeMoversTab === 'gainers' ? '2px solid #4ade80' : '2px solid transparent',
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px'
            }"
          ><Icon name="lucide:trending-up" class="w-3.5 h-3.5" />Gainers</button>
          <button 
            @click="activeMoversTab = 'losers'"
            :style="{
              background: 'none', border: 'none', padding: '6px 10px',
              fontSize: '13px', fontWeight: activeMoversTab === 'losers' ? '600' : '400',
              color: activeMoversTab === 'losers' ? '#f87171' : 'rgba(255,255,255,0.6)',
              borderBottom: activeMoversTab === 'losers' ? '2px solid #f87171' : '2px solid transparent',
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px'
            }"
          ><Icon name="lucide:trending-down" class="w-3.5 h-3.5" />Losers</button>
          <button 
            @click="activeMoversTab = 'traded'"
            :style="{
              background: 'none', border: 'none', padding: '6px 10px',
              fontSize: '13px', fontWeight: activeMoversTab === 'traded' ? '600' : '400',
              color: activeMoversTab === 'traded' ? '#60a5fa' : 'rgba(255,255,255,0.6)',
              borderBottom: activeMoversTab === 'traded' ? '2px solid #60a5fa' : '2px solid transparent',
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px'
            }"
          ><Icon name="lucide:bar-chart-3" class="w-3.5 h-3.5" />Traded</button>
          <NuxtLink to="/market" class="m-section-link" style="margin-left: auto;">View All</NuxtLink>
        </div>

        <!-- Coin List - conditionally show based on activeMoversTab -->
        <div class="m-list m-list--dark">
          <!-- Top Gainers -->
          <template v-if="activeMoversTab === 'gainers'">
            <template v-for="(coin, idx) in topGainers" :key="coin.coin_id">
            <div class="m-coin-card-wrapper">
              <div class="m-list-item m-list-item--with-meta" @click="expandedCoin = expandedCoin === coin.coin_id ? null : coin.coin_id">
                <div class="m-list-item-main">
                  <span class="m-rank">{{ idx + 1 }}</span>
                  <img :src="coin.image" class="m-avatar" />
                  <div class="m-info">
                    <span class="m-info-title">{{ coin.symbol?.toUpperCase() }}</span>
                    <span class="m-info-subtitle">{{ coin.name }}</span>
                  </div>
                  <div class="m-price-col">
                    <span class="m-info-title" :class="getFlashClass(coin.symbol)">{{ formatCurrency(coin.price) }}</span>
                    <span class="m-info-subtitle m-text-success">+{{ coin.change_24h?.toFixed(2) }}%</span>
                  </div>
                  <div class="m-mini-sparkline" style="width: 50px; height: 24px;">
                    <svg viewBox="0 0 50 24" preserveAspectRatio="none" style="width: 100%; height: 100%;">
                      <path :d="generateSparklineFill(coin, 50, 24)" fill="rgba(34,197,94,0.3)"/>
                      <path :d="generateSparkline(coin, 50, 24)" fill="none" stroke="#22c55e" stroke-width="1.5"/>
                    </svg>
                  </div>

                  <Icon name="ph:caret-right" class="w-4 h-4 opacity-30" :class="{ 'rotate-90': expandedCoin === coin.coin_id }" />
                </div>
                <div class="m-list-item-meta">
                  <span class="m-meta-mcap">MCap: {{ formatMarketCap(coin.market_cap) }}</span>
                  <div class="m-meta-asi">
                    <span class="m-meta-asi-label">ASI</span>
                    <div class="m-meta-asi-bar">
                      <div class="m-meta-asi-fill" :class="getAsiClass(coin.asi_score)" :style="{ width: coin.asi_score + '%' }"></div>
                    </div>
                    <span class="m-meta-asi-value" :class="getAsiClass(coin.asi_score)">{{ coin.asi_score }}</span>
                  </div>
                </div>
              </div>
              
              <div v-if="expandedCoin === coin.coin_id" class="m-accordion-panel">
                <div class="m-ai-box">
                  <div class="m-ai-box-header">
                    <Icon name="ph:robot" class="w-4 h-4" />
                    <span>AI ANALYSIS</span>
                  </div>
                  <p class="m-ai-box-text">{{ coin.reasoning || 'Strong bullish momentum detected. Technical indicators suggest upward trend continuation.' }}</p>
                </div>
                
                <div class="m-stats-grid">
                  <div class="m-stat-item">
                    <span class="m-stat-label">VOL 24H</span>
                    <span class="m-stat-value">{{ formatMarketCap(coin.volume_24h) }}</span>
                  </div>
                  <div class="m-stat-item">
                    <span class="m-stat-label">HIGH</span>
                    <span class="m-stat-value">{{ formatCurrency(coin.high_24h || coin.price * 1.02) }}</span>
                  </div>
                  <div class="m-stat-item">
                    <span class="m-stat-label">LOW</span>
                    <span class="m-stat-value">{{ formatCurrency(coin.low_24h || coin.price * 0.98) }}</span>
                  </div>
                </div>
                
                <div class="m-tech-section">
                  <div class="m-tech-title">
                    <Icon name="ph:chart-line" class="w-4 h-4" style="color: #60A5FA;" />
                    Support & Resistance
                  </div>
                  <div class="m-stats-grid m-stats-grid--2col">
                    <div class="m-stat-item m-stat-item--support">
                      <span class="m-stat-label">SUPPORT 1</span>
                      <span class="m-stat-value m-text-danger">{{ formatCurrency(coin.support_1 || coin.price * 0.97) }}</span>
                    </div>
                    <div class="m-stat-item m-stat-item--resistance">
                      <span class="m-stat-label">RESIST 1</span>
                      <span class="m-stat-value m-text-success">{{ formatCurrency(coin.resistance_1 || coin.price * 1.03) }}</span>
                    </div>
                    <div class="m-stat-item m-stat-item--support">
                      <span class="m-stat-label">SUPPORT 2</span>
                      <span class="m-stat-value m-text-danger">{{ formatCurrency(coin.support_2 || coin.price * 0.95) }}</span>
                    </div>
                    <div class="m-stat-item m-stat-item--resistance">
                      <span class="m-stat-label">RESIST 2</span>
                      <span class="m-stat-value m-text-success">{{ formatCurrency(coin.resistance_2 || coin.price * 1.05) }}</span>
                    </div>
                  </div>
                  <div class="m-pivot-row">
                    <span class="m-pivot-label">PIVOT:</span>
                    <span class="m-pivot-value">{{ formatCurrency(coin.pivot_point || coin.price) }}</span>
                    <span class="m-signal-badge" :class="'m-signal-' + (coin.ai_signal || 'hold').toLowerCase().replace('_', '-')">{{ coin.ai_signal || 'HOLD' }}</span>
                  </div>
                </div>
                
                <button class="m-fav-btn" :class="{ 'is-active': favorites.includes(coin.coin_id) }" @click.stop="toggleFavorite(coin.coin_id)">
                  <Icon name="ph:star" :class="favorites.includes(coin.coin_id) ? 'text-yellow-400' : ''" />
                  {{ favorites.includes(coin.coin_id) ? 'Remove Favorite' : 'Add to Favorites' }}
                </button>
            </div>
            </div>
            </template>
          </template>

          <!-- Top Losers -->
          <template v-else-if="activeMoversTab === 'losers'">
            <template v-for="(coin, idx) in topLosers" :key="'loser-'+coin.coin_id">
            <div class="m-coin-card-wrapper">
              <div class="m-list-item m-list-item--with-meta" @click="expandedCoin = expandedCoin === 'loser-'+coin.coin_id ? null : 'loser-'+coin.coin_id">
                <div class="m-list-item-main">
                  <span class="m-rank m-rank--danger">{{ idx + 1 }}</span>
                  <img :src="coin.image" class="m-avatar" />
                  <div class="m-info">
                    <span class="m-info-title">{{ coin.symbol?.toUpperCase() }}</span>
                    <span class="m-info-subtitle">{{ coin.name }}</span>
                  </div>
                  <div class="m-price-col">
                    <span class="m-info-title" :class="getFlashClass(coin.symbol)">{{ formatCurrency(coin.price) }}</span>
                    <span class="m-info-subtitle m-text-danger">{{ coin.change_24h?.toFixed(2) }}%</span>
                  </div>
                  <div class="m-mini-sparkline" style="width: 50px; height: 24px;">
                    <svg viewBox="0 0 50 24" preserveAspectRatio="none" style="width: 100%; height: 100%;">
                      <path :d="generateSparklineFill(coin, 50, 24)" fill="rgba(239,68,68,0.3)"/>
                      <path :d="generateSparkline(coin, 50, 24)" fill="none" stroke="#ef4444" stroke-width="1.5"/>
                    </svg>
                  </div>

                  <Icon name="ph:caret-right" class="w-4 h-4 opacity-30" />
                </div>
                <div class="m-list-item-meta">
                  <span class="m-meta-mcap">MCap: {{ formatMarketCap(coin.market_cap) }}</span>
                  <div class="m-meta-asi">
                    <span class="m-meta-asi-label">ASI</span>
                    <div class="m-meta-asi-bar">
                      <div class="m-meta-asi-fill" :class="getAsiClass(coin.asi_score)" :style="{ width: coin.asi_score + '%' }"></div>
                    </div>
                    <span class="m-meta-asi-value" :class="getAsiClass(coin.asi_score)">{{ coin.asi_score }}</span>
                  </div>
                </div>
              </div>
              
              <div v-if="expandedCoin === 'loser-'+coin.coin_id" class="m-accordion-panel">
                <div class="m-ai-box">
                  <div class="m-ai-box-header">
                    <Icon name="ph:robot" class="w-4 h-4" />
                    <span>AI ANALYSIS</span>
                  </div>
                  <p class="m-ai-box-text">{{ coin.reasoning || 'Bearish pressure detected. Technical indicators suggest downward momentum.' }}</p>
                </div>
                
                <div class="m-stats-grid">
                  <div class="m-stat-item">
                    <span class="m-stat-label">VOL 24H</span>
                    <span class="m-stat-value">{{ formatMarketCap(coin.volume_24h) }}</span>
                  </div>
                  <div class="m-stat-item">
                    <span class="m-stat-label">HIGH</span>
                    <span class="m-stat-value">{{ formatCurrency(coin.high_24h || coin.price * 1.02) }}</span>
                  </div>
                  <div class="m-stat-item">
                    <span class="m-stat-label">LOW</span>
                    <span class="m-stat-value">{{ formatCurrency(coin.low_24h || coin.price * 0.98) }}</span>
                  </div>
                </div>
                
                <div class="m-tech-section">
                  <div class="m-tech-title">
                    <Icon name="ph:chart-line" class="w-4 h-4" style="color: #60A5FA;" />
                    Support & Resistance
                  </div>
                  <div class="m-stats-grid m-stats-grid--2col">
                    <div class="m-stat-item m-stat-item--support">
                      <span class="m-stat-label">SUPPORT 1</span>
                      <span class="m-stat-value m-text-danger">{{ formatCurrency(coin.support_1 || coin.price * 0.97) }}</span>
                    </div>
                    <div class="m-stat-item m-stat-item--resistance">
                      <span class="m-stat-label">RESIST 1</span>
                      <span class="m-stat-value m-text-success">{{ formatCurrency(coin.resistance_1 || coin.price * 1.03) }}</span>
                    </div>
                    <div class="m-stat-item m-stat-item--support">
                      <span class="m-stat-label">SUPPORT 2</span>
                      <span class="m-stat-value m-text-danger">{{ formatCurrency(coin.support_2 || coin.price * 0.95) }}</span>
                    </div>
                    <div class="m-stat-item m-stat-item--resistance">
                      <span class="m-stat-label">RESIST 2</span>
                      <span class="m-stat-value m-text-success">{{ formatCurrency(coin.resistance_2 || coin.price * 1.05) }}</span>
                    </div>
                  </div>
                  <div class="m-pivot-row">
                    <span class="m-pivot-label">PIVOT:</span>
                    <span class="m-pivot-value">{{ formatCurrency(coin.pivot_point || coin.price) }}</span>
                    <span class="m-signal-badge" :class="'m-signal-' + (coin.ai_signal || 'sell').toLowerCase().replace('_', '-')">{{ coin.ai_signal || 'SELL' }}</span>
                  </div>
                </div>
                
                <button class="m-fav-btn" :class="{ 'is-active': favorites.includes(coin.coin_id) }" @click.stop="toggleFavorite(coin.coin_id)">
                  <Icon name="ph:star" :class="favorites.includes(coin.coin_id) ? 'text-yellow-400' : ''" />
                  {{ favorites.includes(coin.coin_id) ? 'Remove Favorite' : 'Add to Favorites' }}
                </button>
            </div>
            </div>
            </template>
          </template>

          <!-- Most Traded -->
          <template v-else>
            <template v-for="(coin, idx) in mostTraded" :key="'traded-'+coin.coin_id">
            <div class="m-coin-card-wrapper">
              <div class="m-list-item m-list-item--with-meta" @click="expandedCoin = expandedCoin === 'traded-'+coin.coin_id ? null : 'traded-'+coin.coin_id">
                <div class="m-list-item-main">
                  <span class="m-rank m-rank--info">{{ idx + 1 }}</span>
                  <img :src="coin.image" class="m-avatar" />
                  <div class="m-info">
                    <span class="m-info-title">{{ coin.symbol?.toUpperCase() }}</span>
                    <span class="m-info-subtitle">{{ coin.name }}</span>
                  </div>
                  <div class="m-price-col">
                    <span class="m-info-title" :class="getFlashClass(coin.symbol)">{{ formatCurrency(coin.price) }}</span>
                    <span class="m-info-subtitle" :class="coin.change_24h >= 0 ? 'm-text-success' : 'm-text-danger'">{{ coin.change_24h >= 0 ? '+' : '' }}{{ coin.change_24h?.toFixed(2) }}%</span>
                  </div>
                  <div class="m-mini-sparkline" style="width: 50px; height: 24px;">
                    <svg viewBox="0 0 50 24" preserveAspectRatio="none" style="width: 100%; height: 100%;">
                      <path :d="generateSparklineFill(coin, 50, 24)" :fill="coin.change_24h >= 0 ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'"/>
                      <path :d="generateSparkline(coin, 50, 24)" fill="none" :stroke="coin.change_24h >= 0 ? '#22c55e' : '#ef4444'" stroke-width="1.5"/>
                    </svg>
                  </div>

                  <Icon name="ph:caret-right" class="w-4 h-4 opacity-30" />
                </div>
                <div class="m-list-item-meta">
                  <span class="m-meta-mcap">Vol: {{ formatMarketCap(coin.volume_24h) }}</span>
                  <div class="m-meta-asi">
                    <span class="m-meta-asi-label">ASI</span>
                    <div class="m-meta-asi-bar">
                      <div class="m-meta-asi-fill" :class="getAsiClass(coin.asi_score)" :style="{ width: coin.asi_score + '%' }"></div>
                    </div>
                    <span class="m-meta-asi-value" :class="getAsiClass(coin.asi_score)">{{ coin.asi_score }}</span>
                  </div>
                </div>
              </div>
              
              <div v-if="expandedCoin === 'traded-'+coin.coin_id" class="m-accordion-panel">
                <div class="m-ai-box">
                  <div class="m-ai-box-header">
                    <Icon :name="coin.change_24h >= 0 ? 'ph:trend-up' : 'ph:trend-down'" class="w-4 h-4" />
                    <span>AI ANALYSIS</span>
                  </div>
                  <p class="m-ai-box-text">{{ coin.reasoning || 'High trading volume detected. Market interest remains strong.' }}</p>
                </div>
                
                <div class="m-stats-grid">
                  <div class="m-stat-item">
                    <span class="m-stat-label">MCAP</span>
                    <span class="m-stat-value">{{ formatMarketCap(coin.market_cap || 0) }}</span>
                  </div>
                  <div class="m-stat-item">
                    <span class="m-stat-label">HIGH</span>
                    <span class="m-stat-value">{{ formatCurrency(coin.high_24h || coin.price * 1.02) }}</span>
                  </div>
                  <div class="m-stat-item">
                    <span class="m-stat-label">LOW</span>
                    <span class="m-stat-value">{{ formatCurrency(coin.low_24h || coin.price * 0.98) }}</span>
                  </div>
                </div>
                
                <div class="m-tech-section">
                  <div class="m-tech-title">
                    <Icon name="ph:chart-line" class="w-4 h-4" style="color: #60A5FA;" />
                    Support & Resistance
                  </div>
                  <div class="m-stats-grid m-stats-grid--2col">
                    <div class="m-stat-item m-stat-item--support">
                      <span class="m-stat-label">SUPPORT 1</span>
                      <span class="m-stat-value m-text-danger">{{ formatCurrency(coin.support_1 || coin.price * 0.97) }}</span>
                    </div>
                    <div class="m-stat-item m-stat-item--resistance">
                      <span class="m-stat-label">RESIST 1</span>
                      <span class="m-stat-value m-text-success">{{ formatCurrency(coin.resistance_1 || coin.price * 1.03) }}</span>
                    </div>
                    <div class="m-stat-item m-stat-item--support">
                      <span class="m-stat-label">SUPPORT 2</span>
                      <span class="m-stat-value m-text-danger">{{ formatCurrency(coin.support_2 || coin.price * 0.95) }}</span>
                    </div>
                    <div class="m-stat-item m-stat-item--resistance">
                      <span class="m-stat-label">RESIST 2</span>
                      <span class="m-stat-value m-text-success">{{ formatCurrency(coin.resistance_2 || coin.price * 1.05) }}</span>
                    </div>
                  </div>
                  <div class="m-pivot-row">
                    <span class="m-pivot-label">PIVOT:</span>
                    <span class="m-pivot-value">{{ formatCurrency(coin.pivot_point || coin.price) }}</span>
                    <span class="m-signal-badge" :class="'m-signal-' + (coin.ai_signal || 'hold').toLowerCase().replace('_', '-')">{{ coin.ai_signal || 'HOLD' }}</span>
                  </div>
                </div>
                
                <button class="m-fav-btn" :class="{ 'is-active': favorites.includes(coin.coin_id) }" @click.stop="toggleFavorite(coin.coin_id)">
                  <Icon name="ph:star" :class="favorites.includes(coin.coin_id) ? 'text-yellow-400' : ''" />
                  {{ favorites.includes(coin.coin_id) ? 'Remove Favorite' : 'Add to Favorites' }}
                </button>
            </div>
            </div>
            </template>
          </template>
        </div>
      </section>



      <!-- Hidden Gems & High Rich Section -->
      <section class="m-section">
        <!-- Header with inline tabs -->
        <div style="display: flex; align-items: center; gap: 16px; padding-bottom: 8px; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">
          <h3 class="m-section-title" style="margin: 0;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M6 3l6 3 6-3"/><path d="M3 8l9 4 9-4"/><path d="M3 8v8l9 5 9-5V8"/><path d="M12 12v9"/></svg>
            Discovery
          </h3>
          <button 
            @click="activeGemTab = 'gems'"
            :style="{
              background: 'none', border: 'none', padding: '6px 10px',
              fontSize: '13px', fontWeight: activeGemTab === 'gems' ? '600' : '400',
              color: activeGemTab === 'gems' ? '#4ade80' : 'rgba(255,255,255,0.6)',
              borderBottom: activeGemTab === 'gems' ? '2px solid #4ade80' : '2px solid transparent',
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px'
            }"
          ><Icon name="lucide:gem" class="w-3.5 h-3.5" />Gems</button>
          <button 
            @click="activeGemTab = 'highrich'"
            :style="{
              background: 'none', border: 'none', padding: '6px 10px',
              fontSize: '13px', fontWeight: activeGemTab === 'highrich' ? '600' : '400',
              color: activeGemTab === 'highrich' ? '#fbbf24' : 'rgba(255,255,255,0.6)',
              borderBottom: activeGemTab === 'highrich' ? '2px solid #fbbf24' : '2px solid transparent',
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px'
            }"
          ><Icon name="lucide:rocket" class="w-3.5 h-3.5" />High Rich</button>
        </div>
        
        <!-- Hidden Gems Content -->
        <div v-if="activeGemTab === 'gems'" class="m-gems-scroll">
          <div class="m-gems-container">
            <div v-for="gem in hiddenGems" :key="gem.coin_id" class="m-gem-card">
              <!-- Header: avatar, symbol, score -->
              <div class="m-gem-header">
                <img :src="gem.image" class="m-gem-avatar" />
                <div class="m-gem-info">
                  <span class="m-gem-symbol">{{ gem.symbol }}</span>
                  <span class="m-gem-rank">#{{ gem.market_cap_rank }}</span>
                </div>
                <span class="m-gem-score" :class="getGemScoreClass(gem.discovery_score)">
                  {{ gem.discovery_score }}
                </span>
              </div>
              
              <!-- Trust Badges -->
              <div class="m-gem-badges">
                <span v-if="gem.is_accumulating" class="m-gem-badge accumulating">
                  🐋 Accum
                </span>
                <span v-if="gem.signal_strength" class="m-gem-badge" :class="'sig-' + gem.signal_strength?.toLowerCase().replace(/_/g, '-')">
                  {{ gem.signal_strength?.replace('_', ' ').substring(0, 12) }}
                </span>
                <span v-if="gem.confirmation_count >= 2" class="m-gem-badge confirmed">
                  ✓{{ gem.confirmation_count }}
                </span>
              </div>
              
              <!-- Metrics Grid -->
              <div class="m-gem-stats">
                <div class="m-gem-stat">
                  <span class="stat-label">24h</span>
                  <span class="stat-value" :class="gem.change_24h >= 0 ? 'positive' : 'negative'">
                    {{ gem.change_24h >= 0 ? '+' : '' }}{{ gem.change_24h?.toFixed(1) }}%
                  </span>
                </div>
                <div class="m-gem-stat">
                  <span class="stat-label">vs BTC</span>
                  <span class="stat-value" :class="gem.rs_vs_btc >= 0 ? 'positive' : 'negative'">
                    {{ gem.rs_vs_btc >= 0 ? '+' : '' }}{{ gem.rs_vs_btc?.toFixed(1) }}%
                  </span>
                </div>
                <div class="m-gem-stat" v-if="gem.volume_ratio">
                  <span class="stat-label">Vol</span>
                  <span class="stat-value" :class="gem.volume_ratio > 1.5 ? 'positive' : ''">
                    {{ gem.volume_ratio?.toFixed(1) }}x
                  </span>
                </div>
                <div class="m-gem-stat" v-if="gem.rsi_14">
                  <span class="stat-label">RSI</span>
                  <span class="stat-value" :class="getRsiClass(gem.rsi_14)">
                    {{ gem.rsi_14?.toFixed(0) }}
                  </span>
                </div>
              </div>
              
              <!-- Technical Footer -->
              <div class="m-gem-footer" v-if="gem.macd_signal_type || gem.bb_position">
                <span v-if="gem.macd_signal_type" class="m-gem-tech" :class="'macd-' + gem.macd_signal_type?.toLowerCase()">
                  MACD: {{ gem.macd_signal_type }}
                </span>
                <span v-if="gem.bb_position" class="m-gem-tech" :class="'bb-' + gem.bb_position?.toLowerCase()">
                  BB: {{ gem.bb_position }}
                </span>
              </div>
            </div>
            <div v-if="hiddenGems.length === 0" class="m-gems-empty">
              <span>No hidden gems at this time</span>
            </div>
          </div>
        </div>
        
        <!-- High Rich Content (Simpler Design) -->
        <div v-else class="m-gems-scroll">
          <div class="m-gems-container">
            <div v-for="item in highRichCoins" :key="item.coin_id" class="m-gem-card" style="min-width: 140px;">
              <!-- Simple Header -->
              <div class="m-gem-header">
                <img :src="item.image" class="m-gem-avatar" />
                <div class="m-gem-info">
                  <span class="m-gem-symbol">{{ item.symbol }}</span>
                  <span class="m-gem-rank">#{{ item.market_cap_rank }}</span>
                </div>
              </div>
              
              <!-- Key Metrics Only -->
              <div class="m-gem-stats" style="margin-top: 8px;">
                <div class="m-gem-stat">
                  <span class="stat-label">1H</span>
                  <span class="stat-value positive" style="font-size: 1.1rem;">
                    +{{ item.change_1h?.toFixed(1) }}%
                  </span>
                </div>
                <div class="m-gem-stat">
                  <span class="stat-label">ASI</span>
                  <span class="stat-value" :class="getAsiClass(item.asi_score)">
                    {{ item.asi_score }}
                  </span>
                </div>
              </div>
              
              <!-- Signal Badge -->
              <div style="margin-top: 8px; text-align: center;">
                <span :class="['m-signal-badge', 'm-signal-badge--compact', 'm-signal-' + (item.ai_signal || 'hold').toLowerCase().replace('_', '-')]">
                  {{ item.ai_signal || 'HOLD' }}
                </span>
              </div>
            </div>
            <div v-if="highRichCoins.length === 0" class="m-gems-empty">
              <span>No high rich opportunities right now</span>
            </div>
          </div>
        </div>
      </section>


      <!-- Technical Signals Section (Matching Desktop Table Design) -->
      <section class="m-section">
        <div class="m-section-header">
          <h3 class="m-section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><path d="M3 12h4l3 8l4-16l3 8h4"/></svg>
            Technical Signals
          </h3>
          <span class="m-section-note">Patterns & Indicators</span>
        </div>
        
        <div class="m-tsig-list">
          <div class="m-tsig-card">
            <div v-for="(coin, idx) in paginatedTechnicalSignals" :key="coin.coin_id" class="m-tsig-row">
              <!-- Top Row: Main Info + Signal -->
              <div class="m-tsig-top">
                <div class="m-tsig-rank-circle" :class="'rank-' + (idx + 1)">{{ idx + 1 }}</div>
                <img :src="coin.image" class="m-tsig-avatar" />
                <div class="m-tsig-info">
                  <span class="m-tsig-symbol">{{ coin.symbol }}</span>
                  <span class="m-tsig-name">{{ coin.name }}</span>
                </div>
                
                <div class="m-tsig-meta-right">
                   <div class="m-tsig-price-box">
                      <span class="m-tsig-price">${{ coin.price?.toFixed(2) }}</span>
                      <span class="m-tsig-change" :class="coin.change_24h >= 0 ? 'positive' : 'negative'">
                        {{ coin.change_24h >= 0 ? '+' : '' }}{{ coin.change_24h?.toFixed(2) }}%
                      </span>
                   </div>
                   
                   <div class="m-tsig-action-col">
                      <span class="signal-label-top">SIGNAL</span>
                      <span class="signal-btn" :class="'btn-' + (coin.signal_strength?.toLowerCase() || 'neutral')">
                        {{ (coin.signal_strength || 'HOLD').replace('_', ' ') }}
                      </span>
                   </div>
                </div>
              </div>
              
              <!-- Bottom Row: Indicators -->
              <div class="m-tsig-indicators-scroll">
                <!-- Pattern -->
                <div class="m-tsig-pill" v-if="coin.pattern_name">
                  <span class="pill-label">PATTERN</span>
                  <span class="pill-val" :class="'pattern-' + (coin.pattern_direction?.toLowerCase() || 'neutral')">
                    {{ coin.pattern_name }}
                  </span>
                </div>
                
                <!-- RSI -->
                <div class="m-tsig-pill">
                  <span class="pill-label">RSI</span>
                  <span class="pill-val" :class="getRsiClass(coin.rsi_14)">
                    {{ coin.rsi_14 }}
                  </span>
                </div>

                <!-- MACD -->
                <div class="m-tsig-pill" v-if="coin.macd_signal_type">
                  <span class="pill-label">MACD</span>
                  <span class="pill-val" :class="'macd-' + coin.macd_signal_type?.toLowerCase()">
                    {{ coin.macd_signal_type }}
                  </span>
                </div>
                
                <!-- Confirm -->
                <div class="m-tsig-pill">
                  <span class="pill-label">CONFIRM</span>
                  <span class="pill-val" :class="getConfirmClass(coin.confirmation_count)">
                    {{ coin.confirmation_count || 0 }}/7
                  </span>
                </div>
              </div>
            </div>
            
            <div v-if="technicalSignals.length === 0" class="m-tsig-empty">
              <span>No technical signals detected</span>
            </div>
          </div>
          
          <!-- Pagination Controls -->
          <div v-if="tsigTotalPages > 1" class="m-tsig-pagination">
            <button 
              class="m-tsig-page-btn" 
              :disabled="tsigPage === 1"
              @click="tsigPage--"
            >
              <Icon name="ph:caret-left" class="w-4 h-4" />
            </button>
            <span class="m-tsig-page-info">{{ tsigPage }} / {{ tsigTotalPages }}</span>
            <button 
              class="m-tsig-page-btn" 
              :disabled="tsigPage >= tsigTotalPages"
              @click="tsigPage++"
            >
              <Icon name="ph:caret-right" class="w-4 h-4" />
            </button>
          </div>
        </div>
      </section>


      <div class="m-bottom-spacer"></div>

    </main>

    <!-- Bottom Navigation (using SharedMobileFooter for consistent NuxtLink routing) -->
    <SharedMobileFooter />
  </div>
</template>

<script setup lang="ts">
import type { Ref } from 'vue'

interface Coin {
  coin_id: string
  symbol: string
  name: string
  image?: string
  price: number
  change_1h?: number
  change_24h: number
  change_7d?: number
  market_cap: number
  market_cap_rank?: number
  volume_24h: number
  high_24h?: number
  low_24h?: number
  asi_score?: number
  signal?: string
  reasoning?: string
  support_1?: number
  support_2?: number
  resistance_1?: number
  resistance_2?: number
  pivot_point?: number
  ai_signal?: string
}

interface SentimentData {
  coin_id: string
  asi_score: number
  signal: string
  reason?: string
}

defineProps<{
  activeTab?: string
  alertCount?: number
}>()

defineEmits<{
  (e: 'setTab', tab: string): void
  (e: 'openSearch'): void
}>()

const api = useApi()
const { updatePrice, getFlashClass } = usePriceFlashRow()
const { generateSparkline, generateSparklineFill, getSparklineColor } = useSparkline()


// State
const loading = ref(true)
const expandedCoin = ref<string | null>(null)
const favorites = ref<string[]>([])
const allCoins = ref<Coin[]>([])
const sentimentMap = ref<Record<string, SentimentData>>({})

// Market Stats
const btcPrice = ref(0)
const btcChange = ref(0)
const totalMarketCap = ref(0)
const avgChange = ref(0)
const btcDominance = ref(0)
const btcDomChange = ref(0)
const fearGreedValue = ref(50)
const total24hVolume = ref(0)

// Multi-Horizon ASI (market average)
const marketAsi = ref<{ short: number | null; medium: number | null; long: number | null }>({
  short: null,
  medium: null,
  long: null,
})

// Active horizon tab for filtering
const activeHorizon = ref<'short' | 'medium' | 'long'>('short')

// Active movers tab for Market Movers section
const activeMoversTab = ref<'gainers' | 'losers' | 'traded'>('gainers')

// Multi-horizon data for all coins (fetched from API)
const multiHorizonData = ref<Record<string, any>>({})

// Hidden gems data from discovery API
const hiddenGems = ref<any[]>([])

// Technical signals data from discovery API
const technicalSignals = ref<any[]>([])
const tsigPage = ref(1)
const tsigPerPage = 5

// Computed: paginated technical signals
const paginatedTechnicalSignals = computed(() => {
  const start = (tsigPage.value - 1) * tsigPerPage
  return technicalSignals.value.slice(start, start + tsigPerPage)
})
const tsigTotalPages = computed(() => Math.ceil(technicalSignals.value.length / tsigPerPage))

// Active gem tab (Hidden Gems vs High Rich)
const activeGemTab = ref<'gems' | 'highrich'>('gems')

// High Rich coins data
const highRichCoins = ref<any[]>([])

// Coins filtered by selected horizon
const horizonCoins = computed(() => {
  const coins = [...allCoins.value].slice(0, 50) // Top 50 coins
  const horizon = activeHorizon.value
  
  // Map coins with horizon-specific ASI data
  return coins
    .map(c => {
      const mhData = multiHorizonData.value[c.coin_id]
      let asi_score: number | null = null
      let signal = 'HOLD'
      let dataSource = 'none'
      
      if (mhData) {
        // Try horizon-specific data first
        if (horizon === 'short') {
          asi_score = mhData.asi_short ?? null
          signal = mhData.signal_short || 'HOLD'
          if (asi_score !== null) dataSource = 'horizon'
        } else if (horizon === 'medium') {
          asi_score = mhData.asi_medium ?? null
          signal = mhData.signal_medium || 'HOLD'
          if (asi_score !== null) dataSource = 'horizon'
        } else {
          asi_score = mhData.asi_long ?? null
          signal = mhData.signal_long || 'HOLD'
          if (asi_score !== null) dataSource = 'horizon'
        }
        
        // Fallback to combined or short-term if specific horizon is null
        if (asi_score === null && mhData.asi_combined !== null) {
          asi_score = mhData.asi_combined
          signal = mhData.signal_combined || 'HOLD'
          dataSource = 'combined'
        } else if (asi_score === null && mhData.asi_short !== null) {
          asi_score = mhData.asi_short
          signal = mhData.signal_short || 'HOLD'
          dataSource = 'short_fallback'
        }
      }
      
      // Final fallback to existing sentiment data
      if (asi_score === null) {
        asi_score = sentimentMap.value[c.coin_id]?.asi_score ?? null
        signal = sentimentMap.value[c.coin_id]?.signal || 'HOLD'
        if (asi_score !== null) dataSource = 'sentiment'
      }
      
      return {
        ...c,
        asi_score,
        signal,
        dataSource,
      }
    })
    .filter(c => c.asi_score !== null)
    .sort((a, b) => (b.asi_score || 0) - (a.asi_score || 0))
    .slice(0, 5)
})

// Stats for current horizon
const horizonStats = computed(() => {
  const coins = horizonCoins.value
  const buySignals = ['BUY', 'STRONG_BUY']
  const sellSignals = ['SELL', 'STRONG_SELL']
  
  const buyCount = coins.filter(c => buySignals.includes(c.signal)).length
  const sellCount = coins.filter(c => sellSignals.includes(c.signal)).length
  const neutralCount = coins.length - buyCount - sellCount
  
  const scores = coins.map(c => c.asi_score || 0).filter(s => s > 0)
  const avgAsi = scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : '--'
  
  return { buyCount, neutralCount, sellCount, avgAsi }
})

// Get rank class based on position
const getRankClass = (idx: number) => {
  if (idx === 0) return 'm-rank--gold'
  if (idx === 1) return 'm-rank--silver'
  if (idx === 2) return 'm-rank--bronze'
  return ''
}

// Computed lists from API data
const topGainers = computed(() => {
  return [...allCoins.value]
    .filter(c => c.change_24h > 0)
    .sort((a, b) => b.change_24h - a.change_24h)
    .slice(0, 5)
    .map(c => ({
      ...c,
      asi_score: sentimentMap.value[c.coin_id]?.asi_score || 50,
      ai_signal: sentimentMap.value[c.coin_id]?.signal || 'HOLD',
      reasoning: sentimentMap.value[c.coin_id]?.reason || '',
    }))
})

const topLosers = computed(() => {
  return [...allCoins.value]
    .filter(c => c.change_24h < 0)
    .sort((a, b) => a.change_24h - b.change_24h)
    .slice(0, 5)
    .map(c => ({
      ...c,
      asi_score: sentimentMap.value[c.coin_id]?.asi_score || 50,
      ai_signal: sentimentMap.value[c.coin_id]?.signal || 'HOLD',
      reasoning: sentimentMap.value[c.coin_id]?.reason || '',
    }))
})

const mostTraded = computed(() => {
  return [...allCoins.value]
    .sort((a, b) => b.volume_24h - a.volume_24h)
    .slice(0, 5)
    .map(c => ({
      ...c,
      asi_score: sentimentMap.value[c.coin_id]?.asi_score || 50,
      ai_signal: sentimentMap.value[c.coin_id]?.signal || 'HOLD',
      reasoning: sentimentMap.value[c.coin_id]?.reason || '',
    }))
})

// Average change for market movers stats bar
const moversAvgChange = computed(() => {
  const gainersChange = topGainers.value.map(c => c.change_24h || 0)
  const losersChange = topLosers.value.map(c => c.change_24h || 0)
  const tradedChange = mostTraded.value.map(c => c.change_24h || 0)
  const allChanges = [...gainersChange, ...losersChange, ...tradedChange]
  if (allChanges.length === 0) return '0%'
  const avg = allChanges.reduce((a, b) => a + b, 0) / allChanges.length
  return (avg >= 0 ? '+' : '') + avg.toFixed(1) + '%'
})

const aiSignals = computed(() => {
  const allWithAsi = [...allCoins.value]
    .map(c => ({
      ...c,
      asi_score: sentimentMap.value[c.coin_id]?.asi_score || 50,
      signal: sentimentMap.value[c.coin_id]?.signal || 'HOLD',
    }))
    .filter(c => c.asi_score !== null && c.asi_score !== undefined)
  
  // Sort by ASI descending
  const sorted = allWithAsi.sort((a, b) => (b.asi_score || 50) - (a.asi_score || 50))
  
  // Take top 6 highest ASI (bullish) + bottom 6 lowest ASI (bearish)
  const topBullish = sorted.slice(0, 6)
  const topBearish = sorted.slice(-6).reverse()  // Reverse to show lowest first in bearish section
  
  return [...topBullish, ...topBearish]  // 12 coins total
})


// Row-based Treemap Layout (like the original design)
// Row 1: 2 items (biggest), Row 2: 3 items, Row 3-5: 5 items each
const treemapLayout = computed(() => {
  const coins = aiSignals.value
  if (!coins.length) return []
  
  // Row configuration: 3 rows with larger tiles for better visibility
  const rowConfig = [
    { count: 3, height: 40 },   // Row 1: Top 3 bullish (40% height)
    { count: 4, height: 35 },   // Row 2: Next 4 (35% height)
    { count: 5, height: 25 },   // Row 3: Next 5 bearish (25% height)
  ]

  
  const layout: any[] = []
  let currentY = 0
  let itemIndex = 0
  
  for (const row of rowConfig) {
    if (itemIndex >= coins.length) break
    
    const rowItems = coins.slice(itemIndex, itemIndex + row.count)
    if (rowItems.length === 0) break
    
    // Equal width for items in each row
    const itemWidth = 100 / rowItems.length
    
    // Layout items in this row
    let currentX = 0
    for (const item of rowItems) {
      layout.push({
        ...item,
        x: currentX,
        y: currentY,
        w: itemWidth,
        h: row.height,
      })
      currentX += itemWidth
    }
    
    currentY += row.height
    itemIndex += rowItems.length
  }
  
  return layout
})


// Treemap tile style based on ASI score (bullish/bearish indicator)
const getTreemapTileStyle = (asiScore: number, change24h: number) => {
  // Color based on ASI score for better sentiment visualization
  let bgColor: string
  
  // Use ASI score for color gradient (0-100)
  if (asiScore >= 70) {
    bgColor = '#00897b'  // Strong bullish - teal
  } else if (asiScore >= 60) {
    bgColor = '#26a69a'  // Bullish - light teal
  } else if (asiScore >= 55) {
    bgColor = '#4db6ac'  // Slightly bullish
  } else if (asiScore >= 45) {
    bgColor = '#546e7a'  // Neutral - blue gray
  } else if (asiScore >= 40) {
    bgColor = '#78909c'  // Slightly bearish
  } else if (asiScore >= 30) {
    bgColor = '#c62828'  // Bearish - red
  } else {
    bgColor = '#b71c1c'  // Strong bearish - dark red
  }
  
  return {
    background: bgColor,
    borderColor: 'rgba(0,0,0,0.2)',
  }
}

const fearGreedLabel = computed(() => {
  if (fearGreedValue.value >= 75) return 'Extreme Greed'
  if (fearGreedValue.value >= 55) return 'Greed'
  if (fearGreedValue.value >= 45) return 'Neutral'
  if (fearGreedValue.value >= 25) return 'Fear'
  return 'Extreme Fear'
})

const fearGreedClass = computed(() => {
  if (fearGreedValue.value >= 55) return 'greed'
  if (fearGreedValue.value >= 45) return 'neutral'
  return 'fear'
})

// Fetch data from API
const fetchData = async () => {
  loading.value = true
  try {
    // Fetch global market stats first
    try {
      const globalRes = await api.getGlobalStats()
      if (globalRes.success && globalRes.data) {
        totalMarketCap.value = globalRes.data.total_market_cap
        total24hVolume.value = globalRes.data.total_volume_24h
        btcDominance.value = globalRes.data.btc_dominance
        avgChange.value = globalRes.data.market_cap_change_24h
        fearGreedValue.value = globalRes.data.fear_greed_index
      }
    } catch (e) {
      console.warn('Failed to fetch global stats:', e)
    }
    
    // Fetch market data
    const marketRes = await api.getMarketData(100)
    if (marketRes.success && marketRes.data) {
      const newCoins = marketRes.data as Coin[]
      
      // Trigger flash animation for price changes
      newCoins.forEach(coin => {
        if (coin.symbol && coin.price) {
          updatePrice(coin.symbol, coin.price)
        }
      })
      
      allCoins.value = newCoins
      
      // Get BTC price for header
      const btc = allCoins.value.find(c => c.coin_id === 'bitcoin')
      if (btc) {
        btcPrice.value = btc.price
        btcChange.value = btc.change_24h
      }
    }
    
    // Fetch sentiment data
    const sentimentRes = await api.getSentiment(100)
    if (sentimentRes?.success && Array.isArray(sentimentRes.data)) {
      sentimentMap.value = {}
      sentimentRes.data.forEach((s: SentimentData) => {
        sentimentMap.value[s.coin_id] = s
      })
    } else if (Array.isArray(sentimentRes)) {
      // Fallback for old format
      sentimentMap.value = {}
      sentimentRes.forEach((s: SentimentData) => {
        sentimentMap.value[s.coin_id] = s
      })
    }
    
    // Fetch multi-horizon ASI (using BTC as market indicator)
    try {
      const config = useRuntimeConfig()
      const asiRes = await $fetch<any>(`${config.public.apiBase}/sentiment/bitcoin/multi-horizon`)
      if (asiRes?.success && asiRes.data) {
        marketAsi.value = {
          short: asiRes.data.asi_short,
          medium: asiRes.data.asi_medium,
          long: asiRes.data.asi_long,
        }
      }
    } catch (e) {
      console.warn('Failed to fetch multi-horizon ASI:', e)
    }
    
    // Fetch multi-horizon ASI for top 10 coins (using batch API to reduce load)
    try {
      const config = useRuntimeConfig()
      const topCoinIds = allCoins.value.slice(0, 10).map(c => c.coin_id)
      
      // Use batch endpoint instead of parallel calls
      const mhRes = await $fetch<any>(`${config.public.apiBase}/sentiment/multi-horizon/batch`, {
        method: 'POST',
        body: { coin_ids: topCoinIds }
      })
      
      if (mhRes?.success && mhRes.data) {
        multiHorizonData.value = mhRes.data
      }
    } catch (e) {
      console.warn('Failed to fetch multi-horizon data for coins:', e)
    }

  } catch (error) {
    console.error('Failed to fetch data:', error)
  } finally {
    loading.value = false
  }
}

// Fetch hidden gems, high rich, and technical signals from discovery API
const fetchDiscoveryData = async () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || '/api/v1'
  
  try {
    const [gemsRes, signalsRes, highRichRes] = await Promise.all([
      $fetch<any>(`${apiBase}/discovery/hidden-gems?limit=8`),
      $fetch<any>(`${apiBase}/discovery/technical-signals?limit=10`),
      $fetch<any>(`${apiBase}/discovery/high-rich?limit=8`)
    ])
    
    if (gemsRes?.success && gemsRes.data) {
      hiddenGems.value = gemsRes.data
    }
    if (signalsRes?.success && signalsRes.data) {
      technicalSignals.value = signalsRes.data
    }
    if (highRichRes?.success && highRichRes.data) {
      highRichCoins.value = highRichRes.data
    }
  } catch (error) {
    console.error('[Mobile] Discovery fetch failed:', error)
  }
}


// Helper for gem score styling
const getGemScoreClass = (score: number) => {
  if (score >= 80) return 'gem-excellent'
  if (score >= 70) return 'gem-good'
  return 'gem-moderate'
}

// Helper for RSI styling
const getRsiClass = (rsi: number) => {
  if (rsi >= 70) return 'rsi-overbought'
  if (rsi <= 30) return 'rsi-oversold'
  return 'rsi-neutral'
}

// Helper for confirmation count styling
const getConfirmClass = (count: number) => {
  if (count >= 5) return 'confirm-strong'
  if (count >= 3) return 'confirm-moderate'
  return 'confirm-weak'
}


// Fetch on mount
onMounted(() => {
  fetchData()
  fetchDiscoveryData()
  
  // Setup real-time WebSocket connection
  setupSocketConnection()
  
  // Fallback: Refresh every 10 seconds if WebSocket not available
  const interval = setInterval(() => {
    if (!socketConnected.value) {
      fetchData()
    }
  }, 10000)
  onUnmounted(() => clearInterval(interval))
})

// Socket.IO integration for real-time updates
const socketConnected = ref(false)
const socketMessageCount = ref(0)

const setupSocketConnection = () => {
  try {
    const { connect, onPriceUpdate, connected } = useSocket()
    
    // Connect to WebSocket
    connect()
    
    // Watch connection status
    watch(connected, (isConnected) => {
      socketConnected.value = isConnected
      console.log('[Dashboard] Socket connected:', isConnected)
    }, { immediate: true })
    
    // Handle price updates
    onPriceUpdate((updates) => {
      socketMessageCount.value++
      
      updates.forEach(update => {
        // Find coin by symbol and update
        const idx = allCoins.value.findIndex(
          c => c.symbol.toUpperCase() === update.s.toUpperCase()
        )
        
        if (idx !== -1) {
          // Trigger flash animation
          updatePrice(allCoins.value[idx].symbol, update.p)
          
          // Update coin data
          allCoins.value[idx] = {
            ...allCoins.value[idx],
            price: update.p,
            change_24h: update.c,
          }
        }
      })
      
      // Update BTC price in header
      const btcUpdate = updates.find(u => u.s === 'BTC')
      if (btcUpdate) {
        btcPrice.value = btcUpdate.p
        btcChange.value = btcUpdate.c
      }
    })
    
  } catch (error) {
    console.error('[Dashboard] Socket setup failed:', error)
  }
}

const formatCurrency = (n: number, decimals = 2) => {
  if (!n) return '$--'
  if (n >= 1e12) return '$' + (n / 1e12).toFixed(2) + 'T'
  if (n >= 1e9) return '$' + (n / 1e9).toFixed(2) + 'B'
  if (n >= 1) return '$' + n.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
  return '$' + n.toFixed(6)
}

const formatMarketCap = (n: number) => {
  if (!n) return '--'
  if (n >= 1e12) return '$' + (n / 1e12).toFixed(2) + 'T'
  if (n >= 1e9) return '$' + (n / 1e9).toFixed(1) + 'B'
  if (n >= 1e6) return '$' + (n / 1e6).toFixed(1) + 'M'
  return '$' + n.toLocaleString()
}

const getAsiClass = (score: number) => {
  if (score >= 60) return 'positive'
  if (score <= 40) return 'negative'
  return 'neutral'
}

const formatSignal = (signal: string | null | undefined) => {
  if (!signal) return 'HOLD'
  // Convert STRONG_BUY to S.BUY, STRONG_SELL to S.SELL for compact display
  const signalMap: Record<string, string> = {
    'STRONG_BUY': 'S.BUY',
    'BUY': 'BUY',
    'NEUTRAL': 'HOLD',
    'HOLD': 'HOLD',
    'SELL': 'SELL',
    'STRONG_SELL': 'S.SELL',
  }
  return signalMap[signal.toUpperCase()] || signal
}

// Generate heatmap gradient style based on ASI score
const getHeatmapStyle = (score: number | null | undefined) => {
  const asi = score ?? 50
  
  // Map ASI (0-100) to color
  // 0-25: Strong bearish (deep red)
  // 25-40: Bearish (red-orange)
  // 40-60: Neutral (yellow-orange)
  // 60-75: Bullish (lime green)
  // 75-100: Strong bullish (bright green)
  
  let r, g, b
  
  if (asi <= 25) {
    // Deep red: rgb(220, 38, 38)
    r = 220; g = 38; b = 38
  } else if (asi <= 40) {
    // Transition from red to orange
    const t = (asi - 25) / 15
    r = Math.round(220 + (245 - 220) * t)
    g = Math.round(38 + (158 - 38) * t)
    b = Math.round(38 + (11 - 38) * t)
  } else if (asi <= 60) {
    // Neutral yellow-orange: rgb(245, 158, 11) to rgb(234, 179, 8)
    const t = (asi - 40) / 20
    r = Math.round(245 + (234 - 245) * t)
    g = Math.round(158 + (179 - 158) * t)
    b = Math.round(11 + (8 - 11) * t)
  } else if (asi <= 75) {
    // Transition to lime green
    const t = (asi - 60) / 15
    r = Math.round(234 + (132 - 234) * t)
    g = Math.round(179 + (204 - 179) * t)
    b = Math.round(8 + (22 - 8) * t)
  } else {
    // Strong bullish bright green: rgb(34, 197, 94)
    r = 34; g = 197; b = 94
  }
  
  return {
    background: `linear-gradient(135deg, rgba(${r}, ${g}, ${b}, 0.25), rgba(${r}, ${g}, ${b}, 0.4))`,
    borderColor: `rgba(${r}, ${g}, ${b}, 0.5)`,
  }
}

const toggleFavorite = (coinId: string) => {
  const idx = favorites.value.indexOf(coinId)
  if (idx > -1) {
    favorites.value.splice(idx, 1)
  } else {
    favorites.value.push(coinId)
  }
}
</script>

<style scoped>
/* Additional component-specific styles */
.rotate-90 {
  transform: rotate(90deg);
}

.text-yellow-400 {
  color: #fbbf24;
}

/* Monospace font for numbers - tabular figures for alignment */
.m-price-col,
.m-info-title,
.stat-value,
.m-horizon-score,
.m-mcap,
.m-volume,
.m-asi-score,
.m-change,
.m-metric-value {
  font-family: 'SF Mono', 'Roboto Mono', 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-variant-numeric: tabular-nums;
}

/* Multi-Horizon ASI Cards */
.m-horizon-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 0 12px;
}

.m-horizon-card {
  background: rgba(15, 25, 35, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px 8px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 2px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
}

.m-horizon-label {
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}

.m-horizon-tf {
  font-size: 9px;
  color: #888;
}

.m-horizon-score {
  font-size: 24px;
  font-weight: 700;
  margin: 4px 0;
}

.m-horizon-score.positive { color: #22c55e; }
.m-horizon-score.neutral { color: #f59e0b; }
.m-horizon-score.negative { color: #ef4444; }

.m-horizon-use {
  font-size: 9px;
  color: #666;
}

/* NEW: Horizon Tabs */
.m-horizon-tabs {
  display: flex;
  gap: 8px;
  padding: 0 12px;
  margin-bottom: 12px;
}

.m-horizon-tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  background: rgba(15, 25, 35, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
}

.m-horizon-tab:hover {
  background: rgb(40 44 52 / 95%);
}

.m-horizon-tab.active {
  background: linear-gradient(135deg, rgba(56, 239, 235, 0.2), rgba(34, 197, 94, 0.15));
  border-color: rgba(56, 239, 235, 0.5);
  box-shadow: rgba(56, 239, 235, 0.3) 0px 0px 12px, rgba(0, 0, 0, 0.24) 0px 6px 12px;
}

.m-horizon-tab .tab-label {
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.m-horizon-tab .tab-tf {
  font-size: 10px;
  color: #888;
  margin-top: 2px;
}

.m-horizon-tab.active .tab-label {
  color: #38efeb;
}

/* Stats Bar */
.m-horizon-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
  padding: 0 12px;
  margin-bottom: 8px;
}

.m-stat-mini {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6px 2px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 8px;
}

.m-stat-mini .stat-value {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
}

.m-stat-mini .stat-value.positive { color: #22c55e; }
.m-stat-mini .stat-value.neutral { color: #f59e0b; }
.m-stat-mini .stat-value.negative { color: #ef4444; }

.m-stat-mini .stat-label {
  font-size: 9px;
  color: #888;
  margin-top: 1px;
}

/* Horizon Coin List */
.m-horizon-list {
  padding: 0 12px;
}

.m-horizon-coin {
  background: rgba(15, 25, 35, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 8px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
}

.m-horizon-coin-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.m-horizon-coin-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}

.m-horizon-coin-bar .m-asi-bar {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.m-horizon-coin-bar .m-asi-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.m-horizon-coin-bar .m-asi-fill.positive { background: linear-gradient(90deg, #22c55e, #16a34a); }
.m-horizon-coin-bar .m-asi-fill.neutral { background: linear-gradient(90deg, #f59e0b, #d97706); }
.m-horizon-coin-bar .m-asi-fill.negative { background: linear-gradient(90deg, #ef4444, #dc2626); }

.m-horizon-coin-bar .m-asi-value {
  font-size: 12px;
  font-weight: 700;
  min-width: 24px;
  text-align: right;
}

.m-horizon-coin-bar .m-asi-value.positive { color: #22c55e; }
.m-horizon-coin-bar .m-asi-value.neutral { color: #f59e0b; }
.m-horizon-coin-bar .m-asi-value.negative { color: #ef4444; }

/* Rank badges */
.m-rank--gold { background: linear-gradient(135deg, #fbbf24, #f59e0b) !important; color: #000 !important; }
.m-rank--silver { background: linear-gradient(135deg, #9ca3af, #6b7280) !important; color: #000 !important; }
.m-rank--bronze { background: linear-gradient(135deg, #d97706, #b45309) !important; color: #fff !important; }

/* Empty state */
.m-horizon-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 32px 0;
  color: #666;
  font-size: 13px;
}

/* Signal Badges for ASI by Horizon */
.m-list-item-meta .m-signal-badge {
  font-size: 9px;
  font-weight: 700;
  padding: 3px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-left: auto;
}

/* Compact signal badge for main row */
.m-signal-badge--compact {
  font-size: 8px;
  font-weight: 700;
  padding: 3px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.2px;
  flex-shrink: 0;
  margin-left: 4px;
}


.m-signal-s-buy,
.m-signal-strong-buy {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.25), rgba(22, 163, 74, 0.35));
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.4);
}

.m-signal-buy {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.m-signal-hold,
.m-signal-neutral {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.m-signal-sell {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.m-signal-s-sell,
.m-signal-strong-sell {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.25), rgba(220, 38, 38, 0.35));
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.4);
}

/* ==================== HEATMAP STYLES ==================== */
.m-heatmap-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
  padding: 0;
}

.m-heatmap-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px 4px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(15, 25, 35, 0.7);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
  transition: all 0.2s ease;
  min-height: 90px;
}

.m-heatmap-tile:active {
  transform: scale(0.97);
}

.m-heatmap-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  margin-bottom: 4px;
}

.m-heatmap-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.m-heatmap-symbol {
  font-size: 10px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.m-heatmap-score {
  font-size: 18px;
  font-weight: 800;
  color: #fff;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
  line-height: 1;
  margin-bottom: 2px;
}

.m-heatmap-signal {
  font-size: 7px;
  font-weight: 700;
  padding: 2px 5px;
  border-radius: 3px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 2px;
}

/* Signal colors in heatmap */
.m-heatmap-signal.signal-strong-buy,
.m-heatmap-signal.signal-s-buy {
  background: rgba(34, 197, 94, 0.3);
  color: #fff;
}

.m-heatmap-signal.signal-buy {
  background: rgba(34, 197, 94, 0.2);
  color: #fff;
}

.m-heatmap-signal.signal-hold,
.m-heatmap-signal.signal-neutral {
  background: rgba(245, 158, 11, 0.3);
  color: #fff;
}

.m-heatmap-signal.signal-sell {
  background: rgba(239, 68, 68, 0.2);
  color: #fff;
}

.m-heatmap-signal.signal-strong-sell,
.m-heatmap-signal.signal-s-sell {
  background: rgba(239, 68, 68, 0.3);
  color: #fff;
}

.m-heatmap-change {
  font-size: 9px;
  font-weight: 600;
}

.m-heatmap-change.up {
  color: #86efac;
}

.m-heatmap-change.down {
  color: #fca5a5;
}

/* Heatmap Legend */
.m-heatmap-legend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin: 12px 12px 0;
  padding: 10px 16px;
  background: rgba(30, 30, 50, 0.6);
  border-radius: 10px;
}

.m-heatmap-legend .legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.m-heatmap-legend .legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.m-heatmap-legend .legend-text {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

/* Treemap ASI Score */
.treemap-asi {
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
  padding: 2px 6px;
  background: rgba(0,0,0,0.3);
  border-radius: 4px;
  margin-top: 2px;
}

.treemap-asi.bullish {
  color: #b9f6ca;
}

.treemap-asi.bearish {
  color: #ffcdd2;
}

.treemap-asi.neutral {
  color: #cfd8dc;
}

/* Landscape/wider screens: show more columns */
@media (min-width: 480px) {
  .m-treemap-container {
    height: 280px;
  }
  
  .treemap-symbol {
    font-size: 16px;
  }

  
  .treemap-change {
    font-size: 12px;
  }
}

/* ==================== TREEMAP STYLES ==================== */
.m-treemap-container {
  position: relative;
  width: calc(100% - 24px);
  height: 180px;
  margin: 0 12px;
  border-radius: 12px;
  overflow: hidden;
  background: #0d1117;
  padding: 4px;
}

.m-treemap-tile {
  position: absolute;
  display: flex;
  box-sizing: border-box;
  padding: 2px;
  transition: transform 0.2s ease;
  cursor: pointer;
}

.m-treemap-tile-inner {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: filter 0.2s ease;
  overflow: hidden;
  padding: 2px;
  box-sizing: border-box;
  position: relative;
}

.treemap-bg-icon {
  position: absolute;
  width: 70%;
  height: 70%;
  object-fit: contain;
  opacity: 0.4;
  pointer-events: none;
  z-index: 0;
}


.m-treemap-tile:hover {
  transform: scale(1.03);
  z-index: 10;
}

.m-treemap-tile:hover .m-treemap-tile-inner {
  filter: brightness(1.15);
}

.treemap-symbol {
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.6);
  letter-spacing: 0.3px;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  position: relative;
  z-index: 1;
}

.treemap-symbol-small {
  font-size: 9px;
}

.treemap-asi {
  font-size: 11px;
  font-weight: 700;
  color: rgba(255,255,255,0.95);
  text-shadow: 0 1px 2px rgba(0,0,0,0.4);
  position: relative;
  z-index: 1;
  margin-top: 1px;
  max-width: 100%;
  overflow: hidden;
}


.treemap-change {
  font-size: 10px;
  font-weight: 600;
  color: rgba(255,255,255,0.9);
  text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
  margin-top: 2px;
}

.treemap-change.up {
  color: #b9f6ca;
}

.treemap-change.down {
  color: #ffcdd2;
}

/* ================================== */
/* Hidden Gems Section Styles         */
/* ================================== */
.m-gems-scroll {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding: 0;
}
.m-gems-scroll::-webkit-scrollbar { display: none; }

.m-gems-container {
  display: flex;
  gap: 12px;
  padding: 4px 0;
}

.m-gem-card {
  flex: 0 0 180px;
  background: rgba(15, 25, 35, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
}

.m-gem-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.m-gem-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.3);
  flex-shrink: 0;
}


.m-gem-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.m-gem-symbol {
  font-size: 12px;
  font-weight: 700;
  color: #fff;
}

.m-gem-rank {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
}

.m-gem-score {
  font-size: 14px;
  font-weight: 800;
  padding: 4px 8px;
  border-radius: 6px;
}

.m-gem-score.gem-excellent { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.m-gem-score.gem-good { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.m-gem-score.gem-moderate { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }

.m-gem-stats {
  display: flex;
  gap: 8px;
}

.m-gem-stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.m-gem-stat .stat-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
}

.m-gem-stat .stat-value {
  font-size: 12px;
  font-weight: 600;
}

.m-gem-stat .stat-value.positive { color: #10b981; }
.m-gem-stat .stat-value.negative { color: #ef4444; }

.m-gems-empty {
  padding: 24px;
  text-align: center;
  color: rgba(255, 255, 255, 0.3);
  font-size: 13px;
}

/* Mobile Gem Enhanced - Badges & Footer */
.m-gem-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin: 8px 0;
}

.m-gem-badge {
  font-size: 8px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 8px;
  text-transform: uppercase;
  background: rgba(100, 116, 139, 0.2);
  color: #94a3b8;
}

.m-gem-badge.accumulating {
  background: rgba(14, 165, 233, 0.2);
  color: #38bdf8;
  border: 1px solid rgba(14, 165, 233, 0.3);
}

.m-gem-badge.confirmed {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.m-gem-badge.sig-accumulation { background: rgba(14, 165, 233, 0.2); color: #38bdf8; }
.m-gem-badge.sig-very-strong-bull,
.m-gem-badge.sig-strong-bullish,
.m-gem-badge.sig-bullish { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.m-gem-badge.sig-very-strong-bear,
.m-gem-badge.sig-bearish { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

.m-gem-footer {
  display: flex;
  gap: 6px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.m-gem-tech {
  font-size: 8px;
  font-weight: 600;
  padding: 2px 5px;
  border-radius: 4px;
  background: rgba(100, 116, 139, 0.15);
  color: #94a3b8;
}

.m-gem-tech.macd-bullish { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.m-gem-tech.macd-bearish { background: rgba(239, 68, 68, 0.12); color: #f87171; }
.m-gem-tech.bb-upper { background: rgba(239, 68, 68, 0.12); color: #f87171; }
.m-gem-tech.bb-lower { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.m-gem-tech.bb-middle { background: rgba(100, 116, 139, 0.15); color: #94a3b8; }

/* RSI classes for gems */
.stat-value.rsi-overbought { color: #ef4444; }
.stat-value.rsi-oversold { color: #10b981; }
.stat-value.rsi-neutral { color: rgba(255, 255, 255, 0.7); }

.m-section-note {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

/* ================================== */
/* Technical Signals Section Styles   */
/* ================================== */
.m-signals-scroll {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding: 0 16px;
}
.m-signals-scroll::-webkit-scrollbar { display: none; }

.m-signals-container {
  display: flex;
  gap: 12px;
  padding: 4px 0;
}

.m-signal-card {
  flex: 0 0 170px;
  background: rgba(15, 25, 35, 0.7);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 12px;
  padding: 12px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
}

.m-signal-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.m-signal-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  flex-shrink: 0;
}

.m-signal-info { flex: 1; display: flex; flex-direction: column; }
.m-signal-symbol { font-size: 12px; font-weight: 700; color: #fff; }
.m-signal-price { font-size: 10px; color: rgba(255, 255, 255, 0.5); }

.m-signal-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 8px;
}

.m-signal-pattern {
  font-size: 10px;
  font-weight: 600;
  padding: 3px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  width: fit-content;
}
.m-signal-pattern.pattern-bullish { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.m-signal-pattern.pattern-bearish { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.m-signal-pattern.pattern-neutral { background: rgba(251, 191, 36, 0.2); color: #fbbf24; }

.m-signal-macd {
  font-size: 10px;
  font-weight: 600;
  padding: 3px 6px;
  border-radius: 4px;
  width: fit-content;
}
.m-signal-macd.macd-bullish { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.m-signal-macd.macd-bearish { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

.m-signal-div {
  font-size: 10px;
  font-weight: 600;
  padding: 3px 6px;
  border-radius: 4px;
  width: fit-content;
}
.m-signal-div.bullish { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.m-signal-div.bearish { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

.m-signal-footer { display: flex; justify-content: flex-end; }
.m-signal-change { font-size: 12px; font-weight: 600; }
.m-signal-change.positive { color: #10b981; }
.m-signal-change.negative { color: #ef4444; }

.m-signals-empty {
  padding: 24px;
  text-align: center;
  color: rgba(255, 255, 255, 0.3);
  font-size: 13px;
}

/* ================================== */
/* Technical Signals List/Table Styles (Matching Desktop) */
/* ================================== */
.m-tsig-list {
  padding: 0;
}

/* Main Container Card (Unified List) */
.m-tsig-card {
  background: rgba(15, 25, 35, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 0;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
}

.m-tsig-row {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding: 12px 14px;
}
.m-tsig-row:last-child {
  border-bottom: none;
}

.m-tsig-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

/* Rank Circle */
.m-tsig-rank-circle {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 800;
  color: #000;
  flex-shrink: 0;
}
.rank-1 { background: #fbbf24; box-shadow: 0 0 8px rgba(251, 191, 36, 0.4); }
.rank-2 { background: #94a3b8; box-shadow: 0 0 8px rgba(148, 163, 184, 0.4); }
.rank-3 { background: #d97706; box-shadow: 0 0 8px rgba(217, 119, 6, 0.4); }
.rank-4, .rank-5, .rank-6, .rank-7, .rank-8, .rank-9, .rank-10 { 
  background: rgba(45, 212, 191, 0.2); 
  color: #2dd4bf; 
}

.m-tsig-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.m-tsig-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.m-tsig-symbol { font-size: 14px; font-weight: 700; color: #fff; }
.m-tsig-name { font-size: 11px; color: rgba(255, 255, 255, 0.4); }

.m-tsig-meta-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.m-tsig-price-box {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.m-tsig-action-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.signal-label-top {
  font-size: 8px;
  color: rgba(255, 255, 255, 0.4);
  font-weight: 600;
  text-transform: uppercase;
}
.m-tsig-price { font-size: 13px; font-weight: 600; color: #fff; }
.m-tsig-change { font-size: 10px; font-weight: 500; }
.m-tsig-change.positive { color: #10b981; }
.m-tsig-change.negative { color: #ef4444; }

/* Signal Button */
.signal-btn {
  font-size: 10px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  min-width: 50px;
  text-align: center;
}
.btn-strong_buy, .btn-buy { background: #10b981; color: #fff; box-shadow: 0 0 10px rgba(16, 185, 129, 0.3); }
.btn-strong_sell, .btn-sell { background: #ef4444; color: #fff; box-shadow: 0 0 10px rgba(239, 68, 68, 0.3); }
.btn-hold, .btn-neutral { background: rgba(255, 255, 255, 0.15); color: rgba(255, 255, 255, 0.7); }

/* Bottom Indicators */
.m-tsig-indicators-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 2px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.m-tsig-indicators-scroll::-webkit-scrollbar { display: none; }

.m-tsig-pill {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.03);
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.pill-label { font-size: 9px; font-weight: 600; color: rgba(255, 255, 255, 0.3); }
.pill-val { font-size: 10px; font-weight: 600; color: #fff; }

.pill-val.pattern-bullish { color: #10b981; }
.pill-val.pattern-bearish { color: #ef4444; }
.pill-val.rsi-oversold { color: #10b981; }
.pill-val.rsi-overbought { color: #ef4444; }
.pill-val.macd-bullish { color: #10b981; }
.pill-val.macd-bearish { color: #ef4444; }

.m-tsig-empty { padding: 32px; text-align: center; color: rgba(255, 255, 255, 0.3); font-size: 13px; }

/* Pagination Controls for Technical Signals */
.m-tsig-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 12px 0;
  margin-top: 8px;
}

.m-tsig-page-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.2s ease;
}

.m-tsig-page-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.m-tsig-page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.m-tsig-page-info {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}


/* Reset Section Styles to be transparent containers */
.m-section {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
  padding: 0 0 16px 0;
}

/* Glassmorphism for Stats Cards */
.m-stat-card-pro {
  background: rgba(15, 25, 35, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
  padding: 16px;
  min-width: 140px; /* Ensure cards have width */
}

/* Ensure padding for stats container since section lost it */
.m-stats-container {
  padding: 4px 12px;
}
</style>

<style scoped>
/* Force Dark Glass Overrides for Cards */
.m-gem-card,
.m-signal-card,
.m-tsig-card,
.m-horizon-card,
.m-horizon-coin,
.m-heatmap-tile,
.m-treemap-container,
.m-horizon-tab,
.m-list--dark {
  background: rgba(15, 25, 35, 0.7) !important;
  backdrop-filter: blur(12px) !important;
  -webkit-backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 16px !important;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3) !important;
}

/* Add padding to the glass list container */
.m-list--dark {
  padding: 8px !important;
}

/* Coin card wrapper - transparent with bottom border separator */
.m-coin-card-wrapper {
  background: transparent !important;
  border: none !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
  box-shadow: none !important;
  border-radius: 0 !important;
  padding-bottom: 12px;
  margin-bottom: 12px;
}

/* Remove border from last item */
.m-coin-card-wrapper:last-child {
  border-bottom: none !important;
  margin-bottom: 0;
  padding-bottom: 0;
}

/* Keep inner items with their original styling */
.m-coin-card-wrapper .m-list-item {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  margin-bottom: 0 !important;
  padding: 2px 2px 0px !important;
}

.m-coin-card-wrapper .m-accordion-panel {
  background: transparent !important;
  border-top: 1px solid rgba(255, 255, 255, 0.05) !important;
  margin-top: 8px !important;
}

/* Specific adjustment for gem card padding/flex if needed */
.m-gem-card {
  padding: 12px;
}

/* Ensure Horizon Tab active state maintains color but keeps glass background base */
.m-horizon-tab.active {
  background: linear-gradient(135deg, rgba(56, 239, 235, 0.2), rgba(34, 197, 94, 0.15)) !important;
  border-color: rgba(56, 239, 235, 0.5) !important;
}
</style>




