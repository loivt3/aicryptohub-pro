<template>
  <div class="users-view">
    <div class="section-header">
      <h2 class="section-title">👥 Users & Roles</h2>
      <n-button type="primary" @click="showAddModal = true">
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
          <div class="stat-value">{{ stats.total_users || 0 }}</div>
          <div class="stat-label">Total Users</div>
        </div>
      </n-gi>
      <n-gi>
        <div class="stat-card">
          <div class="stat-value">{{ stats.premium_users || 0 }}</div>
          <div class="stat-label">Premium</div>
        </div>
      </n-gi>
      <n-gi>
        <div class="stat-card">
          <div class="stat-value">{{ stats.admin_users || 0 }}</div>
          <div class="stat-label">Admins</div>
        </div>
      </n-gi>
      <n-gi>
        <div class="stat-card">
          <div class="stat-value">{{ stats.active_today || 0 }}</div>
          <div class="stat-label">Active Today</div>
        </div>
      </n-gi>
    </n-grid>

    <!-- Filters -->
    <n-card :bordered="false" style="margin-bottom: 16px">
      <n-space>
        <n-input v-model:value="searchQuery" placeholder="Search users..." style="width: 200px" @update:value="debouncedFetch" />
        <n-select v-model:value="roleFilter" :options="roleOptions" placeholder="Filter by role" clearable style="width: 150px" @update:value="fetchUsers" />
      </n-space>
    </n-card>

    <!-- Users Table -->
    <n-card :bordered="false">
      <n-data-table
        :columns="columns"
        :data="users"
        :loading="loading"
        :pagination="pagination"
        :bordered="false"
      />
    </n-card>

    <!-- Add User Modal -->
    <n-modal v-model:show="showAddModal" preset="card" title="Add New User" style="width: 500px">
      <n-form ref="addFormRef" :model="newUser" :rules="formRules">
        <n-form-item label="Name" path="name">
          <n-input v-model:value="newUser.name" placeholder="Enter name" />
        </n-form-item>
        <n-form-item label="Email" path="email">
          <n-input v-model:value="newUser.email" placeholder="Enter email" />
        </n-form-item>
        <n-form-item label="Password" path="password">
          <n-input v-model:value="newUser.password" type="password" placeholder="Enter password" />
        </n-form-item>
        <n-form-item label="Role" path="role">
          <n-select v-model:value="newUser.role" :options="roleOptions" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showAddModal = false">Cancel</n-button>
          <n-button type="primary" :loading="saving" @click="createUser">Create User</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- Edit User Modal -->
    <n-modal v-model:show="showEditModal" preset="card" title="Edit User" style="width: 500px">
      <n-form ref="editFormRef" :model="editingUser">
        <n-form-item label="Name">
          <n-input v-model:value="editingUser.name" />
        </n-form-item>
        <n-form-item label="Email">
          <n-input :value="editingUser.email" disabled />
        </n-form-item>
        <n-form-item label="Role">
          <n-select v-model:value="editingUser.role" :options="roleOptions" />
        </n-form-item>
        <n-form-item label="Status">
          <n-switch v-model:value="editingUser.is_active">
            <template #checked>Active</template>
            <template #unchecked>Banned</template>
          </n-switch>
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showEditModal = false">Cancel</n-button>
          <n-button type="primary" :loading="saving" @click="updateUser">Save Changes</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, h, onMounted } from 'vue'
import { NTag, NButton, NSpace, NSwitch, useMessage, useDialog } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import axios from 'axios'

const API_BASE = '/api/v1'
const message = useMessage()
const dialog = useDialog()

// State
const users = ref([])
const stats = ref({})
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const roleFilter = ref(null)
const showAddModal = ref(false)
const showEditModal = ref(false)
const editingUser = ref({})
const newUser = ref({ name: '', email: '', password: '', role: 'user' })

// Pagination
const pagination = ref({
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 25, 50]
})

// Role options
const roleOptions = [
  { label: 'Admin', value: 'admin' },
  { label: 'Premium', value: 'premium' },
  { label: 'User', value: 'user' },
]

// Form rules
const formRules = {
  name: { required: true, message: 'Name is required' },
  email: { required: true, message: 'Email is required', type: 'email' },
  password: { required: true, message: 'Password is required', min: 6 },
  role: { required: true, message: 'Role is required' },
}

