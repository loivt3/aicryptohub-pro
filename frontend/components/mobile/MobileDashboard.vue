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
        <div class="m-section-header">
          <h3 class="m-section-title">
            <Icon name="ph:pulse" class="w-4 h-4" style="color: #8b5cf6;" />
            ASI by Horizon
          </h3>
          <NuxtLink to="/analysis" class="m-section-link">View All</NuxtLink>
        </div>
        
        <!-- Horizon Tabs -->
        <div class="m-horizon-tabs">
          <button 
            class="m-horizon-tab" 
            :class="{ active: activeHorizon === 'short' }"
            @click="activeHorizon = 'short'"
          >
            <span class="tab-label">Short</span>
            <span class="tab-tf">1h</span>
          </button>
          <button 
            class="m-horizon-tab" 
            :class="{ active: activeHorizon === 'medium' }"
            @click="activeHorizon = 'medium'"
          >
            <span class="tab-label">Medium</span>
            <span class="tab-tf">4h+1d</span>
          </button>
          <button 
            class="m-horizon-tab" 
            :class="{ active: activeHorizon === 'long' }"
            @click="activeHorizon = 'long'"
          >
            <span class="tab-label">Long</span>
            <span class="tab-tf">1w+1M</span>
          </button>
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
                <!-- Mini Sparkline -->
                <div class="m-mini-sparkline" style="width: 50px; height: 24px;">
                  <svg viewBox="0 0 50 24" preserveAspectRatio="none" style="width: 100%; height: 100%;">
                    <path d="M0,20 C5,18 10,14 15,12 C20,10 25,16 30,11 C35,6 40,10 45,8 L50,24 L0,24 Z" :fill="coin.change_24h >= 0 ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'"/>
                    <path d="M0,20 C5,18 10,14 15,12 C20,10 25,16 30,11 C35,6 40,10 45,8" fill="none" :stroke="coin.change_24h >= 0 ? '#22c55e' : '#ef4444'" stroke-width="1.5"/>
                  </svg>
                </div>
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
                <span class="m-signal-badge" :class="'m-signal-' + (coin.signal || 'hold').toLowerCase().replace('_', '-')">
                  {{ formatSignal(coin.signal) }}
                </span>
              </div>
            </div>
          </template>
          
          <div v-if="horizonCoins.length === 0" class="m-horizon-empty">
            <Icon name="ph:chart-bar" class="w-8 h-8 opacity-30" />
            <span>No multi-horizon data yet</span>
          </div>
        </div>
      </section>

      <!-- Top Gainers Section -->
      <section class="m-section">
        <div class="m-section-header">
          <h3 class="m-section-title">
            <Icon name="ph:trend-up" class="w-4 h-4" style="color: #22c55e;" />
            Top Gainers
          </h3>
          <span class="m-section-link">ASI = AI Signal</span>
        </div>
        
        <div class="m-list m-list--dark">
          <template v-for="(coin, idx) in topGainers" :key="coin.coin_id">
            <!-- Main Row + Meta combined -->
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
                <!-- Mini Sparkline -->
                <div class="m-mini-sparkline" style="width: 50px; height: 24px;">
                  <svg viewBox="0 0 50 24" preserveAspectRatio="none" style="width: 100%; height: 100%;">
                    <path d="M0,20 C5,18 10,14 15,12 C20,10 25,16 30,11 C35,6 40,10 45,8 L50,24 L0,24 Z" fill="rgba(34,197,94,0.3)"/>
                    <path d="M0,20 C5,18 10,14 15,12 C20,10 25,16 30,11 C35,6 40,10 45,8" fill="none" stroke="#22c55e" stroke-width="1.5"/>
                  </svg>
                </div>
                <Icon name="ph:caret-right" class="w-4 h-4 opacity-30" :class="{ 'rotate-90': expandedCoin === coin.coin_id }" />
              </div>
              <!-- ASI Meta Row - inside list-item -->
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
            
            <!-- Expanded Panel -->
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
              
              <!-- Support & Resistance -->
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
                <!-- Pivot Point -->
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
          </template>
        </div>
      </section>

      <!-- Top Losers Section -->
      <section class="m-section">
        <div class="m-section-header">
          <h3 class="m-section-title">
            <Icon name="ph:trend-down" class="w-4 h-4" style="color: #ef4444;" />
            Top Losers
          </h3>
        </div>
        
        <div class="m-list m-list--dark">
          <template v-for="(coin, idx) in topLosers" :key="'loser-'+coin.coin_id">
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
                    <path d="M0,8 C5,10 10,14 15,16 C20,18 25,12 30,17 C35,22 40,18 45,20 L50,24 L0,24 Z" fill="rgba(239,68,68,0.3)"/>
                    <path d="M0,8 C5,10 10,14 15,16 C20,18 25,12 30,17 C35,22 40,18 45,20" fill="none" stroke="#ef4444" stroke-width="1.5"/>
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
            
            <!-- Expanded Panel for Losers -->
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
          </template>
        </div>
      </section>

      <!-- Most Traded Section -->
      <section class="m-section">
        <div class="m-section-header">
          <h3 class="m-section-title">
            <Icon name="ph:activity" class="w-4 h-4" style="color: #f97316;" />
            Most Traded
          </h3>
        </div>
        
        <div class="m-list m-list--dark">
          <template v-for="(coin, idx) in mostTraded" :key="'traded-'+coin.coin_id">
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
                    <path d="M0,12 C5,10 10,16 15,14 C20,12 25,18 30,14 C35,10 40,14 45,12" fill="none" :stroke="coin.change_24h >= 0 ? '#22c55e' : '#ef4444'" stroke-width="1.5"/>
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
            
            <!-- Expanded Panel for Most Traded -->
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
          </template>
        </div>
      </section>

      <!-- AI Signals Treemap Section -->
      <section class="m-section">
        <div class="m-section-header">
          <h3 class="m-section-title">
            <Icon name="ph:squares-four" class="w-4 h-4" style="color: #8b5cf6;" />
            Market Heatmap
          </h3>
          <NuxtLink to="/analysis" class="m-section-link">View All</NuxtLink>
        </div>
        
        <!-- Treemap Container -->
        <div class="m-treemap-container" ref="treemapContainer">
          <div 
            v-for="(tile, idx) in treemapLayout" 
            :key="tile.coin_id" 
            class="m-treemap-tile"
            :style="{
              left: tile.x + '%',
              top: tile.y + '%',
              width: tile.w + '%',
              height: tile.h + '%',
              ...getTreemapTileStyle(tile.asi_score, tile.change_24h),
            }"
          >
            <span class="treemap-symbol" :class="{ 'treemap-symbol-small': tile.w < 15 }">
              {{ tile.symbol?.toUpperCase() }}
            </span>
            <span v-if="tile.w >= 12" class="treemap-change" :class="tile.change_24h >= 0 ? 'up' : 'down'">
              {{ tile.change_24h >= 0 ? '+' : '' }}{{ tile.change_24h?.toFixed(1) }}%
            </span>
          </div>
        </div>
        
        <!-- Legend -->
        <div class="m-heatmap-legend">
          <span class="legend-label">Bearish</span>
          <div class="legend-bar"></div>
          <span class="legend-label">Bullish</span>
        </div>
      </section>

      <div class="m-bottom-spacer"></div>
    </main>

    <!-- Bottom Navigation (from WordPress) -->
    <nav class="m-bottom-nav">
      <button class="m-nav-item" :class="{ active: activeTab === 'dashboard' }" @click="$emit('setTab', 'dashboard')">
        <Icon name="ph:squares-four" class="m-nav-icon" />
        <span class="m-nav-label">Dashboard</span>
      </button>
      <button class="m-nav-item" :class="{ active: activeTab === 'market' }" @click="$emit('setTab', 'market')">
        <Icon name="ph:trend-up" class="m-nav-icon" />
        <span class="m-nav-label">Market</span>
      </button>
      <button class="m-nav-item" :class="{ active: activeTab === 'analysis' }" @click="$emit('setTab', 'analysis')">
        <Icon name="ph:chart-line-up" class="m-nav-icon" />
        <span class="m-nav-label">Analysis</span>
      </button>
      <button class="m-nav-item" :class="{ active: activeTab === 'shadow' }" @click="$emit('setTab', 'shadow')">
        <Icon name="ph:eye" class="m-nav-icon" />
        <span class="m-nav-label">Shadow</span>
      </button>
      <button class="m-nav-item" :class="{ active: activeTab === 'aichat' }" @click="$emit('setTab', 'aichat')">
        <Icon name="ph:chat-dots" class="m-nav-icon" />
        <span class="m-nav-label">AI Chat</span>
      </button>
    </nav>
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

