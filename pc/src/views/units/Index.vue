<template>
  <div>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="单位管理" name="units">
        <el-card>
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span>单位列表</span>
              <el-button type="primary" @click="showUnitDialog()">新增单位</el-button>
            </div>
          </template>
          <el-form inline style="margin-bottom:16px">
            <el-form-item>
              <el-input v-model="unitQuery.keyword" placeholder="搜索单位名称/符号" clearable @keyup.enter="loadUnits" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadUnits">查询</el-button>
            </el-form-item>
          </el-form>
          <el-table :data="units" border stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="单位名称" />
            <el-table-column prop="symbol" label="符号" width="100" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 1 ? 'success' : 'danger'">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="showUnitDialog(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteUnit(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="unitQuery.page"
            v-model:page-size="unitQuery.page_size"
            :total="unitTotal"
            layout="total, prev, pager, next"
            style="margin-top:16px;justify-content:flex-end"
            @current-change="loadUnits"
          />
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="单位换算" name="conversions">
        <el-card>
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span>单位换算关系</span>
              <el-button type="primary" @click="showConversionDialog()">新增换算</el-button>
            </div>
          </template>
          <el-form inline style="margin-bottom:16px">
            <el-form-item label="商品">
              <el-select v-model="convQuery.product_id" filterable placeholder="选择商品" clearable style="width:200px">
                <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadConversions">查询</el-button>
            </el-form-item>
          </el-form>
          <el-table :data="conversions" border stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="product_id" label="商品ID" width="100" />
            <el-table-column prop="from_unit_name" label="源单位" />
            <el-table-column prop="to_unit_name" label="目标单位" />
            <el-table-column prop="ratio" label="换算比例" />
            <el-table-column prop="level" label="层级" width="80" />
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="danger" @click="handleDeleteConversion(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 单位编辑弹窗 -->
    <el-dialog v-model="unitDialogVisible" :title="unitForm.id ? '编辑单位' : '新增单位'" width="500px">
      <el-form :model="unitForm" label-width="80px">
        <el-form-item label="单位名称" required>
          <el-input v-model="unitForm.name" placeholder="如：个、箱、件" />
        </el-form-item>
        <el-form-item label="符号">
          <el-input v-model="unitForm.symbol" placeholder="如：pcs、box" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="unitForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="unitDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveUnit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 换算编辑弹窗 -->
    <el-dialog v-model="convDialogVisible" title="新增单位换算" width="500px">
      <el-form :model="convForm" label-width="80px">
        <el-form-item label="商品" required>
          <el-select v-model="convForm.product_id" filterable placeholder="选择商品" style="width:100%">
            <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="源单位" required>
          <el-select v-model="convForm.from_unit_id" placeholder="选择源单位" style="width:100%">
            <el-option v-for="u in allUnits" :key="u.id" :label="`${u.name} (${u.symbol || ''})`" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标单位" required>
          <el-select v-model="convForm.to_unit_id" placeholder="选择目标单位" style="width:100%">
            <el-option v-for="u in allUnits" :key="u.id" :label="`${u.name} (${u.symbol || ''})`" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="换算比例" required>
          <el-input-number v-model="convForm.ratio" :min="0.001" :precision="3" style="width:100%" />
          <div style="color:#999;font-size:12px;margin-top:4px">1 源单位 = ? 目标单位</div>
        </el-form-item>
        <el-form-item label="层级">
          <el-input-number v-model="convForm.level" :min="1" :max="10" style="width:100%" />
          <div style="color:#999;font-size:12px;margin-top:4px">1=第一层换算，2=第二层换算</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="convDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveConversion">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getUnits, createUnit, updateUnit, deleteUnit,
  getUnitConversions, createUnitConversion, deleteUnitConversion,
  getAllUnits, getProducts
} from '../../api'

const activeTab = ref('units')

// 单位相关
const units = ref([])
const unitTotal = ref(0)
const unitQuery = ref({ page: 1, page_size: 20, keyword: '' })
const unitDialogVisible = ref(false)
const unitForm = ref({})

// 换算相关
const conversions = ref([])
const convQuery = ref({ product_id: null })
const convDialogVisible = ref(false)
const convForm = ref({})

// 通用数据
const allUnits = ref([])
const products = ref([])

// 加载单位列表
const loadUnits = async () => {
  try {
    const res = await getUnits(unitQuery.value)
    units.value = res.data || []
    unitTotal.value = res.total || 0
  } catch (e) { console.error("[activeTab]", e) }
}

// 加载所有单位（下拉用）
const loadAllUnits = async () => {
  try {
    const res = await getAllUnits()
    allUnits.value = res.data || []
  } catch (e) { console.error("[activeTab]", e) }
}

// 加载商品列表（下拉用）
const loadProducts = async () => {
  try {
    const res = await getProducts({ page: 1, page_size: 1000 })
    products.value = res.data || []
  } catch (e) { console.error("[activeTab]", e) }
}

// 加载换算列表
const loadConversions = async () => {
  try {
    const res = await getUnitConversions(convQuery.value)
    conversions.value = res.data || []
  } catch (e) { console.error("[activeTab]", e) }
}

// 显示单位弹窗
const showUnitDialog = (row) => {
  unitForm.value = row ? { ...row } : { name: '', symbol: '', description: '' }
  unitDialogVisible.value = true
}

// 保存单位
const handleSaveUnit = async () => {
  if (unitForm.value.id) {
    await updateUnit(unitForm.value.id, unitForm.value)
  } else {
    await createUnit(unitForm.value)
  }
  ElMessage.success('保存成功')
  unitDialogVisible.value = false
  loadUnits()
  loadAllUnits()
}

// 删除单位
const handleDeleteUnit = async (row) => {
  await ElMessageBox.confirm('确定删除该单位？', '提示', { type: 'warning' })
  await deleteUnit(row.id)
  ElMessage.success('删除成功')
  loadUnits()
  loadAllUnits()
}

// 显示换算弹窗
const showConversionDialog = () => {
  convForm.value = { product_id: null, from_unit_id: null, to_unit_id: null, ratio: 1, level: 1 }
  convDialogVisible.value = true
}

// 保存换算
const handleSaveConversion = async () => {
  await createUnitConversion(convForm.value)
  ElMessage.success('保存成功')
  convDialogVisible.value = false
  loadConversions()
}

// 删除换算
const handleDeleteConversion = async (row) => {
  await ElMessageBox.confirm('确定删除该换算关系？', '提示', { type: 'warning' })
  await deleteUnitConversion(row.id)
  ElMessage.success('删除成功')
  loadConversions()
}

onMounted(async () => {
  try {
    await Promise.all([loadUnits(), loadAllUnits(), loadProducts(), loadConversions()])
  } catch (e) { console.error("[activeTab]", e) }
})
</script>
