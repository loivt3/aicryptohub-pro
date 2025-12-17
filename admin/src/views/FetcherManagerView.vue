<template>
  <div class="fetcher-manager">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <h2>📡 Fetcher Process Manager</h2>
        <n-tag :type="isRunning ? 'warning' : 'success'" size="small">
          {{ isRunning ? '● Running' : '○ Idle' }}
        </n-tag>
      </div>
      <div class="header-right">
        <n-button 
          type="primary" 
          :loading="isRunning"
          @click="triggerFetch"
        >
          <template #icon>
            <span>▶️</span>
          </template>
          Run Fetch Now
        </n-button>
      </div>
    </div>

    <!-- Source Status Grid -->
    <n-grid :cols="5" :x-gap="16" :y-gap="16" class="sources-grid">
      <n-gi v-for="source in sources" :key="source.id">
        <div 
          :class="['source-card', `status-${source.status}`]"
          @click="toggleSource(source)"
        >
          <div class="source-header">
            <span class="source-type">{{ source.type.toUpperCase() }}</span>
            <span :class="['status-dot', source.status]"></span>
          </div>
          <div class="source-name">{{ source.name }}</div>
          <div class="source-stats">
            <div v-if="source.items_fetched > 0">
              <span class="stat-value">{{ formatNumber(source.items_fetched) }}</span>
              <span class="stat-label">items</span>
            </div>
            <div v-if="source.duration_ms > 0">
              <span class="stat-value">{{ (source.duration_ms / 1000).toFixed(2) }}s</span>
            </div>
          </div>
          <div class="source-footer">
            <span v-if="source.last_fetch" class="last-fetch">
              {{ formatTimeAgo(source.last_fetch) }}
            </span>
            <span v-else-if="source.error_message" class="error-msg">
              {{ source.error_message }}
            </span>
            <span v-else class="ready">Ready</span>
          </div>
        </div>
      </n-gi>
    </n-grid>

    <!-- Logs Panel -->
    <n-card title="📋 Recent Fetch Logs" :bordered="false" class="logs-card">
      <template #header-extra>
        <n-button size="small" quaternary @click="fetchLogs">
          Refresh
        </n-button>
      </template>
      
      <div class="logs-container">
        <div 
          v-for="log in logs" 
          :key="log.id" 
          :class="['log-entry', `log-${log.level}`]"
        >
          <span class="log-time">{{ formatTime(log.timestamp) }}</span>
          <span class="log-source">[{{ log.source }}]</span>
          <span class="log-message">{{ log.message }}</span>
          <span v-if="log.items_count > 0" class="log-items">
            ({{ log.items_count }} items)
          </span>
          <span v-if="log.duration_ms > 0" class="log-duration">
            {{ log.duration_ms }}ms
          </span>
        </div>
        
        <div v-if="logs.length === 0" class="no-logs">
          No fetch logs yet. Click "Run Fetch Now" to start.
        </div>
      </div>
    </n-card>

    <!-- History Stats -->
    <n-card title="📊 Fetch History (7 days)" :bordered="false" class="history-card">
      <div class="history-stats">
        <div class="history-stat">
          <span class="stat-value">{{ totalFetches }}</span>
          <span class="stat-label">Total Fetches</span>
        </div>
        <div class="history-stat">
          <span class="stat-value">{{ avgDuration }}ms</span>
          <span class="stat-label">Avg Duration</span>
        </div>
        <div class="history-stat">
          <span class="stat-value">{{ totalErrors }}</span>
          <span class="stat-label">Errors</span>
        </div>
        <div class="history-stat">
          <span class="stat-value">{{ lastFetchTime || 'Never' }}</span>
          <span class="stat-label">Last Fetch</span>
        </div>
      </div>
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useMessage } from 'naive-ui'
import axios from 'axios'

const API_BASE = '/api/v1'
const message = useMessage()

// State
const sources = ref([])
const logs = ref([])
const history = ref([])
const isRunning = ref(false)
const lastFullFetch = ref(null)

// Computed
const totalFetches = computed(() => 
  history.value.reduce((sum, h) => sum + (h.fetch_count || 0), 0)
)

const avgDuration = computed(() => {
  if (history.value.length === 0) return 0
  const total = history.value.reduce((sum, h) => sum + (h.avg_duration_ms || 0), 0)
  return Math.round(total / history.value.length)
})

