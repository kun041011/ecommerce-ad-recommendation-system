<template>
  <el-card shadow="hover" style="cursor: pointer" @click="$router.push(`/product/${product.id}`)">
    <div style="padding: 14px">
      <h3 style="margin: 0 0 8px">{{ product.name }}</h3>
      <p style="color: #e74c3c; font-size: 18px; font-weight: bold; margin: 4px 0">
        ¥{{ product.price.toFixed(2) }}
      </p>
      <p style="color: #999; font-size: 12px; margin: 4px 0">销量: {{ product.sales_count }}</p>
    </div>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{ product: any }>()
</script>
