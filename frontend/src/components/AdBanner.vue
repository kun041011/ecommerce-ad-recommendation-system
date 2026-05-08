<template>
  <el-card shadow="hover" style="border: 1px solid #f0ad4e; background: #fffdf5">
    <div style="display: flex; align-items: center; gap: 12px">
      <el-tag type="warning" size="small">推广</el-tag>
      <div style="flex: 1">
        <h4 style="margin: 0">{{ ad.title }}</h4>
        <p style="margin: 4px 0 0; color: #666; font-size: 13px">{{ ad.content }}</p>
      </div>
      <el-button type="warning" size="small" @click.stop="handleClick">查看详情</el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { adApi } from '../api'

const props = defineProps<{ ad: any }>()

function handleClick() {
  adApi.impression({ ad_id: props.ad.id, impression_type: 'click' })
  if (props.ad.target_url) {
    window.location.href = props.ad.target_url
  }
}
</script>
