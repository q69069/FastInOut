<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <div>
        <el-select v-model="filterType" placeholder="模板类型" clearable style="width:150px;margin-right:8px" @change="loadData">
          <el-option v-for="t in templateTypes" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
      </div>
      <el-button type="primary" @click="openDialog()">新增模板</el-button>
    </div>

    <el-table :data="list" border stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="模板名称" min-width="150" />
      <el-table-column prop="template_type" label="类型" width="100">
        <template #default="{ row }">
          {{ typeMap[row.template_type] || row.template_type }}
        </template>
      </el-table-column>
      <el-table-column prop="paper_size" label="纸张" width="80" />
      <el-table-column prop="is_default" label="默认" width="70">
        <template #default="{ row }">
          <el-tag v-if="row.is_default" type="success" size="small">默认</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="70">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="warning" @click="previewTemplate(row)">预览</el-button>
          <el-popconfirm title="确认删除？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      style="margin-top:16px;justify-content:flex-end"
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[20,50,100]"
      layout="total, sizes, prev, pager, next"
      @current-change="loadData"
      @size-change="loadData"
    />

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑模板' : '新增模板'" width="800px" top="5vh">
      <el-form :model="form" label-width="80px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="模板名称" required>
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="模板类型" required>
              <el-select v-model="form.template_type" style="width:100%">
                <el-option v-for="t in templateTypes" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="纸张大小">
              <el-select v-model="form.paper_size" style="width:100%">
                <el-option label="A4" value="A4" />
                <el-option label="58mm" value="58mm" />
                <el-option label="80mm" value="80mm" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>
        <el-form-item label="模板内容">
          <el-input v-model="form.content" type="textarea" :rows="16" placeholder="HTML模板内容，支持 {{variable}} 占位符" />
        </el-form-item>
        <el-form-item label="变量说明">
          <div style="font-size:12px;color:#999;line-height:1.8">
            <div><b>通用：</b>company_name</div>
            <div><b>销售/采购单：</b>customer_name / supplier_name、order_code、order_date、total_amount、items（循环）内含 index product_name spec unit quantity price amount</div>
            <div><b>收款凭证：</b>customer_name、amount、payment_method、receipt_code、receipt_date、salesman</div>
            <div><b>对账单：</b>customer_name、start_date、end_date、opening_balance、total_sales、total_payments、closing_balance、items（循环）</div>
            <div style="margin-top:4px;color:#666">使用方式：在模板内容中用 {变量名} 包裹变量，如 {company_name}，循环用 {#items}...{/items}</div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 预览弹窗 -->
    <el-dialog v-model="previewVisible" title="打印预览" width="850px" top="3vh">
      <div v-if="previewLoading" style="text-align:center;padding:40px">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
        <div style="margin-top:8px">加载预览数据...</div>
      </div>
      <div v-else-if="previewData">
        <div style="margin-bottom:12px;display:flex;gap:8px">
          <el-button size="small" type="primary" @click="doPrint">打印</el-button>
        </div>
        <div ref="printArea" v-html="renderedHtml" style="border:1px solid #ddd;padding:20px;background:#fff;min-height:400px" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { getPrintTemplates, getPrintTemplate, createPrintTemplate, updatePrintTemplate, deletePrintTemplate, getPrintTemplateTypes, previewPrint } from '../../api'

const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filterType = ref('')
const templateTypes = ref([])
const typeMap = computed(() => Object.fromEntries(templateTypes.value.map(t => [t.value, t.label])))

const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const saving = ref(false)
const form = ref({ name: '', template_type: 'sales', paper_size: 'A4', content: '', is_default: false })

const previewVisible = ref(false)
const previewLoading = ref(false)
const previewData = ref(null)
const printArea = ref(null)

const loadData = async () => {
  const res = await getPrintTemplates({ page: page.value, page_size: pageSize.value, template_type: filterType.value || undefined })
  list.value = res.data || []
  total.value = res.total || 0
}

const loadTypes = async () => {
  const res = await getPrintTemplateTypes()
  templateTypes.value = res.data || []
}

onMounted(() => {
  loadData()
  loadTypes()
})

const openDialog = (row) => {
  if (row) {
    isEdit.value = true
    editId.value = row.id
    form.value = { name: row.name, template_type: row.template_type, paper_size: row.paper_size, content: row.content || '', is_default: row.is_default }
  } else {
    isEdit.value = false
    editId.value = null
    form.value = { name: '', template_type: 'sales', paper_size: 'A4', content: '', is_default: false }
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.name || !form.value.template_type) {
    ElMessage.warning('请填写模板名称和类型')
    return
  }
  saving.value = true
  try {
    if (isEdit.value) {
      await updatePrintTemplate(editId.value, form.value)
    } else {
      await createPrintTemplate(form.value)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadData()
  } catch (e) {
    // interceptor handles message
  } finally {
    saving.value = false
  }
}

const handleDelete = async (id) => {
  await deletePrintTemplate(id)
  ElMessage.success('删除成功')
  loadData()
}

// 渲染 Mustache 风格模板
const renderTemplate = (html, data) => {
  if (!html) return ''
  // 处理循环 {{#items}}...{{/items}}
  let result = html.replace(/\{\{#items\}\}([\s\S]*?)\{\{\/items\}\}/g, (_, tpl) => {
    const items = data.items || []
    return items.map(item => {
      let row = tpl
      for (const [k, v] of Object.entries(item)) {
        row = row.replace(new RegExp(`\\{\\{${k}\\}\\}`, 'g'), v ?? '')
      }
      return row
    }).join('')
  })
  // 处理普通变量 {{key}}
  result = result.replace(/\{\{(\w+)\}\}/g, (_, key) => data[key] ?? '')
  return result
}

const renderedHtml = computed(() => {
  if (!previewData.value) return ''
  const { template, data } = previewData.value
  return renderTemplate(template, data)
})

const previewTemplate = async (row) => {
  previewVisible.value = true
  previewLoading.value = true
  previewData.value = null
  try {
    // 用 id=1 做示例预览，不同类型的 doc_type 对应不同
    const docTypeMap = { sales: 'sales', purchase: 'purchase', receipt: 'receipt', statement: 'statement' }
    const docType = docTypeMap[row.template_type] || 'sales'
    const res = await previewPrint(row.id, docType, 1)
    previewData.value = res.data
  } catch (e) {
    ElMessage.warning('暂无预览数据（需要对应类型的单据）')
  } finally {
    previewLoading.value = false
  }
}

const doPrint = () => {
  const content = printArea.value?.innerHTML
  if (!content) return
  const win = window.open('', '_blank')
  win.document.write(`<html><head><title>打印</title><style>
    body{font-family:simsun,serif;margin:0;padding:20px}
    table{border-collapse:collapse;width:100%}
    th,td{border:1px solid #333;padding:6px}
    .print-page{max-width:210mm;margin:0 auto}
    @media print{body{padding:0}}
  </style></head><body>${content}<script>window.print();window.close()<\/script></body></html>`)
  win.document.close()
}
</script>
