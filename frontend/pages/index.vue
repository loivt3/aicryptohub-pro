<template>
  <div>
    <!-- Hero Section -->
    <section class="relative py-20 overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent"></div>
      <div class="max-w-7xl mx-auto px-4 relative">
        <div class="text-center mb-12">
          <h1 class="text-4xl md:text-5xl font-bold mb-4">
            <span class="gradient-text">AI-Powered</span> Crypto Analysis
          </h1>
          <p class="text-xl text-gray-400 max-w-2xl mx-auto">
            Real-time market data, sentiment analysis, and on-chain signals powered by advanced AI.
          </p>
        </div>
        
        <!-- Market Stats Cards -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          <div v-for="stat in marketStats" :key="stat.label" class="glass-card p-4">
            <p class="text-sm text-gray-400 mb-1">{{ stat.label }}</p>
            <p class="text-xl font-bold">{{ stat.value }}</p>
            <p :class="stat.change >= 0 ? 'price-up' : 'price-down'" class="text-sm">
              {{ stat.change >= 0 ? '+' : '' }}{{ stat.change }}%
            </p>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Top Coins Table -->
    <section class="py-12">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold">Top Cryptocurrencies</h2>
          <NuxtLink to="/market" class="text-primary hover:underline">
            View All →
          </NuxtLink>
        </div>
        
        <div class="glass-card overflow-hidden">
          <table class="w-full">
            <thead class="border-b border-white/5">
              <tr class="text-left text-sm text-gray-400">
                <th class="p-4">#</th>
                <th class="p-4">Coin</th>
                <th class="p-4 text-right">Price</th>
                <th class="p-4 text-right">24h</th>
                <th class="p-4 text-right hidden md:table-cell">Market Cap</th>
                <th class="p-4 text-right hidden md:table-cell">AI Signal</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="coin in topCoins" 
                :key="coin.symbol"
                class="border-b border-white/5 hover:bg-white/5 transition-colors"
              >
                <td class="p-4 text-gray-400">{{ coin.rank }}</td>
                <td class="p-4">
                  <div class="flex items-center gap-3">
                    <img :src="coin.image" :alt="coin.name" class="w-8 h-8 rounded-full" />
                    <div>
                      <p class="font-medium">{{ coin.name }}</p>
                      <p class="text-sm text-gray-400">{{ coin.symbol }}</p>
                    </div>
                  </div>
                </td>
                <td class="p-4 text-right font-mono">${{ formatPrice(coin.price) }}</td>
                <td class="p-4 text-right" :class="coin.change24h >= 0 ? 'price-up' : 'price-down'">
                  {{ coin.change24h >= 0 ? '+' : '' }}{{ coin.change24h.toFixed(2) }}%
                </td>
                <td class="p-4 text-right hidden md:table-cell text-gray-400">
                  ${{ formatMarketCap(coin.marketCap) }}
                </td>
                <td class="p-4 text-right hidden md:table-cell">
                  <span 
                    class="px-2 py-1 text-xs font-medium rounded"
                    :class="`signal-${coin.signal.toLowerCase()}`"
                  >
                    {{ coin.signal }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
// SEO Meta
definePageMeta({
  title: 'Dashboard',
})

useSeoMeta({
  title: 'Dashboard - AI Crypto Hub',
  description: 'Real-time cryptocurrency dashboard with AI-powered market analysis and signals.',
})

// Mock data - will be replaced with API calls
const marketStats = ref([
  { label: 'Total Market Cap', value: '$3.2T', change: 2.5 },
  { label: 'BTC Dominance', value: '52.3%', change: -0.3 },
  { label: 'Fear & Greed', value: '72', change: 5 },
  { label: '24h Volume', value: '$142B', change: 8.2 },
])

const topCoins = ref([
  { rank: 1, name: 'Bitcoin', symbol: 'BTC', price: 98500, change24h: 2.4, marketCap: 1900000000000, signal: 'BUY', image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png' },
  { rank: 2, name: 'Ethereum', symbol: 'ETH', price: 3450, change24h: 1.8, marketCap: 415000000000, signal: 'HOLD', image: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png' },
  { rank: 3, name: 'Solana', symbol: 'SOL', price: 185, change24h: 5.2, marketCap: 82000000000, signal: 'BUY', image: 'https://assets.coingecko.com/coins/images/4128/small/solana.png' },
  { rank: 4, name: 'XRP', symbol: 'XRP', price: 2.35, change24h: -1.2, marketCap: 135000000000, signal: 'HOLD', image: 'https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png' },
  { rank: 5, name: 'Cardano', symbol: 'ADA', price: 1.05, change24h: 3.1, marketCap: 37000000000, signal: 'BUY', image: 'https://assets.coingecko.com/coins/images/975/small/cardano.png' },
])

// Utility functions
const formatPrice = (price: number) => {
  if (price >= 1) return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return price.toFixed(6)
}

const formatMarketCap = (cap: number) => {
  if (cap >= 1e12) return (cap / 1e12).toFixed(2) + 'T'
  if (cap >= 1e9) return (cap / 1e9).toFixed(2) + 'B'
  if (cap >= 1e6) return (cap / 1e6).toFixed(2) + 'M'
  return cap.toLocaleString()
}
</script>
