<template>
  <div class="ad-card" @click.stop="handleClick">
    <div class="ad-card__img">
      <span class="ad-card__emoji">📢</span>
      <span class="ad-card__badge">广告</span>
    </div>
    <div class="ad-card__body">
      <div class="ad-card__name">{{ ad.title }}</div>
      <div class="ad-card__desc">{{ ad.content }}</div>
      <div class="ad-card__action">
        <span class="ad-card__link">查看详情 ›</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { adApi } from '../api'

const props = defineProps<{ ad: any }>()
const router = useRouter()

function handleClick() {
  adApi.impression({ ad_id: props.ad.id, impression_type: 'click' })
  if (props.ad.target_url) {
    const url = new URL(props.ad.target_url, window.location.origin)
    router.push({ path: url.pathname, query: Object.fromEntries(url.searchParams) })
  }
}
</script>

<style scoped>
.ad-card {
  background: #fff;
  border: 1px solid #fff3e0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
}
.ad-card:hover {
  border-color: var(--taobao-orange);
  box-shadow: 0 4px 16px rgba(255, 80, 0, 0.1);
  transform: translateY(-2px);
}

.ad-card__img {
  height: 180px;
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.ad-card__emoji { font-size: 56px; }
.ad-card__badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255, 80, 0, 0.85);
  color: #fff;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 3px;
  font-weight: 600;
}

.ad-card__body { padding: 12px; }
.ad-card__name {
  font-size: 14px; color: var(--text-dark); font-weight: 600;
  margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.ad-card__desc { font-size: 12px; color: var(--text-light); margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ad-card__link { font-size: 12px; color: var(--taobao-orange); font-weight: 600; }
</style>
