<template>
  <div>
    <h2 class="section-title">&#x1F4CA; 管理后台</h2>

    <el-row :gutter="16" style="margin-bottom: 24px">
      <el-col :span="6" v-for="(stat, key) in statsCards" :key="key">
        <div class="stat-card" :style="{ background: stat.bg }">
          <div class="stat-icon">{{ stat.icon }}</div>
          <div class="stat-body">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span style="font-weight: 600">&#x1F4C8; 活跃度分布</span>
          </template>
          <div class="activity-bars">
            <div class="bar-item">
              <span class="bar-label">高活跃</span>
              <div class="bar-track">
                <div class="bar-fill bar-high" :style="{ width: activityPct('high') }"></div>
              </div>
              <span class="bar-count">{{ activityDist.high }}</span>
            </div>
            <div class="bar-item">
              <span class="bar-label">普通</span>
              <div class="bar-track">
                <div class="bar-fill bar-normal" :style="{ width: activityPct('normal') }"></div>
              </div>
              <span class="bar-count">{{ activityDist.normal }}</span>
            </div>
            <div class="bar-item">
              <span class="bar-label">低活跃</span>
              <div class="bar-track">
                <div class="bar-fill bar-low" :style="{ width: activityPct('low') }"></div>
              </div>
              <span class="bar-count">{{ activityDist.low }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span style="font-weight: 600">&#x1F4B0; 商业化指标</span>
          </template>
          <div class="metrics-list">
            <div class="metric-item">
              <span class="metric-label">广告总收入</span>
              <span class="metric-value" style="color: #e74c3c">¥{{ dashboard.total_ad_revenue || 0 }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">平均点击率 (CTR)</span>
              <span class="metric-value">{{ ((dashboard.ctr || 0) * 100).toFixed(2) }}%</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">千次展示收入 (RPM)</span>
              <span class="metric-value">¥{{ dashboard.rpm || 0 }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 20px">
      <template #header>
        <span style="font-weight: 600">&#x1F4E2; 广告效果明细</span>
      </template>
      <el-table :data="adPerf" stripe>
        <el-table-column prop="title" label="广告标题" />
        <el-table-column prop="shows" label="展示量" width="100" align="center" />
        <el-table-column prop="clicks" label="点击量" width="100" align="center" />
        <el-table-column label="点击率" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.ctr > 0.02 ? 'success' : 'warning'" effect="plain" size="small">
              {{ (row.ctr * 100).toFixed(1) }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="消耗" width="120" align="center">
          <template #default="{ row }">
            <span style="font-weight: 600; color: #e74c3c">¥{{ row.spent.toFixed(2) }}</span>
          </template>
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

const statsCards = computed(() => [
  { icon: '👥', label: '用户总数', value: dashboard.value.total_users || 0, bg: 'linear-gradient(135deg, #667eea, #764ba2)' },
  { icon: '📦', label: '商品总数', value: dashboard.value.total_products || 0, bg: 'linear-gradient(135deg, #4facfe, #00f2fe)' },
  { icon: '📋', label: '订单总数', value: dashboard.value.total_orders || 0, bg: 'linear-gradient(135deg, #43e97b, #38f9d7)' },
  { icon: '💰', label: '总收入', value: '¥' + (dashboard.value.total_revenue || 0), bg: 'linear-gradient(135deg, #fa709a, #fee140)' },
])

const totalUsers = computed(() => activityDist.value.low + activityDist.value.normal + activityDist.value.high || 1)
function activityPct(level: string) {
  return Math.round(((activityDist.value as any)[level] / totalUsers.value) * 100) + '%'
}

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

<style scoped>
.stat-card {
  border-radius: 12px;
  padding: 20px;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 36px;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
}

.stat-label {
  font-size: 13px;
  opacity: 0.85;
}

.activity-bars {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bar-label {
  width: 60px;
  font-size: 14px;
  color: #666;
  text-align: right;
}

.bar-track {
  flex: 1;
  height: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 0.6s ease;
}

.bar-high { background: linear-gradient(90deg, #67c23a, #38f9d7); }
.bar-normal { background: linear-gradient(90deg, #e6a23c, #fee140); }
.bar-low { background: linear-gradient(90deg, #f56c6c, #fa709a); }

.bar-count {
  width: 40px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.metrics-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.metric-label {
  color: #666;
  font-size: 14px;
}

.metric-value {
  font-size: 18px;
  font-weight: 700;
}
</style>
