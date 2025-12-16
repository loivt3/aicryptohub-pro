<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="logo">🚀</div>
        <h1>Admin Console</h1>
        <p>AI Crypto Hub</p>
      </div>

      <n-form ref="formRef" :model="form" :rules="rules">
        <n-form-item path="email" label="Email">
          <n-input v-model:value="form.email" placeholder="admin@aicryptohub.io" />
        </n-form-item>
        <n-form-item path="password" label="Password">
          <n-input v-model:value="form.password" type="password" placeholder="Password" show-password-on="click" />
        </n-form-item>
        <n-form-item>
          <n-button type="primary" block :loading="loading" @click="handleLogin">
            Login
          </n-button>
        </n-form-item>
      </n-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'

const router = useRouter()
const message = useMessage()

const formRef = ref(null)
const loading = ref(false)
const form = ref({
  email: '',
  password: '',
})

const rules = {
  email: { required: true, message: 'Email required', trigger: 'blur' },
  password: { required: true, message: 'Password required', trigger: 'blur' },
}

async function handleLogin() {
  try {
    await formRef.value?.validate()
    loading.value = true

    // TODO: Call login API
    // For now, just set a dummy token
    localStorage.setItem('admin_token', 'demo_token')
    
    message.success('Login successful')
    router.push({ name: 'dashboard' })
  } catch (error) {
    message.error('Login failed')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0a0f1a 0%, #1a1f2e 100%);
}

.login-card {
  width: 400px;
  background: #111827;
  border-radius: 16px;
  padding: 40px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  font-size: 48px;
  margin-bottom: 16px;
}

.login-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: #f9fafb;
  margin: 0;
}

.login-header p {
  color: #9ca3af;
  margin: 8px 0 0;
}
</style>