// Multi-horizon data for all coins (fetched from API)
const multiHorizonData = ref<Record<string, any>>({})

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

const aiSignals = computed(() => {
  return [...allCoins.value]
    .map(c => ({
      ...c,
      asi_score: sentimentMap.value[c.coin_id]?.asi_score || 50,
      signal: sentimentMap.value[c.coin_id]?.signal || 'HOLD',
    }))
    .sort((a, b) => (b.market_cap || 0) - (a.market_cap || 0))  // Sort by market cap for treemap
    .slice(0, 20)  // Top 20 coins for treemap
})

// Treemap layout calculator - improved row-based algorithm
const treemapLayout = computed(() => {
  const coins = aiSignals.value
  if (!coins.length) return []
  
  // Use logarithmic scale to prevent BTC from dominating
  const items = coins.map(c => ({
    ...c,
    weight: Math.log10((c.market_cap || 1) + 1),
  }))
  
  const totalWeight = items.reduce((sum, c) => sum + c.weight, 0)
  if (totalWeight === 0) return []
  
  // Normalize weights
  items.forEach(item => {
    item.weight = item.weight / totalWeight
  })
  
  // Define rows based on number of items
  // Row 1: Top 2 (biggest)
  // Row 2: Next 3
  // Row 3: Next 5
  // Row 4: Next 5
  // Row 5: Remaining
  const rowConfig = [
    { count: 2, height: 30 },   // 30% height for top 2
    { count: 3, height: 25 },   // 25% for next 3
    { count: 5, height: 20 },   // 20% for next 5
    { count: 5, height: 15 },   // 15% for next 5
    { count: 5, height: 10 },   // 10% for remaining
  ]
  
  const layout: any[] = []
  let currentY = 0
  let itemIndex = 0
  
  for (const row of rowConfig) {
    if (itemIndex >= items.length) break
    
    const rowItems = items.slice(itemIndex, itemIndex + row.count)
    if (rowItems.length === 0) break
    
    // Calculate row weight for proportional widths
    const rowTotalWeight = rowItems.reduce((sum, item) => sum + item.weight, 0)
    
    // Layout items in this row
    let currentX = 0
    for (const item of rowItems) {
      const widthPct = (item.weight / rowTotalWeight) * 100
      layout.push({
        ...item,
        x: currentX,
        y: currentY,
        w: Math.max(widthPct, 8), // Min 8% width for readability
        h: row.height,
      })
      currentX += widthPct
    }
    
    currentY += row.height
    itemIndex += rowItems.length
  }
  
  return layout
})

