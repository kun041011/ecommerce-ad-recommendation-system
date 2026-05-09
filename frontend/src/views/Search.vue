<template>
  <div>
    <div class="search-header">
      <el-input v-model="query" placeholder="搜索商品..." size="large" class="search-bar" @keyup.enter="search">
        <template #prefix>
          <span>&#x1F50D;</span>
        </template>
        <template #append>
          <el-button type="primary" @click="search">搜索</el-button>
        </template>
      </el-input>
    </div>

    <h2 class="section-title" v-if="searched">搜索结果</h2>

    <div class="product-grid">
      <ProductCard v-for="p in products" :key="p.id" :product="p" />
    </div>

    <div v-if="searched && products.length === 0" class="empty-state">
      <p style="font-size: 48px; margin-bottom: 12px">&#x1F50E;</p>
      <p style="color: #999">未找到相关商品，试试其他关键词</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { productApi } from '../api'
import ProductCard from '../components/ProductCard.vue'

const route = useRoute()
const query = ref((route.query.q as string) || '')
const products = ref<any[]>([])
const searched = ref(false)

async function search() {
  const { data } = await productApi.search({ query: query.value })
  products.value = data.items || []
  searched.value = true
}

onMounted(() => { if (query.value) search() })
</script>

<style scoped>
.search-header {
  margin-bottom: 24px;
}

.search-bar :deep(.el-input__wrapper) {
  border-radius: 25px !important;
  padding: 4px 4px 4px 16px;
}

.search-bar :deep(.el-input-group__append) {
  border-radius: 0 25px 25px 0 !important;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}
</style>
