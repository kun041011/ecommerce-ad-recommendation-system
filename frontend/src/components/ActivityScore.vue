<template>
  <div class="activity-card">
    <h3 class="activity-card__title">活跃度仪表盘</h3>
    <div class="activity-layout">
      <div class="activity-gauge">
        <el-progress type="dashboard" :percentage="score" :color="levelColor" :width="140" :stroke-width="10">
          <template #default>
            <span class="gauge-score">{{ score }}</span>
            <span class="gauge-label" :style="{ color: levelColor }">{{ levelText }}</span>
          </template>
        </el-progress>
      </div>
      <div class="activity-info">
        <div class="info-row"><span class="info-label">活跃等级</span><span class="info-val" :style="{ color: levelColor }">{{ levelText }}</span></div>
        <div class="info-row"><span class="info-label">广告频率</span><span class="info-val">{{ adLevelText }}</span></div>
        <div class="info-row"><span class="info-label">活跃度评分</span><span class="info-val">{{ score }} / 100</span></div>
        <p class="info-tip">参与评价和问答可以提升活跃度，活跃度越高推荐越精准。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { activityApi } from '../api'

const score = ref(0)
const level = ref('low')
const adLevel = ref('normal')

const levelColor = computed(() => ({ high: '#67c23a', normal: '#e6a23c', low: '#f56c6c' } as any)[level.value] || '#409eff')
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
.activity-card {
  background: #fff; border: 1px solid var(--border-light);
  border-radius: 8px; padding: 24px;
}
.activity-card__title { font-size: 16px; font-weight: 600; color: var(--text-dark); margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid #f0f0f0; }

.activity-layout { display: flex; align-items: center; gap: 40px; }
.activity-gauge { flex-shrink: 0; text-align: center; }
.gauge-score { font-size: 28px; font-weight: 800; color: var(--text-dark); display: block; }
.gauge-label { font-size: 12px; font-weight: 600; }

.activity-info { flex: 1; }
.info-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f5f5f5; font-size: 14px; }
.info-label { color: var(--text-light); }
.info-val { font-weight: 600; }
.info-tip { margin-top: 12px; font-size: 13px; color: var(--text-light); line-height: 1.6; }

@media (max-width: 600px) { .activity-layout { flex-direction: column; } }
</style>
