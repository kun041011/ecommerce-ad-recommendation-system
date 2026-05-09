<template>
  <el-card>
    <template #header>
      <span class="section-title" style="margin-bottom: 0">&#x1F4CA; 活跃度仪表盘</span>
    </template>
    <div class="activity-layout">
      <div class="activity-gauge">
        <el-progress type="dashboard" :percentage="score" :color="levelColor" :width="160" :stroke-width="12">
          <template #default>
            <span class="gauge-score">{{ score }}</span>
            <el-tag :type="levelType" effect="dark" round size="small" class="gauge-tag">{{ levelText }}</el-tag>
          </template>
        </el-progress>
      </div>
      <div class="activity-info">
        <div class="info-item">
          <span class="info-label">活跃等级</span>
          <span class="info-value" :style="{ color: levelColor }">{{ levelText }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">广告频率</span>
          <span class="info-value">{{ adLevelText }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">活跃度评分</span>
          <span class="info-value">{{ score }} / 100</span>
        </div>
        <p class="info-tip">
          活跃度越高，可享受更多个性化推荐。参与评价和问答可以提升活跃度！
        </p>
      </div>
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
const adLevelText = computed(() => ({ high: '高频推送', normal: '标准频率', low: '低频推送' } as any)[adLevel.value] || '')

onMounted(async () => {
  try {
    const { data } = await activityApi.myScore()
    score.value = Math.round(data.score)
    level.value = data.level
    adLevel.value = data.ad_frequency_level
  } catch {}
})
</script>

<style scoped>
.activity-layout {
  display: flex;
  align-items: center;
  gap: 40px;
}

.activity-gauge {
  flex-shrink: 0;
  text-align: center;
}

.gauge-score {
  font-size: 32px;
  font-weight: 800;
  color: #1a1a2e;
  display: block;
}

.gauge-tag {
  margin-top: 4px;
}

.activity-info {
  flex: 1;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-label {
  color: #999;
  font-size: 14px;
}

.info-value {
  font-weight: 600;
  font-size: 14px;
}

.info-tip {
  margin-top: 16px;
  font-size: 13px;
  color: #999;
  line-height: 1.6;
}

@media (max-width: 600px) {
  .activity-layout {
    flex-direction: column;
  }
}
</style>
