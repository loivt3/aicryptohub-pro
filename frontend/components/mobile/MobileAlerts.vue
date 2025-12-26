<template>
  <div class="mobile-alerts">
    <!-- Header -->
    <SharedMobileHeader active-tab="alerts" />

    <!-- MAIN SINGLE FEED CONTENT -->
    <main class="content-main">
      
      <!-- 0. AI HIGHLIGHTS (NEW) -->
      <section class="mb-6">
        <div class="flex justify-between items-center mb-4 px-1">
            <h3 class="flex items-center gap-2 text-lg font-bold text-white">
                <Icon name="ph:sparkle" class="text-cyan-400" /> AI Highlights
            </h3>
            <button class="text-xs text-cyan-400 hover:underline">View All</button>
        </div>

        <div class="grid grid-cols-2 gap-3">
            <!-- Bullish Signal Card -->
            <div class="ai-highlight-card bullish">
                <div class="ai-highlight-header">
                    <div class="ai-icon bullish">
                        <Icon name="ph:trend-up-bold" size="18" />
                    </div>
                    <div class="ai-meta">
                        <span class="ai-title">Bullish Signal: BTC</span>
                        <span class="ai-confidence">Confidence: 85%</span>
                    </div>
                </div>
                
                <!-- Green Sparkline -->
                <div class="ai-sparkline">
                    <svg viewBox="0 0 100 40" preserveAspectRatio="none">
                        <defs>
                            <linearGradient id="bullish-grad" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" stop-color="rgba(16, 185, 129, 0.4)" />
                                <stop offset="100%" stop-color="rgba(16, 185, 129, 0)" />
                            </linearGradient>
                        </defs>
                        <path d="M0,35 C10,32 20,28 30,22 S50,12 60,10 S80,8 100,5 L100,40 L0,40 Z" fill="url(#bullish-grad)" />
                        <path d="M0,35 C10,32 20,28 30,22 S50,12 60,10 S80,8 100,5" fill="none" stroke="#10b981" stroke-width="2" />
                    </svg>
                </div>
                
                <p class="ai-description">AI predicts upward trend in 4h based on trading volume patterns.</p>
            </div>

            <!-- Risk Alert Card -->
            <div class="ai-highlight-card bearish">
                <div class="ai-highlight-header">
                    <div class="ai-icon bearish">
                        <Icon name="ph:warning-bold" size="18" />
                    </div>
                    <div class="ai-meta">
                        <span class="ai-title">Risk Alert</span>
                        <span class="ai-subtitle">ETH Volatility</span>
                    </div>
                </div>
                
                <!-- Red Sparkline -->
                <div class="ai-sparkline">
                    <svg viewBox="0 0 100 40" preserveAspectRatio="none">
                        <defs>
                            <linearGradient id="bearish-grad" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" stop-color="rgba(239, 68, 68, 0.3)" />
                                <stop offset="100%" stop-color="rgba(239, 68, 68, 0)" />
                            </linearGradient>
                        </defs>
                        <path d="M0,20 L10,15 L20,25 L30,18 L40,28 L50,22 L60,30 L70,20 L80,32 L90,25 L100,28 L100,40 L0,40 Z" fill="url(#bearish-grad)" />
                        <path d="M0,20 L10,15 L20,25 L30,18 L40,28 L50,22 L60,30 L70,20 L80,32 L90,25 L100,28" fill="none" stroke="#ef4444" stroke-width="2" />
                    </svg>
                </div>
                
                <p class="ai-description">Unusually high volatility detected. Consider reducing leverage.</p>
            </div>
        </div>
      </section>

      <!-- 1. ACTIVE MONITORING (Moved to Top as requested) -->
      <section class="mb-6">
        <div class="flex justify-between items-center mb-4 px-1">
            <h3 class="flex items-center gap-2 text-lg font-bold text-white">
                <Icon name="ph:target" class="text-emerald-400" /> Active Monitoring
            </h3>
             <button class="bg-emerald-500/20 text-emerald-400 px-3 py-1.5 rounded-full text-xs font-bold flex items-center gap-1 border border-emerald-500/30">
                <Icon name="ph:plus-bold" /> New Alert
            </button>
        </div>

        <div class="grid grid-cols-2 gap-3">
            <!-- Price Alerts -->
            <div class="bg-slate-800/60 border border-white/5 rounded-2xl p-4 flex flex-col justify-between h-[180px]">
                <div class="flex justify-between items-start">
                    <div class="w-10 h-10 rounded-xl bg-slate-700/50 flex items-center justify-center text-emerald-400">
                        <Icon name="ph:bell-ringing-bold" size="20" />
                    </div>
                    <div class="text-right">
                        <span class="text-[10px] text-slate-500 font-bold uppercase block">Active</span>
                        <span class="text-xl font-bold text-white">3</span>
                    </div>
                </div>
                <div>
                     <span class="text-sm font-bold text-white block mb-3">Price Alerts</span>
                     <div class="space-y-2">
                        <div class="flex justify-between items-center bg-slate-700/30 rounded-lg p-2 border border-white/5">
                            <div class="flex items-center gap-2">
                                <span class="w-2 h-2 rounded-full bg-orange-500"></span>
                                <span class="text-xs font-bold text-white">BTC</span>
                            </div>
                            <span class="text-xs font-mono text-emerald-400">> $100k</span>
                        </div>
                         <div class="flex justify-between items-center bg-slate-700/30 rounded-lg p-2 border border-white/5">
                            <div class="flex items-center gap-2">
                                <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                                <span class="text-xs font-bold text-white">ETH</span>
                            </div>
                            <span class="text-xs font-mono text-emerald-400">< $3.2k</span>
                        </div>
                     </div>
                </div>
            </div>

            <!-- AI Watchdog -->
            <div class="bg-slate-800/60 border border-white/5 rounded-2xl p-4 flex flex-col h-[180px] relative overflow-hidden">
                <div class="flex justify-between items-start mb-3">
                    <div class="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center text-purple-400">
                        <Icon name="ph:robot-bold" size="20" />
                    </div>
                    <span class="bg-purple-500/20 text-purple-300 px-2 py-1 rounded text-[10px] font-bold border border-purple-500/30">NEW SIGNAL</span>
                </div>
                
                <span class="text-sm font-bold text-white mb-1">AI Watchdog</span>
                <p class="text-[10px] text-slate-400 mb-3">Based on predictive models</p>

                <div class="mt-auto bg-purple-500/10 border border-purple-500/20 rounded-xl p-3">
                    <div class="flex gap-2">
                         <Icon name="ph:trend-up-bold" class="text-purple-400 shrink-0 mt-0.5" />
                         <p class="text-[10px] text-slate-200 leading-tight">
                            Abnormal volatility detected in <span class="text-purple-400 font-bold">DeFi Sector</span>.
                         </p>
                    </div>
                </div>
            </div>
        </div>
      </section>

      <!-- 2. ON-CHAIN ALERTS (Timeline) -->
      <section class="mb-6">
        <div class="flex justify-between items-center mb-4 px-1">
            <h3 class="flex items-center gap-2 text-lg font-bold text-white">
                <Icon name="ph:circles-three-plus" class="text-cyan-400" /> On-Chain Alerts
            </h3>
            <span class="text-xs text-slate-400 flex items-center gap-1">Filter <Icon name="ph:funnel" /></span>
        </div>

        <div class="relative pl-4">
            <!-- Timeline Line -->
            <div class="absolute left-[27px] top-4 bottom-0 w-[2px] bg-slate-700"></div>

            <div v-for="event in onChainEvents" :key="event.id" class="relative mb-6 last:mb-0">
                <!-- Icon -->
                <div class="absolute left-0 top-0 w-14 h-14 flex items-center justify-start z-10">
                    <div class="w-10 h-10 rounded-full border-4 border-[#131b2c] flex items-center justify-center bg-slate-800 text-cyan-400 shrink-0 shadow-lg">
                        <Icon :name="getEventIcon(event.action)" size="20" />
                    </div>
                </div>

                <!-- Card -->
                <div class="ml-14 bg-slate-800/60 border border-white/5 rounded-2xl p-4 backdrop-blur-sm">
                    <div class="flex justify-between items-start mb-2">
                        <div class="flex items-center gap-2">
                            <span class="text-xs font-bold text-cyan-400 uppercase tracking-wider">{{ event.title }}</span>
                            <span class="text-xs text-slate-500">{{ event.time }}</span>
                        </div>
                        <Icon name="ph:arrow-square-out" class="text-slate-500 text-sm" />
                    </div>
                    
                    <div class="flex items-center gap-2 mb-3">
                        <div class="flex -space-x-2">
                            <img :src="event.icon1" class="w-6 h-6 rounded-full border border-slate-700" />
                            <Icon name="ph:arrow-right" class="w-6 h-6 p-1 bg-slate-700 rounded-full text-white/50" />
                            <img :src="event.icon2" class="w-6 h-6 rounded-full border border-slate-700" />
                        </div>
                        <span class="text-sm font-semibold text-white">
                            {{ event.entity }} <span class="text-slate-500">→</span> {{ event.target }}
                        </span>
                    </div>

                    <div class="text-xl font-bold text-white mb-2">
                        {{ event.amount }} <span class="text-emerald-400 text-sm font-bold">{{ event.currency }}</span>
                    </div>
                    <p class="text-xs text-slate-400 leading-relaxed">{{ event.desc }}</p>
                </div>
            </div>
        </div>
      </section>

      <!-- 3. AI NEWS FEED -->
      <section class="mb-4">
        <div class="flex justify-between items-center mb-4 px-1">
            <h3 class="flex items-center gap-2 text-lg font-bold text-white">
                <Icon name="ph:sparkle-fill" class="text-emerald-400" /> AI News Feed
            </h3>
            <span class="text-xs text-slate-400 font-semibold">View All</span>
        </div>

        <!-- Hero Card -->
        <div class="relative w-full aspect-[4/3] rounded-3xl overflow-hidden mb-4 group shadow-xl shadow-black/50">
            <img src="https://images.unsplash.com/photo-1642104704074-907c0698cbd9?q=80&w=2832&auto=format&fit=crop" class="absolute inset-0 w-full h-full object-cover" />
            <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent"></div>
            
            <div class="absolute bottom-0 left-0 right-0 p-5">
                <div class="flex items-center gap-2 mb-3">
                    <span class="bg-emerald-500 text-black text-xs font-extrabold px-3 py-1 rounded-full">FOMO</span>
                    <span class="text-xs text-slate-300 font-medium">2m ago • Coindesk</span>
                </div>
                <h2 class="text-2xl font-bold text-white leading-tight mb-4">Bitcoin ETF Approval Imminent?</h2>
                
                <div class="bg-slate-800/80 backdrop-blur-md border border-white/10 rounded-xl p-3 flex gap-3">
                    <div class="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0">
                         <Icon name="ph:brain-bold" />
                    </div>
                    <p class="text-xs text-slate-200 leading-relaxed">
                        SEC hints at positive outcome in latest filing reviews. Analysts predict <span class="font-bold text-emerald-300">90% chance</span> of approval by Tuesday.
                    </p>
                </div>
            </div>
        </div>

        <!-- Feed List -->
        <div class="space-y-3">
            <div v-for="news in aiNewsFeed" :key="news.id" class="bg-slate-800/40 border border-white/5 rounded-2xl p-4 flex gap-4">
                 <div class="w-12 h-12 rounded-xl bg-slate-700/50 shrink-0 overflow-hidden">
                    <img :src="news.image" class="w-full h-full object-cover opacity-80" />
                 </div>
                 <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded" :class="getTagStyle(news.tag)">{{ news.tag }}</span>
                        <span class="text-[10px] text-slate-500">{{ news.time_ago }}</span>
                    </div>
                    <h4 class="text-sm font-bold text-white leading-tight">{{ news.title }}</h4>
                 </div>
            </div>
        </div>
      </section>

    </main>

    <SharedMobileFooter active-tab="alerts" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'

