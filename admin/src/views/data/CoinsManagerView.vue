<template>
  <div class="coins-manager">
    <div class="section-header">
      <h2 class="section-title">Coins Manager</h2>
      <n-space>
        <n-input placeholder="Search coins..." style="width: 250px" v-model:value="searchQuery">
          <template #prefix>
            <n-icon><SearchOutline /></n-icon>
          </template>
        </n-input>
        <n-button type="primary">Add Coin</n-button>
      </n-space>
    </div>

    <n-card :bordered="false">
      <n-data-table
        :columns="columns"
        :data="filteredCoins"
        :pagination="{ pageSize: 20 }"
        :bordered="false"
        :loading="loading"
      />
    </n-card>
  </div>
</template>

<script setup>
import { ref, computed, h } from 'vue'
import { NTag, NButton, NSpace, NSwitch, NAvatar } from 'naive-ui'
import { SearchOutline } from '@vicons/ionicons5'

const loading = ref(false)
const searchQuery = ref('')

const coins = ref([
  { id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', image: '₿', category: 'Layer 1', visible: true, rank: 1 },
  { id: 'ethereum', symbol: 'ETH', name: 'Ethereum', image: 'Ξ', category: 'Layer 1', visible: true, rank: 2 },
  { id: 'solana', symbol: 'SOL', name: 'Solana', image: '◎', category: 'Layer 1', visible: true, rank: 5 },
])

const filteredCoins = computed(() => {
  if (!searchQuery.value) return coins.value
  const q = searchQuery.value.toLowerCase()
  return coins.value.filter(c => 
    c.name.toLowerCase().includes(q) || 
    c.symbol.toLowerCase().includes(q)
  )
})

const columns = [
  { title: '#', key: 'rank', width: 60 },
  {
    title: 'Coin',
    key: 'name',
    render(row) {
      return h('div', { style: 'display: flex; align-items: center; gap: 8px' }, [
        h(NAvatar, { size: 'small', round: true }, { default: () => row.image }),
        h('span', {}, row.name),
        h(NTag, { size: 'small', type: 'info' }, { default: () => row.symbol }),
      ])
    }
  },
  { title: 'Category', key: 'category' },
  {
    title: 'Visible',
    key: 'visible',
    render(row) {
      return h(NSwitch, { value: row.visible, onUpdateValue: (v) => row.visible = v })
    }
  },
  {
    title: 'Actions',
    key: 'actions',
    render(row) {
      return h(NSpace, {}, {
        default: () => [
          h(NButton, { size: 'small', quaternary: true }, { default: () => 'Edit' }),
          h(NButton, { size: 'small', quaternary: true, type: 'error' }, { default: () => 'Delete' }),
        ]
      })
    }
  },
]
</script>

<style scoped>
.coins-manager {
  max-width: 1200px;
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
</style>
