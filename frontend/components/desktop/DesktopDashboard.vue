<template>
  <div class="d-dashboard">
    <!-- Stats Cards Row (WordPress Style) -->
    <section class="d-section">
      <div class="d-stats-grid">
        <!-- Total Market Cap -->
        <div class="d-stat-card">
          <div class="d-stat-header">
            <span class="d-stat-label">TOTAL MARKET CAP</span>
            <span class="d-stat-change" :class="avgChange >= 0 ? 'up' : 'down'">
              {{ avgChange >= 0 ? '▲' : '▼' }} {{ Math.abs(avgChange).toFixed(2) }}%
            </span>
          </div>
          <div class="d-stat-value">{{ formatCurrency(totalMarketCap) }}</div>
          <div class="d-stat-sparkline">
            <svg viewBox="0 0 120 40" preserveAspectRatio="none">
              <defs>
                <linearGradient id="sparkGreen" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="rgba(34, 197, 94, 0.4)" />
                  <stop offset="100%" stop-color="rgba(34, 197, 94, 0)" />
                </linearGradient>
              </defs>
              <path d="M0,35 C8,32 16,28 24,25 C32,22 40,30 48,24 C56,18 64,22 72,16 C80,10 88,15 96,12 C104,9 112,14 120,10 L120,40 L0,40 Z" fill="url(#sparkGreen)" />
              <path d="M0,35 C8,32 16,28 24,25 C32,22 40,30 48,24 C56,18 64,22 72,16 C80,10 88,15 96,12 C104,9 112,14 120,10" fill="none" stroke="#22c55e" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
        </div>

        <!-- BTC Dominance -->
        <div class="d-stat-card">
          <div class="d-stat-header">
            <span class="d-stat-label">BTC DOMINANCE</span>
            <span class="d-stat-change" :class="btcDomChange >= 0 ? 'up' : 'down'">
              {{ btcDomChange >= 0 ? '▲' : '▼' }} {{ Math.abs(btcDomChange).toFixed(2) }}%
            </span>
          </div>
          <div class="d-stat-value">{{ btcDominance.toFixed(1) }}%</div>
          <div class="d-stat-progress">
            <div class="d-stat-bar" :style="{ width: btcDominance + '%' }"></div>
          </div>
        </div>

        <!-- Fear & Greed with Gauge -->
        <div class="d-stat-card d-stat-card--gauge">
          <div class="d-stat-header">
            <span class="d-stat-label">FEAR & GREED INDEX</span>
          </div>
          <div class="d-gauge-wrapper">
            <svg viewBox="0 0 100 60" class="d-gauge-svg">
              <defs>
                <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#ef4444" />
                  <stop offset="25%" stop-color="#f97316" />
                  <stop offset="50%" stop-color="#eab308" />
                  <stop offset="75%" stop-color="#84cc16" />
                  <stop offset="100%" stop-color="#22c55e" />
                </linearGradient>
              </defs>
              <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="8" stroke-linecap="round"/>
              <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="url(#gaugeGrad)" stroke-width="8" stroke-linecap="round"/>
              <line :x1="50" :y1="50" :x2="50 + 28 * Math.cos((180 - fearGreedValue * 1.8) * Math.PI / 180)" :y2="50 - 28 * Math.sin((180 - fearGreedValue * 1.8) * Math.PI / 180)" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
              <circle cx="50" cy="50" r="4" fill="#1a1f2e" stroke="#fff" stroke-width="2"/>
            </svg>
            <div class="d-gauge-value">
              <span class="d-gauge-number" :class="fearGreedClass">{{ fearGreedValue }}</span>
              <span class="d-gauge-label">{{ fearGreedLabel }}</span>
            </div>
          </div>
        </div>

        <!-- 24H Volume -->
        <div class="d-stat-card">
          <div class="d-stat-header">
            <span class="d-stat-label">24H VOLUME</span>
          </div>
          <div class="d-stat-value">{{ formatCurrency(total24hVolume) }}</div>
          <div class="d-stat-sparkline">
            <svg viewBox="0 0 120 40" preserveAspectRatio="none">
              <defs>
                <linearGradient id="sparkCyan" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="rgba(56, 189, 248, 0.4)" />
                  <stop offset="100%" stop-color="rgba(56, 189, 248, 0)" />
                </linearGradient>
              </defs>
              <path d="M0,28 C10,22 20,30 30,18 C40,6 50,20 60,14 C70,8 80,25 90,15 C100,5 110,18 120,12 L120,40 L0,40 Z" fill="url(#sparkCyan)" />
              <path d="M0,28 C10,22 20,30 30,18 C40,6 50,20 60,14 C70,8 80,25 90,15 C100,5 110,18 120,12" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
        </div>
      </div>
    </section>

    <!-- ASI by Horizon Section (Desktop Table Style) -->
    <section class="d-section">
      <div class="d-section-header">
        <h2 class="d-section-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2"><path d="M3 12h4l3 8l4-16l3 8h4"/></svg>
          ASI by Horizon
        </h2>
        <!-- Inline Tabs -->
        <div class="d-inline-tabs">
          <button 
            class="d-inline-tab" 
            :class="{ active: activeHorizon === 'short' }"
            @click="activeHorizon = 'short'"
          >Short (1h)</button>
          <button 
            class="d-inline-tab" 
            :class="{ active: activeHorizon === 'medium' }"
            @click="activeHorizon = 'medium'"
          >Medium (4h+1d)</button>
          <button 
            class="d-inline-tab" 
            :class="{ active: activeHorizon === 'long' }"
            @click="activeHorizon = 'long'"
          >Long (1w+1M)</button>
        </div>
      </div>
      
      <!-- Table Card -->
      <div class="d-table-card">
        <table class="d-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Coin</th>
              <th class="text-right">Price</th>
              <th class="text-right">24h</th>
              <th class="text-center">7D Chart</th>
              <th class="text-right">Market Cap</th>
              <th>ASI</th>
              <th>Signal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(coin, idx) in horizonCoins" :key="coin.coin_id">
              <td><span class="d-rank">{{ idx + 1 }}</span></td>
              <td>
                <div class="d-coin-cell">
                  <img :src="coin.image" class="d-coin-avatar" />
                  <div>
                    <span class="d-coin-name">{{ coin.symbol?.toUpperCase() }}</span>
                    <span class="d-coin-symbol">{{ coin.name }}</span>
                  </div>
                </div>
              </td>
              <td class="text-right font-mono">{{ formatPrice(coin.price) }}</td>
              <td class="text-right" :class="coin.change_24h >= 0 ? 'text-success' : 'text-danger'">
                {{ coin.change_24h >= 0 ? '+' : '' }}{{ coin.change_24h?.toFixed(2) }}%
              </td>
              <td class="d-sparkline-cell">
                <svg class="d-sparkline-svg" viewBox="0 0 80 28" preserveAspectRatio="none">
                  <defs>
                    <linearGradient :id="getGradientId(coin, 'asi')" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" :stop-color="coin.change_24h >= 0 ? 'rgba(0, 230, 118, 0.4)' : 'rgba(255, 82, 82, 0.4)'"/>
                      <stop offset="100%" stop-color="transparent"/>
                    </linearGradient>
                  </defs>
                  <path :d="generateSparklineFill(coin, 80, 28)" :fill="`url(#${getGradientId(coin, 'asi')})`"/>
                  <path :d="generateSparkline(coin, 80, 28)" fill="none" :stroke="getSparklineColor(coin)" stroke-width="1.8" stroke-linecap="round"/>
                </svg>
              </td>
              <td class="text-right font-mono">{{ formatMarketCap(coin.market_cap) }}</td>
              <td>
                <div class="d-asi-cell">
                  <div class="d-asi-bar"><div class="d-asi-fill" :class="getAsiClass(coin.asi_score)" :style="{ width: (coin.asi_score || 50) + '%' }"></div></div>
                  <span class="d-asi-value" :class="getAsiClass(coin.asi_score)">{{ coin.asi_score ?? '--' }}</span>
                </div>
              </td>
              <td><span class="d-signal" :class="'signal-' + (coin.signal || 'hold').toLowerCase()">{{ coin.signal || 'HOLD' }}</span></td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="horizonCoins.length === 0" class="d-table-empty">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.3"><path d="M3 3v18h18"/><path d="M18.5 8l-5.5 5.5-3-3-5 5"/></svg>
          <span>No multi-horizon data yet</span>
        </div>
      </div>
    </section>

    <!-- Top Gainers / Losers / Most Traded (3-column grid) -->
    <section class="d-section">
      <div class="d-triple-grid">
        <!-- Top Gainers -->
        <div class="d-mini-table-card">
          <div class="d-mini-header">
            <h3 class="d-mini-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
              Top Gainers
            </h3>
          </div>
          <div class="d-mini-list">
            <div v-for="(coin, idx) in topGainers" :key="coin.id" class="d-mini-item">
              <span class="d-mini-rank">{{ idx + 1 }}</span>
              <img :src="coin.image" class="d-mini-avatar" />
              <div class="d-mini-info">
                <span class="d-mini-name">{{ coin.symbol }}</span>
                <span class="d-mini-price">{{ formatPrice(coin.price) }}</span>
              </div>
              <svg class="d-mini-sparkline" viewBox="0 0 50 18" preserveAspectRatio="none">
                <defs>
                  <linearGradient :id="getGradientId(coin, 'gain')" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="rgba(0, 230, 118, 0.35)"/>
                    <stop offset="100%" stop-color="transparent"/>
                  </linearGradient>
                </defs>
                <path :d="generateSparklineFill(coin, 50, 18)" :fill="`url(#${getGradientId(coin, 'gain')})`"/>
                <path :d="generateSparkline(coin, 50, 18)" fill="none" stroke="#00E676" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              <span class="d-mini-change text-success">+{{ coin.change24h?.toFixed(2) }}%</span>
            </div>
            <div v-if="topGainers.length === 0" class="d-mini-empty">No data</div>
          </div>
        </div>

        <!-- Top Losers -->
        <div class="d-mini-table-card">
          <div class="d-mini-header">
            <h3 class="d-mini-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/></svg>
              Top Losers
            </h3>
          </div>
          <div class="d-mini-list">
            <div v-for="(coin, idx) in topLosers" :key="coin.id" class="d-mini-item">
              <span class="d-mini-rank">{{ idx + 1 }}</span>
              <img :src="coin.image" class="d-mini-avatar" />
              <div class="d-mini-info">
                <span class="d-mini-name">{{ coin.symbol }}</span>
                <span class="d-mini-price">{{ formatPrice(coin.price) }}</span>
              </div>
              <svg class="d-mini-sparkline" viewBox="0 0 50 18" preserveAspectRatio="none">
                <defs>
                  <linearGradient :id="getGradientId(coin, 'lose')" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="rgba(255, 82, 82, 0.35)"/>
                    <stop offset="100%" stop-color="transparent"/>
                  </linearGradient>
                </defs>
                <path :d="generateSparklineFill(coin, 50, 18)" :fill="`url(#${getGradientId(coin, 'lose')})`"/>
                <path :d="generateSparkline(coin, 50, 18)" fill="none" stroke="#FF5252" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              <span class="d-mini-change text-danger">{{ coin.change24h?.toFixed(2) }}%</span>
            </div>
            <div v-if="topLosers.length === 0" class="d-mini-empty">No data</div>
          </div>
        </div>

        <!-- Most Traded -->
        <div class="d-mini-table-card">
          <div class="d-mini-header">
            <h3 class="d-mini-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2"><path d="M12 2v20M2 12h20"/></svg>
              Most Traded
            </h3>
          </div>
          <div class="d-mini-list">
            <div v-for="(coin, idx) in mostTraded" :key="coin.id" class="d-mini-item">
              <span class="d-mini-rank">{{ idx + 1 }}</span>
              <img :src="coin.image" class="d-mini-avatar" />
              <div class="d-mini-info">
                <span class="d-mini-name">{{ coin.symbol }}</span>
                <span class="d-mini-price">{{ formatPrice(coin.price) }}</span>
              </div>
              <svg class="d-mini-sparkline" viewBox="0 0 50 18" preserveAspectRatio="none">
                <defs>
                  <linearGradient :id="getGradientId(coin, 'vol')" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" :stop-color="coin.change24h >= 0 ? 'rgba(0, 230, 118, 0.35)' : 'rgba(255, 82, 82, 0.35)'"/>
                    <stop offset="100%" stop-color="transparent"/>
                  </linearGradient>
                </defs>
                <path :d="generateSparklineFill(coin, 50, 18)" :fill="`url(#${getGradientId(coin, 'vol')})`"/>
                <path :d="generateSparkline(coin, 50, 18)" fill="none" :stroke="coin.change24h >= 0 ? '#00E676' : '#FF5252'" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              <span class="d-mini-volume">{{ formatMarketCap(coin.volume) }}</span>
            </div>
            <div v-if="mostTraded.length === 0" class="d-mini-empty">No data</div>
          </div>
        </div>
      </div>
    </section>



    <!-- Top Market Signals Section -->
    <section class="d-section">
      <div class="d-section-header">
        <h2 class="d-section-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#a855f7" stroke-width="2"><path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/></svg>
          Top Market Signals
        </h2>
        <span class="d-section-note">AI-powered trading signals</span>
      </div>
      
      <div class="d-table-card">
        <table class="d-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Coin</th>
              <th class="text-right">Price</th>
              <th class="text-right">24h</th>
              <th class="text-center">7D Chart</th>
              <th>ASI Score</th>
              <th>Signal</th>
              <th>Reasoning</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(coin, idx) in marketSignals" :key="coin.id">
              <td><span class="d-rank">{{ idx + 1 }}</span></td>
              <td>
                <div class="d-coin-cell">
                  <img :src="coin.image" class="d-coin-avatar" />
                  <div>
                    <span class="d-coin-name">{{ coin.symbol }}</span>
                    <span class="d-coin-symbol">{{ coin.name }}</span>
                  </div>
                </div>
              </td>
              <td class="text-right font-mono">{{ formatPrice(coin.price) }}</td>
              <td class="text-right" :class="coin.change24h >= 0 ? 'text-success' : 'text-danger'">
                {{ coin.change24h >= 0 ? '+' : '' }}{{ coin.change24h?.toFixed(2) }}%
              </td>
              <td class="d-sparkline-cell">
                <svg class="d-sparkline-svg" viewBox="0 0 80 28" preserveAspectRatio="none">
                  <defs>
                    <linearGradient :id="getGradientId(coin, 'sig')" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" :stop-color="coin.change24h >= 0 ? 'rgba(0, 230, 118, 0.4)' : 'rgba(255, 82, 82, 0.4)'"/>
                      <stop offset="100%" stop-color="transparent"/>
                    </linearGradient>
                  </defs>
                  <path :d="generateSparklineFill(coin, 80, 28)" :fill="`url(#${getGradientId(coin, 'sig')})`"/>
                  <path :d="generateSparkline(coin, 80, 28)" fill="none" :stroke="getSparklineColor(coin)" stroke-width="1.8" stroke-linecap="round"/>
                </svg>
              </td>
              <td>
                <div class="d-asi-cell">
                  <div class="d-asi-bar"><div class="d-asi-fill" :class="getAsiClass(coin.asi)" :style="{ width: coin.asi + '%' }"></div></div>
                  <span class="d-asi-value" :class="getAsiClass(coin.asi)">{{ coin.asi }}</span>
                </div>
              </td>
              <td><span class="d-signal" :class="'signal-' + coin.signal.toLowerCase()">{{ coin.signal }}</span></td>
              <td class="d-reasoning">{{ coin.reasoning || 'Technical analysis in progress...' }}</td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="marketSignals.length === 0" class="d-table-empty">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.3"><path d="M3 3v18h18"/><path d="M18.5 8l-5.5 5.5-3-3-5 5"/></svg>
          <span>No signal data available</span>
        </div>
      </div>
    </section>

    <!-- Technical Signals Section (NEW) -->
    <section class="d-section">
      <div class="d-section-header">
        <h2 class="d-section-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><path d="M3 12h4l3 8l4-16l3 8h4"/></svg>
          Technical Signals
        </h2>
        <div class="d-inline-tabs">
          <button class="d-inline-tab" :class="{ active: signalFilter === 'all' }" @click="signalFilter = 'all'">All</button>
          <button class="d-inline-tab" :class="{ active: signalFilter === 'bullish' }" @click="signalFilter = 'bullish'">Bullish</button>
          <button class="d-inline-tab" :class="{ active: signalFilter === 'bearish' }" @click="signalFilter = 'bearish'">Bearish</button>
        </div>
      </div>
      
      <div class="d-table-card">
        <table class="d-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Coin</th>
              <th class="text-right">Price</th>
              <th class="text-right">24h</th>
              <th>Pattern</th>
              <th>RSI</th>
              <th>MACD</th>
              <th>BB</th>
              <th>Confirm</th>
              <th>Signal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(coin, idx) in technicalSignals" :key="coin.coin_id">
              <td><span class="d-rank">{{ idx + 1 }}</span></td>
              <td>
                <div class="d-coin-cell">
                  <img :src="coin.image" class="d-coin-avatar" />
                  <div>
                    <span class="d-coin-name">{{ coin.symbol }}</span>
                    <span class="d-coin-symbol">{{ coin.name }}</span>
                  </div>
                </div>
              </td>
              <td class="text-right font-mono">{{ formatPrice(coin.price) }}</td>
              <td class="text-right" :class="coin.change_24h >= 0 ? 'text-success' : 'text-danger'">
                {{ coin.change_24h >= 0 ? '+' : '' }}{{ coin.change_24h?.toFixed(2) }}%
              </td>
              <td>
                <div class="d-pattern-cell" v-if="coin.pattern_name">
                  <span class="d-pattern-name" :class="'pattern-' + (coin.pattern_direction?.toLowerCase() || 'neutral')">
                    {{ coin.pattern_name }}
                  </span>
                  <span class="d-pattern-rel" :class="'rel-' + (coin.pattern_reliability?.toLowerCase() || 'low')">
                    {{ coin.pattern_reliability }}
                  </span>
                </div>
                <span v-else class="d-muted">--</span>
              </td>
              <td>
                <div class="d-rsi-cell" v-if="coin.rsi_14">
                  <span class="d-rsi-value" :class="getRsiClass(coin.rsi_14)">{{ coin.rsi_14 }}</span>
                  <span v-if="coin.divergence_type" class="d-divergence" :class="getDivergenceClass(coin.divergence_type)">
                    {{ coin.divergence_type === 'BULLISH_DIV' ? '↗ Div' : '↘ Div' }}
                  </span>
                </div>
                <span v-else class="d-muted">--</span>
              </td>
              <td>
                <span v-if="coin.macd_signal_type" class="d-macd" :class="'macd-' + coin.macd_signal_type?.toLowerCase()">
                  {{ coin.macd_signal_type }}
                </span>
                <span v-else class="d-muted">--</span>
              </td>
              <td>
                <div class="d-bb-cell" v-if="coin.bb_position">
                  <span class="d-bb-pos" :class="'bb-' + coin.bb_position?.toLowerCase()">{{ coin.bb_position }}</span>
                  <span v-if="coin.bb_squeeze" class="d-bb-squeeze">SQUEEZE</span>
                </div>
                <span v-else class="d-muted">--</span>
              </td>
              <td>
                <div class="d-confirm-cell">
                  <span class="d-confirm-count" :class="getConfirmClass(coin.confirmation_count)">
                    {{ coin.confirmation_count }}/7
                  </span>
                  <div class="d-confirm-bar">
                    <div class="d-confirm-fill" :style="{ width: (coin.confirmation_count / 7 * 100) + '%' }"></div>
                  </div>
                </div>
              </td>
              <td>
                <span v-if="coin.signal_strength" class="d-signal-strength" :class="'strength-' + (coin.signal_strength?.toLowerCase() || '')">
                  {{ formatSignalStrength(coin.signal_strength) }}
                </span>
                <span v-else class="d-muted">--</span>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="technicalSignals.length === 0" class="d-table-empty">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.3"><path d="M3 12h4l3 8l4-16l3 8h4"/></svg>
          <span>No technical signals detected</span>
        </div>
      </div>
    </section>

    <!-- Hidden Gems Section (ENHANCED) -->
    <section class="d-section">
      <div class="d-section-header">
        <h2 class="d-section-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
          Hidden Gems
        </h2>
        <span class="d-section-note">High-potential coins with strong signals</span>
      </div>
      
      <div class="d-gems-grid">
        <div v-for="coin in hiddenGems" :key="coin.coin_id" class="d-gem-card">
          <!-- Header with signal strength badge -->
          <div class="d-gem-header">
            <img :src="coin.image" class="d-gem-avatar" />
            <div class="d-gem-info">
              <span class="d-gem-symbol">{{ coin.symbol }}</span>
              <span class="d-gem-rank">#{{ coin.market_cap_rank }}</span>
            </div>
            <span class="d-gem-score" :class="getGemScoreClass(coin.discovery_score)">
              {{ coin.discovery_score }}
            </span>
          </div>
          
          <!-- Trust Badges Row -->
          <div class="d-gem-badges">
            <span v-if="coin.is_accumulating" class="d-gem-badge accumulating" title="Smart money detected">
              🐋 Accumulating
            </span>
            <span v-if="coin.signal_strength" class="d-gem-badge" :class="'sig-' + coin.signal_strength?.toLowerCase().replace(/_/g, '-')">
              {{ coin.signal_strength?.replace('_', ' ') }}
            </span>
            <span v-if="coin.confirmation_count >= 2" class="d-gem-badge confirmed">
              ✓ {{ coin.confirmation_count }} Confirmed
            </span>
          </div>
          
          <!-- Key Metrics Grid -->
          <div class="d-gem-metrics">
            <div class="d-gem-metric">
              <span class="d-gem-label">24h</span>
              <span class="d-gem-value" :class="coin.change_24h >= 0 ? 'text-success' : 'text-danger'">
                {{ coin.change_24h >= 0 ? '+' : '' }}{{ coin.change_24h?.toFixed(1) }}%
              </span>
            </div>
            <div class="d-gem-metric">
              <span class="d-gem-label">vs BTC</span>
              <span class="d-gem-value" :class="coin.rs_vs_btc >= 0 ? 'text-success' : 'text-danger'">
                {{ coin.rs_vs_btc >= 0 ? '+' : '' }}{{ coin.rs_vs_btc?.toFixed(1) }}%
              </span>
            </div>
            <div class="d-gem-metric" v-if="coin.volume_ratio">
              <span class="d-gem-label">Vol Ratio</span>
              <span class="d-gem-value" :class="coin.volume_ratio > 1.5 ? 'text-success' : ''">
                {{ coin.volume_ratio?.toFixed(1) }}x
              </span>
            </div>
            <div class="d-gem-metric" v-if="coin.rsi_14">
              <span class="d-gem-label">RSI</span>
              <span class="d-gem-value" :class="getRsiClass(coin.rsi_14)">
                {{ coin.rsi_14?.toFixed(0) }}
              </span>
            </div>
          </div>
          
          <!-- Technical Indicators Footer -->
          <div class="d-gem-footer" v-if="coin.macd_signal_type || coin.bb_position">
            <span v-if="coin.macd_signal_type" class="d-gem-tech" :class="'macd-' + coin.macd_signal_type?.toLowerCase()">
              MACD: {{ coin.macd_signal_type }}
            </span>
            <span v-if="coin.bb_position" class="d-gem-tech" :class="'bb-' + coin.bb_position?.toLowerCase()">
              BB: {{ coin.bb_position }}
            </span>
          </div>
        </div>
        
        <div v-if="hiddenGems.length === 0" class="d-gems-empty">
          <span>No hidden gems found at this time</span>
        </div>
      </div>
    </section>
  </div>