const api = useApi()

const onChainEvents = ref<any[]>([])
const aiNewsFeed = ref<any[]>([])
const heroNews = ref<any>(null)
const isLoading = ref(true)

// Fetch real data on mount
onMounted(async () => {
    await fetchData()
})

async function fetchData() {
    isLoading.value = true
    
    try {
        // Fetch on-chain whale transactions for alerts
        const onchainRes = await api.getOnchainSummary()
        if (onchainRes?.recent_whale_txs?.length > 0) {
            onChainEvents.value = onchainRes.recent_whale_txs.slice(0, 5).map((tx: any, idx: number) => ({
                id: idx + 1,
                title: tx.tx_type === 'exchange_deposit' ? 'EXCHANGE INFLOW' : 
                       tx.tx_type === 'exchange_withdraw' ? 'EXCHANGE OUTFLOW' : 'WHALE MOVE',
                time: formatTimeAgo(tx.tx_timestamp),
                entity: tx.exchange_name || shortenAddress(tx.from_address),
                target: tx.exchange_name || shortenAddress(tx.to_address),
                action: tx.tx_type === 'exchange_deposit' ? 'transfer' : 
                        tx.tx_type === 'exchange_withdraw' ? 'swap' : 'transfer',
                amount: formatAmount(tx.value_usd),
                currency: tx.coin_id?.toUpperCase() || 'USD',
                desc: tx.tx_type === 'exchange_deposit' 
                    ? 'Large exchange inflow detected. Potential sell pressure.'
                    : tx.tx_type === 'exchange_withdraw'
                    ? 'Exchange outflow detected. Bullish accumulation signal.'
                    : 'Large wallet-to-wallet transfer detected.',
                icon1: `https://assets.coingecko.com/coins/images/${getCoinImage(tx.coin_id)}`,
                icon2: tx.exchange_name 
                    ? `https://assets.coingecko.com/markets/images/52/small/binance.jpg`
                    : `https://assets.coingecko.com/coins/images/1/small/bitcoin.png`,
            }))
        }
        
        // Fetch news - try hero first
        try {
            const heroRes = await api.getHeroNews()
            if (heroRes?.success && heroRes.article) {
                heroNews.value = heroRes.article
            }
        } catch (e) { /* fallback to default hero */ }
        
        // Fetch live news feed from CryptoPanic via NewsAggregator
        try {
            const newsRes = await api.getNewsFeed(5)
            if (newsRes?.success && newsRes.articles?.length > 0) {
                aiNewsFeed.value = newsRes.articles.map((article: any) => ({
                    id: article.id,
                    tag: article.tag || 'NEWS',
                    title: article.title,
                    time_ago: article.time_ago,
                    image: article.image || 'https://images.unsplash.com/photo-1620321023374-d1a68fdd720d?q=80&w=200',
                }))
            }
        } catch (e) { /* keep fallback data */ }
        
    } catch (error) {
        console.error('Failed to fetch alerts data:', error)
    } finally {
        isLoading.value = false
    }
    
    // Use fallback data if APIs return empty
    if (onChainEvents.value.length === 0) {
        onChainEvents.value = [
            { id: 1, title: 'WHALE MOVE', time: '10:45 AM', entity: 'Large Wallet', target: 'Binance', action: 'transfer', amount: '50,000,000', currency: 'USDT', desc: 'Large exchange inflow detected.', icon1: 'https://assets.coingecko.com/coins/images/325/small/Tether.png', icon2: 'https://assets.coingecko.com/markets/images/52/small/binance.jpg' },
        ]
    }
    if (aiNewsFeed.value.length === 0) {
        aiNewsFeed.value = [
            { id: 102, tag: 'LEGIT', title: 'Ethereum Pectra Upgrade Confirmed for Q1', time_ago: '30m ago', image: 'https://images.unsplash.com/photo-1620321023374-d1a68fdd720d?q=80&w=200' },
            { id: 103, tag: 'FUD', title: 'SEC investigation rumors causing panic', time_ago: '45m ago', image: 'https://plus.unsplash.com/premium_photo-1681487767138-ddf2d67b35c1?q=80&w=200' },
        ]
    }
}

