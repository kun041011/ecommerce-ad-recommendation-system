<template>
  <div>
    <h3>商品评价</h3>
    <el-form v-if="showForm" @submit.prevent="submitReview" style="margin-bottom: 16px">
      <el-rate v-model="newReview.rating" />
      <el-input v-model="newReview.content" type="textarea" placeholder="写下你的评价..." style="margin: 8px 0" />
      <el-button type="primary" size="small" native-type="submit">提交评价</el-button>
    </el-form>
    <div v-for="review in reviews" :key="review.id" style="border-bottom: 1px solid #eee; padding: 12px 0">
      <el-rate :model-value="review.rating" disabled />
      <p>{{ review.content }}</p>
      <el-button text size="small" @click="markHelpful(review.id)">
        有用 ({{ review.helpful_count }})
      </el-button>
    </div>
    <p v-if="reviews.length === 0" style="color: #999">暂无评价</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { communityApi } from '../api'
import { ElMessage } from 'element-plus'

const props = defineProps<{ productId: number; showForm: boolean }>()
const reviews = ref<any[]>([])
const newReview = ref({ rating: 5, content: '' })

async function load() {
  const { data } = await communityApi.getReviews(props.productId)
  reviews.value = data
}

async function submitReview() {
  await communityApi.postReview({ product_id: props.productId, ...newReview.value })
  ElMessage.success('评价已提交')
  newReview.value = { rating: 5, content: '' }
  await load()
}

async function markHelpful(id: number) {
  await communityApi.helpful(id)
  await load()
}

onMounted(load)
</script>
