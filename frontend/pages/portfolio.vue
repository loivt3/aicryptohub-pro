<template>
  <div class="py-12">
    <div class="max-w-7xl mx-auto px-4">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-3xl font-bold">My Portfolio</h1>
          <p class="text-gray-400 mt-1">Track your crypto investments</p>
        </div>
        <button 
          @click="showAddModal = true"
          class="px-4 py-2 bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors flex items-center gap-2"
        >
          <Icon name="ph:plus" class="w-5 h-5" />
          Add Holding
        </button>
      </div>
      
      <!-- Summary Cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div class="glass-card p-4">
          <p class="text-sm text-gray-400 mb-1">Total Value</p>
          <p class="text-2xl font-bold">${{ formatValue(summary.total_value) }}</p>
        </div>
        <div class="glass-card p-4">
          <p class="text-sm text-gray-400 mb-1">Total Invested</p>
          <p class="text-2xl font-bold">${{ formatValue(summary.total_invested) }}</p>
        </div>
        <div class="glass-card p-4">
          <p class="text-sm text-gray-400 mb-1">Total P&L</p>
          <p class="text-2xl font-bold" :class="summary.total_pnl >= 0 ? 'price-up' : 'price-down'">
            {{ summary.total_pnl >= 0 ? '+' : '' }}${{ formatValue(summary.total_pnl) }}
          </p>
        </div>
        <div class="glass-card p-4">
          <p class="text-sm text-gray-400 mb-1">P&L %</p>
          <p class="text-2xl font-bold" :class="summary.total_pnl_percent >= 0 ? 'price-up' : 'price-down'">
            {{ summary.total_pnl_percent >= 0 ? '+' : '' }}{{ summary.total_pnl_percent.toFixed(2) }}%
          </p>
        </div>
      </div>
      
      <!-- Holdings List -->
      <div class="glass-card overflow-hidden">
        <div v-if="holdings.length === 0" class="p-12 text-center">
          <Icon name="ph:wallet" class="w-16 h-16 mx-auto text-gray-600 mb-4" />
          <h3 class="text-xl font-medium mb-2">No Holdings Yet</h3>
          <p class="text-gray-400 mb-4">Add your first crypto holding to start tracking</p>
          <button 
            @click="showAddModal = true"
            class="px-6 py-3 bg-primary text-dark-950 rounded-lg font-medium"
          >
            Add Your First Holding
          </button>
        </div>
        
        <table v-else class="w-full">
          <thead class="border-b border-white/5">
            <tr class="text-left text-sm text-gray-400">
              <th class="p-4">Asset</th>
              <th class="p-4 text-right">Holdings</th>
              <th class="p-4 text-right">Avg. Buy Price</th>
              <th class="p-4 text-right">Current Price</th>
              <th class="p-4 text-right">Value</th>
              <th class="p-4 text-right">P&L</th>
              <th class="p-4"></th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="holding in holdings" 
              :key="holding.coin_id"
              class="border-b border-white/5 hover:bg-white/5"
            >
              <td class="p-4">
                <div class="flex items-center gap-3">
                  <img :src="holding.image" :alt="holding.name" class="w-10 h-10 rounded-full" />
                  <div>
                    <p class="font-medium">{{ holding.name }}</p>
                    <p class="text-sm text-gray-400">{{ holding.symbol }}</p>
                  </div>
                </div>
              </td>
              <td class="p-4 text-right font-mono">{{ holding.amount }}</td>
              <td class="p-4 text-right font-mono">${{ formatPrice(holding.buy_price) }}</td>
              <td class="p-4 text-right font-mono">${{ formatPrice(holding.current_price) }}</td>
              <td class="p-4 text-right font-mono">${{ formatValue(holding.value) }}</td>
              <td class="p-4 text-right">
                <span :class="holding.pnl >= 0 ? 'price-up' : 'price-down'">
                  {{ holding.pnl >= 0 ? '+' : '' }}{{ holding.pnl_percent?.toFixed(2) }}%
                </span>
              </td>
              <td class="p-4 text-right">
                <button 
                  @click="deleteHolding(holding.coin_id)"
                  class="p-2 text-gray-400 hover:text-red-400 transition-colors"
                >
                  <Icon name="ph:trash" class="w-5 h-5" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  title: 'Portfolio',
  middleware: ['auth'],
})

useSeoMeta({
  title: 'Portfolio - AI Crypto Hub',
  description: 'Track your cryptocurrency portfolio with real-time prices and P&L calculations.',
})

const showAddModal = ref(false)

// Mock data
const holdings = ref([
  { 
    coin_id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', 
    image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png',
    amount: 0.5, buy_price: 45000, current_price: 98500, 
    value: 49250, pnl: 26750, pnl_percent: 118.89 
  },
  { 
    coin_id: 'ethereum', symbol: 'ETH', name: 'Ethereum', 
    image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png',
    amount: 5, buy_price: 2500, current_price: 3450, 
    value: 17250, pnl: 4750, pnl_percent: 38.0 
  },
])

const summary = computed(() => {
  const total_value = holdings.value.reduce((sum, h) => sum + h.value, 0)
  const total_invested = holdings.value.reduce((sum, h) => sum + (h.amount * h.buy_price), 0)
  const total_pnl = total_value - total_invested
  const total_pnl_percent = total_invested > 0 ? ((total_value / total_invested) - 1) * 100 : 0
  
  return { total_value, total_invested, total_pnl, total_pnl_percent, holdings_count: holdings.value.length }
})

const formatPrice = (price: number) => {
  if (price >= 1) return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return price.toFixed(6)
}

const formatValue = (value: number) => {
  return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const deleteHolding = (coinId: string) => {
  holdings.value = holdings.value.filter(h => h.coin_id !== coinId)
}
</script>
