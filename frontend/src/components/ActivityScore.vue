<template>
  <el-card>
    <template #header>活跃度仪表盘</template>
    <div style="text-align: center">
      <el-progress type="dashboard" :percentage="score" :color="levelColor" :width="150">
        <template #default>
          <span style="font-size: 24px; font-weight: bold">{{ score }}</span>
          <br />
          <el-tag :type="levelType">{{ levelText }}</el-tag>
        </template>
      </el-progress>
      <p style="margin-top: 12px; color: #666">广告频率等级: {{ adLevel }}</p>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { activityApi } from '../api'

const score = ref(0)
const level = ref('low')
const adLevel = ref('normal')

const levelColor = computed(() => ({ high: '#67c23a', normal: '#e6a23c', low: '#f56c6c' } as any)[level.value] || '#409eff')
const levelType = computed(() => ({ high: 'success', normal: 'warning', low: 'danger' } as any)[level.value] || 'info')
const levelText = computed(() => ({ high: '活跃用户', normal: '普通用户', low: '低活跃用户' } as any)[level.value] || '')

onMounted(async () => {
  try {
    const { data } = await activityApi.myScore()
    score.value = Math.round(data.score)
    level.value = data.level
    adLevel.value = data.ad_frequency_level
  } catch {}
})
</script>
