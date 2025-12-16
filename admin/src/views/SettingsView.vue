<template>
  <div class="settings-view">
    <div class="section-header">
      <h2 class="section-title">System Settings</h2>
    </div>

    <n-tabs type="line" animated>
      <!-- Backend Settings -->
      <n-tab-pane name="backend" tab="🔧 Backend Settings">
        <n-card :bordered="false">
          <n-form
            ref="backendFormRef"
            :model="backendSettings"
            label-placement="left"
            label-width="180"
          >
            <n-form-item label="CoinGecko API Key">
              <n-input v-model:value="backendSettings.coingeckoApiKey" type="password" show-password-on="click" />
            </n-form-item>
            <n-form-item label="Etherscan API Key">
              <n-input v-model:value="backendSettings.etherscanApiKey" type="password" show-password-on="click" />
            </n-form-item>
            <n-form-item label="Gemini API Key">
              <n-input v-model:value="backendSettings.geminiApiKey" type="password" show-password-on="click" />
            </n-form-item>
            <n-form-item label="DeepSeek API Key">
              <n-input v-model:value="backendSettings.deepseekApiKey" type="password" show-password-on="click" />
            </n-form-item>
            
            <n-divider />
            
            <n-form-item label="Market Sync Interval (sec)">
              <n-input-number v-model:value="backendSettings.marketSyncInterval" :min="30" :max="3600" />
            </n-form-item>
            <n-form-item label="AI Analysis Interval (sec)">
              <n-input-number v-model:value="backendSettings.aiAnalysisInterval" :min="60" :max="7200" />
            </n-form-item>
            <n-form-item label="On-Chain Sync Interval (sec)">
              <n-input-number v-model:value="backendSettings.onchainSyncInterval" :min="60" :max="7200" />
            </n-form-item>
            
            <n-form-item>
              <n-button type="primary" @click="saveBackendSettings">Save Backend Settings</n-button>
            </n-form-item>
          </n-form>
        </n-card>
      </n-tab-pane>

      <!-- Frontend Settings -->
      <n-tab-pane name="frontend" tab="🎨 Frontend Settings">
        <n-card :bordered="false">
          <n-form
            :model="frontendSettings"
            label-placement="left"
            label-width="180"
          >
            <n-form-item label="Site Name">
              <n-input v-model:value="frontendSettings.siteName" />
            </n-form-item>
            <n-form-item label="Banner Image URL">
              <n-input v-model:value="frontendSettings.bannerImageUrl" />
            </n-form-item>
            <n-form-item label="Announcement Text">
              <n-input v-model:value="frontendSettings.announcementText" type="textarea" :rows="2" />
            </n-form-item>
            <n-form-item label="Maintenance Mode">
              <n-switch v-model:value="frontendSettings.maintenanceMode" />
            </n-form-item>
            
            <n-divider />
            
            <n-form-item label="Meta Title">
              <n-input v-model:value="frontendSettings.metaTitle" />
            </n-form-item>
            <n-form-item label="Meta Description">
              <n-input v-model:value="frontendSettings.metaDescription" type="textarea" :rows="2" />
            </n-form-item>
            
            <n-form-item>
              <n-button type="primary" @click="saveFrontendSettings">Save Frontend Settings</n-button>
            </n-form-item>
          </n-form>
        </n-card>
      </n-tab-pane>

      <!-- AI Tuning -->
      <n-tab-pane name="ai" tab="🤖 AI Tuning">
        <n-card :bordered="false">
          <n-form
            :model="aiSettings"
            label-placement="top"
          >
            <n-form-item label="AI System Prompt">
              <n-input
                v-model:value="aiSettings.systemPrompt"
                type="textarea"
                :rows="8"
                placeholder="Enter system prompt for AI sentiment analysis..."
              />
            </n-form-item>
            
            <n-divider />
            
            <h4 style="margin-bottom: 16px">Technical Indicator Thresholds</h4>
            
            <n-grid :cols="2" :x-gap="24">
              <n-gi>
                <n-form-item label="RSI Overbought">
                  <n-slider v-model:value="aiSettings.rsiOverbought" :min="60" :max="90" :step="1" />
                  <span style="margin-left: 12px">{{ aiSettings.rsiOverbought }}</span>
                </n-form-item>
              </n-gi>
              <n-gi>
                <n-form-item label="RSI Oversold">
                  <n-slider v-model:value="aiSettings.rsiOversold" :min="10" :max="40" :step="1" />
                  <span style="margin-left: 12px">{{ aiSettings.rsiOversold }}</span>
                </n-form-item>
              </n-gi>
              <n-gi>
                <n-form-item label="Whale Alert Threshold ($)">
                  <n-input-number v-model:value="aiSettings.whaleThreshold" :min="10000" :max="10000000" :step="10000" />
                </n-form-item>
              </n-gi>
              <n-gi>
                <n-form-item label="Sentiment Weight (%)">
                  <n-slider v-model:value="aiSettings.sentimentWeight" :min="0" :max="100" :step="5" />
                  <span style="margin-left: 12px">{{ aiSettings.sentimentWeight }}%</span>
                </n-form-item>
              </n-gi>
            </n-grid>
            
            <n-form-item>
              <n-button type="primary" @click="saveAISettings">Save AI Settings</n-button>
            </n-form-item>
          </n-form>
        </n-card>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'

const message = useMessage()

// Backend settings
const backendSettings = ref({
  coingeckoApiKey: '',
  etherscanApiKey: '',
  geminiApiKey: '',
  deepseekApiKey: '',
  marketSyncInterval: 60,
  aiAnalysisInterval: 300,
  onchainSyncInterval: 600,
})

// Frontend settings
const frontendSettings = ref({
  siteName: 'AI Crypto Hub',
  bannerImageUrl: '',
  announcementText: '',
  maintenanceMode: false,
  metaTitle: 'AI Crypto Hub - Cryptocurrency Analytics',
  metaDescription: 'Real-time cryptocurrency market data with AI-powered analysis',
})

// AI settings
const aiSettings = ref({
  systemPrompt: `You are an AI cryptocurrency analyst. Analyze the provided market data and sentiment indicators to provide trading signals.`,
  rsiOverbought: 70,
  rsiOversold: 30,
  whaleThreshold: 100000,
  sentimentWeight: 40,
})

// Save handlers
async function saveBackendSettings() {
  message.loading('Saving backend settings...')
  // TODO: POST /admin/settings/backend
  setTimeout(() => message.success('Backend settings saved'), 1000)
}

async function saveFrontendSettings() {
  message.loading('Saving frontend settings...')
  // TODO: POST /admin/settings/frontend
  setTimeout(() => message.success('Frontend settings saved'), 1000)
}

async function saveAISettings() {
  message.loading('Saving AI settings...')
  // TODO: POST /admin/settings/ai
  setTimeout(() => message.success('AI settings saved'), 1000)
}

// Fetch current settings
async function fetchSettings() {
  try {
    // TODO: GET /admin/settings
  } catch (error) {
    message.error('Failed to load settings')
  }
}

onMounted(() => {
  fetchSettings()
})
</script>

<style scoped>
.settings-view {
  max-width: 900px;
}

.section-header {
  margin-bottom: 24px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
}
</style>
