<template>
  <div class="mobile-portfolio">
    <!-- Header -->
    <section class="m-section">
      <div class="m-section-header">
        <h3 class="m-section-title">💼 Portfolio</h3>
        <button class="m-btn-small" @click="openAddModal">+ Add</button>
      </div>
    </section>

    <!-- Error Message -->
    <div v-if="error" class="m-error-card">
      <p>{{ error }}</p>
    </div>

    <!-- Summary Stats -->
    <section class="m-section">
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
          <div v-if="bestPerformer" class="m-stat-card">
            <span class="m-stat-icon">🏆</span>
            <span class="m-stat-label">Best</span>
            <span class="m-stat-value m-text-success">{{ bestPerformer.symbol }}</span>
          </div>
          <div v-if="worstPerformer" class="m-stat-card">
            <span class="m-stat-icon">📉</span>
            <span class="m-stat-label">Worst</span>
            <span class="m-stat-value m-text-danger">{{ worstPerformer.symbol }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Holdings List -->
    <section class="m-section">
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
            <span class="m-info-subtitle">{{ h.amount.toLocaleString() }} {{ h.symbol }}</span>
          </div>
          <div class="m-price-col">
            <span class="m-info-title">${{ formatPrice(h.currentValue) }}</span>
            <span class="m-info-subtitle" :class="h.pnl >= 0 ? 'm-text-success' : 'm-text-danger'">
              {{ h.pnl >= 0 ? '+' : '' }}${{ formatPrice(h.pnl) }}
            </span>
          </div>
          <div class="m-actions">
            <button class="m-action-btn" @click="openEditModal(h)">✏️</button>
            <button class="m-action-btn" @click="removeHolding(h.coin_id)">🗑️</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="m-modal-overlay" @click.self="closeModal">
      <div class="m-modal">
        <div class="m-modal-header">
          <h3>{{ editingHolding ? 'Edit Holding' : 'Add Holding' }}</h3>
          <button class="m-modal-close" @click="closeModal">×</button>
        </div>
        <div class="m-modal-body">
          <div class="m-form-group">
            <label>Coin</label>
            <select v-model="newHolding.coin_id" class="m-select" :disabled="!!editingHolding">
              <option value="">-- Select --</option>
              <option v-for="coin in availableCoins" :key="coin.coin_id" :value="coin.coin_id">
                {{ coin.name }} ({{ coin.symbol }})
              </option>
            </select>
          </div>
          <div class="m-form-group">
            <label>Amount</label>
            <input v-model.number="newHolding.amount" type="number" step="any" class="m-input" />
          </div>
          <div class="m-form-group">
            <label>Buy Price (USD)</label>
            <input v-model.number="newHolding.buy_price" type="number" step="any" class="m-input" />
          </div>
        </div>
        <div class="m-modal-footer">
          <button class="m-btn" @click="closeModal">Cancel</button>
          <button class="m-btn-primary" @click="saveHolding">
            {{ editingHolding ? 'Update' : 'Add' }}
          </button>
        </div>
      </div>
    </div>
    
    <div class="m-bottom-spacer"></div>
  </div>
</template>

<script setup lang="ts">
const error = ref('')
const showModal = ref(false)
const editingHolding = ref<any>(null)
const newHolding = ref({ coin_id: '', amount: 0, buy_price: 0 })

// Mock data
const holdings = ref([
  { coin_id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png', amount: 0.5, buy_price: 45000, currentValue: 49250, pnl: 4250 },
  { coin_id: 'ethereum', symbol: 'ETH', name: 'Ethereum', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png', amount: 5, buy_price: 2800, currentValue: 17250, pnl: 3250 },
  { coin_id: 'solana', symbol: 'SOL', name: 'Solana', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png', amount: 50, buy_price: 100, currentValue: 9250, pnl: 4250 },
])

const availableCoins = ref([
  { coin_id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin' },
  { coin_id: 'ethereum', symbol: 'ETH', name: 'Ethereum' },
  { coin_id: 'solana', symbol: 'SOL', name: 'Solana' },
  { coin_id: 'cardano', symbol: 'ADA', name: 'Cardano' },
])

const totalValue = computed(() => holdings.value.reduce((sum, h) => sum + h.currentValue, 0))
const totalPnL = computed(() => holdings.value.reduce((sum, h) => sum + h.pnl, 0))

const bestPerformer = computed(() => {
  if (holdings.value.length === 0) return null
  return holdings.value.reduce((best, h) => h.pnl > best.pnl ? h : best)
})

const worstPerformer = computed(() => {
  if (holdings.value.length === 0) return null
  return holdings.value.reduce((worst, h) => h.pnl < worst.pnl ? h : worst)
})

const openAddModal = () => {
  editingHolding.value = null
  newHolding.value = { coin_id: '', amount: 0, buy_price: 0 }
  showModal.value = true
}

const openEditModal = (holding: any) => {
  editingHolding.value = holding
  newHolding.value = { ...holding }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingHolding.value = null
}

const saveHolding = () => {
  console.log('Save holding:', newHolding.value)
  closeModal()
}

const removeHolding = (coinId: string) => {
  holdings.value = holdings.value.filter(h => h.coin_id !== coinId)
}

const formatPrice = (price: number) => {
  return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
</script>

<style scoped>
.mobile-portfolio {
  padding: 0;
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
  margin-bottom: 16px;
  color: #f85149;
}

.m-stat-card {
  flex: 0 0 auto;
  min-width: 110px;
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
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
}

.m-empty-state {
  text-align: center;
  padding: 40px 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
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

.m-actions {
  display: flex;
  gap: 6px;
}

.m-action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

/* Modal */
.m-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 16px;
}

.m-modal {
  width: 100%;
  max-width: 400px;
  background: #141c2b;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
}

.m-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
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
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: #ffffff;
  font-size: 20px;
  cursor: pointer;
}

.m-modal-body {
  padding: 16px;
}

.m-form-group {
  margin-bottom: 16px;
}

.m-form-group label {
  display: block;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 6px;
}

.m-select,
.m-input {
  width: 100%;
  padding: 12px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #ffffff;
  font-size: 14px;
}

.m-select:focus,
.m-input:focus {
  outline: none;
  border-color: #38efeb;
}

.m-modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
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
}

.m-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.m-btn-primary {
  background: linear-gradient(135deg, #38efeb, #0066ff);
  color: #000;
}
</style>
