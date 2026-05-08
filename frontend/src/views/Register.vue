<template>
  <el-card style="max-width: 400px; margin: 40px auto">
    <template #header>用户注册</template>
    <el-form @submit.prevent="handleRegister">
      <el-form-item label="用户名">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="form.email" type="email" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" />
      </el-form-item>
      <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%">注册</el-button>
    </el-form>
    <p style="margin-top: 12px; text-align: center">
      已有账号？<router-link to="/login">登录</router-link>
    </p>
  </el-card>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const form = reactive({ username: '', email: '', password: '' })
const loading = ref(false)
const router = useRouter()
const userStore = useUserStore()

async function handleRegister() {
  loading.value = true
  try {
    await userStore.register(form.username, form.email, form.password)
    ElMessage.success('注册成功')
    router.push('/')
  } catch {
    ElMessage.error('注册失败')
  } finally {
    loading.value = false
  }
}
</script>
