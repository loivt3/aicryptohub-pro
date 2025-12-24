<template>
  <nav class="m-bottom-nav">
    <NuxtLink 
      v-for="item in navItems" 
      :key="item.id"
      :to="item.to"
      class="m-nav-item"
      :class="{ active: route.path === item.to }"
    >
      <Icon :name="item.icon" class="m-nav-icon" />
      <span class="m-nav-label">{{ item.label }}</span>
    </NuxtLink>
  </nav>
</template>

<script setup lang="ts">
const route = useRoute()

// Navigation items - reorganized as requested
const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: 'ph:house', to: '/' },
  { id: 'market', label: 'Market', icon: 'ph:squares-four', to: '/market' },
  { id: 'analysis', label: 'Analysis', icon: 'ph:chart-line-up', to: '/analysis' },
  { id: 'shadow', label: 'Shadow', icon: 'ph:eye', to: '/shadow' },
  { id: 'aichat', label: 'AI Chat', icon: 'ph:chat-dots', to: '/aichat' },
]
</script>

<style scoped>
.m-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  justify-content: space-around;
  background: rgba(20, 28, 43, 0.98);
  backdrop-filter: blur(12px);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding: 8px 0;
  padding-bottom: calc(8px + env(safe-area-inset-bottom));
}

.m-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
  min-width: 60px;
}

.m-nav-item.active,
.m-nav-item.router-link-active {
  color: #38efeb;
}

.m-nav-item:hover {
  color: rgba(255, 255, 255, 0.8);
}

.m-nav-icon {
  width: 22px;
  height: 22px;
}

.m-nav-label {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.2px;
}
</style>
