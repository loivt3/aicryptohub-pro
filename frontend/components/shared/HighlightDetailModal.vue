<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="highlight-modal-overlay" @click.self="close">
        <div class="highlight-modal">
          <!-- Header -->
          <div class="modal-header" :class="highlight?.color">
            <div class="header-left">
              <div class="modal-icon" :class="highlight?.color">
                <Icon :name="getIconName(highlight?.icon)" size="24" />
              </div>
              <div class="header-info">
                <span class="modal-type">{{ formatType(highlight?.highlight_type) }}</span>
                <span class="modal-symbol">{{ highlight?.symbol }}</span>
              </div>
            </div>
            <button class="modal-close" @click="close">
              <Icon name="ph:x-bold" size="20" />
            </button>
          </div>
          
          <!-- Confidence & RSI -->
          <div class="modal-badges">
            <div v-if="highlight?.confidence" class="badge confidence" :class="getConfidenceClass(highlight.confidence)">
              <span class="badge-label">Confidence</span>
              <span class="badge-value">{{ highlight.confidence }}%</span>
            </div>
            <div v-if="highlight?.technical_data?.rsi_14" class="badge rsi" :class="getRsiClass(highlight.technical_data.rsi_14)">
              <span class="badge-label">RSI</span>
              <span class="badge-value">{{ highlight.technical_data.rsi_14.toFixed(0) }}</span>
            </div>
            <div v-if="highlight?.technical_data?.trend" class="badge trend">
              <span class="badge-label">Trend</span>
              <span class="badge-value">{{ highlight.technical_data.trend.toUpperCase() }}</span>
            </div>
          </div>
          
          <!-- Description -->
          <div class="modal-description">
            <p>{{ highlight?.description }}</p>
          </div>
          
          <!-- Action Hint -->
          <div v-if="highlight?.action_hint" class="modal-action-hint">
            <Icon name="ph:lightbulb-bold" size="18" class="hint-icon" />
            <span>{{ highlight.action_hint }}</span>
          </div>
          
          <!-- Technical Details -->
          <div v-if="highlight?.technical_data" class="modal-technical">
            <h4>Technical Analysis</h4>
            <div class="tech-grid">
              <div class="tech-item">
                <span class="tech-label">24h Change</span>
                <span class="tech-value" :class="getChangeClass(highlight.change_24h)">
                  {{ formatChange(highlight.change_24h) }}
                </span>
              </div>
              <div class="tech-item" v-if="highlight.change_7d !== undefined">
                <span class="tech-label">7d Change</span>
                <span class="tech-value" :class="getChangeClass(highlight.change_7d)">
                  {{ formatChange(highlight.change_7d) }}
                </span>
              </div>
              <div class="tech-item" v-if="highlight.technical_data?.volume_ratio">
                <span class="tech-label">Volume Ratio</span>
                <span class="tech-value">{{ highlight.technical_data.volume_ratio.toFixed(1) }}%</span>
              </div>
              <div class="tech-item" v-if="highlight.technical_data?.ath_distance_pct">
                <span class="tech-label">From ATH</span>
                <span class="tech-value">{{ highlight.technical_data.ath_distance_pct.toFixed(1) }}%</span>
              </div>
            </div>
          </div>
          
          <!-- Source indicator -->
          <div class="modal-footer">
            <span class="source-label">
              <Icon name="ph:robot-bold" size="14" />
              AI Analysis
            </span>
            <span class="timestamp">{{ formatTime(highlight?.timestamp) }}</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface TechnicalData {
  rsi_14?: number
  trend?: string
  volume_ratio?: number
  ath_distance_pct?: number
  change_24h?: number
  change_7d?: number
}

interface Highlight {
  highlight_type: string
  symbol: string
  confidence?: number
  description: string
  action_hint?: string
  technical_data?: TechnicalData
  change_24h?: number
  change_7d?: number
  icon?: string
  color?: string
  timestamp?: string
}

const props = defineProps<{
  visible: boolean
  highlight: Highlight | null
}>()

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}

