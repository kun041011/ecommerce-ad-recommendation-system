<template>
  <div style="max-width: 960px; margin: 0 auto">
    <h2 class="page-title">我的订单</h2>

    <!-- Tab filters -->
    <div class="order-tabs">
      <span class="order-tab" :class="{ active: filter === 'all' }" @click="filter = 'all'">全部订单</span>
      <span class="order-tab" :class="{ active: filter === 'pending' }" @click="filter = 'pending'">待付款</span>
      <span class="order-tab" :class="{ active: filter === 'paid' }" @click="filter = 'paid'">待发货</span>
      <span class="order-tab" :class="{ active: filter === 'shipped' }" @click="filter = 'shipped'">已发货</span>
      <span class="order-tab" :class="{ active: filter === 'completed' }" @click="filter = 'completed'">已完成</span>
    </div>

    <div class="order-card" v-for="order in filteredOrders" :key="order.id">
      <div class="order-card__head">
        <div>
          <span class="order-card__id">订单号: {{ order.id }}</span>
          <span class="order-card__time">{{ order.created_at }}</span>
        </div>
        <el-tag :type="statusType(order.status)" size="small" effect="plain">{{ statusText(order.status) }}</el-tag>
      </div>
      <div class="order-card__body">
        <div class="order-card__items">
          <div class="order-thumb" v-for="(_item, i) in order.items.slice(0, 4)" :key="i">🛍️</div>
          <span class="order-card__count">共 {{ order.items.length }} 件</span>
        </div>
        <div class="order-card__amount">
          <span class="label">订单金额:</span>
          <span class="price-symbol">¥</span>
          <span class="price-main" style="font-size:22px">{{ order.total_amount.toFixed(2) }}</span>
        </div>
      </div>
    </div>

    <div v-if="filteredOrders.length === 0" class="empty-state">
      <p style="font-size: 48px; margin-bottom: 12px">📋</p>
      <p>暂无相关订单</p>
      <el-button type="danger" style="margin-top:16px" @click="$router.push('/')">去购物</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { orderApi } from '../api'

const orders = ref<any[]>([])
const filter = ref('all')

const statusMap: Record<string, { type: string; text: string }> = {
  pending: { type: 'warning', text: '待付款' },
  paid: { type: 'primary', text: '待发货' },
  shipped: { type: 'info', text: '已发货' },
  completed: { type: 'success', text: '已完成' },
  cancelled: { type: 'danger', text: '已取消' },
}

function statusType(s: string) { return (statusMap[s]?.type || 'info') as any }
function statusText(s: string) { return statusMap[s]?.text || s }

const filteredOrders = computed(() => {
  if (filter.value === 'all') return orders.value
  return orders.value.filter(o => o.status === filter.value)
})

onMounted(async () => {
  const { data } = await orderApi.list()
  orders.value = data
})
</script>

<style scoped>
.page-title { font-size: 20px; font-weight: 700; margin-bottom: 16px; color: var(--text-dark); }

.order-tabs {
  display: flex; gap: 0; margin-bottom: 16px;
  background: #fff; border: 1px solid var(--border-light); border-radius: 4px; overflow: hidden;
}
.order-tab {
  padding: 10px 24px; font-size: 14px; color: var(--text-body);
  cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.15s;
}
.order-tab:hover { color: var(--jd-red); }
.order-tab.active { color: var(--jd-red); border-bottom-color: var(--jd-red); font-weight: 600; background: #fff5f5; }

.order-card {
  background: #fff; border: 1px solid var(--border-light); border-radius: 8px;
  margin-bottom: 12px; overflow: hidden;
}
.order-card__head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 20px; background: #fafafa; border-bottom: 1px solid #f0f0f0;
}
.order-card__id { font-weight: 600; font-size: 14px; color: var(--text-dark); }
.order-card__time { margin-left: 16px; font-size: 12px; color: var(--text-light); }

.order-card__body {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px;
}
.order-card__items { display: flex; align-items: center; gap: 8px; }
.order-thumb {
  width: 48px; height: 48px; background: #f5f5f5; border-radius: 6px;
  display: flex; align-items: center; justify-content: center; font-size: 20px;
}
.order-card__count { font-size: 13px; color: var(--text-light); margin-left: 4px; }
.order-card__amount { text-align: right; }
.order-card__amount .label { font-size: 13px; color: var(--text-light); margin-right: 4px; }
.price-symbol { color: var(--price-red); font-weight: 700; }
.price-main { color: var(--price-red); font-weight: 700; }
</style>
