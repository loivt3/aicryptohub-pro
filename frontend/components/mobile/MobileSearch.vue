<template>
  <Teleport to="body">
    <div v-if="isOpen" class="m-search-overlay" @click.self="close">
      <div class="m-search-container">
        <!-- Search Header -->
        <div class="m-search-header">
          <div class="m-search-input-wrapper">
            <Icon name="ph:magnifying-glass" class="m-search-icon" />
            <input 
              ref="searchInput"
              v-model="query"
              type="text"
              class="m-search-input"
              placeholder="Search coins..."
              @input="onSearch"
            />
            <button v-if="query" class="m-search-clear" @click="query = ''">
              <Icon name="ph:x" class="w-4 h-4" />
            </button>
          </div>
          <button class="m-search-cancel" @click="close">Cancel</button>
        </div>

        <!-- Quick Filters -->
        <div class="m-search-filters">
          <button 
            v-for="filter in filters" 
            :key="filter.id"
            class="m-filter-chip"
            :class="{ active: activeFilter === filter.id }"
            @click="activeFilter = filter.id"
          >
            {{ filter.label }}
          </button>
        </div>

        <!-- Recent Searches -->
        <div v-if="!query && recentSearches.length" class="m-search-section">
          <div class="m-search-section-header">
            <span>Recent</span>
            <button class="m-search-section-clear" @click="clearRecent">Clear</button>
          </div>
          <div class="m-search-recent">
            <button v-for="item in recentSearches" :key="item" class="m-recent-chip" @click="query = item">
              <Icon name="ph:clock-counter-clockwise" class="w-3 h-3" />
              {{ item }}
            </button>
          </div>
        </div>

        <!-- Search Results -->
        <div v-if="query" class="m-search-results">
          <div v-if="loading" class="m-search-loading">
            <div class="m-spinner"></div>
          </div>
          
          <div v-else-if="results.length === 0" class="m-search-empty">
            <span class="m-search-empty-icon">🔍</span>
            <p>No results for "{{ query }}"</p>
          </div>
          
          <div v-else class="m-result-list">
            <div v-for="coin in results" :key="coin.coin_id" class="m-result-item" @click="selectCoin(coin)">
              <img :src="coin.image" class="m-result-avatar" />
              <div class="m-result-info">
                <span class="m-result-name">{{ coin.name }}</span>
                <span class="m-result-symbol">{{ coin.symbol }}</span>
              </div>
              <div class="m-result-price">
                <span class="m-result-value">${{ formatPrice(coin.price) }}</span>
                <span class="m-result-change" :class="coin.change_24h >= 0 ? 'up' : 'down'">
                  {{ coin.change_24h >= 0 ? '+' : '' }}{{ coin.change_24h.toFixed(2) }}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Trending -->
        <div v-if="!query" class="m-search-section">
          <div class="m-search-section-header">
            <span>🔥 Trending</span>
          </div>
          <div class="m-result-list">
            <div v-for="coin in trending" :key="coin.coin_id" class="m-result-item" @click="selectCoin(coin)">
              <img :src="coin.image" class="m-result-avatar" />
              <div class="m-result-info">
                <span class="m-result-name">{{ coin.name }}</span>
                <span class="m-result-symbol">{{ coin.symbol }}</span>
              </div>
              <div class="m-result-price">
                <span class="m-result-value">${{ formatPrice(coin.price) }}</span>
                <span class="m-result-change up">+{{ coin.change_24h.toFixed(2) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits(['close', 'select'])

const searchInput = ref<HTMLInputElement | null>(null)
const query = ref('')
const loading = ref(false)
const activeFilter = ref('all')

const filters = [
  { id: 'all', label: 'All' },
  { id: 'defi', label: 'DeFi' },
  { id: 'nft', label: 'NFT' },
  { id: 'l1', label: 'Layer 1' },
  { id: 'meme', label: 'Meme' },
]

const recentSearches = ref(['Bitcoin', 'Ethereum', 'Solana'])

const trending = ref([
  { coin_id: 'solana', symbol: 'SOL', name: 'Solana', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png', price: 185, change_24h: 12.5 },
  { coin_id: 'sui', symbol: 'SUI', name: 'Sui', image: 'https://assets.coingecko.com/coins/images/26375/small/sui_asset.jpeg', price: 3.82, change_24h: 8.4 },
  { coin_id: 'render', symbol: 'RNDR', name: 'Render Token', image: 'https://assets.coingecko.com/coins/images/11636/small/rndr.png', price: 8.95, change_24h: 6.2 },
])

const results = ref<any[]>([])

// Mock search
const allCoins = [
  { coin_id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png', price: 98500, change_24h: 2.4 },
  { coin_id: 'ethereum', symbol: 'ETH', name: 'Ethereum', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png', price: 3450, change_24h: 1.8 },
  { coin_id: 'solana', symbol: 'SOL', name: 'Solana', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png', price: 185, change_24h: 5.2 },
  { coin_id: 'cardano', symbol: 'ADA', name: 'Cardano', image: 'https://assets.coingecko.com/coins/images/975/small/cardano.png', price: 1.05, change_24h: 3.1 },
  { coin_id: 'dogecoin', symbol: 'DOGE', name: 'Dogecoin', image: 'https://assets.coingecko.com/coins/images/5/small/dogecoin.png', price: 0.32, change_24h: -1.5 },
]

const onSearch = () => {
  if (!query.value) {
    results.value = []
    return
  }
  
  loading.value = true
  setTimeout(() => {
    const q = query.value.toLowerCase()
    results.value = allCoins.filter(c => 
      c.name.toLowerCase().includes(q) || 
      c.symbol.toLowerCase().includes(q)
    )
    loading.value = false
  }, 300)
}

const selectCoin = (coin: any) => {
  if (!recentSearches.value.includes(coin.name)) {
    recentSearches.value.unshift(coin.name)
    if (recentSearches.value.length > 5) recentSearches.value.pop()
  }
  emit('select', coin)
  close()
}

const clearRecent = () => {
  recentSearches.value = []
}

const close = () => {
  query.value = ''
  emit('close')
}

const formatPrice = (price: number) => {
  if (price >= 1) return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return price.toFixed(6)
}

watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    nextTick(() => {
      searchInput.value?.focus()
    })
  }
})
</script>

<style scoped>
.m-search-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #0b0f19;
  z-index: 99999;
  display: flex;
  flex-direction: column;
}

.m-search-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.m-search-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.m-search-input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.m-search-icon {
  position: absolute;
  left: 12px;
  width: 18px;
  height: 18px;
  color: rgba(255, 255, 255, 0.4);
}

.m-search-input {
  width: 100%;
  padding: 12px 40px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #ffffff;
  font-size: 16px;
}

.m-search-input:focus {
  outline: none;
  border-color: #38efeb;
}

.m-search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.m-search-clear {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
}

.m-search-cancel {
  background: none;
  border: none;
  color: #38efeb;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

/* Filters */
.m-search-filters {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  overflow-x: auto;
  scrollbar-width: none;
}

.m-search-filters::-webkit-scrollbar {
  display: none;
}

.m-filter-chip {
  flex: 0 0 auto;
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
}

.m-filter-chip.active {
  background: rgba(56, 239, 235, 0.15);
  border-color: #38efeb;
  color: #38efeb;
}

/* Sections */
.m-search-section {
  padding: 0 16px;
  margin-bottom: 16px;
}

.m-search-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
}

.m-search-section-clear {
  background: none;
  border: none;
  color: #38efeb;
  font-size: 12px;
  cursor: pointer;
}

.m-search-recent {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.m-recent-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  cursor: pointer;
}

/* Results */
.m-search-results {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px;
}

.m-search-loading,
.m-search-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.5);
}

.m-search-empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.m-result-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.m-result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.m-result-item:active {
  background: rgba(255, 255, 255, 0.08);
}

.m-result-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
}

.m-result-info {
  flex: 1;
}

.m-result-name {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  display: block;
}

.m-result-symbol {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.m-result-price {
  text-align: right;
}

.m-result-value {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  display: block;
}

.m-result-change {
  font-size: 12px;
}

.m-result-change.up { color: #22c55e; }
.m-result-change.down { color: #ef4444; }
</style>
