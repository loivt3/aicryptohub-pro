<template>
  <div class="mobile-news">
    <!-- Header -->
    <SharedMobileHeader active-tab="news" />

    <!-- Main Content -->
    <main class="news-main">
      
      <!-- Trending Carousel (Bento Large) -->
      <section class="news-section">
        <h3 class="section-title">🔥 Trending Now</h3>
        <div class="trending-carousel">
          <div v-for="item in trendingNews" :key="item.id" class="trending-card glass-card">
            <img :src="item.image" class="trending-bg" />
            <div class="trending-overlay">
              <span class="category-badge">{{ item.category }}</span>
              <h4 class="trending-title">{{ item.title }}</h4>
              <span class="trending-time">{{ item.time_ago }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Bento Grid Categories -->
      <section class="news-section">
        <div class="bento-grid">
            <!-- Market Update (Medium) -->
            <div class="bento-card medium glass-card">
                <div class="card-header">
                    <Icon name="ph:chart-line-up" class="w-4 h-4 text-green-400" />
                    <span>Market</span>
                </div>
                <div class="card-body">
                    <p class="news-headline">Bitcoin breaks $98k resistance level</p>
                    <span class="news-meta">CoinDesk • 20m ago</span>
                </div>
            </div>

            <!-- Regulations (Medium) -->
            <div class="bento-card medium glass-card">
                <div class="card-header">
                    <Icon name="ph:gavel" class="w-4 h-4 text-yellow-400" />
                    <span>Policy</span>
                </div>
                <div class="card-body">
                    <p class="news-headline">EU passes new stablecoin regulations</p>
                    <span class="news-meta">Reuters • 1h ago</span>
                </div>
            </div>

            <!-- Latest Speed (Small - List) -->
            <div class="bento-card large glass-card">
                <div class="card-header">
                    <Icon name="ph:lightning" class="w-4 h-4 text-blue-400" />
                    <span>Latest Updates</span>
                </div>
                <div class="quick-list">
                    <div v-for="news in latestNews" :key="news.id" class="quick-item">
                        <img :src="news.sourceIcon" class="source-icon" />
                        <div class="quick-info">
                            <span class="quick-title">{{ news.title }}</span>
                            <span class="quick-time">{{ news.source }} • {{ news.time_ago }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
      </section>

    </main>

    <!-- Footer -->
    <SharedMobileFooter active-tab="news" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const trendingNews = ref([
    { 
        id: 1, 
        title: "Bitcoin ETF Inflows Hit Record High as Institutions buy the dip", 
        image: "https://images.unsplash.com/photo-1518546305927-5a440611f3a3?q=80&w=2671&auto=format&fit=crop", 
        category: "Market", 
        time_ago: "2h ago" 
    },
    { 
        id: 2, 
        title: "Ethereum Upgrade 'Pectra' scheduled for Q1 2025", 
        image: "https://images.unsplash.com/photo-1620321023374-d1a68fdd720d?q=80&w=2697&auto=format&fit=crop", 
        category: "Tech", 
        time_ago: "4h ago" 
    }
])

const latestNews = ref([
    { id: 101, title: "Solana outages reduced by 99% in 2024", source: "Decrypt", sourceIcon: "https://www.google.com/s2/favicons?domain=decrypt.co", time_ago: "15m ago" },
    { id: 102, title: "Binance lists new AI tokens", source: "Binance Blog", sourceIcon: "https://www.google.com/s2/favicons?domain=binance.com", time_ago: "30m ago" },
    { id: 103, title: "MicroStrategy buys another 10k BTC", source: "Bloomberg", sourceIcon: "https://www.google.com/s2/favicons?domain=bloomberg.com", time_ago: "45m ago" },
    { id: 104, title: "Ripple vs SEC lawsuit updates", source: "CoinTelegraph", sourceIcon: "https://www.google.com/s2/favicons?domain=cointelegraph.com", time_ago: "1h ago" }
])

</script>

<style scoped>
/* Glassmorphism & Layout matching MobileHome */
.mobile-news {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0f14 0%, #0d1117 50%, #0a0f14 100%);
  padding-bottom: 80px;
}

.news-main {
  padding: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 12px;
}

.news-section {
  margin-bottom: 24px;
}

/* Trending Carousel */
.trending-carousel {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 4px; /* for scrollbar spacing if needed */
  scrollbar-width: none;
}

.trending-card {
  min-width: 280px;
  height: 160px;
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  flex-shrink: 0;
}

.trending-bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.trending-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);
  padding: 12px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  height: 100%;
}

.category-badge {
  align-self: flex-start;
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  margin-bottom: 6px;
  backdrop-filter: blur(4px);
}

.trending-title {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  line-height: 1.3;
  margin-bottom: 4px;
}

.trending-time {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
}

/* Bento Grid */
.bento-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  gap: 12px;
}

.glass-card {
  background: rgba(15, 25, 35, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 12px;
}

.bento-card.medium {
  grid-column: span 1;
  height: 140px; /* Fixed height for symmetry */
  display: flex;
  flex-direction: column;
}

.bento-card.large {
  grid-column: span 2; /* Full width */
}

.card-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 8px;
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.news-headline {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  line-height: 1.4;
}

.news-meta {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
}

/* Quick List */
.quick-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quick-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.quick-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.source-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.quick-info {
  display: flex;
  flex-direction: column;
}

.quick-title {
  font-size: 13px;
  font-weight: 500;
  color: #e5e7eb;
  line-height: 1.3;
}

.quick-time {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 2px;
}
</style>
