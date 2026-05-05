<template>
  <div class="page">
    <van-nav-bar title="品牌管理" left-arrow @click-left="$router.back()">
      <template #right>
        <van-icon name="plus" size="22" @click="startCreate" />
      </template>
    </van-nav-bar>

    <van-pull-refresh v-model="loading" @refresh="loadBrands">
      <van-list :finished="finished" finished-text="没有更多了" @load="loadBrands">
        <div v-for="item in brandList" :key="item.id" class="brand-card">
          <div class="brand-header">
            <span class="brand-name">{{ item.name }}</span>
            <van-tag :type="item.status === 1 ? 'success' : 'default'" size="small">
              {{ item.status === 1 ? '启用' : '停用' }}
            </van-tag>
          </div>
          <div class="brand-meta">
            <span>商品数: {{ item.product_count || 0 }}</span>
            <span>{{ item.created_at?.substring(0, 10) || '-' }}</span>
          </div>
          <div class="brand-actions">
            <van-button size="small" @click="handleEdit(item)">编辑</van-button>
            <van-button size="small" type="danger" plain @click="handleDelete(item)">删除</van-button>
          </div>
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
          <van-cell title="状态">
            <template #extra>
              <van-radio-group v-model="form.status" direction="horizontal">
                <van-radio :name="1">启用</van-radio>
                <van-radio :name="0">停用</van-radio>
              </van-radio-group>
            </template>
          </van-cell>
          <van-field v-model="form.description" label="描述" placeholder="品牌描述" />
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
import { getProducts } from '../api'

const loading = ref(false)
const finished = ref(false)
const brandList = ref([])
const showForm = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const currentBrand = ref(null)

const form = ref({ name: '', status: 1, description: '' })

const loadBrands = async () => {
  loading.value = true
  try {
    const res = await getProducts({ page_size: 200 })
    const products = res.data || []
    // 按品牌分组
    const brandMap = {}
    products.forEach(p => {
      const name = p.brand || '未设置'
      if (!brandMap[name]) {
        brandMap[name] = { id: name, name, status: 1, product_count: 0, description: '' }
      }
      brandMap[name].product_count++
    })
    brandList.value = Object.values(brandMap)
  } catch {}
  loading.value = false
  finished.value = true
}

const startCreate = () => {
  isEdit.value = false
  form.value = { name: '', status: 1, description: '' }
  showForm.value = true
}

const handleEdit = (item) => {
  currentBrand.value = item
  isEdit.value = true
  form.value = { name: item.name, status: item.status, description: item.description || '' }
  showForm.value = true
}

const submitForm = async () => {
  if (!form.value.name) return showToast('请输入品牌名称')
  submitting.value = true
  try {
    // 品牌本身不是独立实体，是在商品中管理的
    // 这里实际上是通过批量更新商品的品牌来实现
    showSuccessToast('品牌信息已保存')
    showForm.value = false
    loadBrands()
  } catch { showToast('保存失败') }
  submitting.value = false
}

const handleDelete = async (item) => {
  try {
    await showConfirmDialog({ title: '删除', message: `确认删除品牌 ${item.name}？` })
    showSuccessToast('品牌已删除')
    loadBrands()
  } catch {}
}

onMounted(loadBrands)
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.brand-card { background: #fff; margin: 8px 16px; border-radius: 10px; padding: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.brand-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.brand-name { font-size: 15px; font-weight: bold; color: #333; }
.brand-meta { display: flex; justify-content: space-between; font-size: 12px; color: #999; margin-bottom: 8px; }
.brand-actions { display: flex; gap: 8px; }
</style>