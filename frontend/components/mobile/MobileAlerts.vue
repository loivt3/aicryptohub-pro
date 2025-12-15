<template>
  <div class="mobile-alerts">
    <!-- Header -->
    <section class="m-section">
      <div class="m-section-header">
        <h3 class="m-section-title">🔔 Alerts</h3>
        <button class="m-btn-small" @click="openAddAlert">+ New Alert</button>
      </div>
    </section>

    <!-- Active Alerts -->
    <section class="m-section">
      <h3 class="m-section-title">Active ({{ activeAlerts.length }})</h3>
      
      <div v-if="activeAlerts.length === 0" class="m-empty-state">
        <span class="m-empty-icon">🔔</span>
        <p class="m-empty-text">No active alerts</p>
        <button class="m-btn-primary" @click="openAddAlert">Create Alert</button>
      </div>

      <div v-else class="m-list">
        <div v-for="alert in activeAlerts" :key="alert.id" class="m-list-item">
          <img :src="alert.image" class="m-avatar" />
          <div class="m-info">
            <span class="m-info-title">{{ alert.symbol }}</span>
            <span class="m-info-subtitle">
              {{ alert.condition === 'above' ? '↑' : '↓' }} ${{ alert.target_price.toLocaleString() }}
            </span>
          </div>
          <div class="m-price-col">
            <span class="m-info-title">${{ alert.current_price.toLocaleString() }}</span>
            <span class="m-info-subtitle m-text-muted">
              {{ ((alert.target_price - alert.current_price) / alert.current_price * 100).toFixed(1) }}% away
            </span>
          </div>
          <button class="m-action-btn" @click="removeAlert(alert.id)">🗑️</button>
        </div>
      </div>
    </section>

    <!-- Triggered Alerts -->
    <section v-if="triggeredAlerts.length > 0" class="m-section">
      <h3 class="m-section-title">Triggered ({{ triggeredAlerts.length }})</h3>
      
      <div class="m-list">
        <div v-for="alert in triggeredAlerts" :key="alert.id" class="m-list-item m-list-item--triggered">
          <img :src="alert.image" class="m-avatar" />
          <div class="m-info">
            <span class="m-info-title">{{ alert.symbol }}</span>
            <span class="m-info-subtitle m-text-success">✓ Triggered</span>
          </div>
          <div class="m-price-col">
            <span class="m-info-title">${{ alert.target_price.toLocaleString() }}</span>
            <span class="m-info-subtitle m-text-muted">{{ alert.triggered_at }}</span>
          </div>
          <button class="m-action-btn" @click="dismissAlert(alert.id)">×</button>
        </div>
      </div>
    </section>
    
    <div class="m-bottom-spacer"></div>
  </div>
</template>

<script setup lang="ts">
// Mock data
const activeAlerts = ref([
  { id: 1, symbol: 'BTC', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png', condition: 'above', target_price: 100000, current_price: 98500 },
  { id: 2, symbol: 'ETH', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png', condition: 'below', target_price: 3000, current_price: 3450 },
])

const triggeredAlerts = ref([
  { id: 3, symbol: 'SOL', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png', target_price: 180, triggered_at: '2 hours ago' },
])

const openAddAlert = () => {
  console.log('Open add alert modal')
}

const removeAlert = (id: number) => {
  activeAlerts.value = activeAlerts.value.filter(a => a.id !== id)
}

const dismissAlert = (id: number) => {
  triggeredAlerts.value = triggeredAlerts.value.filter(a => a.id !== id)
}
</script>

<style scoped>
.mobile-alerts {
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

.m-btn-primary {
  padding: 12px 24px;
  background: linear-gradient(135deg, #38efeb, #0066ff);
  border: none;
  border-radius: 8px;
  color: #000;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.m-list-item--triggered {
  background: rgba(34, 197, 94, 0.05);
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
</style>
