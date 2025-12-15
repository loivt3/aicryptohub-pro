<template>
  <div class="page-container">
    <template v-if="!isMobile">
      <DesktopHeader />
      <main class="desktop-main">
        <DesktopMarket />
      </main>
    </template>
    <template v-else>
      <MobileMarket />
    </template>
  </div>
</template>

<script setup lang="ts">
const { isMobile } = useDevice()

useSeoMeta({
  title: 'Market Categories | AI Crypto Hub',
  description: 'Explore cryptocurrency market categories with AI-powered analysis.',
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #0b0f19;
  color: #ffffff;
}

.desktop-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}
</style>