</template>


<script setup lang="ts">
interface Coin {
  id: string
  symbol: string
  name: string
  image: string
  price: number
  change24h: number
  change7d: number
  marketCap: number
  asi: number
  signal: string
}

const api = useApi()
const { updatePrice, getFlashClass } = usePriceFlashRow()
const { generateSparkline, generateSparklineFill, getSparklineColor, getGradientId } = useSparkline()

// Stats data
const totalMarketCap = ref(0)
const avgChange = ref(0)
const btcDominance = ref(52.3)
const btcDomChange = ref(0)
const fearGreedValue = ref(50)
const total24hVolume = ref(0)
const loading = ref(true)

// Coins data
const topCoins = ref<Coin[]>([])
const sentimentMap = ref<Record<string, any>>({})

// Socket status
const socketConnected = ref(false)

// ASI by Horizon data
const activeHorizon = ref<'short' | 'medium' | 'long'>('short')
const multiHorizonData = ref<Record<string, any>>({})

// Technical Signals data (NEW)
const signalFilter = ref<'all' | 'bullish' | 'bearish'>('all')
const technicalSignalsRaw = ref<any[]>([])
const hiddenGems = ref<any[]>([])

// Computed: filtered technical signals
const technicalSignals = computed(() => {
  if (signalFilter.value === 'all') return technicalSignalsRaw.value
  if (signalFilter.value === 'bullish') {
    return technicalSignalsRaw.value.filter(c => 
      c.pattern_direction === 'BULLISH' || c.divergence_type === 'BULLISH_DIV'
    )
  }
  return technicalSignalsRaw.value.filter(c => 
    c.pattern_direction === 'BEARISH' || c.divergence_type === 'BEARISH_DIV'
  )
})

