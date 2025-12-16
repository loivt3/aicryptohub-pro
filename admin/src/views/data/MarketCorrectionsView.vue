<template>
  <div class="market-corrections">
    <div class="section-header">
      <h2 class="section-title">Market Corrections</h2>
      <n-space>
        <n-input placeholder="Search by coin..." style="width: 250px" v-model:value="searchQuery">
          <template #prefix>
            <n-icon><SearchOutline /></n-icon>
          </template>
        </n-input>
      </n-space>
    </div>

    <!-- Correction Form -->
    <n-card title="Manual Price Correction" :bordered="false" style="margin-bottom: 24px">
      <n-form
        ref="formRef"
        :model="correctionForm"
        label-placement="left"
        label-width="150"
      >
        <n-grid :cols="3" :x-gap="16">
          <n-gi>
            <n-form-item label="Coin" path="coin_id">
              <n-select
                v-model:value="correctionForm.coin_id"
                :options="coinOptions"
                filterable
                placeholder="Select coin"
              />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="New Price ($)" path="price">
              <n-input-number
                v-model:value="correctionForm.price"
                :min="0"
                :precision="8"
                style="width: 100%"
              />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="Reason" path="reason">
              <n-input v-model:value="correctionForm.reason" placeholder="Why correcting?" />
            </n-form-item>
          </n-gi>
        </n-grid>
        <n-form-item>
          <n-button type="warning" @click="submitCorrection" :loading="submitting">
            Apply Correction
          </n-button>
        </n-form-item>
      </n-form>
    </n-card>

    <!-- Correction History -->
    <n-card title="Correction History" :bordered="false">
      <n-data-table
        :columns="columns"
        :data="corrections"
        :pagination="{ pageSize: 10 }"
        :bordered="false"
        :loading="loading"
      />
    </n-card>
  </div>
</template>

<script setup>
import { ref, computed, h, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { NTag, NButton } from 'naive-ui'
import { SearchOutline } from '@vicons/ionicons5'

const message = useMessage()
const loading = ref(false)
const submitting = ref(false)
const searchQuery = ref('')

// Correction form
const correctionForm = ref({
  coin_id: null,
  price: null,
  reason: '',
})

// Coin options
const coinOptions = ref([
  { label: 'Bitcoin (BTC)', value: 'bitcoin' },
  { label: 'Ethereum (ETH)', value: 'ethereum' },
  { label: 'Solana (SOL)', value: 'solana' },
  { label: 'Cardano (ADA)', value: 'cardano' },
])

// Correction history
const corrections = ref([
  {
    id: 1,
    coin_id: 'bitcoin',
    coin_name: 'Bitcoin',
    old_price: 89500.00,
    new_price: 90000.00,
    reason: 'Exchange API returned stale data',
    applied_by: 'admin@aicryptohub.io',
    created_at: '2024-12-16 20:30:00',
    status: 'applied',
  },
  {
    id: 2,
    coin_id: 'ethereum',
    coin_name: 'Ethereum',
    old_price: 2900.00,
    new_price: 2920.50,
    reason: 'CoinGecko sync delay',
    applied_by: 'admin@aicryptohub.io',
    created_at: '2024-12-16 18:15:00',
    status: 'applied',
  },
])

const columns = [
  { title: 'Coin', key: 'coin_name', width: 120 },
  {
    title: 'Old Price',
    key: 'old_price',
    width: 120,
    render(row) {
      return '$' + row.old_price.toLocaleString()
    }
  },
  {
    title: 'New Price',
    key: 'new_price',
    width: 120,
    render(row) {
      return '$' + row.new_price.toLocaleString()
    }
  },
  { title: 'Reason', key: 'reason' },
  { title: 'Applied By', key: 'applied_by', width: 180 },
  { title: 'Time', key: 'created_at', width: 160 },
  {
    title: 'Status',
    key: 'status',
    width: 100,
    render(row) {
      return h(NTag, { type: 'success', size: 'small' }, { default: () => row.status })
    }
  },
  {
    title: 'Actions',
    key: 'actions',
    width: 100,
    render(row) {
      return h(NButton, { size: 'small', quaternary: true, type: 'error' }, { default: () => 'Revert' })
    }
  },
]

async function submitCorrection() {
  if (!correctionForm.value.coin_id || !correctionForm.value.price) {
    message.error('Please select a coin and enter a price')
    return
  }
  
  submitting.value = true
  try {
    // TODO: POST /admin/data/corrections
    await new Promise(r => setTimeout(r, 1000))
    
    corrections.value.unshift({
      id: Date.now(),
      coin_id: correctionForm.value.coin_id,
      coin_name: coinOptions.value.find(c => c.value === correctionForm.value.coin_id)?.label.split(' ')[0],
      old_price: 0, // Would come from API
      new_price: correctionForm.value.price,
      reason: correctionForm.value.reason,
      applied_by: 'admin@aicryptohub.io',
      created_at: new Date().toISOString().slice(0, 19).replace('T', ' '),
      status: 'applied',
    })
    
    message.success('Price correction applied')
    correctionForm.value = { coin_id: null, price: null, reason: '' }
  } catch (error) {
    message.error('Failed to apply correction')
  } finally {
    submitting.value = false
  }
}

async function fetchCoins() {
  // TODO: Fetch from /admin/data/coins
}

onMounted(() => {
  fetchCoins()
})
</script>

<style scoped>
.market-corrections {
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
