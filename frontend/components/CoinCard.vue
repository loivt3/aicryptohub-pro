<template>
  <div class="glass-card p-4 hover:shadow-glow transition-shadow cursor-pointer" @click="$emit('click')">
    <div class="flex items-center gap-3">
      <img 
        v-if="coin.image" 
        :src="coin.image" 
        :alt="coin.name" 
        class="w-10 h-10 rounded-full"
      />
      <div v-else class="w-10 h-10 rounded-full bg-gradient-to-br from-primary/30 to-accent-purple/30 flex items-center justify-center">
        <span class="font-bold text-sm">{{ coin.symbol?.slice(0, 2) }}</span>
      </div>
      
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <p class="font-medium truncate">{{ coin.name }}</p>
          <span class="text-xs text-gray-500">{{ coin.symbol }}</span>
        </div>
        <p class="text-sm text-gray-400">Rank #{{ coin.market_cap_rank }}</p>
      </div>
      
      <div class="text-right">
        <p class="font-mono font-medium">${{ formatPrice(coin.price) }}</p>
        <p 
          class="text-sm"
          :class="coin.change_24h >= 0 ? 'price-up' : 'price-down'"
        >
          {{ coin.change_24h >= 0 ? '+' : '' }}{{ coin.change_24h?.toFixed(2) }}%
        </p>
      </div>
      
      <span 
        v-if="coin.signal"
        class="px-2 py-1 text-xs font-bold rounded-full hidden md:inline-block"
        :class="getSignalClass(coin.signal)"
      >
        {{ coin.signal }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  coin: {
    coin_id: string
    symbol: string
    name: string
    image?: string
    price: number
    change_24h: number
    market_cap_rank?: number
    signal?: string
  }
}>()

defineEmits(['click'])

const formatPrice = (price: number) => {
  if (price >= 1) return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return price.toFixed(6)
}

const getSignalClass = (signal: string) => {
  if (signal?.includes('BUY')) return 'signal-buy'
  if (signal?.includes('SELL')) return 'signal-sell'
  return 'signal-hold'
}
</script>