// Treemap tile style based on price change (like CoinGecko)
const getTreemapTileStyle = (asiScore: number, change24h: number) => {
  // Color based on change percentage (typical treemap style)
  let bgColor: string
  
  if (change24h >= 5) {
    bgColor = '#00c853'  // Strong green
  } else if (change24h >= 2) {
    bgColor = '#26a69a'  // Teal green
  } else if (change24h >= 0) {
    bgColor = '#2e7d6f'  // Muted teal
  } else if (change24h >= -2) {
    bgColor = '#4a4a4a'  // Gray
  } else if (change24h >= -5) {
    bgColor = '#b71c1c'  // Red
  } else {
    bgColor = '#d32f2f'  // Strong red
  }
  
  return {
    background: bgColor,
    borderColor: 'rgba(0,0,0,0.3)',
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
    if (Array.isArray(sentimentRes)) {
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
    
    // Fetch multi-horizon ASI for top 10 coins
    try {
      const config = useRuntimeConfig()
      const topCoinIds = allCoins.value.slice(0, 10).map(c => c.coin_id)
      
      // Fetch multi-horizon data for each coin in parallel
      const mhPromises = topCoinIds.map(async (coinId) => {
        try {
          const res = await $fetch<any>(`${config.public.apiBase}/sentiment/${coinId}/multi-horizon`)
          if (res?.success && res.data) {
            return { coinId, data: res.data }
          }
          return null
        } catch {
          return null
        }
      })
      
      const mhResults = await Promise.all(mhPromises)
      mhResults.forEach(result => {
        if (result) {
          multiHorizonData.value[result.coinId] = result.data
        }
      })
    } catch (e) {
      console.warn('Failed to fetch multi-horizon data for coins:', e)
    }
  } catch (error) {
    console.error('Failed to fetch data:', error)
  } finally {
    loading.value = false
  }
}

// Fetch on mount
onMounted(() => {
  fetchData()
  
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

/* Multi-Horizon ASI Cards */
.m-horizon-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 0 12px;
}

.m-horizon-card {
  background: rgba(30, 30, 50, 0.8);
  border-radius: 8px;
  padding: 12px 8px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 2px;
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
  padding: 10px 8px;
  background: rgba(30, 30, 50, 0.6);
  border: 1px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.m-horizon-tab:hover {
  background: rgba(40, 40, 70, 0.8);
}

.m-horizon-tab.active {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(56, 189, 248, 0.15));
  border-color: rgba(139, 92, 246, 0.4);
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
  color: #8b5cf6;
}

/* Stats Bar */
.m-horizon-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  padding: 0 12px;
  margin-bottom: 12px;
}

.m-stat-mini {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 4px;
  background: rgba(30, 30, 50, 0.5);
  border-radius: 8px;
}

.m-stat-mini .stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.m-stat-mini .stat-value.positive { color: #22c55e; }
.m-stat-mini .stat-value.neutral { color: #f59e0b; }
.m-stat-mini .stat-value.negative { color: #ef4444; }

.m-stat-mini .stat-label {
  font-size: 10px;
  color: #888;
  margin-top: 2px;
}

/* Horizon Coin List */
.m-horizon-list {
  padding: 0 12px;
}

.m-horizon-coin {
  background: rgba(30, 30, 50, 0.6);
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 8px;
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
  padding: 0 12px;
}

.m-heatmap-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px 4px;
  border-radius: 10px;
  border: 1px solid transparent;
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
  gap: 10px;
  margin: 12px 12px 0;
  padding: 8px;
  background: rgba(30, 30, 50, 0.5);
  border-radius: 8px;
}

.m-heatmap-legend .legend-label {
  font-size: 10px;
  color: #888;
  font-weight: 500;
}

.m-heatmap-legend .legend-bar {
  flex: 1;
  max-width: 160px;
  height: 6px;
  border-radius: 3px;
  background: linear-gradient(
    90deg,
    rgb(220, 38, 38) 0%,
    rgb(245, 158, 11) 40%,
    rgb(234, 179, 8) 50%,
    rgb(132, 204, 22) 70%,
    rgb(34, 197, 94) 100%
  );
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
  width: 100%;
  height: 220px;
  margin: 0 12px;
  border-radius: 8px;
  overflow: hidden;
  background: #1a1a2e;
}

.m-treemap-tile {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(0,0,0,0.3);
  transition: all 0.2s ease;
  cursor: pointer;
  overflow: hidden;
}

.m-treemap-tile:hover {
  filter: brightness(1.2);
  z-index: 10;
}

.treemap-symbol {
  font-size: 14px;
  font-weight: 800;
  color: #fff;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
  letter-spacing: 0.5px;
}

.treemap-symbol-small {
  font-size: 10px;
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
</style>
