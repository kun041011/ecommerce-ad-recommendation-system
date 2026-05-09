<template>
  <div>
    <div class="hero-banner">
      <div class="hero-content">
        <h1 class="hero-title">智能推荐，精准触达</h1>
        <p class="hero-subtitle">基于深度学习的电商广告推荐系统，为你发现最合适的好物</p>
        <div class="hero-search">
          <el-input
            v-model="searchQuery"
            placeholder="搜索你想要的商品..."
            size="large"
            class="search-input"
            @keyup.enter="$router.push({ path: '/search', query: { q: searchQuery } })"
          >
            <template #prefix>
              <span style="font-size: 18px">&#x1F50D;</span>
            </template>
            <template #append>
              <el-button type="primary" @click="$router.push({ path: '/search', query: { q: searchQuery } })">
                搜索
              </el-button>
            </template>
          </el-input>
        </div>
      </div>
    </div>

    <div class="stats-bar" v-if="products.length > 0">
      <div class="stat-item">
        <span class="stat-icon">&#x1F4E6;</span>
        <span class="stat-label">海量商品</span>
      </div>
      <div class="stat-item">
        <span class="stat-icon">&#x1F916;</span>
        <span class="stat-label">AI智能推荐</span>
      </div>
      <div class="stat-item">
        <span class="stat-icon">&#x1F6E1;</span>
        <span class="stat-label">智能频控</span>
      </div>
      <div class="stat-item">
        <span class="stat-icon">&#x1F465;</span>
        <span class="stat-label">社区互动</span>
      </div>
    </div>

    <h2 class="section-title">为你推荐</h2>
    <div class="product-grid">
      <template v-for="item in displayItems" :key="item.type + '-' + item.data.id">
        <AdBanner v-if="item.type === 'ad'" :ad="item.data" />
        <ProductCard v-else :product="item.data" />
      </template>
    </div>

    <div v-if="products.length === 0" class="empty-state">
      <p style="font-size: 48px; margin-bottom: 12px">&#x1F6D2;</p>
      <p style="color: #999">请先登录以获取个性化推荐</p>
      <el-button type="primary" style="margin-top: 16px" @click="$router.push('/login')">去登录</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { recommendApi, adApi } from '../api'
import ProductCard from '../components/ProductCard.vue'
import AdBanner from '../components/AdBanner.vue'

const searchQuery = ref('')
const products = ref<any[]>([])
const ads = ref<any[]>([])

const displayItems = computed(() => {
  const items: { type: string; data: any }[] = []
  let adIdx = 0
  for (let i = 0; i < products.value.length; i++) {
    items.push({ type: 'product', data: products.value[i] })
    if ((i + 1) % 4 === 0 && adIdx < ads.value.length) {
      items.push({ type: 'ad', data: ads.value[adIdx++] })
    }
  }
  return items
})

onMounted(async () => {
  try {
    const [recResp, adResp] = await Promise.all([recommendApi.home(), adApi.fetch()])
    products.value = recResp.data
    ads.value = adResp.data.ads || []
    ads.value.forEach((ad: any) => {
      adApi.impression({ ad_id: ad.id, impression_type: 'show' })
    })
  } catch { /* logged out */ }
})
</script>

<style scoped>
.hero-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 50px 40px;
  margin-bottom: 30px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero-banner::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}

.hero-banner::after {
  content: '';
  position: absolute;
  bottom: -30%;
  left: -10%;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-title {
  color: #fff;
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 12px;
  letter-spacing: 2px;
}

.hero-subtitle {
  color: rgba(255, 255, 255, 0.85);
  font-size: 16px;
  margin-bottom: 30px;
}

.hero-search {
  max-width: 560px;
  margin: 0 auto;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 25px !important;
  padding: 4px 4px 4px 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
}

.search-input :deep(.el-input-group__append) {
  border-radius: 0 25px 25px 0 !important;
  background: linear-gradient(135deg, #667eea, #764ba2) !important;
  border: none !important;
  color: #fff !important;
  padding: 0 24px;
}

.stats-bar {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 30px;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #555;
  font-weight: 500;
}

.stat-icon {
  font-size: 22px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}
</style>
