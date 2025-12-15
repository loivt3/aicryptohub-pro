<template>
  <div class="page-container">
    <template v-if="!isMobile">
      <DesktopHeader />
      <main class="desktop-main">
        <DesktopOnChain />
      </main>
    </template>
    <template v-else>
      <MobileOnChain />
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'blank' })

const { isMobile } = useDevice()

useSeoMeta({
  title: 'On-Chain Signals | AI Crypto Hub',
  description: 'Blockchain analytics, whale tracking, and exchange flows.',
})
</script>

<style scoped>
.page-container { min-height: 100vh; background: #0b0f19; color: #ffffff; }
.desktop-main { max-width: 1400px; margin: 0 auto; padding: 0 24px; }
</style>

