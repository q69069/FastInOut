<template>
  <div>
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span>批次管理</span>
              <el-button type="primary" @click="showDialog()">新增批次</el-button>
            </div>
          </template>
          <el-form inline style="margin-bottom:16px">
            <el-form-item>
              <el-input v-model="query.keyword" placeholder="搜索单号" clearable @keyup.enter="loadData" />
            </el-form-item>
            <el-form-item>
              <el-select v-model="query.warehouse_id" clearable placeholder="选择仓库" style="width:150px">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-select v-model="query.status" clearable placeholder="状态" style="width:100px">
                <el-option label="正常" value="active" />
                <el-option label="已用完" value="used" />
                <el-option label="已过期" value="expired" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadData">查询</el-button>
            </el-form-item>
          </el-form>
          <el-table :data="list" border stripe>
            <el-table-column prop="batch_no" label="批次号" width="120" />
            <el-table-column prop="product_name" label="商品" min-width="120" />
            <el-table-column prop="warehouse_name" label="仓库" width="100" />
            <el-table-column prop="quantity" label="数量" width="80" />
            <el-table-column prop="cost_price" label="成本价" width="80" />
            <el-table-column prop="production_date" label="生产日期" width="100" />
            <el-table-column prop="expire_date" label="过期日期" width="100">
              <template #default="{ row }">
                <span :class="{ 'text-danger': isExpiringSoon(row.expire_date) }">{{ row.expire_date }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : row.status === 'expired' ? 'danger' : 'info'">
                  {{ statusMap[row.status] }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="showDialog(row)">编辑</el-button>
              </template>
            </el-table-column>
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
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>保质期预警</template>
          <div v-if="expiringBatches.length === 0" style="text-align:center;color:#999;padding:20px">
            暂无即将过期的批次
          </div>
          <div v-for="b in expiringBatches" :key="b.id" style="padding:8px 0;border-bottom:1px solid #eee">
            <div style="font-weight:bold">{{ b.product_name }}</div>
            <div style="font-size:12px;color:#666">
              批次: {{ b.batch_no }} | 数量: {{ b.quantity }}
            </div>
            <div style="font-size:12px;color:#e6a23c">
              过期日期: {{ b.expire_date }}
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑批次' : '新增批次'" width="600px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="商品" required>
          <el-select v-model="form.product_id" filterable placeholder="选择商品" style="width:100%">
            <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="批次号" required>
          <el-input v-model="form.batch_no" placeholder="如：B20240101001" />
        </el-form-item>
        <el-form-item label="仓库">
          <el-select v-model="form.warehouse_id" clearable placeholder="选择仓库" style="width:100%">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="form.quantity" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="成本价">
          <el-input-number v-model="form.cost_price" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="生产日期">
          <el-date-picker v-model="form.production_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="过期日期">
          <el-date-picker v-model="form.expire_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getBatches, createBatch, updateBatch, getExpiringBatches, getProducts, getWarehouses } from '../../api'

const statusMap = { active: '正常', used: '已用完', expired: '已过期' }

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, keyword: '', warehouse_id: null, status: '' })
const dialogVisible = ref(false)
const form = ref({})

const products = ref([])
const warehouses = ref([])
const expiringBatches = ref([])

const loadData = async () => {
  try {
    const params = { ...query.value }
    if (!params.warehouse_id) delete params.warehouse_id
    if (!params.status) delete params.status
    const res = await getBatches(params)
    list.value = res.data || []
    total.value = res.total || 0
  } catch (e) { console.error("[statusMap]", e) }
}

const loadExpiring = async () => {
  try {
    const res = await getExpiringBatches(30)
    expiringBatches.value = res.data || []
  } catch (e) { console.error("[statusMap]", e) }
}

const isExpiringSoon = (dateStr) => {
  if (!dateStr) return false
  const expire = new Date(dateStr)
  const now = new Date()
  const diff = (expire - now) / (1000 * 60 * 60 * 24)
  return diff <= 30 && diff >= 0
}

const showDialog = (row) => {
  form.value = row ? { ...row } : {
    product_id: null, batch_no: '', warehouse_id: null, quantity: 0, cost_price: 0,
    production_date: null, expire_date: null, remark: ''
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (form.value.id) {
    await updateBatch(form.value.id, form.value)
  } else {
    await createBatch(form.value)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
  loadExpiring()
}

onMounted(async () => {
  try {
    const [pRes, wRes] = await Promise.all([
      getProducts({ page: 1, page_size: 100 }),
      getWarehouses({ page_size: 100 })
    ])
    products.value = pRes.data || []
    warehouses.value = wRes.data || []
    await Promise.all([loadData(), loadExpiring()])
  } catch (e) { console.error("[statusMap]", e) }
})
</script>

<style scoped>
.text-danger { color: #f56c6c; font-weight: bold; }
</style>
