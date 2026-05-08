<template>
  <div style="max-width: 700px; margin: 0 auto">
    <h2>购物车</h2>
    <el-table :data="cartStore.items" v-if="cartStore.items.length" style="width: 100%">
      <el-table-column prop="name" label="商品" />
      <el-table-column prop="price" label="单价" width="120">
        <template #default="{ row }">¥{{ row.price.toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="quantity" label="数量" width="100" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button text type="danger" @click="cartStore.removeItem(row.product_id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <p v-else style="color: #999; text-align: center; margin: 40px 0">购物车为空</p>
    <div v-if="cartStore.items.length" style="text-align: right; margin-top: 20px">
      <span style="font-size: 18px; margin-right: 20px">合计: <strong style="color: #e74c3c">¥{{ cartStore.total.toFixed(2) }}</strong></span>
      <el-button type="primary" size="large" @click="checkout">结算</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { orderApi } from '../api'
import { useCartStore } from '../stores/cart'

const cartStore = useCartStore()
const router = useRouter()

async function checkout() {
  const items = cartStore.items.map((i) => ({ product_id: i.product_id, quantity: i.quantity }))
  await orderApi.create(items)
  cartStore.clear()
  ElMessage.success('订单创建成功！')
  router.push('/orders')
}
</script>
