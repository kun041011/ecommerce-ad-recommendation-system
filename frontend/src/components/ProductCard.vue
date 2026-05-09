<template>
  <div class="product-card" @click="$router.push(`/product/${product.id}`)">
    <div class="card-image" :style="{ background: gradientColor }">
      <span class="card-emoji">{{ categoryEmoji }}</span>
    </div>
    <div class="card-body">
      <h3 class="card-title">{{ product.name }}</h3>
      <div class="card-meta">
        <span class="card-price">¥{{ product.price.toFixed(2) }}</span>
        <span class="card-sales">{{ product.sales_count }}人已购</span>
      </div>
      <div class="card-tags" v-if="product.tags && product.tags.length">
        <el-tag size="small" v-for="tag in product.tags.slice(0, 2)" :key="tag" class="card-tag" type="info" effect="plain">
          {{ tag }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ product: any }>()

const gradients = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
  'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
  'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
  'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)',
]

const emojiMap: Record<string, string> = {
  '电子产品': '📱', 'electronics': '📱',
  '服装鞋帽': '👗', 'clothing': '👗',
  '图书音像': '📚', 'books': '📚',
  '家居家装': '🏠', 'home': '🏠',
  '食品饮料': '🍔', 'food': '🍔',
  '运动户外': '⚽', 'sports': '⚽',
  '玩具母婴': '🧸', 'toys': '🧸',
  '美妆个护': '💄', 'beauty': '💄',
  '汽车用品': '🚗', 'auto': '🚗',
  '园艺花卉': '🌱', 'garden': '🌱',
}

const gradientColor = computed(() => {
  const idx = (props.product.id || 0) % gradients.length
  return gradients[idx]
})

const categoryEmoji = computed(() => {
  const tags = props.product.tags || []
  for (const tag of tags) {
    if (emojiMap[tag]) return emojiMap[tag]
  }
  return '🛍️'
})
</script>

<style scoped>
.product-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.18);
}

.card-image {
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.card-emoji {
  font-size: 48px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.card-body {
  padding: 16px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 10px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 8px;
}

.card-price {
  font-size: 20px;
  font-weight: 700;
  color: #e74c3c;
}

.card-sales {
  font-size: 12px;
  color: #999;
}

.card-tags {
  display: flex;
  gap: 4px;
}

.card-tag {
  font-size: 11px !important;
  border-radius: 4px !important;
}
</style>
