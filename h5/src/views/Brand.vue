<template>
  <div class="page">
    <van-nav-bar title="品牌管理" left-arrow @click-left="$router.back()">
      <template #right>
        <van-icon name="plus" size="22" @click="startCreate" />
      </template>
    </van-nav-bar>

    <van-search v-model="keyword" placeholder="搜索品牌名称/编码" @search="onSearch" style="margin-bottom:8px" />

    <van-pull-refresh v-model="loading" @refresh="loadBrands">
      <van-list :finished="finished" finished-text="没有更多了" @load="loadBrands">
        <div v-for="item in brandList" :key="item.id" class="brand-card" @click="openDetail(item)">
          <div class="brand-header">
            <span class="brand-name">{{ item.name }}</span>
            <van-tag :type="item.status === 1 ? 'success' : 'default'" size="small">
              {{ item.status === 1 ? '启用' : '停用' }}
            </van-tag>
          </div>
          <div class="brand-info">
            <span v-if="item.code">编码: {{ item.code }}</span>
            <span v-if="item.contact">电话: {{ item.contact }}</span>
          </div>
          <div v-if="item.remark" class="brand-remark">{{ item.remark }}</div>
        </div>
        <van-empty v-if="brandList.length === 0 && !loading" description="暂无品牌数据" />
      </van-list>
    </van-pull-refresh>

    <!-- 新建/编辑 -->
    <van-popup v-model:show="showForm" position="bottom" round>
      <div style="padding:20px">
        <div style="font-weight:bold;text-align:center;margin-bottom:16px">{{ isEdit ? '编辑品牌' : '新建品牌' }}</div>
        <van-cell-group inset>
          <van-field v-model="form.name" label="品牌名称" placeholder="请输入品牌名称" />
          <van-field v-model="form.code" label="品牌编码" placeholder="请输入品牌编码" />
          <van-field v-model="form.contact" label="联系方式" placeholder="请输入联系方式" />
          <van-cell title="状态">
            <template #extra>
              <van-radio-group v-model="form.status" direction="horizontal">
                <van-radio :name="1">启用</van-radio>
                <van-radio :name="0">停用</van-radio>
              </van-radio-group>
            </template>
          </van-cell>
          <van-field v-model="form.remark" label="备注" placeholder="备注" />
        </van-cell-group>
        <div style="display:flex;gap:12px;margin-top:16px">
          <van-button block @click="showForm = false">取消</van-button>
          <van-button type="primary" block :loading="submitting" @click="submitForm">保存</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import { getBrands, createBrand, updateBrand, deleteBrand } from '../api'

const loading = ref(false)
const finished = ref(false)
const brandList = ref([])
const keyword = ref('')
const showForm = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const currentItem = ref(null)

const form = ref({ name: '', code: '', contact: '', remark: '', status: 1 })

const loadBrands = async () => {
  loading.value = true
  try {
    const res = await getBrands({ keyword: keyword.value, page_size: 50 })
    brandList.value = res.data || []
  } catch { brandList.value = [] }
  loading.value = false
  finished.value = true
}

const onSearch = () => { loadBrands() }

const startCreate = () => {
  isEdit.value = false
  form.value = { name: '', code: '', contact: '', remark: '', status: 1 }
  currentItem.value = null
  showForm.value = true
}

const openDetail = (item) => {
  isEdit.value = true
  currentItem.value = item
  form.value = { name: item.name, code: item.code || '', contact: item.contact || '', remark: item.remark || '', status: item.status }
  showForm.value = true
}

const submitForm = async () => {
  if (!form.value.name) return showToast('请输入品牌名称')
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateBrand({ id: currentItem.value.id, ...form.value })
      showSuccessToast('更新成功')
    } else {
      await createBrand(form.value)
      showSuccessToast('创建成功')
    }
    showForm.value = false
    loadBrands()
  } catch { showToast('保存失败') }
  submitting.value = false
}

onMounted(loadBrands)
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.brand-card { background: #fff; margin: 8px 16px; border-radius: 10px; padding: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); cursor: pointer; }
.brand-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.brand-name { font-size: 15px; font-weight: bold; color: #333; }
.brand-info { display: flex; gap: 16px; font-size: 13px; color: #666; margin-bottom: 4px; }
.brand-remark { font-size: 12px; color: #999; margin-top: 4px; }
</style>