<template>
  <div class="profile-page">
    <!-- Left sidebar -->
    <div class="profile-sidebar">
      <div class="sidebar-avatar">
        <div class="avatar-circle">{{ userStore.user?.username?.charAt(0)?.toUpperCase() }}</div>
        <div class="avatar-info">
          <strong>{{ userStore.user?.username }}</strong>
          <el-tag :type="roleType" size="small" effect="plain">{{ roleText }}</el-tag>
        </div>
      </div>
      <div class="sidebar-menu">
        <div class="menu-item active">个人信息</div>
        <div class="menu-item" @click="$router.push('/orders')">我的订单</div>
        <div class="menu-item" @click="$router.push('/cart')">购物车</div>
      </div>
    </div>

    <!-- Right content -->
    <div class="profile-content">
      <div class="content-section">
        <h3 class="content-title">个人信息</h3>
        <div class="info-grid" v-if="userStore.user">
          <div class="info-row"><span class="info-label">用户名</span><span>{{ userStore.user.username }}</span></div>
          <div class="info-row"><span class="info-label">邮箱</span><span>{{ userStore.user.email }}</span></div>
          <div class="info-row"><span class="info-label">角色</span><span>{{ roleText }}</span></div>
          <div class="info-row"><span class="info-label">注册时间</span><span>{{ userStore.user.created_at }}</span></div>
        </div>
      </div>
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
.profile-page { display: flex; gap: 16px; }

.profile-sidebar {
  width: 220px; flex-shrink: 0; background: #fff;
  border: 1px solid var(--border-light); border-radius: 8px;
  padding: 24px 16px; align-self: flex-start;
}
.sidebar-avatar { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #f0f0f0; }
.avatar-circle {
  width: 48px; height: 48px; border-radius: 50%;
  background: var(--jd-red); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; font-weight: 700; flex-shrink: 0;
}
.avatar-info { display: flex; flex-direction: column; gap: 4px; }
.avatar-info strong { font-size: 15px; color: var(--text-dark); }

.sidebar-menu { display: flex; flex-direction: column; gap: 2px; }
.menu-item {
  padding: 10px 12px; font-size: 14px; color: var(--text-body);
  cursor: pointer; border-radius: 4px; transition: all 0.15s;
}
.menu-item:hover { background: #f5f5f5; color: var(--jd-red); }
.menu-item.active { background: #fff5f5; color: var(--jd-red); font-weight: 600; }

.profile-content { flex: 1; }
.content-section {
  background: #fff; border: 1px solid var(--border-light); border-radius: 8px;
  padding: 24px; margin-bottom: 16px;
}
.content-title { font-size: 16px; font-weight: 600; color: var(--text-dark); margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #f0f0f0; }

.info-grid { display: flex; flex-direction: column; }
.info-row { display: flex; padding: 10px 0; border-bottom: 1px solid #fafafa; font-size: 14px; }
.info-label { width: 100px; color: var(--text-light); flex-shrink: 0; }
</style>
