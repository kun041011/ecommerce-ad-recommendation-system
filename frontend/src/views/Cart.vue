<template>
  <div style="max-width: 960px; margin: 0 auto">
    <h2 class="page-title">我的购物车</h2>

    <div v-if="cartStore.items.length" class="cart-container">
      <!-- Cart table -->
      <div class="cart-table">
        <div class="cart-table__head">
          <span class="col-product">商品信息</span>
          <span class="col-price">单价</span>
          <span class="col-qty">数量</span>
          <span class="col-subtotal">小计</span>
          <span class="col-action">操作</span>
        </div>
        <div class="cart-item" v-for="item in cartStore.items" :key="item.product_id">
          <div class="col-product">
            <div class="item-thumb">🛍️</div>
            <span class="item-name">{{ item.name }}</span>
          </div>
          <div class="col-price">
            <span class="price-symbol">¥</span>{{ item.price.toFixed(2) }}
          </div>
          <div class="col-qty">
            <el-input-number v-model="item.quantity" :min="1" size="small" />
          </div>
          <div class="col-subtotal">
            <strong style="color: var(--price-red)">¥{{ (item.price * item.quantity).toFixed(2) }}</strong>
          </div>
          <div class="col-action">
            <a href="javascript:;" @click="cartStore.removeItem(item.product_id)" class="remove-link">删除</a>
          </div>
        </div>
      </div>

      <!-- Bottom bar -->
      <div class="cart-bottom">
        <div class="cart-bottom__left">
          共 <strong>{{ cartStore.items.length }}</strong> 件商品
        </div>
        <div class="cart-bottom__right">
          <span class="cart-total">
            总计: <span class="price-symbol" style="font-size:16px">¥</span>
            <span class="price-main" style="font-size:28px">{{ Math.floor(cartStore.total) }}</span>
            <span class="price-decimal">.{{ ((cartStore.total % 1) * 100).toFixed(0).padStart(2, '0') }}</span>
          </span>
          <el-button class="checkout-btn" size="large" @click="checkout">去结算</el-button>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <p style="font-size: 64px; margin-bottom: 16px">🛒</p>
      <p style="font-size: 16px; margin-bottom: 16px">购物车还是空的</p>
      <el-button type="danger" @click="$router.push('/')">去购物</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { orderApi } from '../api'
import { useCartStore } from '../stores/cart'

const cartStore = useCartStore()
const router = useRouter()

async function checkout() {
  const items = cartStore.items.map((i) => ({ product_id: i.product_id, quantity: i.quantity }))
  await orderApi.create(items)
  cartStore.clear()
  ElMessage.success('订单创建成功！')
  router.push('/orders')
}
</script>

<style scoped>
.page-title { font-size: 20px; font-weight: 700; margin-bottom: 16px; color: var(--text-dark); }

.cart-container { background: #fff; border: 1px solid var(--border-light); border-radius: 8px; }

.cart-table__head {
  display: flex; align-items: center; padding: 12px 20px;
  background: #f5f5f5; font-size: 13px; color: var(--text-light); font-weight: 600;
  border-bottom: 1px solid var(--border-light);
}

.cart-item {
  display: flex; align-items: center; padding: 16px 20px;
  border-bottom: 1px solid #f5f5f5; font-size: 14px;
}

.col-product { flex: 3; display: flex; align-items: center; gap: 12px; }
.col-price { flex: 1; text-align: center; color: var(--text-body); }
.col-qty { flex: 1; display: flex; justify-content: center; }
.col-subtotal { flex: 1; text-align: center; }
.col-action { flex: 0.5; text-align: center; }

.item-thumb {
  width: 60px; height: 60px; background: #f9f9f9; border-radius: 6px;
  display: flex; align-items: center; justify-content: center; font-size: 28px;
  flex-shrink: 0;
}
.item-name { font-weight: 500; color: var(--text-dark); }
.remove-link { color: var(--text-light); font-size: 13px; }
.remove-link:hover { color: var(--jd-red); }

.cart-bottom {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px;
}
.cart-bottom__left { color: var(--text-body); font-size: 14px; }
.cart-bottom__right { display: flex; align-items: center; gap: 20px; }
.cart-total { color: var(--text-dark); }
.price-symbol { color: var(--price-red); font-weight: 700; }
.price-main { color: var(--price-red); font-weight: 700; }
.price-decimal { color: var(--price-red); font-weight: 700; font-size: 16px; }

.checkout-btn {
  background: var(--jd-red) !important; color: #fff !important;
  border: none !important; width: 140px; font-size: 16px !important;
  font-weight: 600 !important; height: 46px !important;
}
.checkout-btn:hover { background: #c91f17 !important; }
</style>
