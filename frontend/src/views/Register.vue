<template>
  <div class="auth-page">
    <el-card class="auth-card">
      <div class="auth-header">
        <span class="auth-icon">&#x1F389;</span>
        <h2>创建账号</h2>
        <p>加入智推商城，发现精彩好物</p>
      </div>
      <el-form @submit.prevent="handleRegister" class="auth-form">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" size="large" prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.email" type="email" placeholder="邮箱" size="large" prefix-icon="Message" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-button type="primary" native-type="submit" :loading="loading" size="large" round style="width: 100%; margin-top: 8px">
          注册
        </el-button>
      </el-form>
      <p class="auth-footer">
        已有账号？<router-link to="/login" class="auth-link">立即登录</router-link>
      </p>
    </el-card>
  </div>
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
