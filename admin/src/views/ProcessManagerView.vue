<template>
  <div class="process-manager">
    <!-- Header -->
    <div class="section-header">
      <h2 class="section-title">Process Manager</h2>
      <n-space>
        <n-button type="success" @click="startAllServices">
          Start All
        </n-button>
        <n-button type="error" @click="stopAllServices">
          Stop All
        </n-button>
        <n-button @click="fetchServices">
          <template #icon>
            <n-icon><RefreshOutline /></n-icon>
          </template>
          Refresh
        </n-button>
      </n-space>
    </div>

    <!-- Services Grid -->
    <n-grid :cols="3" :x-gap="16" :y-gap="16">
      <!-- Scrapers -->
      <n-gi>
        <n-card title="📥 Data Scrapers" :bordered="false">
          <n-space vertical>
            <ServiceCard
              v-for="service in scrapers"
              :key="service.id"
              :service="service"
              @start="handleStart"
              @stop="handleStop"
              @restart="handleRestart"
            />
          </n-space>
        </n-card>
      </n-gi>

      <!-- AI Workers -->
      <n-gi>
        <n-card title="🤖 AI Workers" :bordered="false">
          <n-space vertical>
            <ServiceCard
              v-for="service in aiWorkers"
              :key="service.id"
              :service="service"
              @start="handleStart"
              @stop="handleStop"
              @restart="handleRestart"
            />
          </n-space>
        </n-card>
      </n-gi>

      <!-- On-Chain Collectors -->
      <n-gi>
        <n-card title="⛓️ On-Chain Collectors" :bordered="false">
          <n-space vertical>
            <ServiceCard
              v-for="service in onchainCollectors"
              :key="service.id"
              :service="service"
              @start="handleStart"
              @stop="handleStop"
              @restart="handleRestart"
            />
          </n-space>
        </n-card>
      </n-gi>
    </n-grid>

    <!-- Live Logs Terminal -->
    <n-card title="📟 Live Logs" :bordered="false" style="margin-top: 24px">
      <template #header-extra>
        <n-space>
          <n-select
            v-model:value="selectedLogService"
            :options="logServiceOptions"
            size="small"
            style="width: 200px"
          />
          <n-button size="small" @click="clearLogs">Clear</n-button>
          <n-button size="small" :type="isConnected ? 'success' : 'error'">
            {{ isConnected ? '● Connected' : '○ Disconnected' }}
          </n-button>
        </n-space>
      </template>
      
      <LogTerminal 
        :logs="logs" 
        :is-connected="isConnected"
        @reconnect="connectWebSocket"
      />
    </n-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useMessage } from 'naive-ui'
import { RefreshOutline } from '@vicons/ionicons5'
import ServiceCard from '@/components/ServiceCard.vue'
import LogTerminal from '@/components/LogTerminal.vue'

const message = useMessage()

// Services data
const scrapers = ref([
  { id: 'binance', name: 'Binance Streamer', status: 'running', uptime: '5d 12h 34m', lastLog: 'Synced 450 pairs' },
  { id: 'coingecko', name: 'CoinGecko Fetcher', status: 'running', uptime: '5d 12h 34m', lastLog: 'Updated 5781 coins' },
  { id: 'cmc', name: 'CoinMarketCap', status: 'stopped', uptime: '-', lastLog: 'Rate limit reached' },
])

const aiWorkers = ref([
  { id: 'gemini', name: 'Gemini AI', status: 'running', uptime: '3d 8h 12m', lastLog: 'Analyzed BTC sentiment' },
  { id: 'deepseek', name: 'DeepSeek AI', status: 'running', uptime: '2d 4h 56m', lastLog: 'Technical analysis done' },
  { id: 'sentiment', name: 'Sentiment Analyzer', status: 'running', uptime: '5d 12h 34m', lastLog: 'Processed 100 coins' },
])

const onchainCollectors = ref([
  { id: 'ethereum', name: 'Ethereum Collector', status: 'running', uptime: '4d 6h 22m', lastLog: '1284 whale tx tracked' },
  { id: 'bsc', name: 'BSC Collector', status: 'running', uptime: '4d 6h 22m', lastLog: '567 whale tx tracked' },
  { id: 'solana', name: 'Solana Collector', status: 'stopped', uptime: '-', lastLog: 'RPC connection failed' },
])

// Logs
const logs = ref([])
const selectedLogService = ref('all')
const isConnected = ref(false)
let socket = null

const logServiceOptions = [
  { label: 'All Services', value: 'all' },
  { label: 'Binance Streamer', value: 'binance' },
  { label: 'CoinGecko Fetcher', value: 'coingecko' },
  { label: 'Gemini AI', value: 'gemini' },
  { label: 'Ethereum Collector', value: 'ethereum' },
]

// Service actions
async function handleStart(serviceId) {
  message.loading(`Starting ${serviceId}...`)
  // TODO: Call API POST /admin/process/{serviceId}/start
  setTimeout(() => {
    message.success(`${serviceId} started successfully`)
  }, 1000)
}

async function handleStop(serviceId) {
  message.loading(`Stopping ${serviceId}...`)
  // TODO: Call API POST /admin/process/{serviceId}/stop
  setTimeout(() => {
    message.success(`${serviceId} stopped`)
  }, 1000)
}

async function handleRestart(serviceId) {
  message.loading(`Restarting ${serviceId}...`)
  // TODO: Call API POST /admin/process/{serviceId}/restart
  setTimeout(() => {
    message.success(`${serviceId} restarted`)
  }, 1500)
}

function startAllServices() {
  message.info('Starting all services...')
}

function stopAllServices() {
  message.warning('Stopping all services...')
}

function fetchServices() {
  message.info('Refreshing service status...')
}

// WebSocket for live logs
function connectWebSocket() {
  try {
    // TODO: Connect to real WebSocket
    // socket = new WebSocket('ws://localhost:8000/ws/admin/logs')
    
    isConnected.value = true
    
    // Simulate logs
    const logTypes = ['info', 'warning', 'error', 'success']
    const logMessages = [
      'Market data synced successfully',
      'AI analysis completed for BTC',
      'Rate limit warning from CoinGecko',
      'Whale transaction detected: 500 BTC',
      'Database connection pool: 23/50',
      'WebSocket connection established',
      'Price update: ETH $2920.50',
      'Sentiment score updated: BTC 65/100',
    ]
    
    setInterval(() => {
      if (isConnected.value) {
        const type = logTypes[Math.floor(Math.random() * logTypes.length)]
        const msg = logMessages[Math.floor(Math.random() * logMessages.length)]
        logs.value.push({
          id: Date.now(),
          timestamp: new Date().toISOString(),
          type,
          service: 'system',
          message: msg,
        })
        
        // Keep only last 100 logs
        if (logs.value.length > 100) {
          logs.value = logs.value.slice(-100)
        }
      }
    }, 2000)
    
  } catch (error) {
    console.error('WebSocket connection failed:', error)
    isConnected.value = false
  }
}

function clearLogs() {
  logs.value = []
}

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (socket) {
    socket.close()
  }
})
</script>

<style scoped>
.process-manager {
  max-width: 1400px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
}
</style>
