<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Download /></el-icon>
              <span>导出备份</span>
            </div>
          </template>
          <div class="backup-section">
            <p class="section-desc">将当前数据库导出为备份文件，用于数据迁移或灾难恢复。</p>
            <el-button type="primary" :icon="Download" @click="handleExport" :loading="exporting">
              导出备份
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Upload /></el-icon>
              <span>导入备份</span>
            </div>
          </template>
          <div class="backup-section">
            <el-alert
              title="警告：导入备份将覆盖当前所有数据！"
              type="warning"
              description="此操作不可撤销，建议先导出当前数据作为备份。导入后需要刷新页面以加载新数据。"
              show-icon
              :closable="false"
              style="margin-bottom: 16px"
            />
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :limit="1"
              accept=".db"
              :on-change="handleFileChange"
              :on-exceed="handleExceed"
              :on-remove="handleFileRemove"
              drag
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">
                将数据库备份文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  仅支持 .db 格式的 SQLite 数据库文件
                </div>
              </template>
            </el-upload>
            <el-button
              type="danger"
              :icon="Upload"
              @click="handleImport"
              :loading="importing"
              :disabled="!selectedFile"
              style="margin-top: 16px"
            >
              导入备份
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Upload, UploadFilled } from '@element-plus/icons-vue'
import { exportBackup, importBackup } from '../../api'

const exporting = ref(false)
const importing = ref(false)
const selectedFile = ref(null)
const uploadRef = ref(null)

const handleExport = async () => {
  exporting.value = true
  try {
    const response = await exportBackup()
    // 创建下载链接
    const blob = new Blob([response], { type: 'application/octet-stream' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url

    // 生成文件名
    const now = new Date()
    const timestamp = now.toISOString().replace(/[-:T]/g, '').slice(0, 15)
    link.download = `fastinout_backup_${timestamp}.db`

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('备份文件已开始下载')
  } catch (error) {
    ElMessage.error('导出备份失败')
  } finally {
    exporting.value = false
  }
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const handleFileRemove = () => {
  selectedFile.value = null
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件，请先移除已选文件')
}

const handleImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要导入的备份文件')
    return
  }

  try {
    await ElMessageBox.confirm(
      '导入备份将覆盖当前所有数据，此操作不可撤销。确定要继续吗？',
      '确认导入',
      {
        confirmButtonText: '确定导入',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
  } catch {
    return // 用户取消
  }

  importing.value = true
  try {
    await importBackup(selectedFile.value)
    ElMessage.success('数据库导入成功，请刷新页面以加载新数据')
    // 清空上传组件
    selectedFile.value = null
    uploadRef.value?.clearFiles()
  } catch (error) {
    ElMessage.error('导入备份失败')
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.backup-section {
  padding: 8px 0;
}

.section-desc {
  color: #666;
  margin-bottom: 16px;
  line-height: 1.6;
}
</style>
