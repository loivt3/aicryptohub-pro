<template>
  <div class="dashboard">
    <!-- Stats Overview -->
    <n-grid :cols="4" :x-gap="16" :y-gap="16">
      <n-gi>
        <div class="stat-card">
          <div class="stat-icon" style="color: #3b82f6">👥</div>
          <div class="stat-value">{{ stats.activeUsers }}</div>
          <div class="stat-label">Active Users</div>
        </div>
      </n-gi>
      <n-gi>
        <div class="stat-card">
          <div class="stat-icon" style="color: #10b981">📊</div>
          <div class="stat-value">{{ stats.apiCalls }}/min</div>
          <div class="stat-label">API Calls</div>
        </div>
      </n-gi>
      <n-gi>
        <div class="stat-card">
          <div class="stat-icon" style="color: #f59e0b">💰</div>
          <div class="stat-value">{{ stats.coinsTracked }}</div>
          <div class="stat-label">Coins Tracked</div>
        </div>
      </n-gi>
      <n-gi>
        <div class="stat-card">
          <div class="stat-icon" style="color: #ef4444">⚠️</div>
          <div class="stat-value">{{ stats.errorRate }}%</div>
          <div class="stat-label">Error Rate</div>
        </div>
      </n-gi>
    </n-grid>

    <!-- System Health & Services -->
    <n-grid :cols="2" :x-gap="16" :y-gap="16" style="margin-top: 24px">
      <!-- System Health -->
      <n-gi>
        <n-card title="System Health" :bordered="false">
          <n-space vertical>
            <div class="health-item">
              <span class="health-label">CPU Usage</span>
              <n-progress
                type="line"
                :percentage="systemHealth.cpu"
                :color="getHealthColor(systemHealth.cpu)"
                :rail-color="'rgba(255,255,255,0.1)'"
              />
            </div>
            <div class="health-item">
              <span class="health-label">Memory Usage</span>
              <n-progress
                type="line"
                :percentage="systemHealth.memory"
                :color="getHealthColor(systemHealth.memory)"
                :rail-color="'rgba(255,255,255,0.1)'"
              />
            </div>
            <div class="health-item">
              <span class="health-label">Disk Usage</span>
              <n-progress
                type="line"
                :percentage="systemHealth.disk"
                :color="getHealthColor(systemHealth.disk)"
                :rail-color="'rgba(255,255,255,0.1)'"
              />
            </div>
            <div class="health-item">
              <span class="health-label">Database Connections</span>
              <n-progress
                type="line"
                :percentage="systemHealth.dbConnections"
                :color="getHealthColor(systemHealth.dbConnections)"
                :rail-color="'rgba(255,255,255,0.1)'"
              />
            </div>
          </n-space>
        </n-card>
      </n-gi>

      <!-- Services Status -->
      <n-gi>
        <n-card title="Services Status" :bordered="false">
          <n-space vertical>
            <div v-for="service in services" :key="service.name" class="service-item">
              <div class="service-info">
                <span class="service-name">{{ service.name }}</span>
                <span class="service-uptime">Uptime: {{ service.uptime }}</span>
              </div>
              <span :class="['status-badge', service.status === 'running' ? 'status-running' : 'status-stopped']">
                {{ service.status === 'running' ? '● Running' : '○ Stopped' }}
              </span>
            </div>
          </n-space>
        </n-card>
      </n-gi>
    </n-grid>

    <!-- Recent Activity -->
    <n-card title="Recent Activity" :bordered="false" style="margin-top: 24px">
      <n-timeline>
        <n-timeline-item
          v-for="activity in recentActivity"
          :key="activity.id"
          :type="activity.type"
          :title="activity.title"
          :content="activity.content"
          :time="activity.time"
        />
      </n-timeline>
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Stats data
const stats = ref({
  activeUsers: 0,
  apiCalls: 0,
  coinsTracked: 0,
  errorRate: 0,
})

// System health
const systemHealth = ref({
  cpu: 0,
  memory: 0,
  disk: 0,
  dbConnections: 0,
})

// Services
const services = ref([
  { name: 'Market Streamer', status: 'running', uptime: '5d 12h' },
  { name: 'AI Worker', status: 'running', uptime: '5d 12h' },
  { name: 'On-Chain Collector', status: 'running', uptime: '3d 8h' },
  { name: 'Price Aggregator', status: 'running', uptime: '5d 12h' },
  { name: 'Redis Cache', status: 'running', uptime: '5d 12h' },
])

// Recent activity
const recentActivity = ref([
  { id: 1, type: 'success', title: 'Coin data updated', content: 'Market data synced for 5,781 coins', time: '2 minutes ago' },
  { id: 2, type: 'info', title: 'AI Analysis completed', content: 'Sentiment analysis for top 100 coins', time: '15 minutes ago' },
  { id: 3, type: 'warning', title: 'Rate limit warning', content: 'CoinGecko API approaching rate limit', time: '1 hour ago' },
  { id: 4, type: 'success', title: 'On-chain data synced', content: 'Whale transactions updated', time: '2 hours ago' },
])

// Get health color
function getHealthColor(percentage) {
  if (percentage < 60) return '#10b981'
  if (percentage < 80) return '#f59e0b'
  return '#ef4444'
}

// Fetch data
async function fetchDashboardData() {
  try {
    // TODO: Replace with real API calls
    stats.value = {
      activeUsers: 1247,
      apiCalls: 2340,
      coinsTracked: 5781,
      errorRate: 0.12,
    }
    
    systemHealth.value = {
      cpu: 42,
      memory: 68,
      disk: 55,
      dbConnections: 23,
    }
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
}

.stat-card {
  background: #111827;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
}

.stat-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #f9fafb;
}

.stat-label {
  font-size: 14px;
  color: #9ca3af;
  margin-top: 4px;
}

.health-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.health-label {
  font-size: 14px;
  color: #9ca3af;
}

.service-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.service-item:last-child {
  border-bottom: none;
}

.service-info {
  display: flex;
  flex-direction: column;
}

.service-name {
  font-size: 14px;
  font-weight: 500;
  color: #f9fafb;
}

.service-uptime {
  font-size: 12px;
  color: #6b7280;
}
</style>
