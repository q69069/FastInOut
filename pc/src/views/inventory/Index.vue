<template>
  <div>
    <el-card>
      <template #header>库存查询</template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item>
          <el-input v-model="query.keyword" placeholder="搜索商品名称/编码" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item>
          <el-select v-model="query.warehouse_id" clearable placeholder="选择仓库">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="warehouse_name" label="仓库" width="120" />
        <el-table-column prop="product_code" label="商品编码" width="120" />
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="product_spec" label="规格" width="100" />
        <el-table-column prop="product_unit" label="单位" width="80" />
        <el-table-column prop="quantity" label="库存数量" width="100" />
        <el-table-column prop="cost_price" label="成本价" width="100" />
        <el-table-column prop="total_value" label="库存金额" width="120" />
      </el-table>
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top:16px;justify-content:flex-end"
        @current-change="loadData"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getInventory, getWarehouses } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, keyword: '', warehouse_id: null })
const warehouses = ref([])

const loadData = async () => {
  const res = await getInventory(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

onMounted(async () => {
  const wRes = await getWarehouses({ page_size: 100 })
  warehouses.value = wRes.data || []
  loadData()
})
</script>
