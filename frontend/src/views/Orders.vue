<template>
  <div style="max-width: 800px; margin: 0 auto">
    <h2 class="section-title">&#x1F4CB; 我的订单</h2>

    <el-card v-for="order in orders" :key="order.id" class="order-card">
      <div class="order-header">
        <span class="order-id">订单号: #{{ order.id }}</span>
        <el-tag :type="statusType(order.status)" effect="dark" round>{{ statusText(order.status) }}</el-tag>
      </div>
      <div class="order-body">
        <div class="order-info">
          <span class="order-count">{{ order.items.length }} 件商品</span>
          <span class="order-time">{{ order.created_at }}</span>
        </div>
        <div class="order-amount">
          ¥{{ order.total_amount.toFixed(2) }}
        </div>
      </div>
    </el-card>

    <div v-if="orders.length === 0" class="empty-state">
      <p style="font-size: 48px; margin-bottom: 12px">&#x1F4CB;</p>
      <p style="color: #999">暂无订单</p>
      <el-button type="primary" round style="margin-top: 16px" @click="$router.push('/')">去购物</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { orderApi } from '../api'

const orders = ref<any[]>([])

const statusMap: Record<string, { type: string; text: string }> = {
  pending: { type: 'warning', text: '待付款' },
  paid: { type: 'primary', text: '已付款' },
  shipped: { type: 'info', text: '已发货' },
  completed: { type: 'success', text: '已完成' },
  cancelled: { type: 'danger', text: '已取消' },
}

function statusType(s: string) { return (statusMap[s]?.type || 'info') as any }
function statusText(s: string) { return statusMap[s]?.text || s }

onMounted(async () => {
  const { data } = await orderApi.list()
  orders.value = data
})
</script>

<style scoped>
.order-card {
  margin-bottom: 16px;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.order-id {
  font-weight: 600;
  color: #333;
}

.order-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.order-count {
  color: #666;
  font-size: 14px;
}

.order-time {
  color: #999;
  font-size: 12px;
}

.order-amount {
  font-size: 24px;
  font-weight: 700;
  color: #e74c3c;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}
</style>
