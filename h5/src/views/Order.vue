<template>
  <div class="order-page">
    <van-form @submit="handleSubmit">
      <van-cell-group inset title="客户信息">
        <van-field v-model="form.customer_id" label="客户" placeholder="选择客户" readonly @click="showCustomer = true" />
      </van-cell-group>
      <van-cell-group inset title="商品明细">
        <div v-for="(item, idx) in form.items" :key="idx" class="item-row">
          <van-field v-model="item.product_id" label="商品" placeholder="选择商品" style="flex:1" />
          <van-field v-model="item.quantity" type="number" label="数量" style="width:80px" />
          <van-icon name="cross" @click="form.items.splice(idx, 1)" />
        </div>
        <van-button block plain type="primary" size="small" @click="addItem" style="margin:8px">
          + 添加商品
        </van-button>
      </van-cell-group>
      <van-cell-group inset title="备注">
        <van-field v-model="form.remark" type="textarea" placeholder="备注信息" />
      </van-cell-group>
      <div style="margin:16px">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          提交订单
        </van-button>
      </div>
    </van-form>
    <van-popup v-model:show="showCustomer" position="bottom">
      <van-picker :columns="customerColumns" @change="onCustomerChange" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { showToast } from 'vant'
import { createSalesOrder, getCustomers, getProducts } from '../api'

const form = ref({ customer_id: null, remark: '', items: [] })
const loading = ref(false)
const showCustomer = ref(false)
const customers = ref([])
const products = ref([])
const customerColumns = ref([])

const addItem = () => {
  form.value.items.push({ product_id: null, quantity: 1 })
}

const onCustomerChange = ({ selectedValues }) => {
  form.value.customer_id = selectedValues[0]
  showCustomer.value = false
}

const handleSubmit = async () => {
  if (!form.value.customer_id) return showToast('请选择客户')
  if (!form.value.items.length) return showToast('请添加商品')
  loading.value = true
  try {
    await createSalesOrder(form.value)
    showToast('订单提交成功')
    form.value = { customer_id: null, remark: '', items: [] }
  } catch (e) {
    showToast('提交失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const [c, p] = await Promise.all([getCustomers({ page_size: 100 }), getProducts({ page_size: 100 })])
  customers.value = c.data || []
  products.value = p.data || []
  customerColumns.value = [{ values: customers.value.map(s => ({ text: s.name, value: s.id })) }]
})
</script>

<style scoped>
.order-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-top: 16px;
}
.item-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
}
</style>
