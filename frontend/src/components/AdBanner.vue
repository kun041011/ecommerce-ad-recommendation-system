<template>
  <div class="ad-banner" @click.stop="handleClick">
    <div class="ad-badge">推广</div>
    <div class="ad-content">
      <div class="ad-icon">&#x1F4E2;</div>
      <div class="ad-text">
        <h4 class="ad-title">{{ ad.title }}</h4>
        <p class="ad-desc">{{ ad.content }}</p>
      </div>
      <el-button type="warning" size="small" round class="ad-btn">了解详情</el-button>
    </div>
  </div>
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

<style scoped>
.ad-banner {
  background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
  border-radius: 12px;
  padding: 20px;
  position: relative;
  cursor: pointer;
  border: 1px solid rgba(255, 183, 77, 0.3);
  transition: all 0.3s ease;
  overflow: hidden;
}

.ad-banner:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 183, 77, 0.25);
}

.ad-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: linear-gradient(135deg, #ff9800, #f57c00);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 12px;
  border-radius: 0 12px 0 12px;
}

.ad-content {
  display: flex;
  align-items: center;
  gap: 14px;
}

.ad-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.ad-text {
  flex: 1;
}

.ad-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 4px;
}

.ad-desc {
  font-size: 13px;
  color: #666;
  margin: 0;
}

.ad-btn {
  flex-shrink: 0;
}
</style>
