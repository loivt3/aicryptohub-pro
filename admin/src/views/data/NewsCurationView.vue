<template>
  <div class="news-curation">
    <div class="section-header">
      <h2 class="section-title">News Curation</h2>
      <n-space>
        <n-select v-model:value="statusFilter" :options="statusOptions" style="width: 150px" />
        <n-button type="primary">Add News</n-button>
      </n-space>
    </div>

    <n-grid :cols="1" :y-gap="16">
      <n-gi v-for="article in articles" :key="article.id">
        <n-card :bordered="false">
          <div class="article-row">
            <div class="article-content">
              <h3>{{ article.title }}</h3>
              <p>{{ article.excerpt }}</p>
              <div class="article-meta">
                <n-tag :type="getStatusType(article.status)" size="small">{{ article.status }}</n-tag>
                <span>{{ article.source }}</span>
                <span>{{ article.date }}</span>
              </div>
            </div>
            <div class="article-actions">
              <n-button v-if="article.status === 'pending'" type="success" size="small">Approve</n-button>
              <n-button v-if="article.status === 'pending'" type="warning" size="small">Reject</n-button>
              <n-button type="error" size="small" quaternary>Delete</n-button>
            </div>
          </div>
        </n-card>
      </n-gi>
    </n-grid>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const statusFilter = ref('all')
const statusOptions = [
  { label: 'All', value: 'all' },
  { label: 'Pending', value: 'pending' },
  { label: 'Approved', value: 'approved' },
  { label: 'Rejected', value: 'rejected' },
]

const articles = ref([
  { id: 1, title: 'Bitcoin Surges Past $90,000', excerpt: 'Bitcoin reaches new all-time high amid institutional buying...', status: 'pending', source: 'CoinDesk', date: '2 hours ago' },
  { id: 2, title: 'Ethereum 2.0 Staking Reaches Record', excerpt: 'Over 30 million ETH now staked on the Beacon Chain...', status: 'approved', source: 'CryptoNews', date: '5 hours ago' },
  { id: 3, title: 'Solana Network Congestion', excerpt: 'Solana experiences slowdowns due to high demand...', status: 'rejected', source: 'TheBlock', date: '1 day ago' },
])

function getStatusType(status) {
  const types = { pending: 'warning', approved: 'success', rejected: 'error' }
  return types[status] || 'default'
}
</script>

<style scoped>
.news-curation {
  max-width: 1000px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
}

.article-row {
  display: flex;
  justify-content: space-between;
  gap: 24px;
}

.article-content h3 {
  font-size: 16px;
  margin-bottom: 8px;
}

.article-content p {
  color: #9ca3af;
  font-size: 14px;
  margin-bottom: 12px;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
  color: #6b7280;
}

.article-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
