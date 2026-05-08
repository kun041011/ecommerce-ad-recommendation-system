<template>
  <div>
    <h3>问答</h3>
    <el-form v-if="showForm" @submit.prevent="submitQuestion" style="margin-bottom: 16px">
      <el-input v-model="question" placeholder="提个问题..." />
      <el-button type="primary" size="small" native-type="submit" style="margin-top: 8px">提问</el-button>
    </el-form>
    <div v-for="qa in qas" :key="qa.id" style="border-bottom: 1px solid #eee; padding: 12px 0">
      <p><strong>问:</strong> {{ qa.question }}</p>
      <p v-if="qa.answer"><strong>答:</strong> {{ qa.answer }}</p>
      <p v-else style="color: #999">暂无回答</p>
    </div>
    <p v-if="qas.length === 0" style="color: #999">暂无问答</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { communityApi } from '../api'
import { ElMessage } from 'element-plus'

const props = defineProps<{ productId: number; showForm: boolean }>()
const qas = ref<any[]>([])
const question = ref('')

async function load() {
  const { data } = await communityApi.getQA(props.productId)
  qas.value = data
}

async function submitQuestion() {
  await communityApi.postQuestion({ product_id: props.productId, question: question.value })
  ElMessage.success('问题已提交')
  question.value = ''
  await load()
}

onMounted(load)
</script>
