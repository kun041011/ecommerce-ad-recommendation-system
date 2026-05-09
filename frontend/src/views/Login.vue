<template>
  <div class="auth-page">
    <el-card class="auth-card">
      <div class="auth-header">
        <span class="auth-icon">&#x1F464;</span>
        <h2>欢迎回来</h2>
        <p>登录你的账号</p>
      </div>
      <el-form @submit.prevent="handleLogin" class="auth-form">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" size="large" prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-button type="primary" native-type="submit" :loading="loading" size="large" round style="width: 100%; margin-top: 8px">
          登录
        </el-button>
      </el-form>
      <p class="auth-footer">
        还没有账号？<router-link to="/register" class="auth-link">立即注册</router-link>
      </p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const form = reactive({ username: '', password: '' })
const loading = ref(false)
const router = useRouter()
const userStore = useUserStore()

async function handleLogin() {
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch {
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.auth-card {
  width: 420px;
  padding: 20px;
}

.auth-header {
  text-align: center;
  margin-bottom: 24px;
}

.auth-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.auth-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 4px;
}

.auth-header p {
  color: #999;
  font-size: 14px;
}

.auth-footer {
  text-align: center;
  margin-top: 20px;
  color: #999;
  font-size: 14px;
}

.auth-link {
  color: #667eea;
  font-weight: 600;
  text-decoration: none;
}
</style>
