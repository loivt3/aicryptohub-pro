<template>
  <div class="data-management">
    <div class="section-header">
      <h2 class="section-title">Data Management</h2>
    </div>

    <n-grid :cols="3" :x-gap="16" :y-gap="16">
      <!-- Coins Manager -->
      <n-gi>
        <n-card hoverable @click="$router.push({ name: 'coins-manager' })">
          <template #cover>
            <div class="card-cover" style="background: linear-gradient(135deg, #3b82f6, #1d4ed8)">
              💰
            </div>
          </template>
          <n-card-meta title="Coins Manager" description="Edit metadata, visibility, and categories" />
          <template #footer>
            <n-text depth="3">5,781 coins tracked</n-text>
          </template>
        </n-card>
      </n-gi>

      <!-- Market Corrections -->
      <n-gi>
        <n-card hoverable @click="$router.push({ name: 'market-corrections' })">
          <template #cover>
            <div class="card-cover" style="background: linear-gradient(135deg, #f59e0b, #d97706)">
              📊
            </div>
          </template>
          <n-card-meta title="Market Corrections" description="Manual price fixes for data errors" />
          <template #footer>
            <n-text depth="3">Last correction: 2 hours ago</n-text>
          </template>
        </n-card>
      </n-gi>

      <!-- News Curation -->
      <n-gi>
        <n-card hoverable @click="$router.push({ name: 'news-curation' })">
          <template #cover>
            <div class="card-cover" style="background: linear-gradient(135deg, #10b981, #059669)">
              📰
            </div>
          </template>
          <n-card-meta title="News Curation" description="Review, approve, or remove news articles" />
          <template #footer>
            <n-text depth="3">12 pending review</n-text>
          </template>
        </n-card>
      </n-gi>
    </n-grid>

    <!-- Quick Stats -->
    <n-card title="Data Overview" :bordered="false" style="margin-top: 24px">
      <n-grid :cols="4" :x-gap="16">
        <n-gi>
          <n-statistic label="Total Coins" :value="5781" />
        </n-gi>
        <n-gi>
          <n-statistic label="With AI Signals" :value="1247" />
        </n-gi>
        <n-gi>
          <n-statistic label="On-Chain Data" :value="892" />
        </n-gi>
        <n-gi>
          <n-statistic label="News Articles" :value="3456" />
        </n-gi>
      </n-grid>
    </n-card>
  </div>
</template>

<script setup>
</script>

<style scoped>
.data-management {
  max-width: 1200px;
}

.section-header {
  margin-bottom: 24px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
}

.card-cover {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
}
</style>
