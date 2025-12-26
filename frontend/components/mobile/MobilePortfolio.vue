<template>
  <div class="mobile-portfolio">
    <!-- Header -->
    <SharedMobileHeader 
      title="Portfolio" 
      icon="ph:wallet" 
      @openSearch="$emit('openSearch')" 
    />
    
    <main class="portfolio-main">
    <!-- Section Header (inside page) -->
    <section class="m-section">
      <div class="m-section-header">
        <h3 class="m-section-title">💼 Portfolio</h3>
        <button v-if="isAuthenticated" class="m-btn-small" @click="openAddModal">+ Add</button>
      </div>
    </section>

    <!-- Login Required State -->
    <div v-if="!isAuthenticated" class="m-empty-state">
      <span class="m-empty-icon">🔒</span>
      <p class="m-empty-text">Please log in to view your portfolio.</p>
      <NuxtLink to="/login" class="m-btn-primary" style="display:inline-block; text-decoration:none;">Log In</NuxtLink>
    </div>

    <template v-else>
      <!-- Error Message -->
      <div v-if="error" class="m-error-card">
        <p>{{ error }}</p>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="m-loading-state">
        <div class="m-spinner"></div>
        <p>Loading portfolio...</p>
      </div>

      <!-- Summary Stats -->
      <section v-else class="m-section">
        <div class="m-stats-scroll">
          <div class="m-stats-container">
            <div class="m-stat-card">
              <span class="m-stat-icon">💰</span>
              <span class="m-stat-label">Total Value</span>
              <span class="m-stat-value">${{ formatPrice(totalValue) }}</span>
            </div>
            <div class="m-stat-card">
              <span class="m-stat-icon">📊</span>
              <span class="m-stat-label">P&L</span>
              <span class="m-stat-value" :class="totalPnL >= 0 ? 'm-text-success' : 'm-text-danger'">
                {{ totalPnL >= 0 ? '+' : '' }}${{ formatPrice(totalPnL) }}
              </span>
            </div>
            <div class="m-stat-card">
              <span class="m-stat-icon">📈</span>
              <span class="m-stat-label">P&L %</span>
              <span class="m-stat-value" :class="totalPnLPercent >= 0 ? 'm-text-success' : 'm-text-danger'">
                {{ totalPnLPercent >= 0 ? '+' : '' }}{{ formatNumber(totalPnLPercent) }}%
              </span>
            </div>
            <div v-if="bestPerformer" class="m-stat-card">
              <span class="m-stat-icon">🏆</span>
              <span class="m-stat-label">Best</span>
              <span class="m-stat-value m-text-success">{{ bestPerformer.symbol }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- AI Hedge Fund Tools -->
      <PortfolioAuditor v-if="!isLoading && holdings.length > 0" :refresh-trigger="refreshTrigger" />
      <StressSimulator v-if="!isLoading && holdings.length > 0" :refresh-trigger="refreshTrigger" />

      <!-- Holdings List -->
      <section v-if="!isLoading" class="m-section">
        <h3 class="m-section-title">Holdings ({{ holdings.length }})</h3>
        
        <div v-if="holdings.length === 0" class="m-empty-state">
          <span class="m-empty-icon">💼</span>
          <p class="m-empty-text">No holdings yet</p>
          <button class="m-btn-primary" @click="openAddModal">Add First Holding</button>
        </div>

        <div v-else class="m-list">
          <div v-for="h in holdings" :key="h.coin_id" class="m-list-item">
            <img v-if="h.image" :src="h.image" class="m-avatar" />
            <div class="m-info">
              <span class="m-info-title">{{ h.symbol }}</span>
              <span class="m-info-subtitle">{{ formatNumber(h.amount) }} {{ h.symbol }}</span>
            </div>
            <div class="m-price-col">
              <span class="m-info-title">${{ formatPrice(h.value || 0) }}</span>
              <span class="m-info-subtitle" :class="(h.pnl || 0) >= 0 ? 'm-text-success' : 'm-text-danger'">
                {{ (h.pnl || 0) >= 0 ? '+' : '' }}${{ formatPrice(h.pnl || 0) }}
              </span>
            </div>
            <div class="m-actions">
              <button class="m-action-btn" @click="openEditModal(h)">✏️</button>
              <button class="m-action-btn" @click="confirmRemove(h)">🗑️</button>
            </div>
          </div>
        </div>
      </section>
    </template>

    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="m-modal-overlay" @click.self="closeModal">
      <!-- ... (modal content unchanged) ... -->
      <div class="m-modal">
        <div class="m-modal-header">
          <h3>{{ editingHolding ? 'Edit Holding' : 'Add Holding' }}</h3>
          <button class="m-modal-close" @click="closeModal">×</button>
        </div>
        <div class="m-modal-body">
          <div class="m-form-group">
            <label>Coin</label>
            <select v-model="newHolding.coin_id" class="m-select" :disabled="!!editingHolding">
              <option value="">-- Select Coin --</option>
              <option v-for="coin in availableCoins" :key="coin.id" :value="coin.id">
                {{ coin.name }} ({{ coin.symbol.toUpperCase() }}) - ${{ formatPrice(coin.current_price) }}
              </option>
            </select>
          </div>
          
          <div v-if="selectedCoinPrice" class="m-price-info">
            Current Price: ${{ formatPrice(selectedCoinPrice) }}
          </div>

          <div class="m-form-group">
            <label>Amount</label>
            <input v-model.number="newHolding.amount" type="number" step="any" placeholder="0.00" class="m-input" />
          </div>
          <div class="m-form-group">
            <label>Average Buy Price (USD)</label>
            <input v-model.number="newHolding.buy_price" type="number" step="any" placeholder="0.00" class="m-input" />
          </div>
          
          <div v-if="newHolding.amount && newHolding.buy_price" class="m-calc-info">
            Total Cost: ${{ formatPrice(newHolding.amount * newHolding.buy_price) }}
          </div>
        </div>
        <div class="m-modal-footer">
          <button class="m-btn" @click="closeModal">Cancel</button>
          <button class="m-btn-primary" @click="saveHolding" :disabled="isSaving || !isValidForm">
            {{ isSaving ? 'Saving...' : (editingHolding ? 'Update' : 'Add') }}
          </button>
        </div>
      </div>
    </div>
    
    </main>
    
    <!-- Bottom Navigation -->
    <SharedMobileFooter :activeTab="activeTab" @setTab="$emit('setTab', $event)" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '~/composables/useApi'
import { useAuthStore } from '~/stores/auth'
import PortfolioAuditor from './ai/PortfolioAuditor.vue'
import StressSimulator from './ai/StressSimulator.vue'

// Props & Emits
const props = defineProps<{
  activeTab?: string
}>()

const emit = defineEmits(['setTab', 'openSearch'])

const api = useApi()
const authStore = useAuthStore() // Use auto-import
const error = ref('')
const isLoading = ref(true)
const isSaving = ref(false)
const showModal = ref(false)
const editingHolding = ref<any>(null)
const newHolding = ref({ coin_id: '', amount: 0, buy_price: 0 })
const holdings = ref<any[]>([])
const availableCoins = ref<any[]>([])
const refreshTrigger = ref(0) // Trigger for child components to refresh

// Computed
const isAuthenticated = computed(() => authStore.isAuthenticated)

const totalValue = computed(() => holdings.value.reduce((sum, h) => sum + (h.value || 0), 0))
const totalInvested = computed(() => holdings.value.reduce((sum, h) => sum + (h.amount * h.buy_price), 0))
const totalPnL = computed(() => totalValue.value - totalInvested.value)
const totalPnLPercent = computed(() => totalInvested.value > 0 ? (totalPnL.value / totalInvested.value) * 100 : 0)

const bestPerformer = computed(() => {
  if (holdings.value.length === 0) return null
  return holdings.value.reduce((best, h) => (h.pnl_percent || 0) > (best.pnl_percent || 0) ? h : best, holdings.value[0])
})

const isValidForm = computed(() => {
  return newHolding.value.coin_id && newHolding.value.amount > 0 && newHolding.value.buy_price > 0
})

const selectedCoinPrice = computed(() => {
  if (!newHolding.value.coin_id) return null
  const coin = availableCoins.value.find(c => c.id === newHolding.value.coin_id)
  return coin ? coin.current_price : null
})

// Lifecycle
onMounted(async () => {
  // Initialize auth state from localStorage
  authStore.initAuth()

  // Small delay to ensure state is hydrated
  await new Promise(r => setTimeout(r, 100))

  if (authStore.isAuthenticated) {
    await Promise.all([
      fetchPortfolio(),
      fetchMarketData()
    ])
  } else {
    // Not authenticated - stop loading immediately
    isLoading.value = false
  }
})

// Methods
const fetchPortfolio = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const data = await api.getPortfolio()
    if (data) {
      holdings.value = data
    }
  } catch (err: any) {
    console.error('Failed to fetch portfolio', err)
    // Check if 401 unauthorized
    if (err?.statusCode === 401 || err?.status === 401) {
      error.value = ''
      // Token invalid, clear it
      authStore.logout()
    } else {
      error.value = 'Failed to load portfolio. Please try again.'
    }
  } finally {
    isLoading.value = false
  }
}

