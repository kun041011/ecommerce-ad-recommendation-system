<template>
  <div class="product-card" @click="$router.push(`/product/${product.id}`)">
    <div class="card-img" :style="{ background: gradientColor }">
      <span class="card-emoji">{{ categoryEmoji }}</span>
      <div class="card-badges">
        <span class="badge badge--red" v-if="product.sales_count > 100">热销</span>
        <span class="badge badge--orange">包邮</span>
      </div>
    </div>
    <div class="card-body">
      <div class="card-name">{{ product.name }}</div>
      <div class="card-price-row">
        <span class="price-symbol">¥</span>
        <span class="price-main">{{ Math.floor(product.price) }}</span>
        <span class="price-decimal">.{{ ((product.price % 1) * 100).toFixed(0).padStart(2, '0') }}</span>
        <span class="price-original">¥{{ (product.price * 1.3).toFixed(0) }}</span>
      </div>
      <div class="card-stats">
        <span class="card-sales">已售 {{ product.sales_count }}+</span>
        <span class="card-rating">好评</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ product: any }>()

const gradients = [
  'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
  'linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)',
  'linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%)',
  'linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%)',
  'linear-gradient(135deg, #ffd89b 0%, #19547b 100%)',
  'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
  'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
  'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)',
]

const emojiMap: Record<string, string> = {
  '电子产品': '📱', '服装鞋帽': '👗', '图书音像': '📚', '家居家装': '🏠',
  '食品饮料': '🍔', '运动户外': '⚽', '玩具母婴': '🧸', '美妆个护': '💄',
  '汽车用品': '🚗', '园艺花卉': '🌱',
}

const gradientColor = computed(() => gradients[(props.product.id || 0) % gradients.length])
const categoryEmoji = computed(() => {
  for (const tag of (props.product.tags || [])) { if (emojiMap[tag]) return emojiMap[tag] }
  return '🛍️'
})
</script>

<style scoped>
.product-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
}
.product-card:hover {
  border-color: var(--jd-red);
  box-shadow: 0 4px 16px rgba(225, 37, 27, 0.1);
  transform: translateY(-2px);
}

.card-img {
  height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.card-emoji { font-size: 56px; filter: drop-shadow(0 2px 6px rgba(0,0,0,0.15)); }

.card-badges { position: absolute; top: 8px; left: 8px; display: flex; gap: 4px; }
.badge {
  font-size: 11px; padding: 2px 6px; border-radius: 3px;
  color: #fff; font-weight: 600;
}
.badge--red { background: var(--jd-red); }
.badge--orange { background: var(--taobao-orange); }

.card-body { padding: 12px; }

.card-name {
  font-size: 14px; color: var(--text-dark);
  line-height: 1.4; height: 40px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden; margin-bottom: 8px;
}

.card-price-row { display: flex; align-items: baseline; margin-bottom: 6px; }
.price-symbol { font-size: 14px; font-weight: 700; color: var(--price-red); }
.price-main { font-size: 22px; font-weight: 700; color: var(--price-red); }
.price-decimal { font-size: 14px; font-weight: 700; color: var(--price-red); }
.price-original { font-size: 12px; color: #bbb; text-decoration: line-through; margin-left: 6px; }

.card-stats { display: flex; justify-content: space-between; font-size: 12px; color: var(--text-light); }
.card-rating { color: var(--taobao-orange); }
</style>
