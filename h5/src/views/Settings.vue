<template>
  <div class="settings-page">
    <van-nav-bar title="系统设置" />

    <!-- 公司信息 -->
    <div class="section-title">公司信息</div>
    <van-cell-group inset>
      <van-cell title="公司名称" :value="company.name || '未设置'" is-link @click="showEdit('company')" />
      <van-cell title="联系方式" :value="company.phone || '未设置'" is-link @click="showEdit('phone')" />
      <van-cell title="公司地址" :value="company.address || '未设置'" is-link @click="showEdit('address')" />
    </van-cell-group>

    <!-- 业务设置 -->
    <div class="section-title">业务设置</div>
    <van-cell-group inset>
      <van-cell title="默认仓库" :value="settings.defaultWarehouse || '主仓库'" is-link @click="showWarehousePicker = true" />
      <van-cell title="打印纸张" value="80mm" is-link @click="showPrintSettings = true" />
      <van-cell title="价格精度" :value="settings.priceDecimal + ' 位小数'" is-link />
    </van-cell-group>

    <!-- 权限设置 -->
    <div class="section-title">权限设置</div>
    <van-cell-group inset>
      <van-cell title="角色管理" is-link @click="router.push('/roles')">
        <template #icon><van-icon name="setting-o" style="margin-right: 8px;" /></template>
      </van-cell>
      <van-cell title="审核规则" is-link @click="showAuditRule = true">
        <template #icon><van-icon name="passed" style="margin-right: 8px;" /></template>
      </van-cell>
    </van-cell-group>

    <!-- 数据管理 -->
    <div class="section-title">数据管理</div>
    <van-cell-group inset>
      <van-cell title="数据备份" is-link @click="handleBackup">
        <template #icon><van-icon name="backup-o" style="margin-right: 8px;" /></template>
      </van-cell>
      <van-cell title="清理缓存" is-link @click="clearCache">
        <template #icon><van-icon name="clear" style="margin-right: 8px;" /></template>
      </van-cell>
    </van-cell-group>

    <!-- 系统信息 -->
    <div class="system-info">
      <div class="version">FastInOut v1.0.0</div>
      <div class="copyright">© 2026 All Rights Reserved</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { showToast, showSuccessToast } from 'vant'
import { useRouter } from 'vue-router'
import { getCompanySettings, updateCompanySettings, backupData } from '../api'

const router = useRouter()
const showWarehousePicker = ref(false)
const showPrintSettings = ref(false)
const showAuditRule = ref(false)

const company = reactive({
  name: 'FastInOut 公司',
  phone: '400-888-8888',
  address: '未设置'
})

const settings = reactive({
  defaultWarehouse: '主仓库',
  priceDecimal: 2
})

const showEdit = (field) => {
  showToast('编辑功能开发中')
}

const handleBackup = async () => {
  try {
    await backupData()
    showSuccessToast('备份成功')
  } catch (e) {
    showToast('备份失败')
  }
}

const clearCache = () => {
  localStorage.clear()
  showSuccessToast('缓存已清除')
}
</script>

<style scoped>
.settings-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.section-title { font-size: 14px; font-weight: bold; color: #333; margin: 16px 12px 8px; padding-left: 4px; }
.system-info { text-align: center; padding: 30px 0; }
.version { font-size: 14px; color: #666; }
.copyright { font-size: 12px; color: #999; margin-top: 4px; }
</style>