// Helper functions for technical signals (NEW)
const getRsiClass = (rsi: number | null) => {
  if (!rsi) return ''
  if (rsi < 30) return 'rsi-oversold'
  if (rsi > 70) return 'rsi-overbought'
  return 'rsi-neutral'
}

const getDivergenceClass = (type: string | null) => {
  if (type === 'BULLISH_DIV') return 'div-bullish'
  if (type === 'BEARISH_DIV') return 'div-bearish'
  return ''
}

const getConfirmClass = (count: number) => {
  if (count >= 5) return 'confirm-high'
  if (count >= 3) return 'confirm-medium'
  return 'confirm-low'
}

const getGemScoreClass = (score: number) => {
  if (score >= 80) return 'gem-excellent'
  if (score >= 70) return 'gem-good'
  return 'gem-moderate'
}

const formatSignalStrength = (strength: string | null) => {
  if (!strength) return '--'
  return strength.replace(/_/g, ' ').replace('VERY STRONG ', '⚡ ').replace('CONFIRMED ', '✓ ')
}

// Computed: horizon coins list
const horizonCoins = computed(() => {
  // Use top 5 coins with multi-horizon data
  const horizon = activeHorizon.value
  
  return topCoins.value.slice(0, 5).map(coin => {
    const mhData = multiHorizonData.value[coin.id]
    let asi_score: number | null = null
    let signal = 'HOLD'
    
    if (mhData) {
      // Try horizon-specific data first
      if (horizon === 'short') {
        asi_score = mhData.asi_short ?? null
        signal = mhData.signal_short || 'HOLD'
      } else if (horizon === 'medium') {
        asi_score = mhData.asi_medium ?? null
        signal = mhData.signal_medium || 'HOLD'
      } else {
        asi_score = mhData.asi_long ?? null
        signal = mhData.signal_long || 'HOLD'
      }
      
      // Fallback to combined or short-term if specific horizon is null
      if (asi_score === null && mhData.asi_combined !== null) {
        asi_score = mhData.asi_combined
        signal = mhData.signal_combined || 'HOLD'
      } else if (asi_score === null && mhData.asi_short !== null) {
        asi_score = mhData.asi_short
        signal = mhData.signal_short || 'HOLD'
      }
    }
    
    // Final fallback to existing sentiment data
    if (asi_score === null) {
      asi_score = sentimentMap.value[coin.id]?.asi_score ?? 50
      signal = sentimentMap.value[coin.id]?.signal || 'HOLD'
    }
    
    return {
      ...coin,
      coin_id: coin.id,
      price: coin.price,
      change_24h: coin.change24h,
      market_cap: coin.marketCap,
      asi_score,
      signal,
    }
  })
})

