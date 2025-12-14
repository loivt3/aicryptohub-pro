<template>
  <span 
    class="px-2 py-1 text-xs font-bold rounded-full inline-flex items-center gap-1"
    :class="badgeClass"
  >
    <Icon v-if="icon" :name="icon" class="w-3 h-3" />
    {{ signal }}
  </span>
</template>

<script setup lang="ts">
const props = defineProps<{
  signal: string
  showIcon?: boolean
}>()

const badgeClass = computed(() => {
  const s = props.signal?.toUpperCase()
  if (s?.includes('STRONG_BUY')) return 'bg-green-500/20 text-green-400 border border-green-500/30'
  if (s?.includes('BUY')) return 'signal-buy'
  if (s?.includes('STRONG_SELL')) return 'bg-red-500/20 text-red-400 border border-red-500/30'
  if (s?.includes('SELL')) return 'signal-sell'
  return 'signal-hold'
})

const icon = computed(() => {
  if (!props.showIcon) return null
  const s = props.signal?.toUpperCase()
  if (s?.includes('BUY')) return 'ph:trend-up'
  if (s?.includes('SELL')) return 'ph:trend-down'
  return 'ph:minus'
})
</script>
