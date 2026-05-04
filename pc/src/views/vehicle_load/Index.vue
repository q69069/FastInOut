<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>装车单管理</span>
          <el-button type="primary" @click="showDialog()">新建装车单</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="草稿" value="draft" />
            <el-option label="已装车" value="loaded" />
            <el-option label="已退库" value="returned" />
          </el-select>
        </el-form-item>
        <el-form-item><el-button type="primary" @click="loadData">查询</el-button></el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="load_no" label="单号" width="150" />
        <el-table-column prop="from_warehouse_name" label="来源仓库" width="120" />
        <el-table-column prop="vehicle_warehouse_name" label="目标车仓" width="120" />
        <el-table-column prop="employee_name" label="业务员" width="100" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status==='loaded'?'success':row.status==='returned'?'danger':'info'">
              {{ row.status==='loaded'?'已装车':row.status==='returned'?'已退库':'草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="showDetail(row)">详情</el-button>
            <el-button link type="success" v-if="row.status==='draft'" @click="handleConfirm(row)">确认装车</el-button>
            <el-button link type="warning" v-if="row.status==='loaded'" @click="handleReturn(row)">退库</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total" layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadData" />
    </el-card>

    <!-- 新建弹窗 -->
    <el-dialog v-model="dialogVisible" title="新建装车单" width="800px" :close-on-click-modal="false">
      <el-form :model="form" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="来源仓库" required>
              <el-select v-model="form.from_warehouse_id" filterable placeholder="选择普通仓库" style="width:100%">
                <el-option v-for="w in normalWarehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="目标车仓" required>
              <el-select v-model="form.vehicle_warehouse_id" filterable placeholder="选择车仓" style="width:100%">
                <el-option v-for="w in vehicleWarehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="业务员">
              <el-select v-model="form.employee_id" filterable clearable placeholder="选择业务员" style="width:100%">
                <el-option v-for="e in employees" :key="e.id" :label="e.name" :value="e.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider content-position="left">装车明细</el-divider>
        <el-table :data="form.items" border size="small">
          <el-table-column label="商品" min-width="200">
            <template #default="{ row }">
              <el-select v-model="row.product_id" filterable placeholder="选择商品" style="width:100%">
                <el-option v-for="p in products" :key="p.id" :label="`${p.name}(${p.spec||''})`" :value="p.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="数量" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="0.01" :precision="2" size="small" style="width:100%" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="60">
            <template #default="{ $index }">
              <el-button link type="danger" @click="form.items.splice($index, 1)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button style="margin-top:8px" @click="form.items.push({product_id:null,quantity:1})">+ 添加商品</el-button>
        <el-form-item label="备注" style="margin-top:12px">
          <el-input v-model="form.remark" placeholder="备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="装车单详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="单号">{{ detail.load_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="detail.status==='loaded'?'success':detail.status==='returned'?'danger':'info'">
            {{ detail.status==='loaded'?'已装车':detail.status==='returned'?'已退库':'草稿' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="来源仓库">{{ detail.from_warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="目标车仓">{{ detail.vehicle_warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="业务员">{{ detail.employee_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="detail.items || []" border size="small" style="margin-top:16px">
        <el-table-column prop="product_name" label="商品" />
        <el-table-column prop="quantity" label="装车数量" width="100" align="right" />
        <el-table-column prop="returned_quantity" label="已退数量" width="100" align="right" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getVehicleLoads, createVehicleLoad, getVehicleLoad, confirmVehicleLoad, returnVehicleLoad, getWarehouses, getProducts, getEmployees } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, status: '' })
const dialogVisible = ref(false)
const detailVisible = ref(false)
const saving = ref(false)
const detail = ref({})
const warehouses = ref([])
const products = ref([])
const employees = ref([])
const form = ref({ from_warehouse_id: null, vehicle_warehouse_id: null, employee_id: null, remark: '', items: [{ product_id: null, quantity: 1 }] })

const normalWarehouses = computed(() => warehouses.value.filter(w => w.warehouse_type !== 'vehicle'))
const vehicleWarehouses = computed(() => warehouses.value.filter(w => w.warehouse_type === 'vehicle'))

const loadData = async () => {
  const res = await getVehicleLoads(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadDropdowns = async () => {
  const [w, p, e] = await Promise.all([getWarehouses(), getProducts(), getEmployees()])
  warehouses.value = w.data || []
  products.value = p.data || []
  employees.value = e.data || []
}

const showDialog = () => {
  form.value = { from_warehouse_id: null, vehicle_warehouse_id: null, employee_id: null, remark: '', items: [{ product_id: null, quantity: 1 }] }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.from_warehouse_id) return ElMessage.warning('请选择来源仓库')
  if (!form.value.vehicle_warehouse_id) return ElMessage.warning('请选择目标车仓')
  if (!form.value.items.length || !form.value.items[0].product_id) return ElMessage.warning('请添加商品')
  saving.value = true
  try {
    await createVehicleLoad(form.value)
    ElMessage.success('装车单创建成功')
    dialogVisible.value = false
    loadData()
  } finally { saving.value = false }
}

const showDetail = async (row) => {
  const res = await getVehicleLoad(row.id)
  detail.value = res.data || res
  detailVisible.value = true
}

const handleConfirm = async (row) => {
  await ElMessageBox.confirm('确认装车？将从普通仓库扣减库存并增加车仓库存', '确认装车', { type: 'warning' })
  await confirmVehicleLoad(row.id)
  ElMessage.success('装车确认成功')
  loadData()
}

const handleReturn = async (row) => {
  await ElMessageBox.confirm('确认退库？将从车仓扣减库存并退回普通仓库', '退库确认', { type: 'warning' })
  await returnVehicleLoad(row.id)
  ElMessage.success('退库成功')
  loadData()
}

onMounted(() => { loadData(); loadDropdowns() })
</script>
