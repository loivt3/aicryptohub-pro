<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="risk-modal-overlay" @click.self="close">
        <div class="risk-modal">
          <!-- Header -->
          <div class="modal-header" :class="getRiskClass(risk?.risk_level)">
            <div class="header-left">
              <Icon name="ph:shield-warning-bold" size="24" />
              <div>
                <h3>{{ risk?.symbol }} Risk Analysis</h3>
                <p class="risk-subtitle">{{ risk?.name }}</p>
              </div>
            </div>
            <button class="close-btn" @click="close">
              <Icon name="ph:x-bold" size="20" />
            </button>
          </div>

          <!-- Risk Score -->
          <div class="risk-score-section">
            <div class="score-circle" :class="getRiskClass(risk?.risk_level)">
              <span class="score-value">{{ risk?.risk_score || 0 }}</span>
              <span class="score-label">RISK</span>
            </div>
            <div class="score-info">
              <span class="risk-level-badge" :class="getRiskClass(risk?.risk_level)">
                {{ risk?.risk_label || risk?.risk_level?.replace('_', ' ') }}
              </span>
              <p class="risk-summary">{{ risk?.summary }}</p>
            </div>
          </div>

          <!-- Risk Factors Breakdown -->
          <div class="factors-section">
            <h4>Risk Factors</h4>
            
            <!-- Volatility -->
            <div class="factor-item" v-if="risk?.factors?.volatility">
              <div class="factor-header">
                <Icon name="ph:chart-line-up-bold" size="16" />
                <span>Volatility</span>
                <span class="factor-score">{{ risk.factors.volatility.score }}/100</span>
              </div>
              <div class="factor-bar">
                <div class="factor-fill" :style="{ width: `${risk.factors.volatility.score}%` }"></div>
              </div>
              <p class="factor-desc">{{ risk.factors.volatility.description }}</p>
              <div class="factor-details" v-if="risk.factors.volatility.change_24h !== undefined">
                <span>24h: ±{{ risk.factors.volatility.change_24h }}%</span>
                <span v-if="risk.factors.volatility.change_7d">7d: ±{{ risk.factors.volatility.change_7d }}%</span>
              </div>
            </div>

            <!-- Volume Ratio -->
            <div class="factor-item" v-if="risk?.factors?.volume_ratio">
              <div class="factor-header">
                <Icon name="ph:chart-bar-bold" size="16" />
                <span>Volume Activity</span>
                <span class="factor-score">{{ risk.factors.volume_ratio.score }}/100</span>
              </div>
              <div class="factor-bar">
                <div class="factor-fill" :style="{ width: `${risk.factors.volume_ratio.score}%` }"></div>
              </div>
              <p class="factor-desc">{{ risk.factors.volume_ratio.description }}</p>
              <div class="factor-details" v-if="risk.factors.volume_ratio.volume_ratio !== undefined">
                <span>Vol/Cap: {{ risk.factors.volume_ratio.volume_ratio }}%</span>
              </div>
            </div>

            <!-- Market Cap -->
            <div class="factor-item" v-if="risk?.factors?.market_cap">
              <div class="factor-header">
                <Icon name="ph:coins-bold" size="16" />
                <span>Market Cap</span>
                <span class="factor-score">{{ risk.factors.market_cap.score }}/100</span>
              </div>
              <div class="factor-bar">
                <div class="factor-fill" :style="{ width: `${risk.factors.market_cap.score}%` }"></div>
              </div>
              <p class="factor-desc">{{ risk.factors.market_cap.description }}</p>
            </div>

            <!-- Regulatory -->
            <div class="factor-item" v-if="risk?.factors?.regulatory">
              <div class="factor-header">
                <Icon name="ph:scales-bold" size="16" />
                <span>Regulatory</span>
                <span class="factor-score" :class="{ 'warning': risk.factors.regulatory.has_issues }">
                  {{ risk.factors.regulatory.score }}/100
                </span>
              </div>
              <div class="factor-bar">
                <div class="factor-fill" :class="{ 'danger': risk.factors.regulatory.has_issues }" 
                     :style="{ width: `${risk.factors.regulatory.score}%` }"></div>
              </div>
              <p class="factor-desc">{{ risk.factors.regulatory.description }}</p>
            </div>

            <!-- Age/Maturity -->
            <div class="factor-item" v-if="risk?.factors?.age">
              <div class="factor-header">
                <Icon name="ph:clock-bold" size="16" />
                <span>Maturity</span>
                <span class="factor-score">{{ risk.factors.age.score }}/100</span>
              </div>
              <div class="factor-bar">
                <div class="factor-fill" :style="{ width: `${risk.factors.age.score}%` }"></div>
              </div>
              <p class="factor-desc">{{ risk.factors.age.description }}</p>
            </div>
          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <span class="calculated-at">
              <Icon name="ph:clock" size="14" />
              {{ formatTime(risk?.calculated_at) }}
            </span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
