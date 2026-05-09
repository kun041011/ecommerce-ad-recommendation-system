<template>
  <div v-if="product" class="detail-page">
    <!-- Breadcrumb -->
    <div class="breadcrumb">
      <router-link to="/">首页</router-link>
      <span> › </span>
      <span>{{ (product.tags && product.tags[0]) || '全部商品' }}</span>
      <span> › </span>
      <span class="breadcrumb-current">{{ product.name }}</span>
    </div>

    <!-- Product main -->
    <div class="detail-main">
      <!-- Left: image -->
      <div class="detail-left">
        <div class="detail-img" :style="{ background: gradientColor }">
          <span class="detail-emoji">{{ categoryEmoji }}</span>
        </div>
      </div>
      <!-- Right: info -->
      <div class="detail-right">
        <h1 class="detail-name">{{ product.name }}</h1>
        <p class="detail-desc">{{ product.description }}</p>

        <!-- Price strip -->
        <div class="price-strip">
          <div class="price-strip__row">
            <span class="price-strip__label">促销价</span>
            <span class="price-symbol" style="font-size:18px">¥</span>
            <span class="price-main" style="font-size:36px">{{ Math.floor(product.price) }}</span>
            <span class="price-decimal" style="font-size:18px">.{{ ((product.price % 1) * 100).toFixed(0).padStart(2, '0') }}</span>
            <span class="price-original" style="margin-left:12px;font-size:14px">¥{{ (product.price * 1.3).toFixed(2) }}</span>
          </div>
          <div class="price-strip__tags">
            <span class="promo-tag">满99减10</span>
            <span class="promo-tag">新人专享</span>
          </div>
        </div>

        <!-- Meta -->
        <div class="detail-meta">
          <div class="meta-row"><span class="meta-label">库存</span><span>{{ product.stock }} 件</span></div>
          <div class="meta-row"><span class="meta-label">已售</span><span>{{ product.sales_count }}+</span></div>
          <div class="meta-row"><span class="meta-label">运费</span><span style="color:var(--taobao-orange)">包邮</span></div>
        </div>

        <!-- Quantity -->
        <div class="detail-qty">
          <span class="meta-label">数量</span>
          <el-input-number v-model="quantity" :min="1" :max="product.stock" size="default" />
        </div>

        <!-- Actions -->
        <div class="detail-actions">
          <el-button size="large" class="btn-buy" @click="buyNow">立即购买</el-button>
          <el-button size="large" class="btn-cart" @click="addToCart">加入购物车</el-button>
        </div>
      </div>
    </div>

    <!-- Tabs: reviews + QA -->
    <div class="detail-tabs">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="商品评价" name="reviews">
          <ReviewSection :product-id="product.id" :show-form="!!userStore.user" />
        </el-tab-pane>
        <el-tab-pane label="商品问答" name="qa">
          <QASection :product-id="product.id" :show-form="!!userStore.user" />
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Ad recommendation strip -->
    <div v-if="sideAds.length" class="detail-ad-strip">
      <div class="detail-ad-strip__header">
        <span>🔥 热门推荐</span>
      </div>
      <div class="detail-ad-strip__list">
        <AdBanner v-for="ad in sideAds" :key="ad.id" :ad="ad" />
      </div>
    </div>

    <!-- Similar products -->
    <div v-if="similarProducts.length" style="margin-top: 20px">
      <div class="section-header">
        <span class="section-header__title">看了又看</span>
      </div>
      <div class="product-grid">
        <ProductCard v-for="p in similarProducts" :key="p.id" :product="p" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { productApi, recommendApi, behaviorApi, adApi } from '../api'
import AdBanner from '../components/AdBanner.vue'
import { useCartStore } from '../stores/cart'
import { useUserStore } from '../stores/user'
import ProductCard from '../components/ProductCard.vue'
import ReviewSection from '../components/ReviewSection.vue'
import QASection from '../components/QASection.vue'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()
const userStore = useUserStore()
const product = ref<any>(null)
const similarProducts = ref<any[]>([])
const sideAds = ref<any[]>([])
const quantity = ref(1)
const activeTab = ref('reviews')

const gradients = [
  'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
  'linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)',
  'linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%)',
  'linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%)',
]
const emojiMap: Record<string, string> = {
  '电子产品': '📱', '服装鞋帽': '👗', '图书音像': '📚', '家居家装': '🏠',
  '食品饮料': '🍔', '运动户外': '⚽', '玩具母婴': '🧸', '美妆个护': '💄',
  '汽车用品': '🚗', '园艺花卉': '🌱',
}

