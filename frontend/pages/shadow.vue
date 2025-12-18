<template>
  <div class="shadow-page">
    <MobileShadow />
  </div>
</template>

<script setup>
import MobileShadow from '~/components/mobile/MobileShadow.vue'

// Use mobile layout (no header)
definePageMeta({
  layout: 'mobile'
})

// Page metadata
useHead({
  title: 'Shadow Analysis - AI Crypto Hub',
  meta: [
    {
      name: 'description',
      content: 'Intent Divergence Analysis - Detect whale-crowd behavioral divergence for smart trading signals.'
    }
  ]
})
</script>

<style scoped>
.shadow-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a1a 0%, #12122a 100%);
}
</style>
