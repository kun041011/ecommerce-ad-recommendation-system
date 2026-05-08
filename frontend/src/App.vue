<template>
  <el-container style="min-height: 100vh">
    <el-header>
      <el-menu mode="horizontal" :router="true" :default-active="$route.path">
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/search">搜索</el-menu-item>
        <el-menu-item index="/cart" v-if="userStore.user">购物车</el-menu-item>
        <el-menu-item index="/orders" v-if="userStore.user">订单</el-menu-item>
        <el-menu-item index="/profile" v-if="userStore.user">个人中心</el-menu-item>
        <el-menu-item index="/merchant" v-if="userStore.user?.role === 'merchant'">商家后台</el-menu-item>
        <el-menu-item index="/admin" v-if="userStore.user?.role === 'admin'">管理后台</el-menu-item>
        <div style="flex-grow: 1"></div>
        <el-menu-item v-if="!userStore.user" index="/login">登录</el-menu-item>
        <el-menu-item v-if="userStore.user" @click="userStore.logout()">退出</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from './stores/user'

const userStore = useUserStore()
onMounted(() => userStore.fetchUser())
</script>