// Columns
const columns = [
  { title: 'User', key: 'name', render: (row) => h('div', {}, [
    h('div', { style: { fontWeight: 600 } }, row.name),
    h('div', { style: { fontSize: '12px', color: '#9ca3af' } }, row.email),
  ])},
  {
    title: 'Role',
    key: 'role',
    width: 100,
    render(row) {
      const colors = { admin: 'error', premium: 'warning', user: 'default' }
      return h(NTag, { type: colors[row.role], size: 'small' }, { default: () => row.role })
    }
  },
  {
    title: 'Status',
    key: 'is_active',
    width: 100,
    render(row) {
      return h(NTag, { type: row.is_active ? 'success' : 'error', size: 'small' }, 
        { default: () => row.is_active ? 'Active' : 'Banned' })
    }
  },
  { title: 'Last Login', key: 'last_login', width: 150, render: (row) => formatTimeAgo(row.last_login) },
  {
    title: 'Actions',
    key: 'actions',
    width: 150,
    render(row) {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(NButton, { size: 'small', quaternary: true, onClick: () => openEditModal(row) }, { default: () => 'Edit' }),
          row.is_active 
            ? h(NButton, { size: 'small', quaternary: true, type: 'error', onClick: () => banUser(row) }, { default: () => 'Ban' })
            : h(NButton, { size: 'small', quaternary: true, type: 'success', onClick: () => unbanUser(row) }, { default: () => 'Unban' }),
        ]
      })
    }
  },
]

// Methods
function formatTimeAgo(timestamp) {
  if (!timestamp) return 'Never'
  const date = new Date(timestamp)
  const diff = Math.floor((Date.now() - date) / 1000)
  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

async function fetchUsers() {
  loading.value = true
  try {
    const params = { limit: 50 }
    if (roleFilter.value) params.role = roleFilter.value
    if (searchQuery.value) params.search = searchQuery.value
    
    const response = await axios.get(`${API_BASE}/admin/users`, { params })
    users.value = response.data.users || []
    stats.value = response.data.stats || {}
  } catch (error) {
    console.error('Failed to fetch users:', error)
    message.error('Failed to load users')
  } finally {
    loading.value = false
  }
}

let debounceTimer = null
function debouncedFetch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(fetchUsers, 300)
}

async function createUser() {
  saving.value = true
  try {
    await axios.post(`${API_BASE}/admin/users`, newUser.value)
    message.success('User created successfully')
    showAddModal.value = false
    newUser.value = { name: '', email: '', password: '', role: 'user' }
    fetchUsers()
  } catch (error) {
    message.error(error.response?.data?.detail || 'Failed to create user')
  } finally {
    saving.value = false
  }
}

function openEditModal(user) {
  editingUser.value = { ...user }
  showEditModal.value = true
}

async function updateUser() {
  saving.value = true
  try {
    await axios.put(`${API_BASE}/admin/users/${editingUser.value.id}`, {
      name: editingUser.value.name,
      role: editingUser.value.role,
      is_active: editingUser.value.is_active,
    })
    message.success('User updated successfully')
    showEditModal.value = false
    fetchUsers()
  } catch (error) {
    message.error('Failed to update user')
  } finally {
    saving.value = false
  }
}

async function banUser(user) {
  dialog.warning({
    title: 'Ban User',
    content: `Are you sure you want to ban ${user.name}?`,
    positiveText: 'Ban',
    negativeText: 'Cancel',
    onPositiveClick: async () => {
      try {
        await axios.post(`${API_BASE}/admin/users/${user.id}/ban`)
        message.success(`${user.name} has been banned`)
        fetchUsers()
      } catch (error) {
        message.error('Failed to ban user')
      }
    }
  })
}

async function unbanUser(user) {
  try {
    await axios.put(`${API_BASE}/admin/users/${user.id}`, { is_active: true })
    message.success(`${user.name} has been unbanned`)
    fetchUsers()
  } catch (error) {
    message.error('Failed to unban user')
  }
}

onMounted(() => {
  fetchUsers()
})
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
  margin: 0;
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
  color: #f9fafb;
}

.stat-label {
  font-size: 14px;
  color: #9ca3af;
  margin-top: 4px;
}
</style>
