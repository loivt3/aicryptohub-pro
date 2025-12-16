<template>
  <div class="service-card" :class="{ 'is-stopped': service.status === 'stopped' }">
    <div class="service-header">
      <div class="service-info">
        <span class="service-name">{{ service.name }}</span>
        <span :class="['status-badge', statusClass]">
          {{ statusText }}
        </span>
      </div>
      <n-dropdown :options="actionOptions" @select="handleAction">
        <n-button quaternary circle size="small">
          <template #icon>
            <n-icon><EllipsisVerticalOutline /></n-icon>
          </template>
        </n-button>
      </n-dropdown>
    </div>
    
    <div class="service-meta">
      <div class="meta-item">
        <span class="meta-label">Uptime:</span>
        <span class="meta-value">{{ service.uptime }}</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Last Log:</span>
        <span class="meta-value">{{ service.lastLog }}</span>
      </div>
    </div>
    
    <div class="service-actions">
      <n-button 
        v-if="service.status === 'stopped'"
        type="success" 
        size="small"
        @click="$emit('start', service.id)"
      >
        Start
      </n-button>
      <n-button 
        v-else
        type="error" 
        size="small"
        @click="$emit('stop', service.id)"
      >
        Stop
      </n-button>
      <n-button 
        size="small"
        @click="$emit('restart', service.id)"
        :disabled="service.status === 'stopped'"
      >
        Restart
      </n-button>
    </div>
  </div>
</template>

<script setup>
import { computed, h } from 'vue'
import { NIcon } from 'naive-ui'
import { 
  EllipsisVerticalOutline, 
  PlayOutline, 
  StopOutline, 
  RefreshOutline,
  DocumentTextOutline 
} from '@vicons/ionicons5'

const props = defineProps({
  service: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['start', 'stop', 'restart'])

const statusClass = computed(() => {
  return props.service.status === 'running' ? 'status-running' : 'status-stopped'
})

const statusText = computed(() => {
  return props.service.status === 'running' ? '● Running' : '○ Stopped'
})

const actionOptions = [
  {
    label: 'View Logs',
    key: 'logs',
    icon: () => h(NIcon, null, { default: () => h(DocumentTextOutline) }),
  },
  {
    label: 'Restart',
    key: 'restart',
    icon: () => h(NIcon, null, { default: () => h(RefreshOutline) }),
  },
]

function handleAction(key) {
  if (key === 'restart') {
    emit('restart', props.service.id)
  }
}
</script>

<style scoped>
.service-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s;
}

.service-card:hover {
  background: rgba(255, 255, 255, 0.05);
}

.service-card.is-stopped {
  opacity: 0.7;
}

.service-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.service-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.service-name {
  font-size: 14px;
  font-weight: 600;
  color: #f9fafb;
}

.service-meta {
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  gap: 8px;
  font-size: 12px;
  margin-bottom: 4px;
}

.meta-label {
  color: #6b7280;
}

.meta-value {
  color: #9ca3af;
}

.service-actions {
  display: flex;
  gap: 8px;
}
</style>
