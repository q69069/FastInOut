<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>报损单管理</span>
          <el-button type="primary" @click="showDialog()">新建报损单</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="待审核" value="pending" />
            <el-option label="已调整" value="adjusted" />
          </el-select>
        </el-form-item>
        <el-form-item><el-button type="primary" @click="loadData">查询</el-button></el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="code" label="单号" width="150" />
        <el-table-column prop="warehouse_name" label="仓库" width="120" />
        <el-table-column prop="total_amount" label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status==='adjusted'?'success':'info'">{{ row.status==='adjusted'?'已调整':'待审核' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="showDetail(row)">详情</el-button>
            <el-button link type="success" v-if="row.status==='pending'" @click="handleAudit(row)">审核调整</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total" layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadData" />
    </el-card>

    <el-dialog v-model="dialogVisible" title="新建报损单" width="800px" :close-on-click-modal="false">
      <el-form :model="form" label-width="80px">
        <el-form-item label="仓库" required>
          <el-select v-model="form.warehouse_id" filterable placeholder="选择仓库" style="width:100%">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-table :data="form.items" border size="small">
          <el-table-column label="商品" min-width="180">
            <template #default="{ row }">
              <el-select v-model="row.product_id" filterable placeholder="选择商品" style="width:100%">
                <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="数量" width="100">
            <template #default="{ row }"><el-input-number v-model="row.quantity" :min="0.01" :precision="2" size="small" style="width:100%" /></template>
          </el-table-column>
          <el-table-column label="单位成本" width="100">
            <template #default="{ row }"><el-input-number v-model="row.unit_cost" :min="0" :precision="2" size="small" style="width:100%" /></template>
          </el-table-column>
          <el-table-column label="原因" width="150">
            <template #default="{ row }"><el-input v-model="row.reason" size="small" placeholder="原因" /></template>
          </el-table-column>
          <el-table-column label="操作" width="60">
            <template #default="{ $index }"><el-button link type="danger" @click="form.items.splice($index,1)">删除</el-button></template>
          </el-table-column>
        </el-table>
        <el-button style="margin-top:8px" @click="form.items.push({product_id:null,quantity:1,unit_cost:0,reason:''})">+ 添加</el-button>
        <el-form-item label="备注" style="margin-top:12px">
          <el-input v-model="form.remark" placeholder="备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="报损单详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="单号">{{ detail.code }}</el-descriptions-item>
        <el-descriptions-item label="仓库">{{ detail.warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="总金额">¥{{ Number(detail.total_amount||0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ detail.status==='adjusted'?'已调整':'待审核' }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="detail.items||[]" border size="small" style="margin-top:16px">
        <el-table-column prop="product_name" label="商品" />
        <el-table-column prop="quantity" label="数量" width="80" align="right" />
        <el-table-column prop="unit_cost" label="单位成本" width="80" align="right" />
        <el-table-column prop="amount" label="金额" width="80" align="right" />
        <el-table-column prop="reason" label="原因" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDamageReports, createDamageReport, getDamageReport, auditDamageReport, getWarehouses, getProducts } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, status: '' })
const dialogVisible = ref(false)
const detailVisible = ref(false)
const saving = ref(false)
const detail = ref({})
const warehouses = ref([])
const products = ref([])
const form = ref({ warehouse_id: null, remark: '', items: [{ product_id: null, quantity: 1, unit_cost: 0, reason: '' }] })

const loadData = async () => {
  const res = await getDamageReports(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadDropdowns = async () => {
  const [w, p] = await Promise.all([getWarehouses(), getProducts()])
  warehouses.value = w.data || []
  products.value = p.data || []
}

const showDialog = () => {
  form.value = { warehouse_id: null, remark: '', items: [{ product_id: null, quantity: 1, unit_cost: 0, reason: '' }] }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.warehouse_id) return ElMessage.warning('请选择仓库')
  saving.value = true
  try {
    await createDamageReport(form.value)
    ElMessage.success('报损单创建成功')
    dialogVisible.value = false
    loadData()
  } finally { saving.value = false }
}

const showDetail = async (row) => {
  const res = await getDamageReport(row.id)
  detail.value = res.data || res
  detailVisible.value = true
}

const handleAudit = async (row) => {
  await ElMessageBox.confirm('确认审核报损？将扣减库存', '审核确认', { type: 'warning' })
  await auditDamageReport(row.id)
  ElMessage.success('报损审核通过，库存已扣减')
  loadData()
}

onMounted(() => { loadData(); loadDropdowns() })
</script>
