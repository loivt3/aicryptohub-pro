<template>
  <div class="ai-workers">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <h2>🤖 AI Workers Manager</h2>
        <n-tag :type="isRunning ? 'warning' : 'success'" size="small">
          {{ isRunning ? '● Analyzing' : '○ Idle' }}
        </n-tag>
      </div>
      <div class="header-right">
        <n-button 
          v-if="!isRunning"
          type="primary" 
          @click="triggerAnalysis"
        >
          <template #icon><span>▶️</span></template>
          Run Analysis
        </n-button>
        <n-button 
          v-else
          type="error"
          @click="stopAnalysis"
        >
          <template #icon><span>⏹️</span></template>
          Stop
        </n-button>
      </div>
    </div>

    <!-- Worker Cards -->
    <n-grid :cols="3" :x-gap="16" :y-gap="16" class="workers-grid">
      <n-gi v-for="worker in workers" :key="worker.id">
        <div :class="['worker-card', `status-${worker.status}`]">
          <div class="worker-header">
            <span class="worker-provider">{{ worker.provider.toUpperCase() }}</span>
            <span :class="['status-dot', worker.status]"></span>
          </div>
          <div class="worker-name">{{ worker.name }}</div>
          
          <div class="worker-stats">
            <div v-if="worker.coins_analyzed > 0">
              <span class="stat-value">{{ worker.coins_analyzed }}</span>
              <span class="stat-label">analyzed</span>
            </div>
            <div v-if="worker.rate_limit_max">
              <span class="stat-value">{{ worker.rate_limit_remaining }}/{{ worker.rate_limit_max }}</span>
              <span class="stat-label">RPM</span>
            </div>
          </div>
          
          <div class="worker-footer">
            <span v-if="worker.last_analysis" class="last-time">
              {{ formatTimeAgo(worker.last_analysis) }}
            </span>
            <span v-else-if="worker.error_message" class="error-msg">
              {{ worker.error_message }}
            </span>
            <span v-else class="status-text">
              {{ worker.status === 'disabled' ? 'Disabled' : 'Ready' }}
            </span>
          </div>
        </div>
      </n-gi>
    </n-grid>

    <!-- Progress Section -->
    <n-card title="📊 Analysis Progress" :bordered="false" class="progress-card">
      <div class="progress-container">
        <n-progress 
          type="line" 
          :percentage="progressPercent"
          :color="isRunning ? '#f59e0b' : '#10b981'"
          :rail-color="'rgba(255,255,255,0.1)'"
          :height="24"
          :show-indicator="true"
        />
        <div class="progress-stats">
          <span>{{ analyzedCount }} / {{ totalCoins }} coins</span>
          <span>{{ pendingCount }} pending</span>
        </div>
      </div>
    </n-card>

    <!-- Queue Panel -->
    <n-grid :cols="2" :x-gap="16" :y-gap="16">
      <!-- Queue -->
      <n-gi>
        <n-card title="📋 Analysis Queue" :bordered="false">
          <template #header-extra>
            <n-button size="small" quaternary @click="fetchQueue">Refresh</n-button>
          </template>
          
          <div class="queue-container">
            <div v-for="item in queue" :key="item.symbol" class="queue-item">
              <span class="queue-symbol">{{ item.symbol }}</span>
              <span class="queue-name">{{ item.name }}</span>
              <span class="queue-mcap">${{ formatNumber(item.market_cap) }}</span>
            </div>
            <div v-if="queue.length === 0" class="no-data">
              No coins in queue
            </div>
          </div>
        </n-card>
      </n-gi>
      
      <!-- Logs -->
      <n-gi>
        <n-card title="📝 Recent Analysis" :bordered="false">
          <template #header-extra>
            <n-button size="small" quaternary @click="fetchLogs">Refresh</n-button>
          </template>
          
          <div class="logs-container">
            <div 
              v-for="log in logs" 
              :key="log.id" 
              :class="['log-entry', `log-${log.level}`]"
            >
              <span class="log-time">{{ formatTime(log.timestamp) }}</span>
              <span class="log-worker">[{{ log.worker }}]</span>
              <span class="log-symbol">{{ log.coin_symbol }}</span>
              <span :class="['log-signal', signalClass(log.signal)]">
                {{ log.signal }}
              </span>
              <span class="log-asi">ASI: {{ log.asi_score }}</span>
            </div>
            <div v-if="logs.length === 0" class="no-data">
              No analysis logs yet
            </div>
          </div>
        </n-card>
      </n-gi>
    </n-grid>

    <!-- Stats -->
    <n-card title="📈 Analysis Statistics (24h)" :bordered="false" class="stats-card">
      <div class="stats-grid">
        <div class="stat-box">
          <span class="stat-value">{{ stats.analyzed_today || 0 }}</span>
          <span class="stat-label">Analyzed Today</span>
        </div>
        <div class="stat-box">
          <span class="stat-value">{{ signalBreakdown.STRONG_BUY || 0 }}</span>
          <span class="stat-label signal-buy">Strong Buy</span>
        </div>
        <div class="stat-box">
          <span class="stat-value">{{ signalBreakdown.BUY || 0 }}</span>
          <span class="stat-label signal-buy">Buy</span>
        </div>
        <div class="stat-box">
          <span class="stat-value">{{ signalBreakdown.NEUTRAL || 0 }}</span>
          <span class="stat-label">Neutral</span>
        </div>
        <div class="stat-box">
          <span class="stat-value">{{ signalBreakdown.SELL || 0 }}</span>
          <span class="stat-label signal-sell">Sell</span>
        </div>
        <div class="stat-box">
          <span class="stat-value">{{ Math.round((stats.avg_asi_score || 0.5) * 100) }}</span>
          <span class="stat-label">Avg ASI</span>
        </div>
      </div>
    </n-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useMessage } from 'naive-ui'