const fetchMarketData = async () => {
  try {
    const res = await api.getMarketData(250) // Get top 250 coins for selection
    if (res.success) {
      availableCoins.value = res.data
    }
  } catch (err) {
    console.error('Failed to fetch market data', err)
  }
}

const openAddModal = () => {
  editingHolding.value = null
  newHolding.value = { coin_id: '', amount: 0, buy_price: 0 }
  showModal.value = true
}

// Watch for coin selection to auto-fill current price if adding new
watch(() => newHolding.value.coin_id, (newId) => {
  if (newId && !editingHolding.value && !newHolding.value.buy_price) {
    const coin = availableCoins.value.find(c => c.id === newId)
    if (coin) {
      newHolding.value.buy_price = coin.current_price
    }
  }
})

const openEditModal = (holding: any) => {
  editingHolding.value = holding
  newHolding.value = { 
    coin_id: holding.coin_id, 
    amount: holding.amount, 
    buy_price: holding.buy_price 
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingHolding.value = null
  error.value = ''
}

const saveHolding = async () => {
  if (!isValidForm.value) return
  
  isSaving.value = true
  error.value = ''
  
  try {
    if (editingHolding.value) {
      // Update
      await api.updateHolding(newHolding.value.coin_id, {
        amount: newHolding.value.amount,
        buy_price: newHolding.value.buy_price
      })
    } else {
      // Add
      await api.addHolding({
        coin_id: newHolding.value.coin_id,
        amount: newHolding.value.amount,
        buy_price: newHolding.value.buy_price
      })
    }
    
    await fetchPortfolio()
    refreshTrigger.value++ // Trigger UI update for AI tools
    closeModal()
  } catch (err: any) {
    console.error('Failed to save holding', err)
    error.value = 'Failed to save holding. Please check values.'
  } finally {
    isSaving.value = false
  }
}

const confirmRemove = async (holding: any) => {
  if (confirm(`Are you sure you want to remove ${holding.symbol} from your portfolio?`)) {
    await removeHolding(holding.coin_id)
  }
}

const removeHolding = async (coinId: string) => {
  try {
    await api.deleteHolding(coinId)
    holdings.value = holdings.value.filter(h => h.coin_id !== coinId)
    refreshTrigger.value++ // Trigger UI update for AI tools
  } catch (err) {
    console.error('Failed to delete holding', err)
    error.value = 'Failed to delete holding.'
  }
}

const formatPrice = (price: number) => {
  if (price === 0) return '0.00'
  if (price < 0.01) return new Intl.NumberFormat('en-US', { minimumFractionDigits: 6, maximumFractionDigits: 6 }).format(price)
  if (price < 1) return new Intl.NumberFormat('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 4 }).format(price)
  return new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(price)
}

const formatNumber = (num: number) => {
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(num)
}
</script>

<style scoped>
.mobile-portfolio {
  padding: 0;
  padding-bottom: 80px;
}

.m-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 0 16px;
}

.m-section-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.m-btn-small {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.m-error-card {
  background: rgba(248, 81, 73, 0.1);
  border: 1px solid rgba(248, 81, 73, 0.3);
  border-radius: 12px;
  padding: 12px;
  margin: 0 16px 16px;
  color: #f85149;
  font-size: 13px;
  text-align: center;
}

.m-loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.5);
}