const gradientColor = computed(() => gradients[(product.value?.id || 0) % gradients.length])
const categoryEmoji = computed(() => {
  for (const t of (product.value?.tags || [])) { if (emojiMap[t]) return emojiMap[t] }
  return '🛍️'
})

async function load() {
  const id = Number(route.params.id)
  const { data } = await productApi.get(id)
  product.value = data
  quantity.value = 1
  try {
    const [simResp, adResp] = await Promise.all([
      recommendApi.similar(id),
      adApi.fetch(),
    ])
    similarProducts.value = simResp.data
    sideAds.value = (adResp.data.ads || []).slice(0, 3)
    sideAds.value.forEach((ad: any) => { adApi.impression({ ad_id: ad.id, impression_type: 'show' }) })
    await behaviorApi.track({ product_id: id, behavior_type: 'view' })
  } catch {}
}

function addToCart() {
  cartStore.addItem(product.value)
  ElMessage.success('已加入购物车')
}

function buyNow() {
  cartStore.addItem(product.value)
  router.push('/cart')
}

onMounted(load)
watch(() => route.params.id, load)
</script>

<style scoped>
.detail-page { max-width: 1200px; margin: 0 auto; }

.breadcrumb { font-size: 13px; color: var(--text-light); margin-bottom: 16px; }
.breadcrumb a { color: var(--text-body); text-decoration: none; }
.breadcrumb a:hover { color: var(--jd-red); }
.breadcrumb-current { color: var(--text-dark); }

.detail-main {
  display: flex; gap: 24px; background: #fff;
  border: 1px solid var(--border-light); border-radius: 8px; padding: 24px;
  margin-bottom: 20px;
}

.detail-left { flex-shrink: 0; }
.detail-img {
  width: 400px; height: 400px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
}
.detail-emoji { font-size: 100px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.15)); }

.detail-right { flex: 1; }
.detail-name { font-size: 20px; font-weight: 700; color: var(--text-dark); line-height: 1.5; margin-bottom: 8px; }
.detail-desc { font-size: 13px; color: var(--text-body); line-height: 1.6; margin-bottom: 12px; }

.price-strip {
  background: #fdf0f0; padding: 16px 20px; margin-bottom: 16px; border-radius: 4px;
}
.price-strip__row { display: flex; align-items: baseline; }
.price-strip__label { font-size: 13px; color: var(--text-light); margin-right: 8px; }
.price-strip__tags { margin-top: 8px; display: flex; gap: 8px; }
.promo-tag { font-size: 11px; color: var(--jd-red); border: 1px solid var(--jd-red); padding: 1px 6px; border-radius: 3px; }
.price-symbol { color: var(--price-red); font-weight: 700; }
.price-main { color: var(--price-red); font-weight: 700; }
.price-decimal { color: var(--price-red); font-weight: 700; }
.price-original { color: #bbb; text-decoration: line-through; }

.detail-meta { margin-bottom: 16px; }
.meta-row { display: flex; align-items: center; padding: 8px 0; border-bottom: 1px solid #f5f5f5; font-size: 14px; }
.meta-label { width: 60px; color: var(--text-light); flex-shrink: 0; }

.detail-qty { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }

.detail-actions { display: flex; gap: 12px; }
.btn-buy { background: var(--jd-red) !important; color: #fff !important; border: none !important; width: 160px; font-size: 16px !important; font-weight: 600 !important; height: 48px !important; }
.btn-buy:hover { background: #c91f17 !important; }
.btn-cart { background: var(--taobao-orange) !important; color: #fff !important; border: none !important; width: 160px; font-size: 16px !important; font-weight: 600 !important; height: 48px !important; }
.btn-cart:hover { background: #e04600 !important; }

.detail-tabs {
  background: #fff; border: 1px solid var(--border-light); border-radius: 8px;
  padding: 20px; margin-bottom: 20px;
}

.detail-ad-strip {
  background: #fff;
  border: 2px solid #ff9800;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}
.detail-ad-strip__header {
  font-size: 16px;
  font-weight: 700;
  color: #e1251b;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 2px solid #ffeee6;
}
.detail-ad-strip__list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

@media (max-width: 768px) {
  .detail-main { flex-direction: column; }
  .detail-img { width: 100%; height: 260px; }
}
</style>
