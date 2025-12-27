<template>
  <div class="ai-risk-widget">
    <div class="risk-header">
      <Icon name="ph:shield-warning-bold" size="18" class="risk-icon" />
      <span class="risk-title">AI RISK</span>
    </div>
    
    <div class="risk-items">
      <div 
        v-for="item in riskItems" 
        :key="item.symbol"
        class="risk-item"
        @click="$emit('select', item)"
      >
        <div class="risk-bar-container">
          <div 
            class="risk-bar" 
            :class="getRiskClass(item.risk_level)"
            :style="{ width: `${item.risk_score}%` }"
          ></div>
        </div>
        <span class="risk-label" :class="getRiskClass(item.risk_level)">
          {{ item.risk_label?.toUpperCase() || item.risk_level?.replace('_', ' ') }}
        </span>
      </div>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="risk-loading">
      <div class="risk-skeleton" v-for="i in 5" :key="i"></div>
    </div>
    
    <!-- Empty state -->
    <div v-if="!loading && riskItems.length === 0" class="risk-empty">
      <span>No risk data available</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'

interface RiskItem {
  coin_id: string
  symbol: string
  name: string
  risk_score: number
  risk_level: string
  risk_label: string
  risk_color: string
}

const props = defineProps<{
  limit?: number
}>()

const emit = defineEmits(['select'])

const api = useApi()
const loading = ref(true)
const riskItems = ref<RiskItem[]>([])

const getRiskClass = (level: string) => {
  const classMap: Record<string, string> = {
    'NO_RISK': 'no-risk',
    'SAFE': 'safe',
    'LOW_RISK': 'low-risk',
    'MED_RISK': 'med-risk',
    'VOLATILE': 'volatile',
    'EXTREME': 'extreme',
    'LAWSUIT': 'lawsuit',
  }
  return classMap[level] || 'med-risk'
}

const fetchRiskData = async () => {
  try {
    loading.value = true
    const response = await api.getTopRiskyCoins(props.limit || 7)
    if (Array.isArray(response)) {
      riskItems.value = response
    }
  } catch (e) {
    console.warn('Failed to fetch risk data:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRiskData()
})
</script>

<style scoped>
.ai-risk-widget {
  background: rgba(15, 20, 30, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 16px;
}

.risk-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.risk-icon {
  color: #ef4444;
}

.risk-title {
  font-size: 12px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 1px;
}

.risk-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.risk-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  cursor: pointer;
  transition: transform 0.2s;
}

.risk-item:active {
  transform: scale(0.98);
}

.risk-bar-container {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.risk-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.8s ease-out;
}

/* Risk level colors matching mockup */
.risk-bar.no-risk {
  background: linear-gradient(90deg, #4b5563 0%, #6b7280 100%);
}

.risk-bar.safe {
  background: linear-gradient(90deg, #06b6d4 0%, #38efeb 100%);
}

.risk-bar.low-risk {
  background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
}

.risk-bar.med-risk {
  background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
}

.risk-bar.volatile {
  background: linear-gradient(90deg, #10b981 0%, #eab308 40%, #f97316 60%, #ef4444 80%, #ec4899 100%);
}

.risk-bar.extreme {
  background: linear-gradient(90deg, #ef4444 0%, #f43f5e 50%, #ec4899 100%);
}

.risk-bar.lawsuit {
  background: linear-gradient(90deg, #ec4899 0%, #f43f5e 100%);
}

/* Risk labels */
.risk-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.risk-label.no-risk { color: #6b7280; }
.risk-label.safe { color: #38efeb; }
.risk-label.low-risk { color: #10b981; }
.risk-label.med-risk { color: #eab308; }
.risk-label.volatile { color: #f97316; }
.risk-label.extreme { color: #ef4444; }
.risk-label.lawsuit { color: #ec4899; }

/* Loading state */
.risk-loading {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.risk-skeleton {
  height: 28px;
  background: linear-gradient(90deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.05) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 6px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.risk-empty {
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
  padding: 20px;
}
</style>
