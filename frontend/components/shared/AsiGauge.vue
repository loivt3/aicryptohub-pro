<template>
  <div class="asi-gauge">
    <svg :width="size" :height="size * 0.6" viewBox="0 0 120 72">
      <defs>
        <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#ef4444" />
          <stop offset="50%" stop-color="#f97316" />
          <stop offset="100%" stop-color="#22c55e" />
        </linearGradient>
      </defs>
      <!-- Background arc -->
      <path
        d="M 10 62 A 50 50 0 0 1 110 62"
        fill="none"
        stroke="rgba(255,255,255,0.1)"
        stroke-width="10"
        stroke-linecap="round"
      />
      <!-- Value arc -->
      <path
        :d="arcPath"
        fill="none"
        stroke="url(#gaugeGradient)"
        stroke-width="10"
        stroke-linecap="round"
      />
      <!-- Needle -->
      <line
        :x1="60"
        :y1="62"
        :x2="needleX"
        :y2="needleY"
        stroke="#ffffff"
        stroke-width="2"
        stroke-linecap="round"
      />
      <circle cx="60" cy="62" r="4" fill="#ffffff" />
      <!-- Score text -->
      <text x="60" y="50" text-anchor="middle" fill="#ffffff" font-size="20" font-weight="700">{{ score }}</text>
    </svg>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  score: number
  size?: number
}>()

const size = computed(() => props.size || 100)

const arcPath = computed(() => {
  const angle = (props.score / 100) * 180
  const endAngle = (angle - 180) * (Math.PI / 180)
  const endX = 60 + 50 * Math.cos(endAngle)
  const endY = 62 + 50 * Math.sin(endAngle)
  const largeArc = angle > 90 ? 1 : 0
  return `M 10 62 A 50 50 0 ${largeArc} 1 ${endX} ${endY}`
})

const needleAngle = computed(() => (props.score / 100) * 180 - 180)
const needleX = computed(() => 60 + 35 * Math.cos(needleAngle.value * (Math.PI / 180)))
const needleY = computed(() => 62 + 35 * Math.sin(needleAngle.value * (Math.PI / 180)))
</script>

<style scoped>
.asi-gauge { display: flex; justify-content: center; }
</style>