function formatTimeAgo(timestamp: string): string {
    if (!timestamp) return 'Just now'
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    return `${Math.floor(diffHours / 24)}d ago`
}

function formatAmount(value: number): string {
    if (!value) return '0'
    if (value >= 1000000000) return (value / 1000000000).toFixed(1) + 'B'
    if (value >= 1000000) return (value / 1000000).toFixed(1) + 'M'
    if (value >= 1000) return (value / 1000).toFixed(1) + 'K'
    return value.toFixed(0)
}

function shortenAddress(addr: string): string {
    if (!addr) return 'Unknown'
    return addr.slice(0, 6) + '...' + addr.slice(-4)
}

function getCoinImage(coinId: string): string {
    const mapping: Record<string, string> = {
        'tether': '325/small/Tether.png',
        'usd-coin': '6319/small/USD_Coin_icon.png',
        'chainlink': '877/small/chainlink.png',
        'aave': '12645/small/aave-token.png',
        'uniswap': '12504/small/uniswap.png',
    }
    return mapping[coinId] || '1/small/bitcoin.png'
}

const getEventIcon = (action: string) => {
    if (action === 'transfer') return 'ph:arrows-left-right-bold'
    if (action === 'swap') return 'ph:swap-bold'
    return 'ph:coins-bold'
}

