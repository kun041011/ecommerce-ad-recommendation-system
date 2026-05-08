import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface CartItem {
  product_id: number
  name: string
  price: number
  quantity: number
}

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])

  const total = computed(() =>
    items.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )

  function addItem(product: { id: number; name: string; price: number }) {
    const existing = items.value.find((i) => i.product_id === product.id)
    if (existing) {
      existing.quantity++
    } else {
      items.value.push({ product_id: product.id, name: product.name, price: product.price, quantity: 1 })
    }
  }

  function removeItem(productId: number) {
    items.value = items.value.filter((i) => i.product_id !== productId)
  }

  function clear() {
    items.value = []
  }

  return { items, total, addItem, removeItem, clear }
})