.m-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #38efeb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.m-stats-scroll {
  overflow-x: auto;
  padding: 0 16px;
  margin-bottom: 24px;
}

.m-stats-container {
  display: flex;
  gap: 12px;
  padding-bottom: 4px; /* Space for scrollbar if any */
}

.m-stat-card {
  flex: 0 0 auto;
  min-width: 100px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px;
  text-align: center;
}

.m-stat-icon {
  font-size: 20px;
  display: block;
  margin-bottom: 4px;
}

.m-stat-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  display: block;
  margin-bottom: 4px;
}

.m-stat-value {
  font-size: 15px;
  font-weight: 700;
  color: #ffffff;
}

.m-text-success { color: #4ade80; }
.m-text-danger { color: #f87171; }

.m-empty-state {
  text-align: center;
  padding: 40px 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  margin: 0 16px;
}

.m-empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.m-empty-text {
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 16px;
}

.m-list {
  padding: 0 16px;
}

.m-list-item {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 8px;
}

.m-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin-right: 12px;
}

.m-info {
  flex: 1;
}

.m-info-title {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.m-info-subtitle {
  display: block;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.m-price-col {
  text-align: right;
  margin-right: 12px;
}

.m-actions {
  display: flex;
  gap: 6px;
}

.m-action-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.m-action-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* Modal */
.m-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85); /* Slightly darker overlay */
  backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-end; /* Bottom sheet on mobile? Or center */
  justify-content: center;
  z-index: 9999;
  padding: 16px;
}

@media (min-width: 640px) {
  .m-modal-overlay {
    align-items: center;
  }
}

.m-modal {
  width: 100%;
  max-width: 400px;
  background: #1e293b; /* Dark slate */
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
}

.m-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.m-modal-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.m-modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #94a3b8;
  font-size: 24px;
  cursor: pointer;
}

.m-modal-body {
  padding: 20px;
}

.m-form-group {
  margin-bottom: 16px;
}

.m-form-group label {
  display: block;
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 8px;
  font-weight: 500;
}

.m-select,
.m-input {
  width: 100%;
  padding: 12px;
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #ffffff;
  font-size: 15px;
  transition: border-color 0.2s;
}

.m-select:focus,
.m-input:focus {
  outline: none;
  border-color: #38efeb;
  background: #0f172a;
}

.m-price-info {
  font-size: 12px;
  color: #38efeb;
  margin-top: -10px;
  margin-bottom: 16px;
  text-align: right;
}

.m-calc-info {
  font-size: 13px;
  color: #94a3b8;
  text-align: right;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed rgba(255, 255, 255, 0.1);
}

.m-modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
}

.m-btn,
.m-btn-primary {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.m-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.m-btn-primary {
  background: linear-gradient(135deg, #38efeb, #0066ff);
  color: #ffffff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.m-btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  filter: grayscale(0.5);
}

.m-bottom-spacer {
  height: 20px;
}
</style>
