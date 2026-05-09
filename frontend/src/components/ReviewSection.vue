<template>
  <div>
    <div class="review-header">
      <h3 class="review-title">商品评价 ({{ reviews.length }})</h3>
    </div>

    <!-- Write review -->
    <div v-if="showForm" class="review-form">
      <div class="form-rate">
        <span class="form-label">评分:</span>
        <el-rate v-model="newReview.rating" />
      </div>
      <el-input v-model="newReview.content" type="textarea" :rows="3" placeholder="分享你的使用体验..." style="margin: 8px 0" />
      <el-button type="danger" size="default" @click="submitReview">发表评价</el-button>
    </div>

    <!-- Review list -->
    <div v-for="review in reviews" :key="review.id" class="review-item">
      <div class="review-item__head">
        <div class="reviewer-avatar">{{ 'U' }}</div>
        <div class="reviewer-info">
          <el-rate :model-value="review.rating" disabled size="small" />
          <span class="review-time">{{ review.created_at }}</span>
        </div>
      </div>
      <p class="review-content">{{ review.content }}</p>
      <div class="review-actions">
        <a href="javascript:;" class="helpful-btn" @click="markHelpful(review.id)">
          👍 有用 ({{ review.helpful_count }})
        </a>
      </div>
    </div>
    <p v-if="reviews.length === 0" class="empty-hint">暂无评价，快来抢先评价吧</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { communityApi } from '../api'
import { ElMessage } from 'element-plus'

const props = defineProps<{ productId: number; showForm: boolean }>()
const reviews = ref<any[]>([])
const newReview = ref({ rating: 5, content: '' })

async function load() { const { data } = await communityApi.getReviews(props.productId); reviews.value = data }
async function submitReview() {
  await communityApi.postReview({ product_id: props.productId, ...newReview.value })
  ElMessage.success('评价已提交'); newReview.value = { rating: 5, content: '' }; await load()
}
async function markHelpful(id: number) { await communityApi.helpful(id); await load() }
onMounted(load)
</script>

<style scoped>
.review-title { font-size: 16px; font-weight: 600; color: var(--text-dark); margin-bottom: 16px; }
.review-form { background: #fafafa; padding: 16px; border-radius: 6px; margin-bottom: 16px; }
.form-rate { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.form-label { font-size: 14px; color: var(--text-body); }

.review-item { padding: 16px 0; border-bottom: 1px solid #f5f5f5; }
.review-item__head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.reviewer-avatar { width: 32px; height: 32px; border-radius: 50%; background: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 14px; color: var(--text-light); }
.reviewer-info { display: flex; align-items: center; gap: 12px; }
.review-time { font-size: 12px; color: var(--text-light); }
.review-content { font-size: 14px; color: var(--text-dark); line-height: 1.6; margin-bottom: 8px; }
.helpful-btn { font-size: 13px; color: var(--text-light); text-decoration: none; }
.helpful-btn:hover { color: var(--jd-red); }
.empty-hint { color: var(--text-light); font-size: 14px; padding: 20px 0; }
</style>