const totalErrors = computed(() => 
  history.value.reduce((sum, h) => sum + (h.error_count || 0), 0)
)

const lastFetchTime = computed(() => {
  if (!lastFullFetch.value) return null
  return formatTimeAgo(lastFullFetch.value)
})

// Methods
function formatNumber(num) {
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num
}

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', { hour12: false })
}

function formatTimeAgo(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)
  
  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

async function fetchStatus() {
  try {
    const response = await axios.get(`${API_BASE}/admin/fetcher/status`)
    sources.value = response.data.sources || []
    isRunning.value = response.data.is_running || false
    lastFullFetch.value = response.data.last_full_fetch
  } catch (error) {
    console.error('Failed to fetch status:', error)
  }
}

async function fetchLogs() {
  try {
    const response = await axios.get(`${API_BASE}/admin/fetcher/logs`)
    logs.value = response.data.logs || []
  } catch (error) {
    console.error('Failed to fetch logs:', error)
  }
}

async function fetchHistory() {
  try {
    const response = await axios.get(`${API_BASE}/admin/fetcher/history`)
    history.value = response.data.history || []
  } catch (error) {
    console.error('Failed to fetch history:', error)
  }
}

async function triggerFetch() {
  try {
    isRunning.value = true
    const response = await axios.post(`${API_BASE}/admin/fetcher/trigger`)
    message.success(`Fetch job started: ${response.data.job_id}`)
    
    // Start polling for status updates
    pollStatus()
  } catch (error) {
    console.error('Failed to trigger fetch:', error)
    message.error('Failed to trigger fetch')
    isRunning.value = false
  }
}

async function toggleSource(source) {
  try {
    const enabled = source.status === 'disabled'
    await axios.post(`${API_BASE}/admin/fetcher/source/${source.id}/toggle`, null, {
      params: { enabled }
    })
    message.success(`${source.name} ${enabled ? 'enabled' : 'disabled'}`)
    fetchStatus()
  } catch (error) {
    console.error('Failed to toggle source:', error)
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
    }
  }, 2000)
}

// Auto-refresh
let refreshInterval = null

onMounted(() => {
  fetchStatus()
  fetchLogs()
  fetchHistory()
  
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
.fetcher-manager {
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

.sources-grid {
  margin-bottom: 24px;
}

.source-card {
  background: #111827;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;
}

.source-card:hover {
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.source-card.status-running {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
}

.source-card.status-error {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.source-card.status-disabled {
  opacity: 0.5;
}

.source-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.source-type {
  font-size: 10px;
  color: #6b7280;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #6b7280;
}

.status-dot.ready { background: #10b981; }
.status-dot.running { background: #f59e0b; animation: pulse 1s infinite; }
.status-dot.error { background: #ef4444; }
.status-dot.disabled { background: #374151; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.source-name {
  font-size: 16px;
  font-weight: 600;
  color: #f9fafb;
  margin-bottom: 8px;
}

.source-stats {
  display: flex;
  gap: 12px;
  font-size: 12px;
  margin-bottom: 8px;
}

.stat-value {
  color: #10b981;
  font-weight: 600;
}

.stat-label {
  color: #6b7280;
  margin-left: 4px;
}

.source-footer {
  font-size: 11px;
  color: #6b7280;
}

.error-msg {
  color: #ef4444;
}

.logs-card {
  margin-bottom: 24px;
}

.logs-container {
  max-height: 300px;
  overflow-y: auto;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
}

.log-entry {
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  gap: 8px;
  align-items: center;
}

.log-entry.log-error {
  color: #ef4444;
}

.log-entry.log-warning {
  color: #f59e0b;
}

.log-time {
  color: #6b7280;
  min-width: 70px;
}

.log-source {
  color: #3b82f6;
  min-width: 100px;
}

.log-message {
  flex: 1;
  color: #d1d5db;
}

.log-items {
  color: #10b981;
}

.log-duration {
  color: #6b7280;
  min-width: 60px;
  text-align: right;
}

.no-logs {
  text-align: center;
  color: #6b7280;
  padding: 24px;
}

.history-stats {
  display: flex;
  gap: 48px;
}

.history-stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-stat .stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #f9fafb;
}

.history-stat .stat-label {
  font-size: 12px;
  color: #6b7280;
}
</style>
