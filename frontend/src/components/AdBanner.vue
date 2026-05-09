<template>
  <div class="ad-card" :class="{ 'ad-card--wide': wide }" @click.stop="handleClick">
    <div class="ad-card__img" :class="{ 'ad-card__img--wide': wide }">
      <div class="ad-card__glow"></div>
      <span class="ad-card__emoji">{{ wide ? '🔥' : '📢' }}</span>
      <span class="ad-card__badge">推广</span>
      <div class="ad-card__ribbon" v-if="wide">限时推荐</div>
    </div>
    <div class="ad-card__body">
      <div class="ad-card__name">{{ ad.title }}</div>
      <div class="ad-card__desc">{{ ad.content }}</div>
      <div class="ad-card__action">
        <span class="ad-card__cta">立即查看</span>
        <span class="ad-card__arrow">→</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { adApi } from '../api'

const props = withDefaults(defineProps<{ ad: any; wide?: boolean }>(), { wide: false })
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
  border: 2px solid #ff9800;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  animation: adPulse 3s ease-in-out infinite;
}
.ad-card:hover {
  border-color: #e1251b;
  box-shadow: 0 8px 30px rgba(225, 37, 27, 0.2);
  transform: translateY(-4px) scale(1.02);
}

@keyframes adPulse {
  0%, 100% { box-shadow: 0 2px 8px rgba(255, 152, 0, 0.15); }
  50% { box-shadow: 0 4px 20px rgba(255, 152, 0, 0.3); }
}

.ad-card__img {
  height: 180px;
  background: linear-gradient(135deg, #e1251b 0%, #ff5000 50%, #ffd700 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}
.ad-card__img--wide {
  height: 140px;
}
.ad-card__glow {
  position: absolute;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 60%);
  animation: glowMove 4s ease-in-out infinite;
}
@keyframes glowMove {
  0%, 100% { transform: translate(-30%, -30%); }
  50% { transform: translate(10%, 10%); }
}
.ad-card__emoji { font-size: 60px; z-index: 1; filter: drop-shadow(0 4px 12px rgba(0,0,0,0.3)); }
.ad-card__badge {
  position: absolute;
  top: 0;
  right: 0;
  background: #e1251b;
  color: #fff;
  font-size: 12px;
  padding: 4px 12px;
  font-weight: 700;
  border-radius: 0 0 0 8px;
  letter-spacing: 1px;
}
.ad-card__ribbon {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0,0,0,0.6);
  color: #ffd700;
  text-align: center;
  font-size: 13px;
  font-weight: 700;
  padding: 6px;
  letter-spacing: 2px;
}

.ad-card__body { padding: 14px; }
.ad-card__name {
  font-size: 15px; color: #e1251b; font-weight: 700;
  margin-bottom: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.ad-card__desc {
  font-size: 13px; color: #666; margin-bottom: 10px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.ad-card__action {
  display: flex; align-items: center; justify-content: space-between;
}
.ad-card__cta {
  background: linear-gradient(135deg, #e1251b, #ff5000);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  padding: 6px 20px;
  border-radius: 20px;
  letter-spacing: 1px;
}
.ad-card__arrow {
  font-size: 18px; color: #e1251b; font-weight: bold;
  animation: arrowBounce 1.5s ease-in-out infinite;
}
@keyframes arrowBounce {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(5px); }
}

/* Wide variant for banner ads */
.ad-card--wide {
  grid-column: 1 / -1;
  border: 2px solid #e1251b;
}
.ad-card--wide .ad-card__body {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
}
.ad-card--wide .ad-card__name {
  font-size: 18px;
  flex-shrink: 0;
}
.ad-card--wide .ad-card__desc {
  flex: 1;
  margin-bottom: 0;
  -webkit-line-clamp: 1;
}
</style>
