<template>
  <div>
    <el-steps :active="step" finish-status="success" style="margin-bottom:24px">
      <el-step title="选择类型" />
      <el-step title="上传文件" />
      <el-step title="预览确认" />
      <el-step title="导入结果" />
    </el-steps>

    <!-- Step 1: 选择导入类型 -->
    <div v-if="step === 0">
      <h3>选择导入数据类型</h3>
      <el-radio-group v-model="importType" style="display:flex;flex-direction:column;gap:16px;margin-top:16px">
        <el-radio v-for="t in importTypes" :key="t.value" :value="t.value" border style="height:auto;padding:16px">
          <div style="font-weight:bold;font-size:15px">{{ t.label }}</div>
          <div style="color:#999;font-size:12px;margin-top:4px">字段：{{ t.fields.join('、') }}</div>
        </el-radio>
      </el-radio-group>
      <div style="margin-top:20px">
        <el-button type="primary" @click="step = 1" :disabled="!importType">下一步</el-button>
        <el-button @click="downloadTemplate" :disabled="!importType">下载模板</el-button>
      </div>
    </div>

    <!-- Step 2: 上传文件 -->
    <div v-if="step === 1">
      <h3>上传Excel文件</h3>
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.xls"
        :on-change="onFileChange"
        :on-exceed="() => ElMessage.warning('只能上传一个文件')"
        drag
        style="margin-top:16px"
      >
        <el-icon :size="48"><UploadFilled /></el-icon>
        <div>将Excel文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div style="color:#999;font-size:12px">仅支持 .xlsx / .xls 文件</div>
        </template>
      </el-upload>
      <div style="margin-top:20px">
        <el-button @click="step = 0">上一步</el-button>
        <el-button type="primary" @click="doPreview" :loading="previewing" :disabled="!selectedFile">预览数据</el-button>
      </div>
    </div>

    <!-- Step 3: 预览确认 -->
    <div v-if="step === 2">
      <h3>数据预览</h3>
      <el-alert
        :title="`共 ${previewData.total_rows} 行，有效 ${previewData.valid_count} 行，错误 ${previewData.error_count} 行`"
        :type="previewData.error_count > 0 ? 'warning' : 'success'"
        show-icon
        style="margin-bottom:16px"
      />
      <div v-if="previewData.errors.length > 0" style="margin-bottom:16px">
        <h4 style="color:#e6a23c">错误详情（前50条）</h4>
        <el-table :data="previewData.errors" border size="small" max-height="200">
          <el-table-column prop="row" label="行号" width="70" />
          <el-table-column label="错误信息">
            <template #default="{ row }">
              <span style="color:#f56c6c">{{ row.errors.join('；') }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div v-if="previewData.valid.length > 0">
        <h4>有效数据预览（前100条）</h4>
        <el-table :data="previewData.valid" border size="small" max-height="300">
          <el-table-column prop="row" label="行号" width="70" />
          <el-table-column v-for="h in previewData.headers" :key="h" :label="h" min-width="100">
            <template #default="{ row }">{{ row.data[getMapKey(h)] ?? '' }}</template>
          </el-table-column>
        </el-table>
      </div>
      <div style="margin-top:20px">
        <el-button @click="step = 1">上一步</el-button>
        <el-button type="primary" @click="doImport" :loading="importing" :disabled="previewData.valid_count === 0">
          确认导入 ({{ previewData.valid_count }} 条)
        </el-button>
      </div>
    </div>

    <!-- Step 4: 导入结果 -->
    <div v-if="step === 3">
      <el-result
        :icon="importResult.errors.length === 0 ? 'success' : 'warning'"
        :title="`导入完成：成功 ${importResult.imported} 条`"
        :sub-title="importResult.errors.length > 0 ? `失败 ${importResult.errors.length} 条` : '全部成功'"
      />
      <div v-if="importResult.errors.length > 0" style="margin-top:16px">
        <h4>失败详情</h4>
        <el-table :data="importResult.errors" border size="small" max-height="300">
          <el-table-column prop="row" label="行号" width="70" />
          <el-table-column label="错误信息">
            <template #default="{ row }">
              <span style="color:#f56c6c">{{ row.errors.join('；') }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div style="margin-top:20px">
        <el-button type="primary" @click="resetImport">继续导入</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { getImportTypes, downloadImportTemplate, previewImport, executeImport } from '../../api'

const step = ref(0)
const importTypes = ref([])
const importType = ref('')
const selectedFile = ref(null)
const previewing = ref(false)
const importing = ref(false)
const previewData = ref({ total_rows: 0, valid_count: 0, error_count: 0, valid: [], errors: [], headers: [] })
const importResult = ref({ imported: 0, errors: [] })

const fieldMap = {
  '编码': 'code', '条码': 'barcode', '名称': 'name', '规格': 'spec', '单位': 'unit',
  '进货价': 'purchase_price', '零售价': 'retail_price', '库存下限': 'stock_min', '库存上限': 'stock_max',
  '联系人': 'contact', '电话': 'phone', '地址': 'address', '等级': 'level',
  '信用额度': 'credit_limit', '期初应收': 'receivable_balance', '账期': 'payment_term',
  '期初应付': 'payable_balance', '仓库编码': 'warehouse_id', '商品编码': 'product_id',
  '数量': 'quantity', '成本价': 'cost_price',
}

const getMapKey = (header) => fieldMap[header] || header

onMounted(async () => {
  const res = await getImportTypes()
  importTypes.value = res.data || []
})

const onFileChange = (file) => {
  selectedFile.value = file.raw
}

const downloadTemplate = async () => {
  try {
    const res = await downloadImportTemplate(importType.value)
    const url = URL.createObjectURL(res)
    const a = document.createElement('a')
    a.href = url
    a.download = importTypes.value.find(t => t.value === importType.value)?.label + '导入模板.xlsx'
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error('下载模板失败')
  }
}

const doPreview = async () => {
  if (!selectedFile.value) return
  previewing.value = true
  try {
    const res = await previewImport(importType.value, selectedFile.value)
    previewData.value = res.data
    step.value = 2
  } catch (e) {
    // interceptor handles
  } finally {
    previewing.value = false
  }
}

const doImport = async () => {
  importing.value = true
  try {
    const res = await executeImport(importType.value, selectedFile.value)
    importResult.value = res.data
    step.value = 3
  } catch (e) {
    // interceptor handles
  } finally {
    importing.value = false
  }
}

const resetImport = () => {
  step.value = 0
  importType.value = ''
  selectedFile.value = null
  previewData.value = { total_rows: 0, valid_count: 0, error_count: 0, valid: [], errors: [], headers: [] }
  importResult.value = { imported: 0, errors: [] }
}
</script>
