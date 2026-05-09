<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-brand">
        <div class="brand-icon">智推</div>
        <span class="brand-text">MALL</span>
      </div>
      <h2 class="auth-title">账号登录</h2>
      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <input v-model="form.username" class="form-input" placeholder="请输入用户名" />
        </div>
        <div class="form-group">
          <input v-model="form.password" type="password" class="form-input" placeholder="请输入密码" />
        </div>
        <button type="submit" class="auth-submit" :disabled="loading">
          {{ loading ? '登录中...' : '登  录' }}
        </button>
      </form>
      <div class="auth-footer">
        <router-link to="/register" class="auth-link">免费注册 ›</router-link>
      </div>
      <div class="auth-agreement">
        登录即表示同意 <a href="javascript:;">《用户服务协议》</a> 和 <a href="javascript:;">《隐私政策》</a>
      </div>
    </div>
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
  display: flex; justify-content: center; align-items: center;
  min-height: 65vh; padding: 40px 20px;
}
.auth-card {
  width: 380px; background: #fff; border-radius: 8px;
  padding: 40px 32px; box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  border: 1px solid var(--border-light);
}
.auth-brand { display: flex; align-items: center; justify-content: center; gap: 6px; margin-bottom: 24px; }
.brand-icon { background: var(--jd-red); color: #fff; font-size: 16px; font-weight: 800; padding: 4px 8px; border-radius: 4px; }
.brand-text { font-size: 20px; font-weight: 700; color: var(--text-dark); }

.auth-title { text-align: center; font-size: 18px; font-weight: 600; color: var(--text-dark); margin-bottom: 24px; }

.form-group { margin-bottom: 16px; }
.form-input {
  width: 100%; height: 44px; padding: 0 14px;
  border: 1px solid #ddd; border-radius: 4px; font-size: 14px;
  outline: none; transition: border-color 0.15s;
}
.form-input:focus { border-color: var(--jd-red); }

.auth-submit {
  width: 100%; height: 44px; background: var(--jd-red); color: #fff;
  border: none; border-radius: 4px; font-size: 16px; font-weight: 600;
  cursor: pointer; letter-spacing: 4px; margin-top: 8px;
}
.auth-submit:hover { background: #c91f17; }
.auth-submit:disabled { opacity: 0.7; cursor: not-allowed; }

.auth-footer { text-align: right; margin-top: 16px; }
.auth-link { color: var(--jd-red); font-size: 14px; text-decoration: none; }
.auth-link:hover { text-decoration: underline; }

.auth-agreement { margin-top: 20px; font-size: 12px; color: var(--text-light); text-align: center; }
.auth-agreement a { color: var(--text-body); }
</style>
