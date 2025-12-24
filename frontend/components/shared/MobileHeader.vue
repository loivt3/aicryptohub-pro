<template>
  <header class="glass-header">
    <div class="header-content">
      <!-- Left: Avatar + Logo + Page Title -->
      <div class="header-left">
        <!-- User Avatar (clickable for Portfolio) -->
        <button class="avatar-btn" @click="$emit('setTab', 'portfolio')" title="Portfolio">
          <Icon name="ph:user" class="avatar-icon" />
        </button>
        
        <!-- Logo + Page Title -->
        <div class="brand-info">
          <span class="brand-name">COINXSIGHT</span>
          <span class="page-title">{{ pageTitle }}</span>
        </div>
      </div>
      
      <!-- Right: Actions (plain icons, no borders) -->
      <div class="header-right">
        <button class="icon-btn" @click="$emit('openSearch')" title="Search">
          <Icon name="ph:magnifying-glass" class="icon" />
        </button>
        <button 
          class="icon-btn"
          @click="$emit('setTab', 'alerts')"
          title="Notifications"
        >
          <Icon name="ph:bell" class="icon" />
          <span v-if="alertCount > 0" class="badge">{{ alertCount > 9 ? '9+' : alertCount }}</span>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{
  activeTab?: string
}>()

defineEmits<{
  (e: 'setTab', tab: string): void
  (e: 'openSearch'): void
}>()

const alertCount = ref(0)

// Page title based on active tab
const pageTitle = computed(() => {
  switch (props.activeTab) {
    case 'dashboard': return 'Dashboard'
    case 'market': return 'Market'
    case 'analysis': return 'Analysis'
    case 'portfolio': return 'Portfolio'
    case 'aichat': return 'AI Chat'
    case 'shadow': return 'Shadow'
    default: return 'Dashboard'
  }
})

// Handle avatar image error (fallback to icon)
const handleAvatarError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
}
</script>

<style scoped>
.glass-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(10, 15, 20, 0.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  /* No bottom border */
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Avatar button - circular, clickable, MEDIUM size */
.avatar-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #10b981;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.3), rgba(56, 239, 235, 0.2));
  padding: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-icon {
  width: 20px;
  height: 20px;
  color: #10b981;
}

.brand-info {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-size: 9px;
  font-weight: 600;
  color: #10b981;
  letter-spacing: 1.2px;
  line-height: 1;
  text-transform: uppercase;
}

.page-title {
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.2;
  margin-top: 2px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Plain icon buttons - no background, no border, MEDIUM */
.icon-btn {
  position: relative;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: opacity 0.2s;
}

.icon-btn:hover,
.icon-btn:active {
  opacity: 0.7;
}

.icon {
  width: 20px;
  height: 20px;
  color: rgba(255, 255, 255, 0.8);
}

.badge {
  position: absolute;
  top: 2px;
  right: 2px;
  min-width: 14px;
  height: 14px;
  padding: 0 3px;
  background: #ef4444;
  color: white;
  font-size: 8px;
  font-weight: 700;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
