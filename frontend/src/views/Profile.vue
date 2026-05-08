<template>
  <div style="max-width: 800px; margin: 0 auto">
    <el-card style="margin-bottom: 16px">
      <template #header>个人信息</template>
      <el-descriptions :column="2" border v-if="userStore.user">
        <el-descriptions-item label="用户名">{{ userStore.user.username }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ userStore.user.email }}</el-descriptions-item>
        <el-descriptions-item label="角色">{{ userStore.user.role }}</el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ userStore.user.created_at }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
    <ActivityScore />
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '../stores/user'
import ActivityScore from '../components/ActivityScore.vue'

const userStore = useUserStore()
</script>
