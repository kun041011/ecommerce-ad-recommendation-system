<template>
  <div v-if="product" class="detail-page">
    <el-card class="detail-card">
      <div class="detail-layout">
        <div class="detail-image" :style="{ background: gradientColor }">
          <span class="detail-emoji">{{ categoryEmoji }}</span>
        </div>
        <div class="detail-info">
          <h1 class="detail-name">{{ product.name }}</h1>
          <div class="price-box">
            <span class="price-label">价格</span>
            <span class="price-value">¥{{ product.price.toFixed(2) }}</span>
          </div>
          <p class="detail-desc">{{ product.description }}</p>
          <div class="detail-meta">
            <el-tag effect="plain" type="info">库存: {{ product.stock }}</el-tag>
            <el-tag effect="plain" type="success">已售: {{ product.sales_count }}</el-tag>
          </div>
          <div class="detail-actions">
            <el-button type="primary" size="large" @click="addToCart" round>
              &#x1F6D2; 加入购物车
            </el-button>
            <el-button size="large" round @click="$router.push('/cart')">
              立即购买
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <el-card class="section-card">
      <ReviewSection :product-id="product.id" :show-form="!!userStore.user" />
    </el-card>

    <el-card class="section-card">
      <QASection :product-id="product.id" :show-form="!!userStore.user" />
    </el-card>

    <el-card class="section-card" v-if="similarProducts.length">
      <h3 class="section-title">相似推荐</h3>
      <div class="product-grid" style="grid-template-columns: repeat(auto-fill, minmax(200px, 1fr))">
        <ProductCard v-for="p in similarProducts" :key="p.id" :product="p" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { productApi, recommendApi, behaviorApi } from '../api'
import { useCartStore } from '../stores/cart'
import { useUserStore } from '../stores/user'
import ProductCard from '../components/ProductCard.vue'
import ReviewSection from '../components/ReviewSection.vue'
import QASection from '../components/QASection.vue'

const route = useRoute()
const cartStore = useCartStore()
const userStore = useUserStore()
const product = ref<any>(null)
const similarProducts = ref<any[]>([])

const gradients = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
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

const gradientColor = computed(() => gradients[(product.value?.id || 0) % gradients.length])
const categoryEmoji = computed(() => {
  const tags = product.value?.tags || []
  for (const t of tags) { if (emojiMap[t]) return emojiMap[t] }
  return '🛍️'
})

async function load() {
  const id = Number(route.params.id)
  const { data } = await productApi.get(id)
  product.value = data
  try {
    const simResp = await recommendApi.similar(id)
    similarProducts.value = simResp.data
    await behaviorApi.track({ product_id: id, behavior_type: 'view' })
  } catch {}
}

function addToCart() {
  cartStore.addItem(product.value)
  ElMessage.success('已加入购物车')
}

onMounted(load)
watch(() => route.params.id, load)
</script>

<style scoped>
.detail-page {
  max-width: 960px;
  margin: 0 auto;
}

.detail-card {
  margin-bottom: 20px;
}

.detail-layout {
  display: flex;
  gap: 40px;
}

.detail-image {
  width: 360px;
  height: 360px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.detail-emoji {
  font-size: 100px;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.detail-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.detail-name {
  font-size: 26px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 16px;
}

.price-box {
  background: #fff5f5;
  padding: 16px 20px;
  border-radius: 10px;
  margin-bottom: 16px;
}

.price-label {
  font-size: 13px;
  color: #999;
  margin-right: 8px;
}

.price-value {
  font-size: 32px;
  font-weight: 800;
  color: #e74c3c;
}

.detail-desc {
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
}

.detail-meta {
  display: flex;
  gap: 10px;
  margin-bottom: 24px;
}

.detail-actions {
  display: flex;
  gap: 12px;
}

.section-card {
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .detail-layout {
    flex-direction: column;
  }
  .detail-image {
    width: 100%;
    height: 240px;
  }
}
</style>
