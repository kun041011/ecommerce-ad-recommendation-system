<template>
  <div style="max-width: 800px; margin: 0 auto">
    <h2 class="section-title">&#x1F6D2; 购物车</h2>

    <el-card v-if="cartStore.items.length">
      <el-table :data="cartStore.items" style="width: 100%">
        <el-table-column prop="name" label="商品名称">
          <template #default="{ row }">
            <span style="font-weight: 600">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="单价" width="140" align="center">
          <template #default="{ row }">
            <span style="color: #e74c3c; font-weight: 600">¥{{ row.price.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="100" align="center" />
        <el-table-column label="小计" width="140" align="center">
          <template #default="{ row }">
            <span style="color: #e74c3c; font-weight: 600">¥{{ (row.price * row.quantity).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button text type="danger" @click="cartStore.removeItem(row.product_id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="cart-footer">
        <div class="cart-total">
          合计: <span class="total-price">¥{{ cartStore.total.toFixed(2) }}</span>
        </div>
        <el-button type="primary" size="large" round @click="checkout">去结算</el-button>
      </div>
    </el-card>

    <div v-else class="empty-state">
      <p style="font-size: 64px; margin-bottom: 16px">&#x1F6D2;</p>
      <p style="color: #999; font-size: 16px">购物车还是空的</p>
      <el-button type="primary" round style="margin-top: 16px" @click="$router.push('/')">去逛逛</el-button>
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

<style scoped>
.cart-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 24px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.cart-total {
  font-size: 16px;
  color: #666;
}

.total-price {
  font-size: 28px;
  font-weight: 800;
  color: #e74c3c;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}
</style>
