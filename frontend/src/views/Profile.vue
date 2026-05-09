<template>
  <div style="max-width: 800px; margin: 0 auto">
    <h2 class="section-title">&#x1F464; 个人中心</h2>

    <el-card class="profile-card">
      <div class="profile-header">
        <div class="avatar">
          <span>{{ userStore.user?.username?.charAt(0)?.toUpperCase() }}</span>
        </div>
        <div class="profile-name">
          <h3>{{ userStore.user?.username }}</h3>
          <el-tag :type="roleType" effect="dark" size="small" round>{{ roleText }}</el-tag>
        </div>
      </div>
      <el-descriptions :column="2" border v-if="userStore.user" class="profile-desc">
        <el-descriptions-item label="邮箱">{{ userStore.user.email }}</el-descriptions-item>
        <el-descriptions-item label="角色">{{ roleText }}</el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ userStore.user.created_at }}</el-descriptions-item>
        <el-descriptions-item label="最后活跃">{{ userStore.user.last_active_at }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <div style="margin-top: 20px">
      <ActivityScore />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useUserStore } from '../stores/user'
import ActivityScore from '../components/ActivityScore.vue'

const userStore = useUserStore()

const roleMap: Record<string, { type: string; text: string }> = {
  consumer: { type: 'primary', text: '消费者' },
  merchant: { type: 'warning', text: '商家' },
  admin: { type: 'danger', text: '管理员' },
}

const roleType = computed(() => (roleMap[userStore.user?.role]?.type || 'info') as any)
const roleText = computed(() => roleMap[userStore.user?.role]?.text || userStore.user?.role)
</script>

<style scoped>
.profile-card {
  margin-bottom: 20px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 28px;
  font-weight: 700;
}

.profile-name h3 {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 6px;
}
</style>
