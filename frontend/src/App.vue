<template>
  <el-container style="min-height: 100vh; display: flex; flex-direction: column">
    <el-header class="app-header" height="64px">
      <div class="header-inner">
        <div class="logo" @click="$router.push('/')">
          <span class="logo-icon">&#x1F6D2;</span>
          <span class="logo-text">智推商城</span>
        </div>
        <el-menu
          mode="horizontal"
          :router="true"
          :default-active="$route.path"
          class="nav-menu"
          background-color="transparent"
          text-color="#fff"
          active-text-color="#ffd700"
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/search">搜索</el-menu-item>
          <el-menu-item index="/cart" v-if="userStore.user">
            购物车
          </el-menu-item>
          <el-menu-item index="/orders" v-if="userStore.user">订单</el-menu-item>
          <el-menu-item index="/profile" v-if="userStore.user">个人中心</el-menu-item>
          <el-menu-item index="/merchant" v-if="userStore.user?.role === 'merchant'">商家后台</el-menu-item>
          <el-menu-item index="/admin" v-if="userStore.user?.role === 'admin'">管理后台</el-menu-item>
        </el-menu>
        <div class="header-right">
          <template v-if="userStore.user">
            <span class="welcome-text">{{ userStore.user.username }}</span>
            <el-button text class="logout-btn" @click="userStore.logout()">退出</el-button>
          </template>
          <template v-else>
            <el-button class="login-btn" @click="$router.push('/login')">登录</el-button>
            <el-button class="register-btn" type="primary" @click="$router.push('/register')">注册</el-button>
          </template>
        </div>
      </div>
    </el-header>
    <el-main class="app-main">
      <div class="page-container">
        <router-view />
      </div>
    </el-main>
    <footer class="app-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <span class="logo-icon">&#x1F6D2;</span> 智推商城
        </div>
        <div class="footer-links">
          <span>智能推荐引擎</span>
          <span class="dot">·</span>
          <span>社区驱动频控</span>
          <span class="dot">·</span>
          <span>商业化最大化</span>
        </div>
        <div class="footer-copy">&copy; 2026 E-Commerce Ad Recommendation System</div>
      </div>
    </footer>
  </el-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from './stores/user'

const userStore = useUserStore()
onMounted(() => userStore.fetchUser())
</script>

<style scoped>
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 12px rgba(102, 126, 234, 0.4);
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  height: 64px;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-right: 20px;
  flex-shrink: 0;
}

.logo-icon {
  font-size: 28px;
  margin-right: 8px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1px;
}

.nav-menu {
  flex: 1;
  border-bottom: none !important;
}

.nav-menu .el-menu-item {
  font-size: 14px;
  font-weight: 500;
  border-bottom: none !important;
  transition: all 0.2s;
}

.nav-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  border-radius: 8px;
}

.nav-menu .el-menu-item.is-active {
  background: rgba(255, 255, 255, 0.2) !important;
  border-radius: 8px;
  border-bottom: none !important;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.welcome-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
}

.logout-btn {
  color: rgba(255, 255, 255, 0.8) !important;
  font-size: 14px;
}

.login-btn {
  color: #fff !important;
  border-color: rgba(255, 255, 255, 0.5) !important;
  background: transparent !important;
  border-radius: 20px !important;
}

.register-btn {
  border-radius: 20px !important;
  background: rgba(255, 255, 255, 0.2) !important;
  border-color: transparent !important;
}

.app-main {
  flex: 1;
  padding: 30px 0;
  background: #f5f7fa;
}

.app-footer {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.7);
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.footer-brand {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 12px;
}

.footer-links {
  font-size: 14px;
  margin-bottom: 16px;
}

.footer-links .dot {
  margin: 0 10px;
  color: rgba(255, 255, 255, 0.3);
}

.footer-copy {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}
</style>
