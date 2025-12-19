<template>
  <div class="py-12">
    <div class="max-w-7xl mx-auto px-4">
      <!-- Back button -->
      <NuxtLink to="/market" class="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-6">
        <Icon name="ph:arrow-left" class="w-5 h-5" />
        Back to Market
      </NuxtLink>
      
      <!-- Coin Header -->
      <div class="glass-card p-6 mb-6">
        <div class="flex flex-col md:flex-row md:items-center gap-6">
          <img 
            :src="coin.image" 
            :alt="coin.name" 
            class="w-20 h-20 rounded-full"
          />
          
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h1 class="text-3xl font-bold">{{ coin.name }}</h1>
              <span class="px-2 py-1 bg-dark-700 text-gray-300 text-sm rounded">{{ coin.symbol }}</span>
              <span class="px-2 py-1 bg-primary/20 text-primary text-sm rounded">Rank #{{ coin.market_cap_rank }}</span>
            </div>
            
            <div class="flex items-end gap-4">
              <span class="text-4xl font-bold font-mono">${{ formatPrice(coin.price) }}</span>
              <span 
                class="text-xl font-medium"
                :class="coin.change_24h >= 0 ? 'price-up' : 'price-down'"
              >
                {{ coin.change_24h >= 0 ? '+' : '' }}{{ coin.change_24h?.toFixed(2) }}%
              </span>
            </div>
          </div>
          
          <!-- AI Signal -->
          <div class="text-center">
            <div class="w-24 h-24 mx-auto relative mb-2">
              <svg class="w-full h-full transform -rotate-90">
                <circle cx="48" cy="48" r="40" class="fill-none stroke-dark-700" stroke-width="8" />
                <circle 
                  cx="48" cy="48" r="40" 
                  class="fill-none stroke-primary transition-all duration-500"
                  stroke-width="8"
                  :stroke-dasharray="`${coin.asi_score * 2.51} 251`"
                />
              </svg>
              <span class="absolute inset-0 flex items-center justify-center text-2xl font-bold">
                {{ coin.asi_score }}
              </span>
            </div>
            <span 
              class="px-3 py-1 text-sm font-bold rounded-full"
              :class="getSignalClass(coin.signal)"
            >
              {{ coin.signal }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- Stats Grid -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="glass-card p-4">
          <p class="text-sm text-gray-400 mb-1">Market Cap</p>
          <p class="text-xl font-bold">${{ formatMarketCap(coin.market_cap) }}</p>
        </div>
        <div class="glass-card p-4">
          <p class="text-sm text-gray-400 mb-1">24h Volume</p>
          <p class="text-xl font-bold">${{ formatMarketCap(coin.volume_24h) }}</p>
        </div>
        <div class="glass-card p-4">
          <p class="text-sm text-gray-400 mb-1">24h High</p>
          <p class="text-xl font-bold font-mono">${{ formatPrice(coin.high_24h) }}</p>
        </div>
        <div class="glass-card p-4">
          <p class="text-sm text-gray-400 mb-1">24h Low</p>
          <p class="text-xl font-bold font-mono">${{ formatPrice(coin.low_24h) }}</p>
        </div>
      </div>
      
      <!-- Price Changes -->
      <div class="glass-card p-6 mb-6">
        <h2 class="text-xl font-bold mb-4">Price Changes</h2>
        <div class="grid grid-cols-4 gap-4">
          <div v-for="(change, period) in priceChanges" :key="period" class="text-center">
            <p class="text-sm text-gray-400 mb-1">{{ period }}</p>
            <p 
              class="text-lg font-bold"
              :class="change >= 0 ? 'price-up' : 'price-down'"
            >
              {{ change >= 0 ? '+' : '' }}{{ change?.toFixed(2) }}%
            </p>
          </div>
        </div>
      </div>
      
      <!-- AI Analysis -->
      <div class="glass-card p-6">
        <h2 class="text-xl font-bold mb-4">AI Analysis</h2>
        <p class="text-gray-300 leading-relaxed">{{ coin.reason }}</p>
        
        <div class="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-dark-800 p-3 rounded-lg">
            <p class="text-sm text-gray-400">RSI (14)</p>
            <p class="text-lg font-mono">{{ coin.indicators?.rsi_14 || '--' }}</p>
          </div>
          <div class="bg-dark-800 p-3 rounded-lg">
            <p class="text-sm text-gray-400">MACD</p>
            <p class="text-lg font-mono" :class="(coin.indicators?.macd_histogram || 0) >= 0 ? 'price-up' : 'price-down'">
              {{ coin.indicators?.macd_histogram?.toFixed(4) || '--' }}
            </p>
          </div>
          <div class="bg-dark-800 p-3 rounded-lg">
            <p class="text-sm text-gray-400">Stochastic</p>
            <p class="text-lg font-mono">{{ coin.indicators?.stoch_k || '--' }}</p>
          </div>
          <div class="bg-dark-800 p-3 rounded-lg">
            <p class="text-sm text-gray-400">ADX</p>
            <p class="text-lg font-mono">{{ coin.indicators?.adx || '--' }}</p>
          </div>
        </div>
      </div>
      
      <!-- Multi-Horizon ASI (New!) -->
      <div class="mt-6">
        <MultiHorizonAsi :coin-id="coinId" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const coinId = route.params.id as string

// SEO
useSeoMeta({
  title: () => `${coin.value.name} (${coin.value.symbol}) Price & Analysis - AI Crypto Hub`,
  description: () => `${coin.value.name} current price $${formatPrice(coin.value.price)}, 24h change ${coin.value.change_24h?.toFixed(2)}%. AI analysis: ${coin.value.signal}`,
})

// Mock data - will fetch from API
const coin = ref({
  coin_id: coinId,
  name: 'Bitcoin',
  symbol: 'BTC',
  image: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png',
  price: 98500,
  change_1h: 0.5,
  change_24h: 2.4,
  change_7d: 8.5,
  change_30d: 15.2,
  market_cap: 1900000000000,
  market_cap_rank: 1,
  volume_24h: 45000000000,
  high_24h: 99200,
  low_24h: 96800,
  asi_score: 72,
  signal: 'BUY',
  reason: 'Bitcoin shows strong bullish momentum with RSI at neutral levels and MACD histogram positive. Price is trending above all major EMAs. ADX indicates a strong trend. Overall market sentiment remains positive with institutional interest continuing.',
  indicators: {
    rsi_14: 52,
    macd_histogram: 0.0045,
    stoch_k: 65,
    adx: 32,
  }
})

const priceChanges = computed(() => ({
  '1H': coin.value.change_1h,
  '24H': coin.value.change_24h,
  '7D': coin.value.change_7d,
  '30D': coin.value.change_30d,
}))

const formatPrice = (price: number) => {
  if (!price) return '0.00'
  if (price >= 1) return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return price.toFixed(6)
}

const formatMarketCap = (cap: number) => {
  if (!cap) return '0'
  if (cap >= 1e12) return (cap / 1e12).toFixed(2) + 'T'
  if (cap >= 1e9) return (cap / 1e9).toFixed(2) + 'B'
  if (cap >= 1e6) return (cap / 1e6).toFixed(2) + 'M'
  return cap.toLocaleString()
}

const getSignalClass = (signal: string) => {
  if (signal?.includes('BUY')) return 'signal-buy'
  if (signal?.includes('SELL')) return 'signal-sell'
  return 'signal-hold'
}
</script>
