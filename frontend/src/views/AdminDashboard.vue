<template>
  <div>
    <h2>管理后台</h2>
    <el-row :gutter="16" style="margin-bottom: 20px">
      <el-col :span="6" v-for="(stat, key) in stats" :key="key">
        <el-statistic :title="stat.label" :value="stat.value" />
      </el-col>
    </el-row>

    <el-card style="margin-bottom: 16px">
      <template #header>活跃度分布</template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="低活跃">{{ activityDist.low }}</el-descriptions-item>
        <el-descriptions-item label="普通">{{ activityDist.normal }}</el-descriptions-item>
        <el-descriptions-item label="高活跃">{{ activityDist.high }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card>
      <template #header>广告效果</template>
      <el-table :data="adPerf">
        <el-table-column prop="title" label="广告" />
        <el-table-column prop="shows" label="展示" width="100" />
        <el-table-column prop="clicks" label="点击" width="100" />
        <el-table-column prop="ctr" label="CTR" width="100">
          <template #default="{ row }">{{ (row.ctr * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column prop="spent" label="消耗" width="100">
          <template #default="{ row }">¥{{ row.spent.toFixed(2) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { analyticsApi } from '../api'

const dashboard = ref<any>({})
const activityDist = ref({ low: 0, normal: 0, high: 0 })
const adPerf = ref<any[]>([])

const stats = computed(() => ({
  users: { label: '用户总数', value: dashboard.value.total_users || 0 },
  products: { label: '商品总数', value: dashboard.value.total_products || 0 },
  orders: { label: '订单总数', value: dashboard.value.total_orders || 0 },
  revenue: { label: '总收入 (¥)', value: dashboard.value.total_revenue || 0 },
}))

onMounted(async () => {
  const [dResp, aResp, pResp] = await Promise.all([
    analyticsApi.dashboard(),
    analyticsApi.activityDist(),
    analyticsApi.adPerformance(),
  ])
  dashboard.value = dResp.data
  activityDist.value = aResp.data
  adPerf.value = pResp.data
})
</script>
