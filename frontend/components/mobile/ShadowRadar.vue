<template>
  <div class="shadow-radar-container">
    <!-- Header -->
    <div class="radar-header">
      <div class="header-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <circle cx="12" cy="12" r="6"/>
          <circle cx="12" cy="12" r="2"/>
          <line x1="12" y1="2" x2="12" y2="6"/>
        </svg>
      </div>
      <div class="header-text">
        <h2>Shadow Radar</h2>
        <span class="subtitle">Intent Divergence Analysis</span>
      </div>
      <div class="intent-badge" :class="intentBadgeClass">
        {{ divergenceData?.divergence_label || 'Analyzing...' }}
      </div>
    </div>

    <!-- Radar Chart -->
    <div class="radar-chart-wrapper">
      <client-only>
        <apexchart
          v-if="chartOptions && chartSeries.length"
          type="radar"
          height="320"
          :options="chartOptions"
          :series="chartSeries"
        />
      </client-only>
    </div>

    <!-- Intent Score -->
    <div class="intent-score-section">
      <div class="score-label">Intent Strength</div>
      <div class="score-bar-container">
        <div 
          class="score-bar" 
          :style="{ width: `${divergenceData?.intent_score || 50}%` }"
          :class="scoreBarClass"
        ></div>
      </div>
      <div class="score-value">{{ divergenceData?.intent_score || 50 }}/100</div>
    </div>

    <!-- Shadow Insight -->
    <div class="shadow-insight" v-if="divergenceData?.shadow_insight">
      <div class="insight-icon">💡</div>
      <div class="insight-content">
        <div class="insight-title">Shadow Insight</div>
        <p class="insight-text">{{ divergenceData.shadow_insight }}</p>
        <div class="insight-action" v-if="divergenceData.action_hint">
          <span class="action-label">Hint:</span> {{ divergenceData.action_hint }}
        </div>
      </div>
    </div>

    <!-- Whale Profiles -->
    <div class="whale-profiles" v-if="divergenceData?.active_whale_profiles?.length">
      <div class="profiles-header">
        <span class="profiles-icon">🐋</span>
        <span>Active Whale Profiles</span>
      </div>
      <div class="profiles-list">
        <div 
          v-for="profile in divergenceData.active_whale_profiles.slice(0, 3)" 
          :key="profile.behavior"
          class="profile-chip"
          :class="`profile-${profile.behavior}`"
        >
          <span class="profile-label">{{ formatBehavior(profile.behavior) }}</span>
          <span class="profile-count">×{{ profile.count }}</span>
        </div>
      </div>
    </div>

    <!-- Golden Shadow Alert -->
    <div class="golden-shadow-alert" v-if="divergenceData?.is_golden_shadow">
      <div class="golden-icon">⚡</div>
      <div class="golden-text">
        <strong>Golden Shadow Entry Detected!</strong>
        <span>High-confidence divergence signal</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const props = defineProps({
  coinId: {
    type: String,
    default: 'bitcoin'
  },
  divergenceData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update', 'golden-shadow'])

// Reactive data
const loading = ref(false)
const localData = ref(null)

// Use prop data or local data
const divergenceData = computed(() => props.divergenceData || localData.value)

// Chart configuration
const chartOptions = computed(() => ({
  chart: {
    type: 'radar',
    toolbar: { show: false },
    background: 'transparent',
    dropShadow: {
      enabled: true,
      blur: 4,
      left: 1,
      top: 3,
      opacity: 0.3,
      color: '#00d4ff'
    }
  },
  colors: ['#00d4ff'],
  fill: {
    opacity: 0.3,
    colors: ['#00d4ff']
  },
  stroke: {
    width: 2,
    colors: ['#00d4ff']
  },
  markers: {
    size: 4,
    colors: ['#00d4ff'],
    strokeColors: '#0a0a1a',
    strokeWidth: 2
  },
  xaxis: {
    categories: [
      'Crowd Sentiment',
      'Whale Momentum', 
      'Exchange Pressure',
      'Network Growth',
      'Intent Strength'
    ],
    labels: {
      style: {
        colors: ['#8b8fa3', '#8b8fa3', '#8b8fa3', '#8b8fa3', '#8b8fa3'],
        fontSize: '11px',
        fontFamily: 'Inter, sans-serif'
      }
    }
  },
  yaxis: {
    show: false,
    min: 0,
    max: 100
  },
  plotOptions: {
    radar: {
      size: 120,
      polygons: {
        strokeColors: 'rgba(255,255,255,0.1)',
        strokeWidth: 1,
        connectorColors: 'rgba(255,255,255,0.1)',
        fill: {
          colors: ['rgba(10,10,26,0.8)', 'rgba(20,20,40,0.6)']
        }
      }
    }
  },
  tooltip: {
    theme: 'dark',
    y: {
      formatter: (val) => `${val}/100`
    }
  }
}))

const chartSeries = computed(() => {
  if (!divergenceData.value) {
    return [{ name: 'Signals', data: [50, 50, 50, 50, 50] }]
  }
  
  return [{
    name: 'Signals',
    data: [
      divergenceData.value.sentiment_score || 50,
      divergenceData.value.whale_score || 50,
      normalizeExchangePressure(divergenceData.value.whale_net_flow_usd),
      50, // Network growth - would come from DAU data
      divergenceData.value.intent_score || 50
    ]
  }]
})

// Computed classes
const intentBadgeClass = computed(() => {
  const type = divergenceData.value?.divergence_type || 'neutral'
  return {
    'badge-accumulation': type === 'shadow_accumulation',
    'badge-trap': type === 'bull_trap',
    'badge-confirmation': type === 'confirmation',
    'badge-neutral': type === 'neutral'
  }
})

const scoreBarClass = computed(() => {
  const score = divergenceData.value?.intent_score || 50
  if (score >= 75) return 'bar-strong'
  if (score >= 50) return 'bar-moderate'
  return 'bar-weak'
})

// Helper functions
function normalizeExchangePressure(flow) {
  if (!flow) return 50
  // Normalize whale flow to 0-100 scale
  // Negative flow (outflow) = bullish = higher score
  // Positive flow (inflow) = bearish = lower score
  const normalized = 50 - (flow / 100000) * 50
  return Math.max(0, Math.min(100, normalized))
}

function formatBehavior(behavior) {
  const labels = {
    'value_hunter': 'Value Hunter',
    'accumulator': 'Accumulator',
    'distributor': 'Distributor',
    'panic_seller': 'Panic Seller',
    'mixed': 'Mixed',
    'unknown': 'Unknown'
  }
  return labels[behavior] || behavior
}

// Fetch data
async function fetchDivergence() {
  if (!props.coinId) return
  
  loading.value = true
  try {
    const response = await fetch(`/api/v1/intent-divergence/${props.coinId}`)
    if (response.ok) {
      localData.value = await response.json()
      
      if (localData.value?.is_golden_shadow) {
        emit('golden-shadow', localData.value)
      }
    }
  } catch (error) {
    console.error('Failed to fetch divergence data:', error)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  if (!props.divergenceData) {
    fetchDivergence()
  }
})

watch(() => props.coinId, () => {
  if (!props.divergenceData) {
    fetchDivergence()
  }
})
</script>

<style scoped>
.shadow-radar-container {
  background: linear-gradient(135deg, rgba(10, 10, 26, 0.95) 0%, rgba(20, 20, 50, 0.9) 100%);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(0, 212, 255, 0.2);
}

.radar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.header-icon {
  color: #00d4ff;
  display: flex;
  align-items: center;
}

.header-text h2 {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.header-text .subtitle {
  font-size: 12px;
  color: #8b8fa3;
}

.intent-badge {
  margin-left: auto;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-accumulation {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
  border: 1px solid rgba(0, 255, 136, 0.4);
}

.badge-trap {
  background: rgba(255, 68, 68, 0.2);
  color: #ff4444;
  border: 1px solid rgba(255, 68, 68, 0.4);
}

.badge-confirmation {
  background: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
  border: 1px solid rgba(0, 212, 255, 0.4);
}

.badge-neutral {
  background: rgba(139, 143, 163, 0.2);
  color: #8b8fa3;
  border: 1px solid rgba(139, 143, 163, 0.4);
}

.radar-chart-wrapper {
  margin: 0 -10px;
}

.intent-score-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  margin-bottom: 16px;
}

.score-label {
  font-size: 13px;
  color: #8b8fa3;
  min-width: 100px;
}

.score-bar-container {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.score-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.bar-weak { background: linear-gradient(90deg, #8b8fa3, #a0a4b8); }
.bar-moderate { background: linear-gradient(90deg, #00d4ff, #00a8cc); }
.bar-strong { background: linear-gradient(90deg, #00ff88, #00cc6a); }

.score-value {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  min-width: 60px;
  text-align: right;
}

.shadow-insight {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 150, 200, 0.05) 100%);
  border-radius: 12px;
  border: 1px solid rgba(0, 212, 255, 0.2);
  margin-bottom: 16px;
}

.insight-icon {
  font-size: 24px;
}

.insight-title {
  font-size: 13px;
  font-weight: 600;
  color: #00d4ff;
  margin-bottom: 6px;
}

.insight-text {
  font-size: 14px;
  color: #e0e2e8;
  line-height: 1.5;
  margin: 0 0 8px;
}

.insight-action {
  font-size: 12px;
  color: #8b8fa3;
}

.insight-action .action-label {
  color: #00d4ff;
  font-weight: 600;
}

.whale-profiles {
  margin-bottom: 16px;
}

.profiles-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #8b8fa3;
  margin-bottom: 10px;
}

.profiles-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.profile-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  font-size: 12px;
}

.profile-label { color: #e0e2e8; }
.profile-count { color: #8b8fa3; }

.profile-value_hunter { border-left: 3px solid #00ff88; }
.profile-accumulator { border-left: 3px solid #00d4ff; }
.profile-distributor { border-left: 3px solid #ffa500; }
.profile-panic_seller { border-left: 3px solid #ff4444; }

.golden-shadow-alert {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.15) 0%, rgba(255, 165, 0, 0.1) 100%);
  border-radius: 12px;
  border: 1px solid rgba(255, 215, 0, 0.4);
  animation: pulse-gold 2s infinite;
}

.golden-icon {
  font-size: 28px;
}

.golden-text strong {
  display: block;
  font-size: 14px;
  color: #ffd700;
  margin-bottom: 2px;
}

.golden-text span {
  font-size: 12px;
  color: #e0e2e8;
}

@keyframes pulse-gold {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.4); }
  50% { box-shadow: 0 0 20px 5px rgba(255, 215, 0, 0.2); }
}
</style>
