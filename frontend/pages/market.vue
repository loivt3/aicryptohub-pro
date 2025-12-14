<template>
  <div class="py-12">
    <div class="max-w-7xl mx-auto px-4">
      <h1 class="text-3xl font-bold mb-8">Market Overview</h1>
      
      <!-- Search & Filters -->
      <div class="flex flex-col md:flex-row gap-4 mb-6">
        <div class="flex-1 relative">
          <Icon name="ph:magnifying-glass" class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input 
            v-model="searchQuery"
            type="text" 
            placeholder="Search coins..."
            class="w-full pl-10 pr-4 py-3 bg-dark-800 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-primary/50"
          />
        </div>
        <select 
          v-model="sortBy"
          class="px-4 py-3 bg-dark-800 border border-white/10 rounded-xl text-white focus:outline-none"
        >
          <option value="market_cap">Market Cap</option>
          <option value="price">Price</option>
          <option value="change_24h">24h Change</option>
          <option value="volume">Volume</option>
        </select>
      </div>
      
      <!-- Coins Grid -->
      <div class="grid gap-4">
        <div 
          v-for="coin in filteredCoins" 
          :key="coin.id"
          class="glass-card p-4 flex items-center gap-4 hover:bg-white/5 transition-colors cursor-pointer"
          @click="navigateTo(`/coin/${coin.id}`)"
        >
          <span class="text-gray-500 w-8 text-center">{{ coin.rank }}</span>
          <img :src="coin.image" :alt="coin.name" class="w-10 h-10 rounded-full" />
          <div class="flex-1">
            <p class="font-medium">{{ coin.name }}</p>
            <p class="text-sm text-gray-400">{{ coin.symbol }}</p>
          </div>
          <div class="text-right">
            <p class="font-mono">${{ formatPrice(coin.price) }}</p>
            <p :class="coin.change24h >= 0 ? 'price-up' : 'price-down'" class="text-sm">
              {{ coin.change24h >= 0 ? '+' : '' }}{{ coin.change24h.toFixed(2) }}%
            </p>
          </div>
          <div class="hidden md:block text-right w-32">
            <p class="text-gray-400 text-sm">Market Cap</p>
            <p>${{ formatMarketCap(coin.marketCap) }}</p>
          </div>
          <span 
            class="px-3 py-1 text-xs font-medium rounded-full hidden md:inline-block"
            :class="`signal-${coin.signal.toLowerCase()}`"
          >
            {{ coin.signal }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  title: 'Market',
})

useSeoMeta({
  title: 'Cryptocurrency Market - AI Crypto Hub',
  description: 'Browse all cryptocurrencies with real-time prices, market data, and AI-powered trading signals.',
})

const searchQuery = ref('')
const sortBy = ref('market_cap')

// Mock data
const coins = ref([
  { id: 'bitcoin', rank: 1, name: 'Bitcoin', symbol: 'BTC', price: 98500, change24h: 2.4, marketCap: 1900000000000, signal: 'BUY', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png' },
  { id: 'ethereum', rank: 2, name: 'Ethereum', symbol: 'ETH', price: 3450, change24h: 1.8, marketCap: 415000000000, signal: 'HOLD', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png' },
  { id: 'solana', rank: 3, name: 'Solana', symbol: 'SOL', price: 185, change24h: 5.2, marketCap: 82000000000, signal: 'BUY', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png' },
])

const filteredCoins = computed(() => {
  let result = coins.value
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(c => 
      c.name.toLowerCase().includes(query) || 
      c.symbol.toLowerCase().includes(query)
    )
  }
  return result
})

const formatPrice = (price: number) => {
  if (price >= 1) return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return price.toFixed(6)
}

const formatMarketCap = (cap: number) => {
  if (cap >= 1e12) return (cap / 1e12).toFixed(2) + 'T'
  if (cap >= 1e9) return (cap / 1e9).toFixed(2) + 'B'
  return cap.toLocaleString()
}
</script>
