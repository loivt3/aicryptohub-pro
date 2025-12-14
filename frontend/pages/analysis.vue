<template>
  <div class="py-12">
    <div class="max-w-7xl mx-auto px-4">
      <h1 class="text-3xl font-bold mb-8">AI Market Analysis</h1>
      
      <!-- Overview Stats -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div class="glass-card p-4">
          <p class="text-sm text-gray-400 mb-1">Bullish Signals</p>
          <p class="text-2xl font-bold price-up">{{ bullishCount }}</p>
        </div>
        <div class="glass-card p-4">
          <p class="text-sm text-gray-400 mb-1">Bearish Signals</p>
          <p class="text-2xl font-bold price-down">{{ bearishCount }}</p>
        </div>
        <div class="glass-card p-4">
          <p class="text-sm text-gray-400 mb-1">Neutral Signals</p>
          <p class="text-2xl font-bold text-yellow-400">{{ neutralCount }}</p>
        </div>
        <div class="glass-card p-4">
          <p class="text-sm text-gray-400 mb-1">Last Updated</p>
          <p class="text-lg font-medium">Just now</p>
        </div>
      </div>
      
      <!-- Sentiment Table -->
      <div class="glass-card overflow-hidden">
        <div class="p-4 border-b border-white/5">
          <h2 class="text-xl font-bold">AI Sentiment Signals</h2>
        </div>
        
        <table class="w-full">
          <thead class="border-b border-white/5 bg-dark-900/50">
            <tr class="text-left text-sm text-gray-400">
              <th class="p-4">Coin</th>
              <th class="p-4 text-center">ASI Score</th>
              <th class="p-4 text-center">Signal</th>
              <th class="p-4">Analysis</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="item in sentimentData" 
              :key="item.coin_id"
              class="border-b border-white/5 hover:bg-white/5"
            >
              <td class="p-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary/20 to-accent-purple/20 flex items-center justify-center">
                    <span class="font-bold text-sm">{{ item.symbol?.slice(0, 2) }}</span>
                  </div>
                  <div>
                    <p class="font-medium">{{ item.name || item.symbol }}</p>
                    <p class="text-sm text-gray-400">{{ item.symbol }}</p>
                  </div>
                </div>
              </td>
              <td class="p-4">
                <div class="flex flex-col items-center">
                  <div class="w-16 h-16 relative">
                    <svg class="w-full h-full transform -rotate-90">
                      <circle
                        cx="32" cy="32" r="28"
                        class="fill-none stroke-dark-700"
                        stroke-width="6"
                      />
                      <circle
                        cx="32" cy="32" r="28"
                        class="fill-none transition-all duration-500"
                        :class="getScoreColor(item.asi_score)"
                        stroke-width="6"
                        :stroke-dasharray="`${item.asi_score * 1.76} 176`"
                      />
                    </svg>
                    <span class="absolute inset-0 flex items-center justify-center text-sm font-bold">
                      {{ Math.round(item.asi_score) }}
                    </span>
                  </div>
                </div>
              </td>
              <td class="p-4 text-center">
                <span 
                  class="px-3 py-1 text-xs font-bold rounded-full"
                  :class="getSignalClass(item.signal)"
                >
                  {{ item.signal }}
                </span>
              </td>
              <td class="p-4">
                <p class="text-sm text-gray-300 line-clamp-2">{{ item.reason }}</p>
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
  title: 'Analysis',
})

useSeoMeta({
  title: 'AI Market Analysis - AI Crypto Hub',
  description: 'AI-powered cryptocurrency sentiment analysis with technical indicators and trading signals.',
})

// Mock data
const sentimentData = ref([
  { coin_id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', asi_score: 72, signal: 'BUY', reason: 'RSI(45) neutral, MACD bullish momentum, Strong uptrend (ADX:32)' },
  { coin_id: 'ethereum', symbol: 'ETH', name: 'Ethereum', asi_score: 68, signal: 'BUY', reason: 'RSI(52) neutral, MACD bullish, Near middle BB' },
  { coin_id: 'solana', symbol: 'SOL', name: 'Solana', asi_score: 78, signal: 'STRONG_BUY', reason: 'RSI(38) approaching oversold, Strong bullish momentum' },
  { coin_id: 'xrp', symbol: 'XRP', name: 'XRP', asi_score: 45, signal: 'NEUTRAL', reason: 'RSI(55) neutral, Weak trend (ADX:18)' },
  { coin_id: 'cardano', symbol: 'ADA', name: 'Cardano', asi_score: 62, signal: 'BUY', reason: 'MACD bullish crossover, Price near lower BB' },
  { coin_id: 'dogecoin', symbol: 'DOGE', name: 'Dogecoin', asi_score: 35, signal: 'SELL', reason: 'RSI(72) overbought, MACD bearish divergence' },
])

const bullishCount = computed(() => sentimentData.value.filter(s => s.signal.includes('BUY')).length)
const bearishCount = computed(() => sentimentData.value.filter(s => s.signal.includes('SELL')).length)
const neutralCount = computed(() => sentimentData.value.filter(s => s.signal === 'NEUTRAL').length)

const getScoreColor = (score: number) => {
  if (score >= 60) return 'stroke-green-500'
  if (score >= 40) return 'stroke-yellow-500'
  return 'stroke-red-500'
}

const getSignalClass = (signal: string) => {
  if (signal.includes('BUY')) return 'signal-buy'
  if (signal.includes('SELL')) return 'signal-sell'
  return 'signal-hold'
}
</script>
