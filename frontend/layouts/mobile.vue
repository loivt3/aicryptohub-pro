<template>
  <div class="mobile-app-layout">
    <!-- Mobile pages have their own SharedMobileHeader -->
    <slot />
  </div>
</template>

<style scoped>
.mobile-app-layout {
  min-height: 100vh;
  background: var(--aihub-bg-primary);
}
</style>