import axios from 'axios'

const API_BASE = '/api/v1'
const message = useMessage()

// State
const workers = ref([])
const queue = ref([])
const logs = ref([])
const stats = ref({})
const isRunning = ref(false)
const totalCoins = ref(0)
const analyzedCount = ref(0)
const pendingCount = ref(0)

// Computed
const progressPercent = computed(() => {
  if (totalCoins.value === 0) return 0
  return Math.round((analyzedCount.value / totalCoins.value) * 100)
})

const signalBreakdown = computed(() => {
  const breakdown = {}
  Object.entries(stats.value.signal_breakdown || {}).forEach(([signal, data]) => {
    breakdown[signal] = data.count || 0
  })
  return breakdown
})

// Methods
function formatNumber(num) {
  if (!num) return '0'
  if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B'
  if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M'
  if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K'
  return num.toFixed(0)
}

function formatTime(timestamp) {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleTimeString('en-US', { hour12: false })
}

function formatTimeAgo(timestamp) {
  if (!timestamp) return ''
  const diff = Math.floor((Date.now() - new Date(timestamp)) / 1000)
  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  return `${Math.floor(diff / 3600)}h ago`
}

function signalClass(signal) {
  if (signal?.includes('BUY')) return 'signal-buy'
  if (signal?.includes('SELL')) return 'signal-sell'
  return 'signal-neutral'
}

async function fetchStatus() {
  try {
    const response = await axios.get(`${API_BASE}/admin/ai/status`)
    const data = response.data
    workers.value = data.workers || []
    isRunning.value = data.is_running || false
    totalCoins.value = data.total_coins || 0
    analyzedCount.value = data.analyzed_count || 0
    pendingCount.value = data.pending_count || 0
  } catch (error) {
    console.error('Failed to fetch status:', error)
  }
}

async function fetchQueue() {
  try {
    const response = await axios.get(`${API_BASE}/admin/ai/queue`)
    queue.value = response.data.queue || []
  } catch (error) {
    console.error('Failed to fetch queue:', error)
  }
}

async function fetchLogs() {
  try {
    const response = await axios.get(`${API_BASE}/admin/ai/logs?limit=20`)
    logs.value = response.data.logs || []
  } catch (error) {
    console.error('Failed to fetch logs:', error)
  }
}

