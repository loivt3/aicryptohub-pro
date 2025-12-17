<template>
  <Transition name="slide-up">
    <div 
      v-if="visible" 
      class="intent-alert"
      :class="alertClass"
      @click="handleClick"
    >
      <div class="alert-icon">
        <span v-if="alertType === 'golden_shadow'">⚡</span>
        <span v-else-if="alertType === 'shadow_accumulation'">🟢</span>
        <span v-else-if="alertType === 'bull_trap'">🔴</span>
        <span v-else>📊</span>
      </div>
      
      <div class="alert-content">
        <div class="alert-title">{{ title }}</div>
        <div class="alert-message">{{ message }}</div>
        <div class="alert-coin" v-if="coinId">
          <span class="coin-label">{{ coinSymbol }}</span>
          <span class="intent-score">Intent: {{ intentScore }}/100</span>
        </div>
      </div>
      
      <button class="close-btn" @click.stop="dismiss">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  alertType: {
    type: String,
    default: 'neutral',
    validator: (val) => ['golden_shadow', 'shadow_accumulation', 'bull_trap', 'confirmation', 'neutral'].includes(val)
  },
  coinId: {
    type: String,
    default: ''
  },
  coinSymbol: {
    type: String,
    default: ''
  },
  intentScore: {
    type: Number,
    default: 50
  },
  message: {
    type: String,
    default: ''
  },
  duration: {
    type: Number,
    default: 8000 // Auto-dismiss after 8 seconds
  },
  autoShow: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['dismiss', 'click'])

const visible = ref(false)
let timer = null

// Computed
const title = computed(() => {
  const titles = {
    'golden_shadow': '⚡ Golden Shadow Entry!',
    'shadow_accumulation': '🐋 Shadow Accumulation',
    'bull_trap': '⚠️ Bull Trap Warning',
    'confirmation': '✓ Trend Confirmation',
    'neutral': '📊 Market Update'
  }
  return titles[props.alertType] || titles.neutral
})

const alertClass = computed(() => ({
  'alert-golden': props.alertType === 'golden_shadow',
  'alert-accumulation': props.alertType === 'shadow_accumulation',
  'alert-trap': props.alertType === 'bull_trap',
  'alert-confirmation': props.alertType === 'confirmation',
  'alert-neutral': props.alertType === 'neutral'
}))

// Methods
function show() {
  visible.value = true
  
  if (props.duration > 0) {
    timer = setTimeout(() => {
      dismiss()
    }, props.duration)
  }
}

function dismiss() {
  visible.value = false
  if (timer) {
    clearTimeout(timer)
    timer = null
  }
  emit('dismiss')
}

function handleClick() {
  emit('click', { coinId: props.coinId, alertType: props.alertType })
}

// Lifecycle
onMounted(() => {
  if (props.autoShow) {
    // Slight delay for animation
    setTimeout(show, 100)
  }
})

onUnmounted(() => {
  if (timer) clearTimeout(timer)
})

// Expose for parent control
defineExpose({ show, dismiss })
</script>

<style scoped>
.intent-alert {
  position: fixed;
  bottom: 80px; /* Above bottom navigation */
  left: 16px;
  right: 16px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 16px;
  backdrop-filter: blur(20px);
  cursor: pointer;
  z-index: 1000;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.alert-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 4px;
}

.alert-message {
  font-size: 13px;
  line-height: 1.4;
  opacity: 0.9;
  margin-bottom: 8px;
}

.alert-coin {
  display: flex;
  align-items: center;
  gap: 12px;
}

.coin-label {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.15);
}

.intent-score {
  font-size: 12px;
  opacity: 0.8;
}

.close-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: inherit;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.close-btn:hover {
  opacity: 1;
}

/* Alert variants */
.alert-golden {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.25) 0%, rgba(255, 165, 0, 0.2) 100%);
  border: 1px solid rgba(255, 215, 0, 0.5);
  color: #fff;
  animation: glow-gold 2s infinite;
}

.alert-golden .alert-title { color: #ffd700; }

.alert-accumulation {
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.2) 0%, rgba(0, 200, 100, 0.15) 100%);
  border: 1px solid rgba(0, 255, 136, 0.4);
  color: #fff;
}

.alert-accumulation .alert-title { color: #00ff88; }

.alert-trap {
  background: linear-gradient(135deg, rgba(255, 68, 68, 0.2) 0%, rgba(200, 50, 50, 0.15) 100%);
  border: 1px solid rgba(255, 68, 68, 0.4);
  color: #fff;
}

.alert-trap .alert-title { color: #ff4444; }

.alert-confirmation {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(0, 150, 200, 0.15) 100%);
  border: 1px solid rgba(0, 212, 255, 0.4);
  color: #fff;
}

.alert-confirmation .alert-title { color: #00d4ff; }

.alert-neutral {
  background: linear-gradient(135deg, rgba(139, 143, 163, 0.2) 0%, rgba(100, 100, 120, 0.15) 100%);
  border: 1px solid rgba(139, 143, 163, 0.4);
  color: #fff;
}

/* Animations */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(100%);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(100%);
}

@keyframes glow-gold {
  0%, 100% { 
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 0 rgba(255, 215, 0, 0.4); 
  }
  50% { 
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 30px 10px rgba(255, 215, 0, 0.2); 
  }
}
</style>