interface RiskData {
  coin_id: string
  symbol: string
  name: string
  risk_score: number
  risk_level: string
  risk_label: string
  risk_color: string
  factors: Record<string, any>
  summary: string
  calculated_at: string
}

const props = defineProps<{
  visible: boolean
  risk: RiskData | null
}>()

const emit = defineEmits(['close'])

const close = () => emit('close')

const getRiskClass = (level: string | undefined) => {
  const classMap: Record<string, string> = {
    'NO_RISK': 'no-risk',
    'SAFE': 'safe',
    'LOW_RISK': 'low-risk',
    'MED_RISK': 'med-risk',
    'VOLATILE': 'volatile',
    'EXTREME': 'extreme',
    'LAWSUIT': 'lawsuit',
  }
  return classMap[level || ''] || 'med-risk'
}

const formatTime = (isoString: string | undefined) => {
  if (!isoString) return ''
  return new Date(isoString).toLocaleString()
}
</script>

<style scoped>
.risk-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 9999;
}

.risk-modal {
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  background: linear-gradient(180deg, #1a1f2e 0%, #0f1420 100%);
  border-radius: 24px 24px 0 0;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.risk-subtitle {
  margin: 4px 0 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

/* Header colors by risk level */
.modal-header.no-risk { color: #6b7280; }
.modal-header.safe { color: #38efeb; }
.modal-header.low-risk { color: #10b981; }
.modal-header.med-risk { color: #eab308; }
.modal-header.volatile { color: #f97316; }
.modal-header.extreme { color: #ef4444; }
.modal-header.lawsuit { color: #ec4899; }

.close-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  cursor: pointer;
}

/* Risk Score Section */
.risk-score-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 3px solid currentColor;
}

.score-circle.no-risk { border-color: #6b7280; color: #6b7280; }
.score-circle.safe { border-color: #38efeb; color: #38efeb; }
.score-circle.low-risk { border-color: #10b981; color: #10b981; }
.score-circle.med-risk { border-color: #eab308; color: #eab308; }
.score-circle.volatile { border-color: #f97316; color: #f97316; }
.score-circle.extreme { border-color: #ef4444; color: #ef4444; }
.score-circle.lawsuit { border-color: #ec4899; color: #ec4899; }

.score-value {
  font-size: 28px;
  font-weight: 700;
}

.score-label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1px;
  opacity: 0.7;
}

.score-info {
  flex: 1;
}

.risk-level-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: rgba(255, 255, 255, 0.1);
}

.risk-level-badge.no-risk { background: rgba(107, 114, 128, 0.2); color: #6b7280; }
.risk-level-badge.safe { background: rgba(56, 239, 235, 0.2); color: #38efeb; }
.risk-level-badge.low-risk { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.risk-level-badge.med-risk { background: rgba(234, 179, 8, 0.2); color: #eab308; }
.risk-level-badge.volatile { background: rgba(249, 115, 22, 0.2); color: #f97316; }
.risk-level-badge.extreme { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.risk-level-badge.lawsuit { background: rgba(236, 72, 153, 0.2); color: #ec4899; }

.risk-summary {
  margin: 12px 0 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
}

/* Factors Section */
.factors-section {
  padding: 0 20px 20px;
}

.factors-section h4 {
  margin: 0 0 16px;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.factor-item {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 10px;
}

.factor-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  font-weight: 500;
}

.factor-score {
  margin-left: auto;
  font-weight: 600;
  color: #10b981;
}

.factor-score.warning {
  color: #ef4444;
}

.factor-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 8px;
}

.factor-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #eab308);
  border-radius: 2px;
  transition: width 0.5s ease-out;
}

.factor-fill.danger {
  background: linear-gradient(90deg, #ef4444, #ec4899);
}

.factor-desc {
  margin: 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.factor-details {
  display: flex;
  gap: 12px;
  margin-top: 8px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

/* Footer */
.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  text-align: center;
}

.calculated-at {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

/* Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .risk-modal,
.modal-leave-to .risk-modal {
  transform: translateY(100%);
}
</style>
