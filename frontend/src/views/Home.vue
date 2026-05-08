<template>
  <div>
    <el-input v-model="searchQuery" placeholder="搜索商品..." size="large" style="margin-bottom: 20px"
      @keyup.enter="$router.push({ path: '/search', query: { q: searchQuery } })">
      <template #append>
        <el-button @click="$router.push({ path: '/search', query: { q: searchQuery } })">搜索</el-button>
      </template>
    </el-input>

    <h2>为你推荐</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px">
      <template v-for="item in displayItems" :key="item.type + '-' + item.data.id">
        <AdBanner v-if="item.type === 'ad'" :ad="item.data" />
        <ProductCard v-else :product="item.data" />
      </template>
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
  } catch { /* logged out — show empty */ }
})
</script>
