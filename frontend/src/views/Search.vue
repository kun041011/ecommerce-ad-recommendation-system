<template>
  <div>
    <el-input v-model="query" placeholder="搜索商品..." size="large" @keyup.enter="search">
      <template #append>
        <el-button @click="search">搜索</el-button>
      </template>
    </el-input>
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; margin-top: 20px">
      <ProductCard v-for="p in products" :key="p.id" :product="p" />
    </div>
    <p v-if="searched && products.length === 0" style="color: #999; text-align: center; margin-top: 40px">
      未找到相关商品
    </p>
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
