<template>
  <div class="multi-horizon-asi">
    <div class="asi-header">
      <h3>Multi-Horizon ASI</h3>
      <span v-if="loading" class="loading-indicator">Loading...</span>
    </div>
    
    <!-- Combined Score -->
    <div class="asi-combined" v-if="data?.asi_combined !== null">
      <div class="combined-gauge">
        <AsiGauge :score="data?.asi_combined || 50" :size="100" :show-label="true" />
      </div>
      <div class="combined-signal" :class="signalClass(data?.signal_combined)">
        {{ data?.signal_combined || 'NEUTRAL' }}
      </div>
    </div>
    
    <!-- Horizon Scores -->
    <div class="asi-horizons">
      <!-- Short-term -->
      <div class="horizon-card">
        <div class="horizon-label">Short-term</div>
        <div class="horizon-timeframe">1h</div>
        <div class="horizon-score" v-if="data?.asi_short !== null">
          <span class="score-value" :class="scoreClass(data?.asi_short)">{{ data?.asi_short }}</span>
        </div>
        <div class="horizon-score insufficient" v-else>
          <span class="no-data">Insufficient data</span>
        </div>
        <div class="horizon-signal" :class="signalClass(data?.signal_short)">
          {{ data?.signal_short || '-' }}
        </div>
        <div class="horizon-use">Day trade</div>
      </div>
      
      <!-- Medium-term -->
      <div class="horizon-card">
        <div class="horizon-label">Medium-term</div>
        <div class="horizon-timeframe">4h + 1d</div>
        <div class="horizon-score" v-if="data?.asi_medium !== null">
          <span class="score-value" :class="scoreClass(data?.asi_medium)">{{ data?.asi_medium }}</span>
        </div>
        <div class="horizon-score insufficient" v-else>
          <span class="no-data">Insufficient data</span>
        </div>
        <div class="horizon-signal" :class="signalClass(data?.signal_medium)">
          {{ data?.signal_medium || '-' }}
        </div>
        <div class="horizon-use">Swing trade</div>
      </div>
      
      <!-- Long-term -->
      <div class="horizon-card">
        <div class="horizon-label">Long-term</div>
        <div class="horizon-timeframe">1w + 1M</div>
        <div class="horizon-score" v-if="data?.asi_long !== null">
          <span class="score-value" :class="scoreClass(data?.asi_long)">{{ data?.asi_long }}</span>
        </div>
        <div class="horizon-score insufficient" v-else>
          <span class="no-data">Insufficient data</span>
        </div>
        <div class="horizon-signal" :class="signalClass(data?.signal_long)">
          {{ data?.signal_long || '-' }}
        </div>
        <div class="horizon-use">HODL</div>
      </div>
    </div>
    
    <!-- On-chain Score -->
    <div class="onchain-section" v-if="data?.onchain_score?.available">
      <div class="onchain-header">On-chain Data</div>
      <div class="onchain-score">
        <span class="score-value" :class="scoreClass(data?.onchain_score?.score)">
          {{ data?.onchain_score?.score }}
        </span>
        <span class="onchain-signal" :class="signalClass(data?.onchain_score?.whale_signal)">
          {{ data?.onchain_score?.whale_signal }}
        </span>
      </div>
    </div>
    
    <!-- Data Status -->
    <div class="data-status" v-if="data?.data_status">
      <span 
        v-for="(status, key) in data.data_status" 
        :key="key"
        class="status-badge"
        :class="{ 'status-ok': status === 'OK', 'status-insufficient': status !== 'OK' }"
      >
        {{ key }}: {{ status }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import AsiGauge from './AsiGauge.vue'

interface MultiHorizonData {
  asi_short: number | null
  asi_medium: number | null
  asi_long: number | null
  asi_combined: number | null
  signal_short: string | null
  signal_medium: string | null
  signal_long: string | null
  signal_combined: string | null
  onchain_score?: {
    available: boolean
    score: number | null
    whale_signal?: string
  }
  data_status?: {
    short: string
    medium: string
    long: string
    combined: string
  }
}

const props = defineProps<{
  coinId: string
}>()

const data = ref<MultiHorizonData | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const fetchData = async () => {
  loading.value = true
  error.value = null
  try {
    const config = useRuntimeConfig()
    const response = await $fetch<{ success: boolean; data: MultiHorizonData }>(
      `${config.public.apiBase}/sentiment/${props.coinId}/multi-horizon`
    )
    if (response.success) {
      data.value = response.data
    }
  } catch (e: any) {
    error.value = e.message || 'Failed to load'
  } finally {
    loading.value = false
  }
}

const scoreClass = (score: number | null | undefined) => {
  if (score === null || score === undefined) return ''
  if (score >= 60) return 'score-bullish'
  if (score >= 40) return 'score-neutral'
  return 'score-bearish'
}

const signalClass = (signal: string | null | undefined) => {
  if (!signal) return ''
  if (signal === 'STRONG_BUY' || signal === 'BUY' || signal === 'BULLISH' || signal === 'STRONG_BULLISH') return 'signal-bullish'
  if (signal === 'NEUTRAL') return 'signal-neutral'
  return 'signal-bearish'
}

onMounted(() => {
  fetchData()
})

watch(() => props.coinId, () => {
  fetchData()
})
</script>

<style scoped>
.multi-horizon-asi {
  background: var(--bg-secondary, #1a1a2e);
  border-radius: 12px;
  padding: 20px;
}

.asi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.asi-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #fff);
  margin: 0;
}

.loading-indicator {
  font-size: 12px;
  color: var(--text-secondary, #888);
}

.asi-combined {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background: var(--bg-tertiary, #0f0f1a);
  border-radius: 8px;
}

.combined-gauge {
  width: 100px;
  height: 100px;
}

.combined-signal {
  font-size: 18px;
  font-weight: 700;
  padding: 8px 16px;
  border-radius: 20px;
}

.asi-horizons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.horizon-card {
  background: var(--bg-tertiary, #0f0f1a);
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.horizon-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary, #fff);
  margin-bottom: 4px;
}

.horizon-timeframe {
  font-size: 10px;
  color: var(--text-secondary, #888);
  margin-bottom: 8px;
}

.horizon-score .score-value {
  font-size: 28px;
  font-weight: 700;
}

.horizon-score.insufficient .no-data {
  font-size: 11px;
  color: var(--text-muted, #666);
}

.horizon-signal {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 12px;
  margin: 8px 0;
  display: inline-block;
}

.horizon-use {
  font-size: 10px;
  color: var(--text-secondary, #888);
}

/* Color classes */
.score-bullish { color: #10b981; }
.score-neutral { color: #f59e0b; }
.score-bearish { color: #ef4444; }

.signal-bullish { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.signal-neutral { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.signal-bearish { background: rgba(239, 68, 68, 0.2); color: #ef4444; }

.onchain-section {
  padding: 12px;
  background: var(--bg-tertiary, #0f0f1a);
  border-radius: 8px;
  margin-bottom: 12px;
}

.onchain-header {
  font-size: 12px;
  color: var(--text-secondary, #888);
  margin-bottom: 8px;
}

.onchain-score {
  display: flex;
  align-items: center;
  gap: 12px;
}

.onchain-score .score-value {
  font-size: 24px;
  font-weight: 700;
}

.onchain-signal {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 12px;
}

.data-status {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.status-badge {
  font-size: 10px;
  padding: 4px 8px;
  border-radius: 8px;
  text-transform: capitalize;
}

.status-ok {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.status-insufficient {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

@media (max-width: 480px) {
  .asi-horizons {
    grid-template-columns: 1fr;
  }
}
</style>
