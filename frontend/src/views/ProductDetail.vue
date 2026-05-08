<template>
  <div v-if="product" style="max-width: 900px; margin: 0 auto">
    <el-card>
      <h1>{{ product.name }}</h1>
      <p style="color: #e74c3c; font-size: 24px; font-weight: bold">¥{{ product.price.toFixed(2) }}</p>
      <p>{{ product.description }}</p>
      <p>库存: {{ product.stock }} | 销量: {{ product.sales_count }}</p>
      <el-button type="primary" @click="addToCart">加入购物车</el-button>
    </el-card>
    <el-card style="margin-top: 16px">
      <ReviewSection :product-id="product.id" :show-form="!!userStore.user" />
    </el-card>
    <el-card style="margin-top: 16px">
      <QASection :product-id="product.id" :show-form="!!userStore.user" />
    </el-card>
    <el-card style="margin-top: 16px" v-if="similarProducts.length">
      <h3>相似商品</h3>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px">
        <ProductCard v-for="p in similarProducts" :key="p.id" :product="p" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
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

async function load() {
  const id = Number(route.params.id)
  const { data } = await productApi.get(id)
  product.value = data
  try {
    const simResp = await recommendApi.similar(id)
    similarProducts.value = simResp.data
    await behaviorApi.track({ product_id: id, behavior_type: 'view' })
  } catch { /* not logged in */ }
}

function addToCart() {
  cartStore.addItem(product.value)
  ElMessage.success('已加入购物车')
}

onMounted(load)
watch(() => route.params.id, load)
</script>