async function fetchStats() {
  try {
    const response = await axios.get(`${API_BASE}/admin/ai/stats`)
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

async function triggerAnalysis() {
  try {
    isRunning.value = true
    const response = await axios.post(`${API_BASE}/admin/ai/trigger?limit=100`)
    message.success(`Analysis started: ${response.data.coins_queued} coins queued`)
    pollStatus()
  } catch (error) {
    console.error('Failed to trigger analysis:', error)
    message.error('Failed to start analysis')
    isRunning.value = false
  }
}

async function stopAnalysis() {
  try {
    await axios.post(`${API_BASE}/admin/ai/stop`)
    message.info('Stop signal sent')
  } catch (error) {
    console.error('Failed to stop:', error)
  }
}

let pollInterval = null

function pollStatus() {
  if (pollInterval) clearInterval(pollInterval)
  
  pollInterval = setInterval(async () => {
    await fetchStatus()
    await fetchLogs()
    
    if (!isRunning.value) {
      clearInterval(pollInterval)
      pollInterval = null
      fetchStats()
    }
  }, 3000)
}

let refreshInterval = null

onMounted(() => {
  fetchStatus()
  fetchQueue()
  fetchLogs()
  fetchStats()
  
  refreshInterval = setInterval(() => {
    if (!isRunning.value) {
      fetchStatus()
    }
  }, 30000)
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<style scoped>
.ai-workers {
  max-width: 1400px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
  color: #f9fafb;
}

.workers-grid {
  margin-bottom: 24px;
}

.worker-card {
  background: #111827;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  min-height: 140px;
}

.worker-card.status-running {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
}

.worker-card.status-error {
  border-color: #ef4444;
}

.worker-card.status-disabled {
  opacity: 0.5;
}

.worker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.worker-provider {
  font-size: 10px;
  color: #6b7280;
  font-weight: 600;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-dot.ready { background: #10b981; }
.status-dot.running { background: #f59e0b; animation: pulse 1s infinite; }
.status-dot.error { background: #ef4444; }
.status-dot.disabled { background: #374151; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.worker-name {
  font-size: 18px;
  font-weight: 600;
  color: #f9fafb;
  margin-bottom: 12px;
}

.worker-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
}

.stat-value {
  color: #10b981;
  font-weight: 600;
  font-size: 14px;
}

.stat-label {
  color: #6b7280;
  font-size: 12px;
  margin-left: 4px;
}

.worker-footer {
  font-size: 12px;
  color: #6b7280;
}

.error-msg {
  color: #ef4444;
}

.progress-card {
  margin-bottom: 24px;
}

.progress-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #9ca3af;
}

.queue-container, .logs-container {
  max-height: 200px;
  overflow-y: auto;
}

.queue-item, .log-entry {
  display: flex;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 13px;
}

.queue-symbol {
  color: #3b82f6;
  font-weight: 600;
  min-width: 60px;
}

.queue-name {
  flex: 1;
  color: #d1d5db;
}

.queue-mcap {
  color: #6b7280;
}

.log-time {
  color: #6b7280;
  min-width: 60px;
}

.log-worker {
  color: #8b5cf6;
  min-width: 80px;
}

.log-symbol {
  color: #3b82f6;
  font-weight: 600;
  min-width: 60px;
}

.log-signal {
  font-weight: 600;
  min-width: 100px;
}

.signal-buy { color: #10b981; }
.signal-sell { color: #ef4444; }
.signal-neutral { color: #6b7280; }

.log-asi {
  color: #f59e0b;
}

.no-data {
  text-align: center;
  color: #6b7280;
  padding: 24px;
}

.stats-card {
  margin-top: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}

.stat-box {
  text-align: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.stat-box .stat-value {
  display: block;
  font-size: 24px;
  color: #f9fafb;
  margin-bottom: 4px;
}

.stat-box .stat-label {
  display: block;
  font-size: 12px;
  color: #9ca3af;
}
</style>
