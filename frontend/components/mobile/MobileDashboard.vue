<template>
  <div class="mobile-layout">
    <!-- Header (from WordPress template-main-mobile.php) -->
    <header class="m-header">
      <div class="m-header-content">
        <!-- Logo -->
        <div class="m-logo">
          <span class="m-logo-icon">🔥</span>
          <span class="m-logo-text">AI Hub</span>
        </div>

        <!-- BTC Ticker -->
        <div class="m-ticker">
          <span class="m-ticker-label">BTC</span>
          <span class="m-ticker-value" :class="{ negative: btcChange < 0 }">
            {{ formatCurrency(btcPrice, 0) }}
          </span>
        </div>

        <!-- Header Actions -->
        <div class="m-actions">
          <a href="https://aicryptohub.io" class="m-action-btn" title="Home">
            <Icon name="ph:house" class="m-icon" />
          </a>
          <button class="m-action-btn" @click="$emit('openSearch')" title="Search">
            <Icon name="ph:magnifying-glass" class="m-icon" />
          </button>
          <button class="m-action-btn" :class="{ active: activeTab === 'alerts' }" @click="$emit('setTab', 'alerts')" title="Alerts">
            <Icon name="ph:bell" class="m-icon" />
            <span v-if="alertCount > 0" class="m-badge">{{ alertCount > 9 ? '9+' : alertCount }}</span>
          </button>
          <button class="m-action-btn" :class="{ active: activeTab === 'portfolio' }" @click="$emit('setTab', 'portfolio')" title="Portfolio">
            <Icon name="ph:briefcase" class="m-icon" />
          </button>
        </div>
      </div>
    </header>

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
                      <stop offset="0%" stop-color="rgba(34, 197, 94, 0.4)" />
                      <stop offset="100%" stop-color="rgba(34, 197, 94, 0)" />
                    </linearGradient>
                  </defs>
                  <path d="M0,35 C8,32 16,28 24,25 C32,22 40,30 48,24 C56,18 64,22 72,16 C80,10 88,15 96,12 C104,9 112,14 120,10 L120,40 L0,40 Z" 
                        :fill="avgChange >= 0 ? 'url(#mSparkGreen)' : 'url(#mSparkRed)'" />
                  <path d="M0,35 C8,32 16,28 24,25 C32,22 40,30 48,24 C56,18 64,22 72,16 C80,10 88,15 96,12 C104,9 112,14 120,10" 
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
                <span class="m-gauge-number" :class="fearGreedClass">{{ fearGreedValue }}</span>
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

      <!-- Top Gainers Section -->
      <section class="m-section">
        <div class="m-section-header">
          <h3 class="m-section-title">
            <Icon name="ph:trend-up" class="w-4 h-4" style="color: #22c55e;" />
            Top Gainers
          </h3>
          <span class="m-section-link">ASI = AI Sentiment</span>
        </div>
        
        <div class="m-list m-list--dark">
          <template v-for="(coin, idx) in topGainers" :key="coin.coin_id">
            <!-- Main Row -->
            <div class="m-list-item" @click="expandedCoin = expandedCoin === coin.coin_id ? null : coin.coin_id">
              <span class="m-rank">{{ idx + 1 }}</span>
              <img :src="coin.image" class="m-avatar" />
              <div class="m-info">
                <span class="m-info-title">{{ coin.symbol?.toUpperCase() }}</span>
                <span class="m-info-subtitle">{{ coin.name }}</span>
              </div>
              <div class="m-price-col">
                <span class="m-info-title">{{ formatCurrency(coin.price) }}</span>
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
            
            <!-- ASI Meta Row -->
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
            <div class="m-list-item" @click="expandedCoin = expandedCoin === 'loser-'+coin.coin_id ? null : 'loser-'+coin.coin_id">
              <span class="m-rank m-rank--danger">{{ idx + 1 }}</span>
              <img :src="coin.image" class="m-avatar" />
              <div class="m-info">
                <span class="m-info-title">{{ coin.symbol?.toUpperCase() }}</span>
                <span class="m-info-subtitle">{{ coin.name }}</span>
              </div>
              <div class="m-price-col">
                <span class="m-info-title">{{ formatCurrency(coin.price) }}</span>
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
            <div class="m-list-item" @click="expandedCoin = expandedCoin === 'traded-'+coin.coin_id ? null : 'traded-'+coin.coin_id">
              <span class="m-rank m-rank--info">{{ idx + 1 }}</span>
              <img :src="coin.image" class="m-avatar" />
              <div class="m-info">
                <span class="m-info-title">{{ coin.symbol?.toUpperCase() }}</span>
                <span class="m-info-subtitle">{{ coin.name }}</span>
              </div>
              <div class="m-price-col">
                <span class="m-info-title">{{ formatCurrency(coin.price) }}</span>
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

      <!-- AI Signals Section -->
      <section class="m-section">
        <div class="m-section-header">
          <h3 class="m-section-title">
            <Icon name="ph:chart-bar" class="w-4 h-4" style="color: #8b5cf6;" />
            Top 10 Market Signals
          </h3>
          <NuxtLink to="/analysis" class="m-section-link">View All</NuxtLink>
        </div>
        
        <div class="m-list">
          <div v-for="coin in aiSignals" :key="coin.coin_id" class="m-signal-card">
            <div class="m-signal-row">
              <img :src="coin.image" class="m-avatar" />
              <div class="m-info">
                <span class="m-info-title">{{ coin.symbol }}</span>
                <span class="m-info-subtitle">{{ coin.name }}</span>
              </div>
              <span class="m-signal-badge" :class="'m-signal-' + coin.signal.toLowerCase().replace('_', '-')">
                {{ coin.signal }}
              </span>
            </div>
            <div class="m-asi-row">
              <div class="m-asi-bar">
                <div class="m-asi-fill" :class="getAsiClass(coin.asi_score)" :style="{ width: coin.asi_score + '%' }"></div>
              </div>
              <span class="m-asi-label" :class="getAsiClass(coin.asi_score)">ASI: {{ coin.asi_score }}</span>
            </div>
          </div>
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
      <button class="m-nav-item" :class="{ active: activeTab === 'news' }" @click="$emit('setTab', 'news')">
        <Icon name="ph:newspaper" class="m-nav-icon" />
        <span class="m-nav-label">News</span>
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
    .filter(c => c.signal !== 'HOLD')
    .sort((a, b) => b.asi_score - a.asi_score)
    .slice(0, 10)
})

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
    // Fetch market data
    const marketRes = await api.getMarketData(100)
    if (marketRes.success && marketRes.data) {
      allCoins.value = marketRes.data as Coin[]
      
      // Calculate market stats
      const btc = allCoins.value.find(c => c.coin_id === 'bitcoin')
      if (btc) {
        btcPrice.value = btc.price
        btcChange.value = btc.change_24h
      }
      
      totalMarketCap.value = allCoins.value.reduce((sum, c) => sum + (c.market_cap || 0), 0)
      total24hVolume.value = allCoins.value.reduce((sum, c) => sum + (c.volume_24h || 0), 0)
      
      // Calculate average change
      const changes = allCoins.value.map(c => c.change_24h).filter(c => c !== undefined)
      avgChange.value = changes.length > 0 ? changes.reduce((a, b) => a + b, 0) / changes.length : 0
      
      // Calculate BTC dominance
      if (btc && totalMarketCap.value > 0) {
        btcDominance.value = (btc.market_cap / totalMarketCap.value) * 100
      }
      
      // Calculate Fear & Greed from average sentiment
      const avgAsi = Object.values(sentimentMap.value).reduce((sum, s) => sum + s.asi_score, 0) / 
                     Math.max(1, Object.keys(sentimentMap.value).length)
      fearGreedValue.value = avgAsi || 50
    }
    
    // Fetch sentiment data
    const sentimentRes = await api.getSentiment(100)
    if (Array.isArray(sentimentRes)) {
      sentimentMap.value = {}
      sentimentRes.forEach((s: SentimentData) => {
        sentimentMap.value[s.coin_id] = s
      })
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
  
  // Refresh every 30 seconds
  const interval = setInterval(fetchData, 30000)
  onUnmounted(() => clearInterval(interval))
})

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
</style>
