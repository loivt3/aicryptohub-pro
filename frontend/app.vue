<template>
  <div class="min-h-screen bg-dark-950">
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<script setup lang="ts">
// App-level setup
useHead({
  titleTemplate: (title) => title ? `${title} | AI Crypto Hub` : 'AI Crypto Hub',
})
</script>
