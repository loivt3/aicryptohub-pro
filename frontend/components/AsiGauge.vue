<template>
  <div class="relative w-full h-full">
    <svg class="w-full h-full transform -rotate-90">
      <circle
        :cx="center"
        :cy="center"
        :r="radius"
        class="fill-none stroke-dark-700"
        :stroke-width="strokeWidth"
      />
      <circle
        :cx="center"
        :cy="center"
        :r="radius"
        class="fill-none transition-all duration-500"
        :class="scoreColorClass"
        :stroke-width="strokeWidth"
        :stroke-dasharray="dashArray"
        stroke-linecap="round"
      />
    </svg>
    <div class="absolute inset-0 flex flex-col items-center justify-center">
      <span class="text-2xl font-bold">{{ Math.round(score) }}</span>
      <span v-if="showLabel" class="text-xs text-gray-400">ASI</span>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  score: number
  size?: number
  strokeWidth?: number
  showLabel?: boolean
}>(), {
  size: 80,
  strokeWidth: 6,
  showLabel: false,
})

const center = computed(() => props.size / 2)
const radius = computed(() => (props.size - props.strokeWidth) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const dashArray = computed(() => `${(props.score / 100) * circumference.value} ${circumference.value}`)

const scoreColorClass = computed(() => {
  if (props.score >= 60) return 'stroke-green-500'
  if (props.score >= 40) return 'stroke-yellow-500'
  return 'stroke-red-500'
})
</script>
