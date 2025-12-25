<template>
  <div class="m-simulator-card">
    <div class="m-sim-header" @click="isOpen = !isOpen">
      <div class="m-sim-title">
        <span>🌪️ AI Stress Simulator</span>
        <small>Test "What-If" scenarios</small>
      </div>
      <span class="m-arrow" :class="{ open: isOpen }">▼</span>
    </div>

    <div v-if="isOpen" class="m-sim-body">
      <div class="m-slider-container">
        <label>If Bitcoin moves: <span :class="btcChange >= 0 ? 'g' : 'r'">{{ btcChange }}%</span></label>
        <input 
          type="range" 
          v-model.number="btcChange" 
          min="-50" 
          max="50" 
          step="5" 
          class="m-range"
          @change="runSimulation" 
        />
        <div class="m-range-labels">
          <span>-50%</span>
          <span>0%</span>
          <span>+50%</span>
        </div>
      </div>

      <div v-if="loading" class="m-loading">
        Calculating...
      </div>

      <div v-else-if="result" class="m-result">
        <div class="m-result-row">
          <span>Projected Value:</span>
          <span class="m-val">${{ formatPrice(result.projected_value) }}</span>
        </div>
        <div class="m-result-row">
          <span>Est. PnL Change:</span>
          <span class="m-val" :class="result.change_amount >= 0 ? 'g' : 'r'">
            {{ result.change_amount >= 0 ? '+' : '' }}${{ formatPrice(result.change_amount) }}
            ({{ formatNumber(result.change_percent) }}%)
          </span>
        </div>
        
        <div class="m-impact-list" v-if="result.details && result.details.length > 0">
          <div class="m-impact-label">Highest Impact:</div>
          <div v-for="coin in topImpacts" :key="coin.symbol" class="m-impact-item">
            <span>{{ coin.symbol }} (Beta {{ coin.beta }})</span>
            <span :class="coin.projected_change_pct >= 0 ? 'g' : 'r'">
              {{ coin.projected_change_pct > 0 ? '+' : ''}}{{ coin.projected_change_pct }}%
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useApi } from '~/composables/useApi'

const api = useApi()
const isOpen = ref(false)
const btcChange = ref(-10)
const loading = ref(false)
const result = ref<any>(null)

const props = defineProps({
  refreshTrigger: Number
})

const runSimulation = async () => {
  if (loading.value) return
  loading.value = true
  try {
    const res = await api.simulatePortfolio(btcChange.value)
    result.value = res
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const topImpacts = computed(() => {
  if (!result.value?.details) return []
  // Show top 3 most affected
  // If drop, show biggest losers. If pump, biggest gainers.
  const sorted = [...result.value.details].sort((a, b) => 
    btcChange.value < 0 ? a.projected_change_pct - b.projected_change_pct : b.projected_change_pct - a.projected_change_pct
  )
  return sorted.slice(0, 3)
})

watch(isOpen, (val) => {
  if (val && !result.value) {
    runSimulation()
  }
})

const formatPrice = (price: number) => {
  return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatNumber = (num: number) => {
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(num)
}
</script>

<style scoped>
.m-simulator-card {
  background: linear-gradient(135deg, rgba(88, 28, 135, 0.2), rgba(124, 58, 237, 0.1));
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 16px;
  margin: 16px 16px 0;
  overflow: hidden;
}

.m-sim-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.m-sim-title {
  display: flex;
  flex-direction: column;
}

.m-sim-title span {
  font-weight: 700;
  color: #ddd6fe;
  font-size: 14px;
}

.m-sim-title small {
  font-size: 11px;
  color: rgba(221, 214, 254, 0.6);
}

.m-arrow {
  color: #ddd6fe;
  font-size: 12px;
  transition: transform 0.3s;
}
.m-arrow.open { transform: rotate(180deg); }

.m-sim-body {
  padding: 0 16px 16px;
  border-top: 1px solid rgba(139, 92, 246, 0.2);
}

.m-slider-container {
  padding: 16px 0;
}

.m-slider-container label {
  display: block;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 10px;
}

.m-range {
  width: 100%;
  -webkit-appearance: none;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  outline: none;
}

.m-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  background: #a78bfa;
  border-radius: 50%;
  cursor: pointer;
}

.m-range-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.3);
}

.m-loading {
  text-align: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  padding: 10px;
}

.m-result-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}
.m-result-row span:first-child { color: rgba(255, 255, 255, 0.6); }
.m-val { font-weight: 600; color: #fff; }

.g { color: #4ade80; }
.r { color: #f87171; }

.m-impact-list {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed rgba(255, 255, 255, 0.1);
}

.m-impact-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 6px;
  text-transform: uppercase;
}

.m-impact-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 4px;
  color: rgba(255, 255, 255, 0.8);
}
</style>
