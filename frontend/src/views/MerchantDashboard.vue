<template>
  <div>
    <h2>商家后台</h2>
    <el-tabs>
      <el-tab-pane label="我的广告">
        <el-button type="primary" @click="showAdForm = true" style="margin-bottom: 16px">创建广告</el-button>
        <el-dialog v-model="showAdForm" title="创建广告">
          <el-form>
            <el-form-item label="标题"><el-input v-model="adForm.title" /></el-form-item>
            <el-form-item label="内容"><el-input v-model="adForm.content" type="textarea" /></el-form-item>
            <el-form-item label="出价"><el-input-number v-model="adForm.bid_amount" :min="0.1" :step="0.1" /></el-form-item>
            <el-form-item label="日预算"><el-input-number v-model="adForm.daily_budget" :min="10" /></el-form-item>
            <el-form-item label="总预算"><el-input-number v-model="adForm.total_budget" :min="100" /></el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="showAdForm = false">取消</el-button>
            <el-button type="primary" @click="createAd">创建</el-button>
          </template>
        </el-dialog>
        <el-table :data="myAds">
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="bid_amount" label="出价" width="100" />
          <el-table-column prop="spent_amount" label="已消耗" width="100" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adApi } from '../api'

const myAds = ref<any[]>([])
const showAdForm = ref(false)
const adForm = reactive({
  title: '', content: '', bid_amount: 1.0, daily_budget: 100, total_budget: 1000,
})

async function loadAds() {
  const { data } = await adApi.my()
  myAds.value = data
}

async function createAd() {
  await adApi.create(adForm)
  ElMessage.success('广告已创建')
  showAdForm.value = false
  await loadAds()
}

onMounted(loadAds)
</script>
