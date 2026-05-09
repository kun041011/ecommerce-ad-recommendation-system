<template>
  <div>
    <h2 class="section-title">&#x1F3EA; 商家后台</h2>

    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="font-weight: 600">我的广告</span>
          <el-button type="primary" round @click="showAdForm = true">+ 创建广告</el-button>
        </div>
      </template>

      <el-table :data="myAds" stripe v-if="myAds.length">
        <el-table-column prop="title" label="广告标题" />
        <el-table-column prop="bid_amount" label="出价" width="100" align="center">
          <template #default="{ row }">¥{{ row.bid_amount }}</template>
        </el-table-column>
        <el-table-column prop="daily_budget" label="日预算" width="100" align="center">
          <template #default="{ row }">¥{{ row.daily_budget }}</template>
        </el-table-column>
        <el-table-column prop="spent_amount" label="已消耗" width="100" align="center">
          <template #default="{ row }">
            <span style="color: #e74c3c; font-weight: 600">¥{{ row.spent_amount.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'active' ? 'success' : row.status === 'exhausted' ? 'danger' : 'info'"
              effect="dark" round size="small"
            >{{ row.status === 'active' ? '投放中' : row.status === 'exhausted' ? '已耗尽' : '暂停' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div v-else style="text-align: center; padding: 40px; color: #999">
        <p style="font-size: 40px; margin-bottom: 8px">&#x1F4E2;</p>
        <p>暂无广告，点击上方按钮创建</p>
      </div>
    </el-card>

    <el-dialog v-model="showAdForm" title="创建新广告" width="480px">
      <el-form label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="adForm.title" placeholder="输入广告标题" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="adForm.content" type="textarea" :rows="3" placeholder="广告描述" />
        </el-form-item>
        <el-form-item label="出价">
          <el-input-number v-model="adForm.bid_amount" :min="0.1" :step="0.1" :precision="2" />
          <span style="margin-left: 8px; color: #999; font-size: 12px">元/点击</span>
        </el-form-item>
        <el-form-item label="日预算">
          <el-input-number v-model="adForm.daily_budget" :min="10" :step="10" />
          <span style="margin-left: 8px; color: #999; font-size: 12px">元</span>
        </el-form-item>
        <el-form-item label="总预算">
          <el-input-number v-model="adForm.total_budget" :min="100" :step="100" />
          <span style="margin-left: 8px; color: #999; font-size: 12px">元</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdForm = false">取消</el-button>
        <el-button type="primary" @click="createAd">确认创建</el-button>
      </template>
    </el-dialog>
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
  ElMessage.success('广告创建成功')
  showAdForm.value = false
  adForm.title = ''
  adForm.content = ''
  await loadAds()
}

onMounted(loadAds)
</script>
