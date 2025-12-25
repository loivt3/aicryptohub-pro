<template>
  <div class="m-auditor-card">
    <div v-if="loading" class="m-loading-state">
      <div class="m-spinner-small"></div>
      <span>AI Auditing...</span>
    </div>
    
    <div v-else-if="auditData" class="m-audit-content">
      <!-- Header / Score -->
      <div class="m-audit-header">
        <div class="m-health-badge" :class="healthClass">
          {{ auditData.health }} Health
        </div>
        <div class="m-score-circle" :style="scoreStyle">
          <span class="m-score-val">{{ auditData.score }}</span>
          <span class="m-score-label">Score</span>
        </div>
      </div>

      <!-- Warnings -->
      <div v-if="auditData.warnings && auditData.warnings.length > 0" class="m-warnings-list">
        <div v-for="(warn, i) in auditData.warnings" :key="i" class="m-warning-item">
          ⚠️ {{ warn }}
        </div>
      </div>
      <div v-else class="m-no-warnings">
        ✅ Your portfolio is well diversified and healthy.
      </div>

      <!-- Breakdown -->
      <div class="m-breakdown">
        <div class="m-breakdown-item">
          <span>Diversification</span>
          <div class="m-bar-bg">
            <div class="m-bar-fill" :style="{ width: auditData.breakdown.diversification_score + '%' }"></div>
          </div>
        </div>
        <div class="m-breakdown-item">
          <span>Risk Profile (Beta: {{ auditData.metric_beta }})</span>
          <div class="m-bar-bg">
            <div class="m-bar-fill" :style="{ width: auditData.breakdown.risk_score + '%' }"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useApi } from '~/composables/useApi'

const api = useApi()
const loading = ref(true)
const auditData = ref<any>(null)

const props = defineProps({
  refreshTrigger: Number
})

onMounted(() => {
  fetchAudit()
})

const fetchAudit = async () => {
  loading.value = true
  try {
    const res = await api.getPortfolioAudit()
    auditData.value = res
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const healthClass = computed(() => {
  if (!auditData.value) return ''
  const s = auditData.value.score
  if (s < 60) return 'm-bg-critical'
  if (s < 75) return 'm-bg-fair'
  return 'm-bg-good'
})

const scoreStyle = computed(() => {
  if (!auditData.value) return {}
  const color = auditData.value.score < 60 ? '#f87171' : auditData.value.score < 75 ? '#facc15' : '#4ade80'
  return {
    borderColor: color,
    color: color
  }
})

// Re-fetch when trigger changes (e.g. holding added)
watch(() => props.refreshTrigger, () => {
  fetchAudit()
})
</script>

<style scoped>
.m-auditor-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 16px;
  margin: 16px 16px 0;
}

.m-loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
  padding: 10px;
}

.m-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: #38efeb;
  border-radius: 50%;
  animation: spin 1s infinite linear;
}

.m-audit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.m-health-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: #000;
}
.m-bg-critical { background: #f87171; }
.m-bg-fair { background: #facc15; }
.m-bg-good { background: #4ade80; }

.m-score-circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: 4px solid #4ade80;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.m-score-val {
  font-size: 16px;
  font-weight: 800;
}

.m-score-label {
  font-size: 8px;
  text-transform: uppercase;
  opacity: 0.8;
}

.m-warnings-list {
  background: rgba(248, 113, 113, 0.1);
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 16px;
}

.m-warning-item {
  font-size: 12px;
  color: #fca5a5;
  margin-bottom: 4px;
}
.m-warning-item:last-child { margin-bottom: 0; }

.m-no-warnings {
  font-size: 12px;
  color: #86efac;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.m-breakdown-item {
  margin-bottom: 8px;
}

.m-breakdown-item span {
  display: block;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 4px;
}

.m-bar-bg {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.m-bar-fill {
  height: 100%;
  background: #38efeb;
  border-radius: 3px;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
