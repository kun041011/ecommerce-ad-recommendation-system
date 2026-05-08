import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('../views/Home.vue') },
  { path: '/login', component: () => import('../views/Login.vue') },
  { path: '/register', component: () => import('../views/Register.vue') },
  { path: '/product/:id', component: () => import('../views/ProductDetail.vue') },
  { path: '/search', component: () => import('../views/Search.vue') },
  { path: '/cart', component: () => import('../views/Cart.vue') },
  { path: '/orders', component: () => import('../views/Orders.vue') },
  { path: '/profile', component: () => import('../views/Profile.vue') },
  { path: '/merchant', component: () => import('../views/MerchantDashboard.vue') },
  { path: '/admin', component: () => import('../views/AdminDashboard.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