const getTagStyle = (tag: string) => {
    if (tag === 'LEGIT') return 'bg-blue-500/20 text-blue-400'
    if (tag === 'FUD') return 'bg-red-500/20 text-red-400'
    if (tag === 'FOMO') return 'bg-emerald-500/20 text-emerald-400'
    if (tag === 'BREAKING') return 'bg-orange-500/20 text-orange-400'
    return 'bg-slate-700 text-slate-300'
}

</script>

<style scoped>
.mobile-alerts {
  min-height: 100vh;
  /* Exact gradient match from MobileHome.vue */
  background: linear-gradient(180deg, #0a0f14 0%, #0d1117 50%, #0a0f14 100%);
  padding-bottom: 90px;
  font-family: 'Inter', sans-serif;
  color: #f8fafc;
}
.content-main { padding: 16px; margin-top: 8px; }

/* AI Highlights Cards */
.ai-highlight-card {
  background: rgba(15, 25, 35, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 16px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  min-height: 180px;
  position: relative;
  overflow: hidden;
}

.ai-highlight-card.bullish {
  border: 1px solid rgba(16, 185, 129, 0.25);
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.1);
}

.ai-highlight-card.bearish {
  border: 1px solid rgba(239, 68, 68, 0.25);
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.1);
}

.ai-highlight-header {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 12px;
}

.ai-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ai-icon.bullish {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.ai-icon.bearish {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.ai-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ai-title {
  font-size: 13px;
  font-weight: 700;
  color: #fff;
}

.ai-confidence {
  font-size: 11px;
  color: #10b981;
  font-weight: 500;
}

.ai-subtitle {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

.ai-sparkline {
  flex: 1;
  min-height: 50px;
  margin: 8px 0;
}

.ai-sparkline svg {
  width: 100%;
  height: 100%;
}

.ai-description {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.4;
  margin-top: auto;
}
</style>
