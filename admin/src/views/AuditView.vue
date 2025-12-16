<template>
  <div class="audit-view">
    <div class="section-header">
      <h2 class="section-title">Audit & Security</h2>
    </div>

    <n-tabs type="line" animated>
      <!-- API Logs -->
      <n-tab-pane name="api" tab="📡 API Logs">
        <n-card :bordered="false">
          <n-data-table
            :columns="apiLogColumns"
            :data="apiLogs"
            :pagination="{ pageSize: 10 }"
            :bordered="false"
          />
        </n-card>
      </n-tab-pane>

      <!-- Login History -->
      <n-tab-pane name="login" tab="🔐 Login History">
        <n-card :bordered="false">
          <n-data-table
            :columns="loginColumns"
            :data="loginHistory"
            :pagination="{ pageSize: 10 }"
            :bordered="false"
          />
        </n-card>
      </n-tab-pane>

      <!-- IP Blacklist -->
      <n-tab-pane name="blacklist" tab="🚫 IP Blacklist">
        <n-card :bordered="false">
          <template #header-extra>
            <n-button type="error" size="small">Add IP</n-button>
          </template>
          <n-data-table
            :columns="blacklistColumns"
            :data="blacklist"
            :pagination="{ pageSize: 10 }"
            :bordered="false"
          />
        </n-card>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup>
import { ref, h } from 'vue'
import { NTag, NButton } from 'naive-ui'

// API Logs
const apiLogColumns = [
  { title: 'Time', key: 'time', width: 180 },
  { title: 'Method', key: 'method', width: 80 },
  { title: 'Endpoint', key: 'endpoint' },
  {
    title: 'Status',
    key: 'status',
    width: 100,
    render(row) {
      const type = row.status < 400 ? 'success' : row.status < 500 ? 'warning' : 'error'
      return h(NTag, { type, size: 'small' }, { default: () => row.status })
    }
  },
  { title: 'IP', key: 'ip', width: 140 },
  { title: 'Duration', key: 'duration', width: 100 },
]

const apiLogs = ref([
  { time: '2024-12-16 21:45:00', method: 'GET', endpoint: '/api/v1/market', status: 200, ip: '192.168.1.1', duration: '45ms' },
  { time: '2024-12-16 21:44:55', method: 'POST', endpoint: '/api/v1/auth/login', status: 200, ip: '192.168.1.2', duration: '120ms' },
  { time: '2024-12-16 21:44:50', method: 'GET', endpoint: '/api/v1/sentiment', status: 200, ip: '192.168.1.1', duration: '32ms' },
  { time: '2024-12-16 21:44:45', method: 'GET', endpoint: '/api/v1/onchain/signals/bitcoin', status: 500, ip: '192.168.1.3', duration: '5000ms' },
])

// Login History
const loginColumns = [
  { title: 'User', key: 'user' },
  { title: 'Time', key: 'time' },
  { title: 'IP Address', key: 'ip' },
  { title: 'Location', key: 'location' },
  {
    title: 'Status',
    key: 'status',
    render(row) {
      const type = row.status === 'success' ? 'success' : 'error'
      return h(NTag, { type, size: 'small' }, { default: () => row.status })
    }
  },
]

const loginHistory = ref([
  { user: 'admin@aicryptohub.io', time: '2024-12-16 21:30:00', ip: '192.168.1.1', location: 'Vietnam', status: 'success' },
  { user: 'unknown', time: '2024-12-16 21:25:00', ip: '185.220.101.1', location: 'Germany', status: 'failed' },
])

// Blacklist
const blacklistColumns = [
  { title: 'IP Address', key: 'ip' },
  { title: 'Reason', key: 'reason' },
  { title: 'Added', key: 'added' },
  { title: 'Expires', key: 'expires' },
  {
    title: 'Actions',
    key: 'actions',
    render(row) {
      return h(NButton, { size: 'small', quaternary: true }, { default: () => 'Remove' })
    }
  },
]

const blacklist = ref([
  { ip: '185.220.101.1', reason: 'Brute force attempt', added: '2024-12-15', expires: 'Never' },
  { ip: '45.155.205.0/24', reason: 'Known malicious range', added: '2024-12-10', expires: 'Never' },
])
</script>

<style scoped>
.audit-view {
  max-width: 1200px;
}

.section-header {
  margin-bottom: 24px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
}
</style>
