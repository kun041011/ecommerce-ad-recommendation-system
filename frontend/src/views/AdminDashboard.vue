<template>
  <div class="admin-dashboard">
    <h2 class="page-title">管理后台</h2>

    <!-- Stats Cards -->
    <el-row :gutter="20" style="margin-bottom: 24px">
      <el-col :span="6">
        <el-card class="stat-card stat-card--blue">
          <div class="stat-card__content">
            <div class="stat-card__info">
              <p class="stat-card__label">用户总数</p>
              <p class="stat-card__value">{{ dashboard.total_users || 0 }}</p>
            </div>
            <div class="stat-card__icon">👥</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card stat-card--green">
          <div class="stat-card__content">
            <div class="stat-card__info">
              <p class="stat-card__label">商品总数</p>
              <p class="stat-card__value">{{ dashboard.total_products || 0 }}</p>
            </div>
            <div class="stat-card__icon">📦</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card stat-card--orange">
          <div class="stat-card__content">
            <div class="stat-card__info">
              <p class="stat-card__label">订单总数</p>
              <p class="stat-card__value">{{ dashboard.total_orders || 0 }}</p>
            </div>
            <div class="stat-card__icon">📋</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card stat-card--red">
          <div class="stat-card__content">
            <div class="stat-card__info">
              <p class="stat-card__label">广告收入</p>
              <p class="stat-card__value">¥{{ (dashboard.total_ad_revenue || 0).toFixed(0) }}</p>
            </div>
            <div class="stat-card__icon">💰</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- KPI Row -->
    <el-row :gutter="20" style="margin-bottom: 24px">
      <el-col :span="8">
        <el-card>
          <div style="text-align: center; padding: 12px">
            <p style="color: #666; margin-bottom: 8px">广告点击率 (CTR)</p>
            <p style="font-size: 32px; font-weight: bold; color: #409eff">{{ ((dashboard.ctr || 0) * 100).toFixed(2) }}%</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div style="text-align: center; padding: 12px">
            <p style="color: #666; margin-bottom: 8px">千次展示收入 (RPM)</p>
            <p style="font-size: 32px; font-weight: bold; color: #67c23a">¥{{ (dashboard.rpm || 0).toFixed(2) }}</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div style="text-align: center; padding: 12px">
            <p style="color: #666; margin-bottom: 8px">商品交易总额</p>
            <p style="font-size: 32px; font-weight: bold; color: #e6a23c">¥{{ (dashboard.total_revenue || 0).toFixed(0) }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Row 1 -->
    <el-row :gutter="20" style="margin-bottom: 24px">
      <el-col :span="12">
        <el-card>
          <template #header><span style="font-weight: 600">用户活跃度分布</span></template>
          <div ref="pieChartRef" style="height: 320px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span style="font-weight: 600">频控策略效果</span></template>
          <div ref="freqChartRef" style="height: 320px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Row 2 -->
    <el-row :gutter="20" style="margin-bottom: 24px">
      <el-col :span="24">
        <el-card>
          <template #header><span style="font-weight: 600">广告效果排行</span></template>
          <div ref="barChartRef" style="height: 350px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Ad Performance Table -->
    <el-card>
      <template #header><span style="font-weight: 600">广告详细数据</span></template>
      <el-table :data="adPerf" stripe>
        <el-table-column prop="title" label="广告名称" />
        <el-table-column prop="shows" label="展示次数" width="120" sortable />
        <el-table-column prop="clicks" label="点击次数" width="120" sortable />
        <el-table-column label="点击率" width="120" sortable>
          <template #default="{ row }">
            <el-tag :type="row.ctr > 0.05 ? 'success' : row.ctr > 0.02 ? 'warning' : 'danger'" size="small">
              {{ (row.ctr * 100).toFixed(2) }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="消耗金额" width="120" sortable>
          <template #default="{ row }">¥{{ row.spent.toFixed(2) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { analyticsApi } from '../api'

const dashboard = ref<any>({})
const activityDist = ref({ low: 0, normal: 0, high: 0 })
const adPerf = ref<any[]>([])

const pieChartRef = ref<HTMLElement>()
const barChartRef = ref<HTMLElement>()
const freqChartRef = ref<HTMLElement>()

function initPieChart() {
  if (!pieChartRef.value) return
  const chart = echarts.init(pieChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c}人 ({d}%)' },
    legend: { bottom: 10 },
    color: ['#f56c6c', '#e6a23c', '#67c23a'],
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, fontSize: 14 },
      data: [
        { value: activityDist.value.low, name: '低活跃' },
        { value: activityDist.value.normal, name: '普通' },
        { value: activityDist.value.high, name: '高活跃' },
      ]
    }]
  })
  window.addEventListener('resize', () => chart.resize())
}

