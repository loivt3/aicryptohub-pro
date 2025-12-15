<template>
  <div class="page-container">
    <template v-if="!isMobile">
      <DesktopHeader />
      <main class="desktop-main">
        <DesktopAnalysis />
      </main>
    </template>
    <template v-else>
      <MobileAnalysis />
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'blank' })

const { isMobile } = useDevice()

useSeoMeta({
  title: 'AI Analysis | AI Crypto Hub',
  description: 'AI-powered sentiment and technical analysis for cryptocurrencies.',
})
</script>

<style scoped>
.page-container { min-height: 100vh; background: #0b0f19; color: #ffffff; }
.desktop-main { max-width: 1400px; margin: 0 auto; padding: 0 24px; }
</style>

