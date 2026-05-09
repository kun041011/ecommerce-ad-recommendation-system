<template>
  <div class="app-wrapper">
    <!-- Top utility bar -->
    <div class="top-bar">
      <div class="top-bar__inner page-container">
        <div class="top-bar__left">
          <template v-if="userStore.user">
            <span>你好，<strong>{{ userStore.user.username }}</strong></span>
            <a href="javascript:;" @click="userStore.logout()">退出登录</a>
          </template>
          <template v-else>
            <span>你好，请</span>
            <router-link to="/login">登录</router-link>
            <router-link to="/register">免费注册</router-link>
          </template>
        </div>
        <div class="top-bar__right">
          <router-link to="/orders" v-if="userStore.user">我的订单</router-link>
          <router-link to="/profile" v-if="userStore.user">个人中心</router-link>
          <router-link to="/merchant" v-if="userStore.user?.role === 'merchant'">商家后台</router-link>
          <router-link to="/admin" v-if="userStore.user?.role === 'admin'">管理后台</router-link>
        </div>
      </div>
    </div>

    <!-- Main header -->
    <header class="main-header">
      <div class="main-header__inner page-container">
        <div class="logo" @click="$router.push('/')">
          <div class="logo__icon">智推</div>
          <span class="logo__text">MALL</span>
        </div>
        <div class="header-search">
          <input
            v-model="searchQuery"
            class="header-search__input"
            placeholder="搜索商品、品牌、品类..."
            @keyup.enter="doSearch"
          />
          <button class="header-search__btn" @click="doSearch">搜索</button>
        </div>
        <div class="header-cart" @click="$router.push('/cart')" v-if="userStore.user">
          <span class="header-cart__icon">🛒</span>
          <span class="header-cart__text">购物车</span>
          <span class="header-cart__badge" v-if="cartCount > 0">{{ cartCount }}</span>
        </div>
      </div>
    </header>

    <!-- Navigation bar -->
    <nav class="nav-bar">
      <div class="nav-bar__inner page-container">
        <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">首页</router-link>
        <router-link to="/search?category=电子产品" class="nav-link">电子产品</router-link>
        <router-link to="/search?category=服装鞋帽" class="nav-link">服装鞋帽</router-link>
        <router-link to="/search?category=食品饮料" class="nav-link">食品饮料</router-link>
        <router-link to="/search?category=家居家装" class="nav-link">家居家装</router-link>
        <router-link to="/search?category=美妆个护" class="nav-link">美妆个护</router-link>
        <router-link to="/search?category=运动户外" class="nav-link">运动户外</router-link>
        <router-link to="/search?category=图书音像" class="nav-link">图书音像</router-link>
      </div>
    </nav>

    <!-- Main content -->
    <main class="app-main">
      <div class="page-container">
        <router-view />
      </div>
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <div class="page-container">
        <div class="footer-grid">
          <div class="footer-col">
            <h4>购物指南</h4>
            <p>购物流程</p>
            <p>会员介绍</p>
            <p>常见问题</p>
          </div>
          <div class="footer-col">
            <h4>配送方式</h4>
            <p>上门自提</p>
            <p>配送服务</p>
            <p>配送范围</p>
          </div>
          <div class="footer-col">
            <h4>支付方式</h4>
            <p>在线支付</p>
            <p>货到付款</p>
            <p>分期付款</p>
          </div>
          <div class="footer-col">
            <h4>售后服务</h4>
            <p>售后政策</p>
            <p>退换货流程</p>
            <p>联系客服</p>
          </div>
          <div class="footer-col">
            <h4>关于我们</h4>
            <p>智能推荐引擎</p>
            <p>社区驱动频控</p>
            <p>商业化最大化</p>
          </div>
        </div>
        <div class="footer-bottom">
          <p>© 2026 智推商城 — 基于社区数据反馈的电商广告推荐系统</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from './stores/user'
import { useCartStore } from './stores/cart'

const userStore = useUserStore()
const cartStore = useCartStore()
const router = useRouter()
const searchQuery = ref('')

const cartCount = computed(() => cartStore.items.reduce((s, i) => s + i.quantity, 0))

function doSearch() {
  if (searchQuery.value.trim()) {
    router.push({ path: '/search', query: { q: searchQuery.value } })
  }
}

onMounted(() => userStore.fetchUser())
</script>

<style scoped>
.app-wrapper { display: flex; flex-direction: column; min-height: 100vh; }

/* Top bar */
.top-bar { background: #333; font-size: 12px; color: #ccc; line-height: 30px; }
.top-bar__inner { display: flex; justify-content: space-between; }
.top-bar__left, .top-bar__right { display: flex; gap: 12px; align-items: center; }
.top-bar a { color: #ccc; text-decoration: none; }
.top-bar a:hover { color: #fff; }

/* Main header */
.main-header { background: #fff; border-bottom: 1px solid #e8e8e8; }
.main-header__inner { display: flex; align-items: center; height: 80px; gap: 40px; }

.logo { display: flex; align-items: center; cursor: pointer; flex-shrink: 0; gap: 6px; }
.logo__icon {
  background: var(--jd-red);
  color: #fff;
  font-size: 18px;
  font-weight: 800;
  padding: 6px 10px;
  border-radius: 6px;
  letter-spacing: 2px;
}
.logo__text { font-size: 22px; font-weight: 700; color: var(--text-dark); letter-spacing: 1px; }

.header-search { flex: 1; max-width: 560px; display: flex; height: 40px; }
.header-search__input {
  flex: 1;
  border: 2px solid var(--jd-red);
  border-right: none;
  padding: 0 16px;
  font-size: 14px;
  outline: none;
  border-radius: 0;
}
.header-search__btn {
  width: 80px;
  background: var(--jd-red);
  color: #fff;
  border: 2px solid var(--jd-red);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  letter-spacing: 2px;
}
.header-search__btn:hover { background: #c91f17; border-color: #c91f17; }

.header-cart {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 20px;
  border: 1px solid var(--border-light);
  border-radius: 4px;
  cursor: pointer;
  position: relative;
  font-size: 14px;
  color: var(--text-body);
}
.header-cart:hover { border-color: var(--jd-red); color: var(--jd-red); }
.header-cart__icon { font-size: 20px; }
.header-cart__badge {
  position: absolute;
  top: -6px; right: -6px;
  background: var(--jd-red);
  color: #fff;
  font-size: 11px;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

/* Nav bar */
.nav-bar { background: #fff; border-bottom: 2px solid var(--jd-red); }
.nav-bar__inner { display: flex; gap: 0; height: 40px; align-items: stretch; }
.nav-link {
  display: flex; align-items: center;
  padding: 0 18px;
  font-size: 14px;
  color: var(--text-dark);
  text-decoration: none;
  font-weight: 500;
  transition: background 0.15s;
}
.nav-link:hover, .nav-link.active { background: var(--jd-red); color: #fff; text-decoration: none; }

/* Main */
.app-main { flex: 1; padding: 20px 0; }

/* Footer */
.app-footer { background: #333; padding: 40px 0 0; color: #999; margin-top: 40px; }
.footer-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 30px; padding-bottom: 30px; border-bottom: 1px solid #444; }
.footer-col h4 { color: #fff; font-size: 14px; margin-bottom: 12px; }
.footer-col p { font-size: 12px; line-height: 2; cursor: pointer; }
.footer-col p:hover { color: #fff; }
.footer-bottom { text-align: center; padding: 20px 0; font-size: 12px; color: #666; }
</style>
