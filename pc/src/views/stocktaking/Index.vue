<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>盘点管理</span>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="盘点中" :value="1" />
            <el-option label="已审核" :value="2" />
            <el-option label="已调整" :value="3" />
            <el-option label="已作废" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="仓库">
          <el-select v-model="query.warehouse_id" clearable filterable placeholder="全部" style="width:160px">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="code" label="单号" width="150" />
        <el-table-column prop="warehouse_name" label="仓库" width="120" />
        <el-table-column prop="item_count" label="商品数" width="80" align="center" />
        <el-table-column prop="total_diff" label="差异总数" width="100" align="right" />
        <el-table-column label="差异率" width="100" align="right">
          <template #default="{ row }">
            <span :style="{ color: row.diff_rate > 5 ? '#f56c6c' : '' }">{{ row.diff_rate }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type">{{ statusMap[row.status]?.label || '未知' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="showDetail(row)">详情</el-button>
            <el-button link type="success" v-if="row.status===1" @click="handleAudit(row)">审核</el-button>
            <el-button link type="warning" v-if="row.status===2" @click="handleAdjust(row)">调整库存</el-button>
            <el-button link type="danger" v-if="row.status===1||row.status===2" @click="handleVoid(row)">作废</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total" layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadData" />
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="盘点单详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="单号">{{ detail.code }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusMap[detail.status]?.type">{{ statusMap[detail.status]?.label }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="仓库">{{ detail.warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ detail.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="detail.items || []" border size="small" style="margin-top:16px">
        <el-table-column prop="product_name" label="商品" />
        <el-table-column prop="product_code" label="编码" width="120" />
        <el-table-column prop="system_qty" label="系统数量" width="100" align="right" />
        <el-table-column prop="actual_qty" label="实际数量" width="100" align="right" />
        <el-table-column prop="diff_qty" label="差异" width="80" align="right">
          <template #default="{ row }">
            <span :style="{ color: row.diff_qty > 0 ? '#67c23a' : row.diff_qty < 0 ? '#f56c6c' : '' }">{{ row.diff_qty }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="diff_type" label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.diff_type==='盘盈'?'success':row.diff_type==='盘亏'?'danger':'info'" size="small">{{ row.diff_type }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getStocktaking, getStocktakingDetail, auditStocktaking, adjustStocktaking, voidStocktaking, getWarehouses } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, status: '', warehouse_id: '' })
const detailVisible = ref(false)
const detail = ref({})
const warehouses = ref([])

const statusMap = {
  1: { label: '盘点中', type: 'info' },
  2: { label: '已审核', type: 'success' },
  3: { label: '已调整', type: '' },
  4: { label: '已作废', type: 'danger' }
}

const loadData = async () => {
  const res = await getStocktaking(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadWarehouses = async () => {
  const res = await getWarehouses()
  warehouses.value = res.data || []
}

const showDetail = async (row) => {
  const res = await getStocktakingDetail(row.id)
  detail.value = res.data || res
  detail.value.warehouse_name = row.warehouse_name
  detailVisible.value = true
}

const handleAudit = async (row) => {
  await ElMessageBox.confirm('确认审核此盘点单？差异率超过5%将标记需复核', '审核确认', { type: 'warning' })
  await auditStocktaking(row.id)
  ElMessage.success('审核完成')
  loadData()
}

const handleAdjust = async (row) => {
  await ElMessageBox.confirm('确认按实际库存调整系统库存？此操作不可逆', '调整确认', { type: 'warning' })
  await adjustStocktaking(row.id)
  ElMessage.success('库存已调整')
  loadData()
}

const handleVoid = async (row) => {
  await ElMessageBox.confirm('确认作废此盘点单？', '作废确认', { type: 'warning' })
  await voidStocktaking(row.id)
  ElMessage.success('已作废')
  loadData()
}

onMounted(() => { loadData(); loadWarehouses() })
</script>
