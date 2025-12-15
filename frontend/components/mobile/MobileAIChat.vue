<template>
  <div class="mobile-aichat">
    <!-- Header -->
    <section class="m-section">
      <h3 class="m-section-title">🤖 AI Chat</h3>
      <p class="m-text-muted" style="font-size: 12px;">Ask me anything about crypto!</p>
    </section>

    <!-- Chat Messages -->
    <section class="m-section">
      <div class="m-chat-container" ref="chatContainer">
        <div v-for="msg in messages" :key="msg.id" class="m-chat-msg" :class="msg.role">
          <div class="m-chat-avatar">
            {{ msg.role === 'user' ? '👤' : '🤖' }}
          </div>
          <div class="m-chat-bubble">
            <p class="m-chat-text" v-html="msg.content"></p>
            <span class="m-chat-time m-text-muted">{{ msg.time }}</span>
          </div>
        </div>
        
        <!-- Typing Indicator -->
        <div v-if="isTyping" class="m-chat-msg assistant">
          <div class="m-chat-avatar">🤖</div>
          <div class="m-chat-bubble typing">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </section>

    <!-- Quick Suggestions -->
    <section class="m-section" v-if="messages.length <= 1">
      <div class="m-suggestions">
        <button 
          v-for="suggestion in suggestions" 
          :key="suggestion"
          class="m-suggestion-chip"
          @click="sendMessage(suggestion)"
        >
          {{ suggestion }}
        </button>
      </div>
    </section>

    <!-- Input Area -->
    <div class="m-chat-input-area">
      <input 
        v-model="inputMessage"
        type="text"
        class="m-chat-input"
        placeholder="Ask about crypto..."
        @keyup.enter="sendMessage(inputMessage)"
      />
      <button class="m-send-btn" @click="sendMessage(inputMessage)" :disabled="!inputMessage.trim()">
        <Icon name="ph:paper-plane-right-fill" class="w-5 h-5" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const chatContainer = ref<HTMLElement | null>(null)
const inputMessage = ref('')
const isTyping = ref(false)

const suggestions = [
  'What is Bitcoin?',
  'Best altcoins to buy?',
  'Explain DeFi',
  'Market analysis today',
]

const messages = ref([
  { 
    id: 1, 
    role: 'assistant', 
    content: 'Hello! I\'m your AI crypto assistant. How can I help you today?', 
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  },
])

const sendMessage = async (text: string) => {
  if (!text.trim()) return
  
  // Add user message
  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: text,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })
  
  inputMessage.value = ''
  isTyping.value = true
  
  // Scroll to bottom
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
  
  // Simulate AI response
  setTimeout(() => {
    isTyping.value = false
    messages.value.push({
      id: Date.now(),
      role: 'assistant',
      content: getAIResponse(text),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    })
  }, 1500)
}

const getAIResponse = (query: string): string => {
  const q = query.toLowerCase()
  if (q.includes('bitcoin')) {
    return 'Bitcoin (BTC) is the first and most well-known cryptocurrency, created by Satoshi Nakamoto in 2009. It\'s often called "digital gold" and has a maximum supply of 21 million coins. Currently trading around $98,500.'
  }
  if (q.includes('altcoin')) {
    return 'Top altcoins to consider include Ethereum (ETH), Solana (SOL), and Cardano (ADA). Always do your own research and consider factors like technology, team, and market cap before investing.'
  }
  if (q.includes('defi')) {
    return 'DeFi (Decentralized Finance) refers to financial services built on blockchain without intermediaries. Popular DeFi protocols include Uniswap, Aave, and Compound. Total DeFi TVL is currently around $85B.'
  }
  if (q.includes('market') || q.includes('analysis')) {
    return 'The crypto market is showing bullish momentum with BTC above $98k. Key resistance at $100k. Altcoins following with strong performance from L1/L2 tokens. Overall sentiment: Greed (72).'
  }
  return 'That\'s a great question! I can help you understand cryptocurrency markets, analyze coins, and provide insights on DeFi, NFTs, and more. What specific topic interests you?'
}
</script>

<style scoped>
.mobile-aichat {
  padding: 0;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 140px);
}

.m-chat-container {
  flex: 1;
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
}

.m-chat-msg {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.m-chat-msg.user {
  flex-direction: row-reverse;
}

.m-chat-avatar {
  width: 32px;
  height: 32px;
  min-width: 32px;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.m-chat-bubble {
  max-width: 80%;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  border-top-left-radius: 4px;
}

.m-chat-msg.user .m-chat-bubble {
  background: rgba(56, 239, 235, 0.15);
  border-top-left-radius: 16px;
  border-top-right-radius: 4px;
}

.m-chat-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
  color: #ffffff;
}

.m-chat-time {
  font-size: 10px;
  margin-top: 4px;
  display: block;
}

/* Typing Indicator */
.m-chat-bubble.typing {
  padding: 12px 18px;
}

.m-chat-bubble.typing span {
  display: inline-block;
  width: 8px;
  height: 8px;
  margin: 0 2px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  animation: typing 1.2s infinite;
}

.m-chat-bubble.typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.m-chat-bubble.typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 100% { opacity: 0.4; transform: translateY(0); }
  50% { opacity: 1; transform: translateY(-4px); }
}

.m-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.m-suggestion-chip {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.m-suggestion-chip:active {
  background: rgba(56, 239, 235, 0.15);
  border-color: #38efeb;
  color: #38efeb;
}

.m-chat-input-area {
  position: fixed;
  bottom: 70px;
  left: 0;
  right: 0;
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: #0b0f19;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.m-chat-input {
  flex: 1;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  color: #ffffff;
  font-size: 14px;
}

.m-chat-input:focus {
  outline: none;
  border-color: #38efeb;
}

.m-chat-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.m-send-btn {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #38efeb, #0066ff);
  border: none;
  border-radius: 50%;
  color: #000;
  cursor: pointer;
  transition: transform 0.2s;
}

.m-send-btn:active {
  transform: scale(0.95);
}

.m-send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
