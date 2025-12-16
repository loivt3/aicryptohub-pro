<template>
  <div class="log-terminal" ref="terminalRef">
    <div v-if="logs.length === 0" class="terminal-empty">
      <span v-if="isConnected">Waiting for logs...</span>
      <span v-else>
        Not connected. 
        <n-button text type="primary" @click="$emit('reconnect')">Reconnect</n-button>
      </span>
    </div>
    
    <div 
      v-for="log in logs" 
      :key="log.id" 
      class="log-line"
      :class="logClass(log.type)"
    >
      <span class="log-time">{{ formatTime(log.timestamp) }}</span>
      <span class="log-service">[{{ log.service }}]</span>
      <span class="log-message">{{ log.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  logs: {
    type: Array,
    default: () => [],
  },
  isConnected: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['reconnect'])

const terminalRef = ref(null)

// Auto-scroll to bottom
watch(() => props.logs.length, async () => {
  await nextTick()
  if (terminalRef.value) {
    terminalRef.value.scrollTop = terminalRef.value.scrollHeight
  }
})

function formatTime(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', { hour12: false })
}

function logClass(type) {
  const classes = {
    error: 'log-error',
    warning: 'log-warning',
    info: 'log-info',
    success: 'log-success',
  }
  return classes[type] || ''
}
</script>

<style scoped>
.log-terminal {
  background: #000;
  border-radius: 8px;
  padding: 16px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  height: 400px;
  overflow-y: auto;
  color: #10b981;
}

.terminal-empty {
  color: #6b7280;
  text-align: center;
  padding: 40px;
}

.log-line {
  white-space: pre-wrap;
  word-break: break-all;
  padding: 2px 0;
}

.log-time {
  color: #6b7280;
  margin-right: 8px;
}

.log-service {
  color: #3b82f6;
  margin-right: 8px;
}

.log-message {
  color: #d1d5db;
}

.log-error .log-message {
  color: #ef4444;
}

.log-warning .log-message {
  color: #f59e0b;
}

.log-info .log-message {
  color: #3b82f6;
}

.log-success .log-message {
  color: #10b981;
}
</style>