// Computed: horizon stats
const horizonStats = computed(() => {
  const coins = horizonCoins.value
  const buyCount = coins.filter(c => c.signal === 'BUY' || c.signal === 'STRONG_BUY').length
  const sellCount = coins.filter(c => c.signal === 'SELL' || c.signal === 'STRONG_SELL').length
  const neutralCount = coins.length - buyCount - sellCount
  const avgAsi = coins.length > 0 
    ? Math.round(coins.reduce((sum, c) => sum + (c.asi_score || 50), 0) / coins.length)
    : 50
  return { buyCount, neutralCount, sellCount, avgAsi }
})

// Top Gainers (top 5 by 24h change)
const topGainers = computed(() => {
  return [...topCoins.value]
    .filter(c => c.change24h > 0)
    .sort((a, b) => b.change24h - a.change24h)
    .slice(0, 5)
})

// Top Losers (top 5 by negative 24h change)
const topLosers = computed(() => {
  return [...topCoins.value]
    .filter(c => c.change24h < 0)
    .sort((a, b) => a.change24h - b.change24h)
    .slice(0, 5)
})

// Most Traded (top 5 by volume - using marketCap as proxy since volume not in interface)
const mostTraded = computed(() => {
  return [...topCoins.value]
    .sort((a, b) => b.marketCap - a.marketCap)
    .slice(0, 5)
    .map(c => ({ ...c, volume: c.marketCap * 0.05 })) // Approximate 5% daily volume
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

const signalCounts = computed(() => ({
  buy: topCoins.value.filter(c => c.signal === 'BUY' || c.signal === 'STRONG_BUY').length,
  hold: topCoins.value.filter(c => c.signal === 'HOLD').length,
  sell: topCoins.value.filter(c => c.signal === 'SELL' || c.signal === 'STRONG_SELL').length,
}))

const trendingCoins = computed(() => {
  return [...topCoins.value]
    .sort((a, b) => b.change24h - a.change24h)
    .slice(0, 3)
    .map(c => ({
      id: c.id,
      symbol: c.symbol,
      image: c.image,
      change: c.change24h,
    }))
})

// Market Signals - top 10 by ASI score (highest confidence signals)
const marketSignals = computed(() => {
  return [...topCoins.value]
    .filter(c => c.asi)
    .sort((a, b) => b.asi - a.asi)
    .slice(0, 10)
    .map(c => ({
      id: c.id,
      symbol: c.symbol,
      name: c.name,
      image: c.image,
      price: c.price,
      change24h: c.change24h,
      asi: c.asi || 50,
      signal: c.signal || 'HOLD',
      reasoning: c.reasoning || null
    }))
})

const whaleTransactions = ref([
  { id: 1, type: 'buy', symbol: 'BTC', amount: '500', value: '49.2M', time: '2h' },
  { id: 2, type: 'sell', symbol: 'ETH', amount: '15K', value: '51.7M', time: '4h' },
  { id: 3, type: 'buy', symbol: 'SOL', amount: '250K', value: '46.2M', time: '5h' },
])

// Fetch data from API
const fetchData = async () => {
  loading.value = true
  try {
    // Fetch market data
    const marketRes = await api.getMarketData(50)
    if (marketRes.success && marketRes.data) {
      topCoins.value = marketRes.data.map((coin: any) => ({
        id: coin.coin_id,
        symbol: coin.symbol?.toUpperCase(),
        name: coin.name,
        image: coin.image,
        price: coin.price || coin.current_price || 0,
        change24h: coin.change_24h || coin.price_change_percentage_24h || 0,
        change7d: coin.change_7d || coin.price_change_percentage_7d || 0,
        marketCap: coin.market_cap || 0,
        asi: sentimentMap.value[coin.coin_id]?.asi_score || 50,
        signal: sentimentMap.value[coin.coin_id]?.signal || 'HOLD',
      }))

      // Calculate market stats
      totalMarketCap.value = topCoins.value.reduce((sum, c) => sum + c.marketCap, 0)
      total24hVolume.value = marketRes.data.reduce((sum: number, c: any) => sum + (c.volume_24h || 0), 0)
      
      const changes = topCoins.value.map(c => c.change24h).filter(c => c !== undefined)
      avgChange.value = changes.length > 0 ? changes.reduce((a, b) => a + b, 0) / changes.length : 0
      
      // Calculate BTC dominance
      const btc = topCoins.value.find(c => c.id === 'bitcoin')
      if (btc && totalMarketCap.value > 0) {
        btcDominance.value = (btc.marketCap / totalMarketCap.value) * 100
      }
    }

    // Fetch sentiment data
    const sentimentRes = await api.getSentiment(50)
    const sentimentData = sentimentRes?.success && Array.isArray(sentimentRes.data) 
      ? sentimentRes.data 
      : (Array.isArray(sentimentRes) ? sentimentRes : [])
    
    if (sentimentData.length > 0) {
      sentimentMap.value = {}
      sentimentData.forEach((s: any) => {
        sentimentMap.value[s.coin_id] = s
      })
      
      // Update coins with sentiment
      topCoins.value = topCoins.value.map(coin => ({
        ...coin,
        asi: sentimentMap.value[coin.id]?.asi_score || 50,
        signal: sentimentMap.value[coin.id]?.signal || 'HOLD',
      }))
      
      // Calculate Fear & Greed from average ASI
      const avgAsi = Object.values(sentimentMap.value).reduce((sum: number, s: any) => sum + (s.asi_score || 50), 0) / 
                     Math.max(1, Object.keys(sentimentMap.value).length)
      fearGreedValue.value = Math.round(avgAsi) || 50
    }

    
    // Fetch multi-horizon ASI for top coins (using batch API to reduce load)
    try {
      const config = useRuntimeConfig()
      const topCoinIds = topCoins.value.slice(0, 10).map(c => c.id)
      
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

// Socket.IO integration
const setupSocketConnection = () => {
  try {
    const { connect, onPriceUpdate, connected } = useSocket()
    
    connect()
    
    watch(connected, (isConnected) => {
      socketConnected.value = isConnected
    }, { immediate: true })
    
    onPriceUpdate((updates) => {
      updates.forEach((update: any) => {
        const idx = topCoins.value.findIndex(
          c => c.symbol === update.s
        )
        
        if (idx !== -1) {
          updatePrice(topCoins.value[idx].symbol, update.p)
          topCoins.value[idx] = {
            ...topCoins.value[idx],
            price: update.p,
            change24h: update.c,
          }
        }
      })
    })
  } catch (error) {
    console.error('[Desktop] Socket setup failed:', error)
  }
}

onMounted(() => {
  fetchData()
  fetchTechnicalSignals()
  setupSocketConnection()
  
  // Fallback refresh if WebSocket not connected (every 10s)
  const interval = setInterval(() => {
    if (!socketConnected.value) {
      fetchData()
    }
  }, 10000)
  
  // Refresh technical signals every 5 min
  const techInterval = setInterval(() => fetchTechnicalSignals(), 300000)
  
  onUnmounted(() => {
    clearInterval(interval)
    clearInterval(techInterval)
  })
})

// Fetch technical signals from discovery API
const fetchTechnicalSignals = async () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || 'http://localhost:8000/api/v1'
  
  try {
    // Fetch technical signals
    const [signalsRes, gemsRes] = await Promise.all([
      $fetch(`${apiBase}/discovery/technical-signals?limit=15`),
      $fetch(`${apiBase}/discovery/hidden-gems?limit=8`)
    ])


    
    if (signalsRes?.success && signalsRes.data) {
      technicalSignalsRaw.value = signalsRes.data
    }
    if (gemsRes?.success && gemsRes.data) {
      hiddenGems.value = gemsRes.data
    }
  } catch (error) {
    console.error('[Dashboard] Technical signals fetch failed:', error)
  }
}


const formatCurrency = (n: number) => '$' + (n >= 1e12 ? (n/1e12).toFixed(2) + 'T' : n >= 1e9 ? (n/1e9).toFixed(2) + 'B' : n.toLocaleString())
const formatPrice = (p: number) => '$' + (p >= 1 ? p.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : p.toFixed(6))
const formatMarketCap = (n: number) => n >= 1e12 ? '$' + (n/1e12).toFixed(2) + 'T' : '$' + (n/1e9).toFixed(1) + 'B'
const getAsiClass = (v: number) => v >= 60 ? 'positive' : v <= 40 ? 'negative' : 'neutral'
</script>

<style scoped>
/* Dashboard Styles - WordPress AI Hub Pro Design */
.d-dashboard { 
  padding: var(--aihub-spacing-xl) 0; 
  background: var(--aihub-bg-primary);
  min-height: 100vh;
}

.d-section { margin-bottom: var(--aihub-spacing-xl); }

.d-section-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 20px; 
}

.d-section-title { 
  display: flex; 
  align-items: center; 
  gap: 10px; 
  font-size: 22px; 
  font-weight: 700; 
  margin: 0; 
  color: #ffffff; 
}

.d-section-note { 
  font-size: 13px; 
  color: rgba(255, 255, 255, 0.4); 
}

/* Stats Grid - Premium Cards */
.d-stats-grid { 
  display: grid; 
  grid-template-columns: repeat(4, 1fr); 
  gap: 20px; 
}

.d-stat-card { 
  background: var(--aihub-bg-card); 
  border: 1px solid rgba(255, 255, 255, 0.08); 
  border-radius: 20px; 
  padding: 24px; 
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.d-stat-card:hover { 
  border-color: rgba(0, 212, 255, 0.4);
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.15);
  transform: translateY(-4px); 
}

.d-stat-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 12px; 
}

.d-stat-label { 
  font-size: 11px; 
  font-weight: 600; 
  color: rgba(255, 255, 255, 0.5); 
  letter-spacing: 1px; 
}

.d-stat-change { 
  font-size: 13px; 
  font-weight: 700;
  font-family: 'SF Mono', 'Roboto Mono', monospace;
}

.d-stat-change.up { color: #00ff88; }
.d-stat-change.down { color: #ff4757; }

.d-stat-value { 
  font-size: 32px; 
  font-weight: 800; 
  font-family: 'SF Mono', 'Roboto Mono', monospace;
  color: #ffffff; 
  margin-bottom: 16px;
  background: linear-gradient(135deg, #ffffff, #00d4ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.d-stat-sparkline { height: 48px; }
.d-stat-sparkline svg { width: 100%; height: 100%; }

.d-stat-progress { 
  height: 8px; 
  background: rgba(255,255,255,0.08); 
  border-radius: 4px; 
  overflow: hidden; 
}

.d-stat-bar { 
  height: 100%; 
  background: linear-gradient(90deg, #00d4ff, #0066ff); 
  border-radius: 4px; 
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

/* Gauge - Premium */
.d-stat-card--gauge { display: flex; flex-direction: column; }
.d-gauge-wrapper { display: flex; flex-direction: column; align-items: center; flex: 1; }
.d-gauge-svg { width: 100%; max-width: 160px; }
.d-gauge-value { text-align: center; margin-top: -8px; }

.d-gauge-number { 
  font-size: 40px; 
  font-weight: 800; 
  font-family: 'SF Mono', 'Roboto Mono', monospace;
  display: block; 
}

.d-gauge-number.greed { 
  color: #00ff88; 
  text-shadow: 0 0 30px rgba(0, 255, 136, 0.5);
}

.d-gauge-number.neutral { color: #ffa502; }

.d-gauge-number.fear { 
  color: #ff4757; 
  text-shadow: 0 0 30px rgba(255, 71, 87, 0.5);
}

.d-gauge-label { font-size: 13px; color: rgba(255, 255, 255, 0.5); font-weight: 500; }

/* Content Grid */
.d-content-grid { display: grid; grid-template-columns: 1fr 380px; gap: 28px; }

.d-table-card { 
  background: var(--aihub-bg-card); 
  border: 1px solid rgba(255, 255, 255, 0.08); 
  border-radius: 20px; 
  overflow: hidden;
}

.d-table { width: 100%; border-collapse: collapse; }

.d-table th, .d-table td { padding: 16px 20px; text-align: left; }

.d-table th { 
  font-size: 12px; 
  font-weight: 600; 
  color: rgba(255, 255, 255, 0.5); 
  border-bottom: 1px solid rgba(255, 255, 255, 0.06); 
  background: var(--aihub-bg-secondary);
  letter-spacing: 0.5px;
}

.d-table tbody tr { 
  border-bottom: 1px solid rgba(255, 255, 255, 0.04); 
  cursor: pointer; 
  transition: all 0.2s ease;
}

.d-table tbody tr:hover { 
  background: rgba(0, 212, 255, 0.05);
}

.d-rank { 
  display: inline-flex; 
  align-items: center; 
  justify-content: center; 
  width: 28px; 
  height: 28px; 
  background: rgba(0, 212, 255, 0.15); 
  border-radius: 50%; 
  font-size: 12px; 
  font-weight: 700;
  font-family: 'SF Mono', 'Roboto Mono', monospace; 
  color: #00d4ff; 
}

.d-coin-cell { display: flex; align-items: center; gap: 14px; }

.d-coin-avatar { 
  width: 40px; 
  height: 40px; 
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.d-coin-name { display: block; font-weight: 700; font-size: 15px; color: #ffffff; }
.d-coin-symbol { display: block; font-size: 12px; color: rgba(255, 255, 255, 0.5); }

.text-right { text-align: right; }
.text-success { color: #00ff88; font-weight: 600; }
.text-danger { color: #ff4757; font-weight: 600; }
.font-mono { font-family: 'SF Mono', 'Roboto Mono', monospace; }

/* ASI Bar - Premium */
.d-asi-cell { display: flex; align-items: center; gap: 10px; }

.d-asi-bar { 
  width: 70px; 
  height: 8px; 
  background: rgba(255,255,255,0.08); 
  border-radius: 4px; 
  overflow: hidden; 
}

.d-asi-fill { 
  height: 100%; 
  border-radius: 4px; 
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.d-asi-fill.positive { background: linear-gradient(90deg, #00ff88, #00d4ff); }
.d-asi-fill.neutral { background: linear-gradient(90deg, #ffa502, #ff7f50); }
.d-asi-fill.negative { background: linear-gradient(90deg, #ff4757, #ff6b81); }

.d-asi-value { 
  font-size: 13px; 
  font-weight: 700; 
  font-family: 'SF Mono', 'Roboto Mono', monospace;
  min-width: 28px; 
}

.d-asi-value.positive { color: #00ff88; }
.d-asi-value.neutral { color: #ffa502; }
.d-asi-value.negative { color: #ff4757; }

/* Signal Badge - Premium */
.d-signal { 
  padding: 6px 14px; 
  border-radius: 20px; 
  font-size: 11px; 
  font-weight: 700; 
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.signal-strong_buy,
.signal-strong-buy { 
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.2), rgba(0, 200, 100, 0.3)); 
  color: #00ff88;
  border: 1px solid rgba(0, 255, 136, 0.5);
  box-shadow: 0 0 12px rgba(0, 255, 136, 0.2);
}

.signal-buy { 
  background: rgba(0, 255, 136, 0.15); 
  color: #00ff88;
  border: 1px solid rgba(0, 255, 136, 0.3);
}

.signal-hold,
.signal-neutral { 
  background: rgba(255, 165, 2, 0.15); 
  color: #ffa502;
  border: 1px solid rgba(255, 165, 2, 0.3);
}

.signal-sell { 
  background: rgba(255, 71, 87, 0.15); 
  color: #ff4757;
  border: 1px solid rgba(255, 71, 87, 0.3);
}

.signal-strong_sell,
.signal-strong-sell { 
  background: linear-gradient(135deg, rgba(255, 71, 87, 0.2), rgba(220, 38, 38, 0.3)); 
  color: #ff4757;
  border: 1px solid rgba(255, 71, 87, 0.5);
  box-shadow: 0 0 12px rgba(255, 71, 87, 0.2);
}

/* Sidebar - Premium */
.d-sidebar { display: flex; flex-direction: column; gap: 20px; }

.d-sidebar-card { 
  background: var(--aihub-bg-card); 
  border: 1px solid rgba(255, 255, 255, 0.08); 
  border-radius: 20px; 
  padding: 24px;
  transition: all 0.3s ease;
}

.d-sidebar-card:hover {
  border-color: rgba(168, 85, 247, 0.3);
  box-shadow: 0 0 20px rgba(168, 85, 247, 0.1);
}

.d-sidebar-title { 
  font-size: 18px; 
  font-weight: 700; 
  margin: 0 0 20px; 
  color: #ffffff; 
}

.d-signals-summary { display: flex; justify-content: space-around; text-align: center; }
.d-signal-stat { padding: 14px; }

.d-signal-count { 
  display: block; 
  font-size: 36px; 
  font-weight: 800;
  font-family: 'SF Mono', 'Roboto Mono', monospace;
}

.d-signal-stat.buy .d-signal-count { 
  color: #00ff88;
  text-shadow: 0 0 20px rgba(0, 255, 136, 0.4);
}

.d-signal-stat.hold .d-signal-count { color: #ffa502; }

.d-signal-stat.sell .d-signal-count { 
  color: #ff4757;
  text-shadow: 0 0 20px rgba(255, 71, 87, 0.4);
}

.d-signal-label { font-size: 13px; color: rgba(255, 255, 255, 0.5); font-weight: 500; }

.d-trending-list { display: flex; flex-direction: column; gap: 14px; }

.d-trending-item { 
  display: flex; 
  align-items: center; 
  gap: 14px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  transition: all 0.2s;
}

.d-trending-item:hover {
  background: rgba(0, 212, 255, 0.05);
}

.d-trending-avatar { 
  width: 40px; 
  height: 40px; 
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.d-trending-info { flex: 1; }
.d-trending-name { font-weight: 700; font-size: 15px; display: block; color: #ffffff; }

.d-trending-change { 
  font-size: 14px; 
  font-weight: 700;
  font-family: 'SF Mono', 'Roboto Mono', monospace;
}

.d-trending-change.up { color: #00ff88; }
.d-trending-change.down { color: #ff4757; }

.d-whale-list { display: flex; flex-direction: column; gap: 12px; }

.d-whale-item { 
  display: flex; 
  align-items: center; 
  gap: 12px; 
  padding: 14px; 
  background: rgba(255,255,255,0.03); 
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.04);
  transition: all 0.2s;
}

.d-whale-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
}

.d-whale-type { font-size: 18px; }
.d-whale-info { flex: 1; }
.d-whale-amount { display: block; font-weight: 700; font-size: 14px; color: #ffffff; }
.d-whale-value { font-size: 12px; color: rgba(255, 255, 255, 0.5); }
.d-whale-time { font-size: 12px; color: rgba(255, 255, 255, 0.3); }

/* ASI by Horizon Section - CoinMarketCap Inspired */
.d-inline-tabs {
  display: flex;
  gap: 8px;
}

.d-inline-tab {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.d-inline-tab:hover {
  border-color: rgba(139, 92, 246, 0.4);
  color: #fff;
}

.d-inline-tab.active {
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.d-table-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  color: rgba(255, 255, 255, 0.4);
  font-size: 14px;
}

/* Triple Grid - Top Gainers/Losers/Most Traded */
.d-triple-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.d-mini-table-card {
  background: var(--aihub-bg-card);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.d-mini-table-card:hover {
  border-color: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.08);
}

.d-mini-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.d-mini-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.d-mini-list {
  padding: 8px 0;
}

.d-mini-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  transition: background 0.2s;
}

.d-mini-item:hover {
  background: rgba(255, 255, 255, 0.03);
}

.d-mini-rank {
  width: 20px;
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.4);
}

.d-mini-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
}

.d-mini-info {
  flex: 1;
}

.d-mini-name {
  display: block;
  font-weight: 600;
  font-size: 13px;
  color: #fff;
}

.d-mini-price {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-family: 'SF Mono', 'Roboto Mono', monospace;
}

.d-mini-change {
  font-size: 13px;
  font-weight: 600;
  font-family: 'SF Mono', 'Roboto Mono', monospace;
}

.d-mini-volume {
  font-size: 12px;
  color: #38bdf8;
  font-family: 'SF Mono', 'Roboto Mono', monospace;
}

.d-mini-empty {
  padding: 24px;
  text-align: center;
  color: rgba(255, 255, 255, 0.3);
  font-size: 13px;
}

/* Reasoning column for Market Signals */
.d-reasoning {
  max-width: 280px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Sparkline Charts */
.d-sparkline-cell {
  padding: 8px 12px !important;
  width: 100px;
  text-align: center;
}

.d-sparkline-svg {
  width: 80px;
  height: 28px;
  display: block;
}

/* Mini card sparkline */
.d-mini-sparkline {
  width: 50px;
  height: 18px;
  flex-shrink: 0;
}

.text-center {
  text-align: center;
}

/* ================================== */
/* Technical Signals Styles (NEW)     */
/* ================================== */

/* Pattern cell */
.d-pattern-cell { display: flex; flex-direction: column; gap: 2px; }
.d-pattern-name {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}
.d-pattern-name.pattern-bullish { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.d-pattern-name.pattern-bearish { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.d-pattern-name.pattern-neutral { background: rgba(148, 163, 184, 0.15); color: #94a3b8; }

.d-pattern-rel { font-size: 9px; opacity: 0.6; }
.d-pattern-rel.rel-high { color: #fbbf24; }
.d-pattern-rel.rel-medium { color: #94a3b8; }
.d-pattern-rel.rel-low { color: #64748b; }

/* RSI cell */
.d-rsi-cell { display: flex; align-items: center; gap: 4px; }
.d-rsi-value {
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-mono);
}
.d-rsi-value.rsi-oversold { color: #10b981; }
.d-rsi-value.rsi-overbought { color: #ef4444; }
.d-rsi-value.rsi-neutral { color: #94a3b8; }

.d-divergence {
  font-size: 9px;
  padding: 1px 4px;
  border-radius: 3px;
  font-weight: 500;
}
.d-divergence.div-bullish { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.d-divergence.div-bearish { background: rgba(239, 68, 68, 0.2); color: #ef4444; }

/* MACD */
.d-macd {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}
.d-macd.macd-bullish, .d-macd.macd-bullish_cross { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.d-macd.macd-bearish, .d-macd.macd-bearish_cross { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

/* Bollinger Bands */
.d-bb-cell { display: flex; flex-direction: column; gap: 2px; }
.d-bb-pos {
  font-size: 10px;
  font-weight: 500;
}
.d-bb-pos.bb-upper { color: #ef4444; }
.d-bb-pos.bb-middle { color: #94a3b8; }
.d-bb-pos.bb-lower { color: #10b981; }

.d-bb-squeeze {
  font-size: 8px;
  padding: 1px 4px;
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
  border-radius: 3px;
  font-weight: 600;
}

/* Confirmation cell */
.d-confirm-cell { display: flex; flex-direction: column; gap: 4px; align-items: center; }
.d-confirm-count {
  font-size: 11px;
  font-weight: 600;
}
.d-confirm-count.confirm-high { color: #10b981; }
.d-confirm-count.confirm-medium { color: #fbbf24; }
.d-confirm-count.confirm-low { color: #94a3b8; }

.d-confirm-bar {
  width: 40px;
  height: 3px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}
.d-confirm-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #34d399);
  border-radius: 2px;
}

/* Signal strength */
.d-signal-strength {
  font-size: 10px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
  white-space: nowrap;
}
.d-signal-strength.strength-very_strong_bull { background: rgba(16, 185, 129, 0.25); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.4); }
.d-signal-strength.strength-very_strong_bear { background: rgba(239, 68, 68, 0.25); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.4); }
.d-signal-strength.strength-strong_bullish { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.d-signal-strength.strength-strong_bearish { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.d-signal-strength.strength-confirmed_bull { background: rgba(16, 185, 129, 0.1); color: #34d399; }
.d-signal-strength.strength-confirmed_bear { background: rgba(239, 68, 68, 0.1); color: #f87171; }
.d-signal-strength.strength-bullish { color: #10b981; }
.d-signal-strength.strength-bearish { color: #ef4444; }

.d-muted { color: rgba(255, 255, 255, 0.3); font-size: 12px; }

/* ================================== */
/* Hidden Gems Grid Styles            */
/* ================================== */
.d-gems-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.d-gem-card {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 12px;
  padding: 16px;
  transition: all 0.2s ease;
}
.d-gem-card:hover {
  transform: translateY(-2px);
  border-color: rgba(139, 92, 246, 0.3);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.d-gem-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.d-gem-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.3);
}

.d-gem-symbol { font-weight: 700; font-size: 14px; color: #fff; display: block; }
.d-gem-rank { font-size: 10px; color: rgba(255, 255, 255, 0.4); }

.d-gem-score {
  margin-left: auto;
  font-size: 18px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 8px;
}
.d-gem-score.gem-excellent { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.d-gem-score.gem-good { background: rgba(139, 92, 246, 0.2); color: #a78bfa; }
.d-gem-score.gem-moderate { background: rgba(148, 163, 184, 0.2); color: #94a3b8; }

.d-gem-body {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.d-gem-stat { text-align: center; }
.d-gem-label { font-size: 9px; color: rgba(255, 255, 255, 0.4); display: block; margin-bottom: 2px; text-transform: uppercase; }
.d-gem-value { font-size: 12px; font-weight: 600; color: #fff; }

.d-gem-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.d-gem-pattern {
  font-size: 9px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}
.d-gem-pattern.pattern-bullish { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.d-gem-pattern.pattern-bearish { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

.d-gem-signal { font-size: 10px; color: rgba(255, 255, 255, 0.6); }

.d-gems-empty {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.3);
}

/* Hidden Gems Enhanced - Trust Badges & Metrics */
.d-gem-info { flex: 1; }

.d-gem-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.d-gem-badge {
  font-size: 9px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  background: rgba(100, 116, 139, 0.2);
  color: #94a3b8;
}

.d-gem-badge.accumulating {
  background: rgba(14, 165, 233, 0.2);
  color: #38bdf8;
  border: 1px solid rgba(14, 165, 233, 0.3);
}

.d-gem-badge.confirmed {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.d-gem-badge.sig-accumulation {
  background: rgba(14, 165, 233, 0.2);
  color: #38bdf8;
}
.d-gem-badge.sig-very-strong-bull,
.d-gem-badge.sig-strong-bullish,
.d-gem-badge.sig-confirmed-bull,
.d-gem-badge.sig-bullish {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}
.d-gem-badge.sig-very-strong-bear,
.d-gem-badge.sig-strong-bearish,
.d-gem-badge.sig-confirmed-bear,
.d-gem-badge.sig-bearish {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.d-gem-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
  margin-bottom: 12px;
}

.d-gem-metric {
  text-align: center;
  padding: 6px 4px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
}

.d-gem-footer {
  display: flex;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.d-gem-tech {
  font-size: 9px;
  font-weight: 600;
  padding: 3px 6px;
  border-radius: 4px;
  background: rgba(100, 116, 139, 0.15);
  color: #94a3b8;
}

.d-gem-tech.macd-bullish { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.d-gem-tech.macd-bearish { background: rgba(239, 68, 68, 0.12); color: #f87171; }
.d-gem-tech.bb-upper { background: rgba(239, 68, 68, 0.12); color: #f87171; }
.d-gem-tech.bb-lower { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.d-gem-tech.bb-middle { background: rgba(100, 116, 139, 0.15); color: #94a3b8; }
</style>

