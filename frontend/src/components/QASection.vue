<template>
  <div>
    <h3 class="qa-title">商品问答 ({{ qas.length }})</h3>

    <div v-if="showForm" class="qa-form">
      <el-input v-model="question" placeholder="有什么想问的？" />
      <el-button type="danger" size="default" @click="submitQuestion" style="margin-top: 8px">提问</el-button>
    </div>

    <div v-for="qa in qas" :key="qa.id" class="qa-item">
      <div class="qa-question">
        <span class="qa-badge qa-badge--q">问</span>
        <span>{{ qa.question }}</span>
      </div>
      <div class="qa-answer" v-if="qa.answer">
        <span class="qa-badge qa-badge--a">答</span>
        <span>{{ qa.answer }}</span>
      </div>
      <div class="qa-answer qa-no-answer" v-else>
        <span class="qa-badge qa-badge--a">答</span>
        <span>暂无回答</span>
      </div>
    </div>
    <p v-if="qas.length === 0" class="empty-hint">暂无问答</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { communityApi } from '../api'
import { ElMessage } from 'element-plus'

const props = defineProps<{ productId: number; showForm: boolean }>()
const qas = ref<any[]>([])
const question = ref('')

async function load() { const { data } = await communityApi.getQA(props.productId); qas.value = data }
async function submitQuestion() {
  await communityApi.postQuestion({ product_id: props.productId, question: question.value })
  ElMessage.success('问题已提交'); question.value = ''; await load()
}
onMounted(load)
</script>

<style scoped>
.qa-title { font-size: 16px; font-weight: 600; color: var(--text-dark); margin-bottom: 16px; }
.qa-form { background: #fafafa; padding: 16px; border-radius: 6px; margin-bottom: 16px; }
.qa-item { padding: 14px 0; border-bottom: 1px solid #f5f5f5; }
.qa-question, .qa-answer { display: flex; align-items: flex-start; gap: 8px; font-size: 14px; line-height: 1.6; }
.qa-answer { margin-top: 8px; color: var(--text-body); }
.qa-no-answer { color: var(--text-light); font-style: italic; }
.qa-badge { display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 3px; font-size: 12px; font-weight: 700; flex-shrink: 0; margin-top: 2px; }
.qa-badge--q { background: var(--jd-red); color: #fff; }
.qa-badge--a { background: #4caf50; color: #fff; }
.empty-hint { color: var(--text-light); font-size: 14px; padding: 20px 0; }
</style>