const getIconName = (icon?: string) => {
  const iconMap: Record<string, string> = {
    'trend-up': 'ph:trend-up-bold',
    'trend-down': 'ph:trend-down-bold',
    'warning': 'ph:warning-bold',
    'chart-bar': 'ph:chart-bar-bold',
    'lightning': 'ph:lightning-bold',
    'fish': 'ph:fish-bold',
    'target': 'ph:target-bold',
    'rocket': 'ph:rocket-bold',
    'arrow-down-circle': 'ph:arrow-circle-down-bold',
    'alert-triangle': 'ph:warning-circle-bold',
  }
  return iconMap[icon || ''] || 'ph:sparkle-bold'
}

const formatType = (type?: string) => {
  if (!type) return ''
  const typeMap: Record<string, string> = {
    'bullish_signal': 'Bullish Signal',
    'bearish_signal': 'Bearish Signal',
    'risk_alert': 'Risk Alert',
    'volume_surge': 'Volume Surge',
    'breakout': 'Breakout',
    'whale_activity': 'Whale Activity',
    'opportunity': 'Opportunity',
    'dip_buy': 'Dip Buy Opportunity',
    'oversold_alert': 'Oversold Alert',
    'overbought_alert': 'Overbought Warning',
    'momentum_surge': 'Momentum Surge',
  }
  return typeMap[type] || type
}

const getConfidenceClass = (confidence: number) => {
  if (confidence >= 80) return 'high'
  if (confidence >= 60) return 'medium'
  return 'low'
}

const getRsiClass = (rsi: number) => {
  if (rsi <= 30) return 'oversold'
  if (rsi >= 70) return 'overbought'
  return 'neutral'
}

const getChangeClass = (change?: number) => {
  if (!change) return ''
  return change > 0 ? 'positive' : 'negative'
}

const formatChange = (change?: number) => {
  if (!change) return '--'
  return `${change > 0 ? '+' : ''}${change.toFixed(2)}%`
}

const formatTime = (timestamp?: string) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.highlight-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 9999;
  padding: 16px;
}

.highlight-modal {
  background: linear-gradient(180deg, rgba(25, 30, 40, 0.98) 0%, rgba(15, 20, 28, 0.98) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px 20px 0 0;
  width: 100%;
  max-width: 420px;
  max-height: 85vh;
  overflow-y: auto;
  padding-bottom: env(safe-area-inset-bottom);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.modal-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-icon.green { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.modal-icon.red { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.modal-icon.blue { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
.modal-icon.cyan { background: rgba(56, 239, 235, 0.2); color: #38efeb; }
.modal-icon.purple { background: rgba(168, 85, 247, 0.2); color: #a855f7; }
.modal-icon.yellow { background: rgba(234, 179, 8, 0.2); color: #eab308; }
.modal-icon.orange { background: rgba(249, 115, 22, 0.2); color: #f97316; }

.header-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.modal-type {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.modal-symbol {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.modal-close {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 10px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
}

.modal-badges {
  display: flex;
  gap: 10px;
  padding: 16px 20px;
  flex-wrap: wrap;
}

.badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.badge-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
}

.badge-value {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.badge.confidence.high .badge-value { color: #10b981; }
.badge.confidence.medium .badge-value { color: #eab308; }
.badge.confidence.low .badge-value { color: #ef4444; }

.badge.rsi.oversold { border-color: rgba(16, 185, 129, 0.4); }
.badge.rsi.oversold .badge-value { color: #10b981; }
.badge.rsi.overbought { border-color: rgba(239, 68, 68, 0.4); }
.badge.rsi.overbought .badge-value { color: #ef4444; }

.modal-description {
  padding: 0 20px 16px;
}

.modal-description p {
  margin: 0;
  font-size: 15px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.85);
}

.modal-action-hint {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin: 0 20px 16px;
  padding: 14px;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 12px;
  color: #fbbf24;
  font-size: 13px;
  line-height: 1.5;
}

.hint-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.modal-technical {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-technical h4 {
  margin: 0 0 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.tech-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
}

.tech-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.tech-value {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.tech-value.positive { color: #10b981; }
.tech-value.negative { color: #ef4444; }

.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.source-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.timestamp {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

/* Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-active .highlight-modal,
.modal-leave-active .highlight-modal {
  transition: transform 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .highlight-modal,
.modal-leave-to .highlight-modal {
  transform: translateY(100%);
}
</style>
