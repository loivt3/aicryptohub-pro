<template>
  <n-layout has-sider style="min-height: 100vh">
    <!-- Sidebar -->
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="260"
      :collapsed="collapsed"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
      :native-scrollbar="false"
      style="background: #111827"
    >
      <!-- Logo -->
      <div class="sidebar-logo">
        <div class="logo-icon">🚀</div>
        <span v-if="!collapsed" class="logo-text">Admin Console</span>
      </div>

      <!-- Menu -->
      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        :value="activeKey"
        @update:value="handleMenuSelect"
      />

      <!-- User Info -->
      <div v-if="!collapsed" class="sidebar-footer">
        <div class="user-info">
          <n-avatar round size="small">A</n-avatar>
          <div class="user-details">
            <div class="user-name">Admin</div>
            <div class="user-role">Super Admin</div>
          </div>
        </div>
        <n-button quaternary circle @click="handleLogout">
          <template #icon>
            <n-icon><LogOutOutline /></n-icon>
          </template>
        </n-button>
      </div>
    </n-layout-sider>

    <!-- Main Content -->
    <n-layout>
      <!-- Header -->
      <n-layout-header bordered style="height: 64px; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; background: #111827">
        <div class="header-left">
          <n-breadcrumb>
            <n-breadcrumb-item>Admin</n-breadcrumb-item>
            <n-breadcrumb-item>{{ currentTitle }}</n-breadcrumb-item>
          </n-breadcrumb>
        </div>
        <div class="header-right">
          <n-space>
            <n-button quaternary circle>
              <template #icon>
                <n-icon><RefreshOutline /></n-icon>
              </template>
            </n-button>
            <n-badge :value="3" :max="99">
              <n-button quaternary circle>
                <template #icon>
                  <n-icon><NotificationsOutline /></n-icon>
                </template>
              </n-button>
            </n-badge>
          </n-space>
        </div>
      </n-layout-header>

      <!-- Content -->
      <n-layout-content style="padding: 24px; background: #0a0f1a">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup>
import { ref, computed, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NIcon } from 'naive-ui'
import {
  HomeOutline,
  SettingsOutline,
  ServerOutline,
  PeopleOutline,
  ShieldCheckmarkOutline,
  ConstructOutline,
  LogOutOutline,
  RefreshOutline,
  NotificationsOutline,
  FlashOutline,
} from '@vicons/ionicons5'

const route = useRoute()
const router = useRouter()
const collapsed = ref(false)

// Current page title
const currentTitle = computed(() => route.meta?.title || 'Dashboard')

// Active menu key
const activeKey = computed(() => route.name)

// Render icon helper
function renderIcon(icon) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

// Menu options
const menuOptions = [
  {
    label: 'Dashboard',
    key: 'dashboard',
    icon: renderIcon(HomeOutline),
  },
  {
    label: 'Process Manager',
    key: 'process-manager',
    icon: renderIcon(SettingsOutline),
    children: [
      { label: 'Overview', key: 'process-manager' },
      { label: 'Fetcher Manager', key: 'fetcher-manager' },
      { label: 'AI Workers', key: 'ai-workers' },
    ],
  },
  {
    label: 'Data Management',
    key: 'data-management',
    icon: renderIcon(ServerOutline),
    children: [
      { label: 'Coins Manager', key: 'coins-manager' },
      { label: 'News Curation', key: 'news-curation' },
    ],
  },
  {
    label: 'System Settings',
    key: 'settings',
    icon: renderIcon(ConstructOutline),
    children: [
      { label: 'Backend Settings', key: 'backend-settings' },
      { label: 'Frontend Settings', key: 'frontend-settings' },
      { label: 'AI Tuning', key: 'ai-tuning' },
    ],
  },
  {
    label: 'Users & Roles',
    key: 'users',
    icon: renderIcon(PeopleOutline),
  },
  {
    label: 'Audit & Security',
    key: 'audit',
    icon: renderIcon(ShieldCheckmarkOutline),
  },
]

// Handle menu selection
function handleMenuSelect(key) {
  router.push({ name: key })
}

// Handle logout
function handleLogout() {
  localStorage.removeItem('admin_token')
  router.push({ name: 'login' })
}
</script>

<style scoped>
.sidebar-logo {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #f9fafb;
}

.sidebar-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: #111827;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #f9fafb;
}

.user-role {
  font-size: 12px;
  color: #9ca3af;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}
</style>
