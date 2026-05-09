<template>
  <div>
    <!-- Hero Banner / Carousel -->
    <div class="hero-carousel">
      <div class="hero-slide" :style="{ background: heroSlides[currentSlide].bg }">
        <div class="hero-slide__content">
          <h1>{{ heroSlides[currentSlide].title }}</h1>
          <p>{{ heroSlides[currentSlide].sub }}</p>
        </div>
        <div class="hero-dots">
          <span v-for="(_s, i) in heroSlides" :key="i" class="dot" :class="{ active: i === currentSlide }" @click="currentSlide = i"></span>
        </div>
      </div>
    </div>

    <!-- Category quick nav -->
    <div class="cat-nav">
      <div class="cat-nav__item" v-for="cat in categories" :key="cat.name"
           @click="$router.push({ path: '/search', query: { category: cat.name } })">
        <span class="cat-nav__icon">{{ cat.icon }}</span>
        <span class="cat-nav__label">{{ cat.name }}</span>
      </div>
    </div>

    <!-- Flash deals -->
    <div class="section-header" v-if="products.length">
      <span class="section-header__title">⚡ 限时特惠</span>
      <span class="section-header__more">更多优惠 ›</span>
    </div>
    <div class="flash-deals" v-if="products.length">
      <div class="flash-card" v-for="p in products.slice(0, 5)" :key="'flash-'+p.id"
           @click="$router.push(`/product/${p.id}`)">
        <div class="flash-card__img" :style="{ background: getGradient(p.id) }">
          <span class="flash-card__emoji">{{ getEmoji(p) }}</span>
        </div>
        <div class="flash-card__info">
          <div class="flash-card__name">{{ p.name }}</div>
          <div class="flash-card__price">
            <span class="price-symbol">¥</span><span class="price-main">{{ Math.floor(p.price) }}</span>
            <span class="price-original">¥{{ (p.price * 1.3).toFixed(0) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Top banner ad -->
    <div v-if="ads.length" class="banner-ad-section">
      <AdBanner :ad="ads[0]" :wide="true" />
    </div>

    <!-- Recommended products + ads -->
    <div class="section-header" v-if="products.length">
      <span class="section-header__title">📦 为你推荐</span>
      <span class="section-header__more">查看更多 ›</span>
    </div>
    <div class="product-grid">
      <template v-for="item in displayItems" :key="item.type + '-' + item.data.id">
        <AdBanner v-if="item.type === 'ad'" :ad="item.data" />
        <ProductCard v-else :product="item.data" />
      </template>
    </div>

    <!-- Bottom banner ad -->
    <div v-if="ads.length > 1" class="banner-ad-section" style="margin-top: 20px">
      <AdBanner :ad="ads[ads.length > 1 ? 1 : 0]" :wide="true" />
    </div>

    <!-- Empty / login prompt -->
    <div v-if="products.length === 0" class="empty-state">
      <p style="font-size: 48px; margin-bottom: 12px">🛒</p>
      <p style="margin-bottom: 16px">请先登录以获取个性化推荐</p>
      <el-button type="danger" @click="$router.push('/login')">去登录</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { recommendApi, adApi } from '../api'
import ProductCard from '../components/ProductCard.vue'
import AdBanner from '../components/AdBanner.vue'

const products = ref<any[]>([])
const ads = ref<any[]>([])
const currentSlide = ref(0)

const heroSlides = [
  { title: '智能推荐 · 精准触达', sub: '基于深度学习的个性化商品推荐', bg: 'linear-gradient(135deg, #e1251b 0%, #ff5000 100%)' },
  { title: '社区互动 · 好物分享', sub: '百万用户真实评价，购物更放心', bg: 'linear-gradient(135deg, #ff5000 0%, #ffd700 100%)' },
  { title: '限时特惠 · 超值好价', sub: '每日精选好物，低价不停', bg: 'linear-gradient(135deg, #e1251b 0%, #c91f17 100%)' },
]

const categories = [
  { name: '电子产品', icon: '📱' }, { name: '服装鞋帽', icon: '👗' },
  { name: '食品饮料', icon: '🍔' }, { name: '家居家装', icon: '🏠' },
  { name: '美妆个护', icon: '💄' }, { name: '运动户外', icon: '⚽' },
  { name: '图书音像', icon: '📚' }, { name: '玩具母婴', icon: '🧸' },
  { name: '汽车用品', icon: '🚗' }, { name: '园艺花卉', icon: '🌱' },
]

const gradients = [
  'linear-gradient(135deg,#ffecd2,#fcb69f)', 'linear-gradient(135deg,#a1c4fd,#c2e9fb)',
  'linear-gradient(135deg,#d4fc79,#96e6a1)', 'linear-gradient(135deg,#fbc2eb,#a6c1ee)',
  'linear-gradient(135deg,#ffd89b,#19547b)', 'linear-gradient(135deg,#ff9a9e,#fecfef)',
  'linear-gradient(135deg,#a18cd1,#fbc2eb)', 'linear-gradient(135deg,#89f7fe,#66a6ff)',
]
const emojiMap: Record<string, string> = {
  '电子产品': '📱', '服装鞋帽': '👗', '图书音像': '📚', '家居家装': '🏠',
  '食品饮料': '🍔', '运动户外': '⚽', '玩具母婴': '🧸', '美妆个护': '💄',
  '汽车用品': '🚗', '园艺花卉': '🌱',
}

function getGradient(id: number) { return gradients[id % gradients.length] }
function getEmoji(p: any) {
  for (const t of (p.tags || [])) { if (emojiMap[t]) return emojiMap[t] }
  return '🛍️'
}

const displayItems = computed(() => {
  const items: { type: string; data: any }[] = []
  let adIdx = 2
  for (let i = 0; i < products.value.length; i++) {
    items.push({ type: 'product', data: products.value[i] })
    if ((i + 1) % 3 === 0 && adIdx < ads.value.length) {
      items.push({ type: 'ad', data: ads.value[adIdx++ % ads.value.length] })
    }
  }
  return items
})

let slideTimer: any
onMounted(async () => {
  slideTimer = setInterval(() => { currentSlide.value = (currentSlide.value + 1) % heroSlides.length }, 4000)
  try {
    const [recResp, adResp] = await Promise.all([recommendApi.home(), adApi.fetch()])
    products.value = recResp.data
    ads.value = adResp.data.ads || []
    ads.value.forEach((ad: any) => { adApi.impression({ ad_id: ad.id, impression_type: 'show' }) })
  } catch {}
})
onUnmounted(() => { if (slideTimer) clearInterval(slideTimer) })
</script>

<style scoped>
/* Hero */
.hero-carousel { margin-bottom: 20px; border-radius: 8px; overflow: hidden; }
.hero-slide {
  height: 260px; display: flex; align-items: center; justify-content: center;
  position: relative; transition: background 0.5s;
}
.hero-slide__content { text-align: center; color: #fff; z-index: 1; }
.hero-slide__content h1 { font-size: 34px; font-weight: 800; margin-bottom: 10px; letter-spacing: 3px; text-shadow: 0 2px 8px rgba(0,0,0,0.2); }
.hero-slide__content p { font-size: 16px; opacity: 0.9; }
.hero-dots { position: absolute; bottom: 16px; display: flex; gap: 8px; left: 50%; transform: translateX(-50%); }
.dot { width: 10px; height: 10px; border-radius: 50%; background: rgba(255,255,255,0.4); cursor: pointer; transition: all 0.2s; }
.dot.active { background: #fff; width: 24px; border-radius: 5px; }

/* Category nav */
.cat-nav {
  display: grid; grid-template-columns: repeat(10, 1fr); gap: 8px;
  background: #fff; padding: 20px 16px; border-radius: 8px; margin-bottom: 20px;
  border: 1px solid var(--border-light);
}
.cat-nav__item {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  cursor: pointer; padding: 8px 0; border-radius: 8px; transition: background 0.15s;
}
.cat-nav__item:hover { background: #fff5f5; }
.cat-nav__icon { font-size: 28px; }
.cat-nav__label { font-size: 12px; color: var(--text-body); }

/* Flash deals */
.flash-deals {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 28px;
}
.flash-card {
  background: #fff; border: 1px solid var(--border-light); border-radius: 8px;
  overflow: hidden; cursor: pointer; transition: box-shadow 0.2s;
}
.flash-card:hover { box-shadow: var(--card-hover-shadow); }
.flash-card__img { height: 120px; display: flex; align-items: center; justify-content: center; }
.flash-card__emoji { font-size: 40px; }
.flash-card__info { padding: 10px 12px; }
.flash-card__name { font-size: 13px; color: var(--text-dark); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 6px; }
.flash-card__price { display: flex; align-items: baseline; }

/* Banner ad section */
.banner-ad-section { margin-bottom: 24px; }
</style>
