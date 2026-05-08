<template>
  <div style="max-width: 800px; margin: 0 auto">
    <h2>我的订单</h2>
    <el-card v-for="order in orders" :key="order.id" style="margin-bottom: 12px">
      <div style="display: flex; justify-content: space-between; align-items: center">
        <div>
          <p>订单号: {{ order.id }} | 状态: <el-tag :type="statusType(order.status)">{{ order.status }}</el-tag></p>
          <p>金额: <strong style="color: #e74c3c">¥{{ order.total_amount.toFixed(2) }}</strong></p>
          <p style="color: #999; font-size: 12px">{{ order.created_at }}</p>
        </div>
        <div>
          <p>{{ order.items.length }} 件商品</p>
        </div>
      </div>
    </el-card>
    <p v-if="orders.length === 0" style="color: #999; text-align: center">暂无订单</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { orderApi } from '../api'

const orders = ref<any[]>([])

function statusType(status: string) {
  const map: Record<string, string> = { pending: 'warning', paid: 'primary', shipped: 'info', completed: 'success', cancelled: 'danger' }
  return (map[status] || 'info') as any
}

onMounted(async () => {
  const { data } = await orderApi.list()
  orders.value = data
})
</script>