function initBarChart() {
  if (!barChartRef.value || adPerf.value.length === 0) return
  const chart = echarts.init(barChartRef.value)
  const sortedAds = [...adPerf.value].sort((a: any, b: any) => b.ctr - a.ctr).slice(0, 10)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: sortedAds.map((a: any) => a.title.length > 8 ? a.title.slice(0, 8) + '...' : a.title),
      axisLabel: { rotate: 30, fontSize: 11 },
    },
    yAxis: [
      { type: 'value', name: '点击率(%)', axisLabel: { formatter: '{value}%' } },
      { type: 'value', name: '消耗(¥)' },
    ],
    series: [
      {
        name: '点击率',
        type: 'bar',
        data: sortedAds.map((a: any) => (a.ctr * 100).toFixed(2)),
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#409eff' },
            { offset: 1, color: '#79bbff' },
          ])
        },
      },
      {
        name: '消耗',
        type: 'line',
        yAxisIndex: 1,
        data: sortedAds.map((a: any) => a.spent.toFixed(2)),
        smooth: true,
        lineStyle: { color: '#e6a23c', width: 2 },
        itemStyle: { color: '#e6a23c' },
      }
    ]
  })
  window.addEventListener('resize', () => chart.resize())
}

function initFreqChart() {
  if (!freqChartRef.value) return
  const chart = echarts.init(freqChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { bottom: 10 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['低活跃用户', '普通用户', '高活跃用户'],
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '每页广告数',
        type: 'bar',
        data: [1, 2, 3],
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#67c23a' },
            { offset: 1, color: '#95d475' },
          ])
        },
      },
      {
        name: '每日上限',
        type: 'bar',
        data: [10, 30, 50],
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#409eff' },
            { offset: 1, color: '#79bbff' },
          ])
        },
      },
      {
        name: '最小间隔(秒)',
        type: 'line',
        data: [300, 120, 60],
        smooth: true,
        lineStyle: { color: '#e6a23c', width: 2 },
        itemStyle: { color: '#e6a23c' },
      }
    ]
  })
  window.addEventListener('resize', () => chart.resize())
}

onMounted(async () => {
  try {
    const [dResp, aResp, pResp] = await Promise.all([
      analyticsApi.dashboard(),
      analyticsApi.activityDist(),
      analyticsApi.adPerformance(),
    ])
    dashboard.value = dResp.data
    activityDist.value = aResp.data
    adPerf.value = pResp.data

    await nextTick()
    initPieChart()
    initBarChart()
    initFreqChart()
  } catch (e) {
    console.error('Failed to load analytics:', e)
  }
})
</script>

<style scoped>
.admin-dashboard { max-width: 1400px; margin: 0 auto; }
.page-title { font-size: 20px; font-weight: 700; margin-bottom: 20px; color: var(--text-dark); }

.stat-card { border: 1px solid var(--border-light) !important; border-radius: 8px !important; }
.stat-card__content { display: flex; justify-content: space-between; align-items: center; }
.stat-card__label { font-size: 13px; color: var(--text-light); margin-bottom: 8px; }
.stat-card__value { font-size: 26px; font-weight: 700; margin: 0; }
.stat-card__icon { font-size: 36px; opacity: 0.7; }

.stat-card--blue .stat-card__value { color: #409eff; }
.stat-card--green .stat-card__value { color: #67c23a; }
.stat-card--orange .stat-card__value { color: var(--taobao-orange); }
.stat-card--red .stat-card__value { color: var(--jd-red); }
</style>
