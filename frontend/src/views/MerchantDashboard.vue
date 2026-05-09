<template>
  <div class="merchant-page">
    <div class="merchant-sidebar">
      <div class="sidebar-title">商家中心</div>
      <div class="sidebar-menu">
        <div class="menu-item active">广告管理</div>
        <div class="menu-item">商品管理</div>
        <div class="menu-item">数据概览</div>
      </div>
    </div>

    <div class="merchant-content">
      <!-- Stats -->
      <div class="stats-row">
        <div class="stat-box">
          <div class="stat-box__value">{{ myAds.length }}</div>
          <div class="stat-box__label">广告总数</div>
        </div>
        <div class="stat-box">
          <div class="stat-box__value">{{ myAds.filter(a => a.status === 'active').length }}</div>
          <div class="stat-box__label">投放中</div>
        </div>
        <div class="stat-box">
          <div class="stat-box__value">¥{{ totalSpent.toFixed(0) }}</div>
          <div class="stat-box__label">总消耗</div>
        </div>
      </div>

      <!-- Table -->
      <div class="content-section">
        <div class="section-head">
          <h3>我的广告</h3>
          <el-button type="danger" size="default" @click="showAdForm = true">+ 创建广告</el-button>
        </div>
        <el-table :data="myAds" stripe v-if="myAds.length">
          <el-table-column prop="title" label="广告标题" />
          <el-table-column prop="bid_amount" label="出价" width="100" align="center">
            <template #default="{ row }">¥{{ row.bid_amount }}</template>
          </el-table-column>
          <el-table-column prop="daily_budget" label="日预算" width="100" align="center">
            <template #default="{ row }">¥{{ row.daily_budget }}</template>
          </el-table-column>
          <el-table-column label="已消耗" width="100" align="center">
            <template #default="{ row }">
              <span style="color:var(--price-red);font-weight:600">¥{{ row.spent_amount.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : row.status === 'exhausted' ? 'danger' : 'info'" size="small">
                {{ row.status === 'active' ? '投放中' : row.status === 'exhausted' ? '已耗尽' : '暂停' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        <div v-else class="empty-state" style="padding:40px">
          <p>暂无广告，点击上方按钮创建</p>
        </div>
      </div>
    </div>

    <el-dialog v-model="showAdForm" title="创建新广告" width="480px">
      <el-form label-width="80px">
        <el-form-item label="标题"><el-input v-model="adForm.title" placeholder="输入广告标题" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="adForm.content" type="textarea" :rows="3" placeholder="广告描述" /></el-form-item>
        <el-form-item label="出价"><el-input-number v-model="adForm.bid_amount" :min="0.1" :step="0.1" :precision="2" /></el-form-item>
        <el-form-item label="日预算"><el-input-number v-model="adForm.daily_budget" :min="10" :step="10" /></el-form-item>
        <el-form-item label="总预算"><el-input-number v-model="adForm.total_budget" :min="100" :step="100" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdForm = false">取消</el-button>
        <el-button type="danger" @click="createAd">确认创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { adApi } from '../api'

const myAds = ref<any[]>([])
const showAdForm = ref(false)
const adForm = reactive({ title: '', content: '', bid_amount: 1.0, daily_budget: 100, total_budget: 1000 })
const totalSpent = computed(() => myAds.value.reduce((s, a) => s + (a.spent_amount || 0), 0))

async function loadAds() { const { data } = await adApi.my(); myAds.value = data }
async function createAd() {
  await adApi.create(adForm); ElMessage.success('广告创建成功')
  showAdForm.value = false; adForm.title = ''; adForm.content = ''; await loadAds()
}
onMounted(loadAds)
</script>

<style scoped>
.merchant-page { display: flex; gap: 16px; }

.merchant-sidebar {
  width: 200px; flex-shrink: 0; background: #fff;
  border: 1px solid var(--border-light); border-radius: 8px;
  padding: 20px 0; align-self: flex-start;
}
.sidebar-title { font-size: 16px; font-weight: 700; color: var(--text-dark); padding: 0 20px 16px; border-bottom: 1px solid #f0f0f0; }
.sidebar-menu { padding-top: 8px; }
.menu-item { padding: 10px 20px; font-size: 14px; color: var(--text-body); cursor: pointer; }
.menu-item:hover { color: var(--jd-red); background: #fafafa; }
.menu-item.active { color: var(--jd-red); font-weight: 600; background: #fff5f5; border-right: 3px solid var(--jd-red); }

.merchant-content { flex: 1; }

.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }
.stat-box { background: #fff; border: 1px solid var(--border-light); border-radius: 8px; padding: 20px; text-align: center; }
.stat-box__value { font-size: 28px; font-weight: 700; color: var(--jd-red); }
.stat-box__label { font-size: 13px; color: var(--text-light); margin-top: 4px; }

.content-section { background: #fff; border: 1px solid var(--border-light); border-radius: 8px; padding: 20px; }
.section-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.section-head h3 { font-size: 16px; font-weight: 600; }
</style>
