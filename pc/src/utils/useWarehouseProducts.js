import { ref, watch, computed } from 'vue'
import { getProducts } from '../api'

/**
 * 加载商品列表，支持仓库切换时自动刷新可用库存
 * @param {Function|import('vue').Ref|import('vue').ComputedRef} warehouseIdSource - 仓库ID的getter函数或ref
 * @param {Object} options
 * @param {number} options.pageSize - 每页数量，默认5000
 * @param {number} options.status - 商品状态，默认1（启用）
 */
export function useWarehouseProducts(warehouseIdSource, options = {}) {
  const { pageSize = 5000, status = 1 } = options
  const products = ref([])
  const productsLoading = ref(false)

  const warehouseIdRef = typeof warehouseIdSource === 'function'
    ? computed(warehouseIdSource)
    : warehouseIdSource

  const loadProducts = async () => {
    productsLoading.value = true
    try {
      const params = { page_size: pageSize, status }
      if (warehouseIdRef.value) params.warehouse_id = warehouseIdRef.value
      const res = await getProducts(params)
      products.value = res.data?.list || res.data || []
    } catch (e) {
      console.error('加载商品失败:', e)
    } finally {
      productsLoading.value = false
    }
  }

  watch(warehouseIdRef, () => { loadProducts() })

  return { products, productsLoading, loadProducts }
}
