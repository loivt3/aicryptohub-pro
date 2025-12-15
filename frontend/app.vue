<template>
  <div class="min-h-screen" :class="isDark ? 'theme-dark' : 'theme-light'">
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<script setup lang="ts">
import '~/assets/css/theme.css'

const { isDark } = useTheme()

// App-level setup
useHead({
  titleTemplate: (title) => title ? `${title} | AI Crypto Hub` : 'AI Crypto Hub',
})
</script>
