<template>
  <div>
    <!-- Search bar -->
    <div class="search-bar-wrap">
      <input v-model="query" class="search-input" placeholder="搜索商品..." @keyup.enter="search" />
      <button class="search-btn" @click="search">搜索</button>
    </div>

    <!-- Sort bar -->
    <div class="sort-bar" v-if="searched">
      <span class="sort-bar__count">共 <strong>{{ products.length }}</strong> 件商品</span>
      <div class="sort-bar__options">
        <span class="sort-opt" :class="{ active: sortBy === 'default' }" @click="sortBy = 'default'">综合</span>
        <span class="sort-opt" :class="{ active: sortBy === 'sales' }" @click="sortBy = 'sales'">销量</span>
        <span class="sort-opt" :class="{ active: sortBy === 'price_asc' }" @click="sortBy = 'price_asc'">价格↑</span>
        <span class="sort-opt" :class="{ active: sortBy === 'price_desc' }" @click="sortBy = 'price_desc'">价格↓</span>
      </div>
    </div>

    <div class="product-grid">
      <ProductCard v-for="p in sortedProducts" :key="p.id" :product="p" />
    </div>

    <div v-if="searched && products.length === 0" class="empty-state">
      <p style="font-size: 48px; margin-bottom: 12px">🔍</p>
      <p>未找到相关商品，试试其他关键词</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { productApi } from '../api'
import ProductCard from '../components/ProductCard.vue'

const route = useRoute()
const query = ref((route.query.q as string) || (route.query.category as string) || '')
const products = ref<any[]>([])
const searched = ref(false)
const sortBy = ref('default')

const sortedProducts = computed(() => {
  const arr = [...products.value]
  if (sortBy.value === 'sales') arr.sort((a, b) => b.sales_count - a.sales_count)
  if (sortBy.value === 'price_asc') arr.sort((a, b) => a.price - b.price)
  if (sortBy.value === 'price_desc') arr.sort((a, b) => b.price - a.price)
  return arr
})

async function search() {
  const params: Record<string, any> = {}
  if (query.value) params.query = query.value
  const { data } = await productApi.search(params)
  products.value = data.items || []
  searched.value = true
}

onMounted(() => { if (query.value) search() })

watch(() => route.query, () => {
  query.value = (route.query.q as string) || (route.query.category as string) || ''
  if (query.value) search()
})
</script>

<style scoped>
.search-bar-wrap {
  display: flex; height: 44px; margin-bottom: 16px;
  border: 2px solid var(--jd-red); border-radius: 4px; overflow: hidden;
}
.search-input {
  flex: 1; border: none; padding: 0 16px; font-size: 14px; outline: none;
}
.search-btn {
  width: 100px; background: var(--jd-red); color: #fff; border: none;
  font-size: 15px; font-weight: 600; cursor: pointer; letter-spacing: 2px;
}
.search-btn:hover { background: #c91f17; }

.sort-bar {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 12px 16px; border: 1px solid var(--border-light);
  border-radius: 4px; margin-bottom: 16px; font-size: 14px;
}
.sort-bar__count { color: var(--text-light); }
.sort-bar__options { display: flex; gap: 20px; }
.sort-opt {
  color: var(--text-body); cursor: pointer; padding: 4px 0;
  border-bottom: 2px solid transparent; transition: all 0.15s;
}
.sort-opt:hover { color: var(--jd-red); }
.sort-opt.active { color: var(--jd-red); border-bottom-color: var(--jd-red); font-weight: 600; }
</style>
