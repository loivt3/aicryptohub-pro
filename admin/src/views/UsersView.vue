<template>
  <div class="users-view">
    <div class="section-header">
      <h2 class="section-title">Users & Roles</h2>
      <n-button type="primary">
        <template #icon>
          <n-icon><AddOutline /></n-icon>
        </template>
        Add User
      </n-button>
    </div>

    <!-- Stats -->
    <n-grid :cols="4" :x-gap="16" style="margin-bottom: 24px">
      <n-gi>
        <div class="stat-card">
          <div class="stat-value">1,247</div>
          <div class="stat-label">Total Users</div>
        </div>
      </n-gi>
      <n-gi>
        <div class="stat-card">
          <div class="stat-value">89</div>
          <div class="stat-label">Premium</div>
        </div>
      </n-gi>
      <n-gi>
        <div class="stat-card">
          <div class="stat-value">5</div>
          <div class="stat-label">Admins</div>
        </div>
      </n-gi>
      <n-gi>
        <div class="stat-card">
          <div class="stat-value">23</div>
          <div class="stat-label">Active Today</div>
        </div>
      </n-gi>
    </n-grid>

    <!-- Users Table -->
    <n-card :bordered="false">
      <n-data-table
        :columns="columns"
        :data="users"
        :pagination="pagination"
        :bordered="false"
      />
    </n-card>
  </div>
</template>

<script setup>
import { ref, h } from 'vue'
import { NTag, NButton, NSpace } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'

const columns = [
  { title: 'User', key: 'name' },
  { title: 'Email', key: 'email' },
  {
    title: 'Role',
    key: 'role',
    render(row) {
      const colors = { admin: 'error', premium: 'warning', user: 'default' }
      return h(NTag, { type: colors[row.role], size: 'small' }, { default: () => row.role })
    }
  },
  {
    title: 'Status',
    key: 'status',
    render(row) {
      return h(NTag, { type: row.status === 'active' ? 'success' : 'default', size: 'small' }, { default: () => row.status })
    }
  },
  { title: 'Last Login', key: 'lastLogin' },
  {
    title: 'Actions',
    key: 'actions',
    render(row) {
      return h(NSpace, {}, {
        default: () => [
          h(NButton, { size: 'small', quaternary: true }, { default: () => 'Edit' }),
          h(NButton, { size: 'small', quaternary: true, type: 'error' }, { default: () => 'Ban' }),
        ]
      })
    }
  },
]

const users = ref([
  { id: 1, name: 'Admin User', email: 'admin@aicryptohub.io', role: 'admin', status: 'active', lastLogin: '5 mins ago' },
  { id: 2, name: 'John Doe', email: 'john@example.com', role: 'premium', status: 'active', lastLogin: '1 hour ago' },
  { id: 3, name: 'Jane Smith', email: 'jane@example.com', role: 'user', status: 'active', lastLogin: '2 days ago' },
])

const pagination = { pageSize: 10 }
</script>

<style scoped>
.users-view {
  max-width: 1200px;
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

.stat-card {
  background: #111827;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
}

.stat-label {
  font-size: 14px;
  color: #9ca3af;
  margin-top: 4px;
}
</style>
