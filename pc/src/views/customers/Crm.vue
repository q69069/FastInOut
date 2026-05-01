<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>客户关系管理</span>
        </div>
      </template>

      <!-- 客户筛选 -->
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="客户">
          <el-select
            v-model="selectedCustomerId"
            placeholder="选择客户筛选"
            clearable
            filterable
            style="width:240px"
            @change="handleCustomerChange"
          >
            <el-option
              v-for="c in customerList"
              :key="c.id"
              :label="c.name"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <!-- Tabs -->
      <el-tabs v-model="activeTab">
        <!-- 联系人 Tab -->
        <el-tab-pane label="联系人" name="contacts">
          <div style="margin-bottom:12px;text-align:right">
            <el-button type="primary" @click="showContactDialog()">新增联系人</el-button>
          </div>
          <el-table :data="contactList" border stripe>
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="position" label="职位" width="120" />
            <el-table-column prop="phone" label="电话" width="140" />
            <el-table-column prop="email" label="邮箱" width="180" />
            <el-table-column label="主要联系人" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_primary ? 'success' : 'info'" size="small">
                  {{ row.is_primary ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" show-overflow-tooltip />
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="showContactDialog(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteContact(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="contactQuery.page"
            v-model:page-size="contactQuery.page_size"
            :total="contactTotal"
            layout="total, prev, pager, next"
            style="margin-top:16px;justify-content:flex-end"
            @current-change="loadContacts"
          />
        </el-tab-pane>

        <!-- 拜访记录 Tab -->
        <el-tab-pane label="拜访记录" name="visits">
          <div style="margin-bottom:12px;text-align:right">
            <el-button type="primary" @click="showVisitDialog()">新增拜访记录</el-button>
          </div>
          <el-table :data="visitList" border stripe>
            <el-table-column prop="visit_date" label="拜访日期" width="160">
              <template #default="{ row }">
                {{ row.visit_date ? row.visit_date.slice(0, 10) : '' }}
              </template>
            </el-table-column>
            <el-table-column prop="content" label="拜访内容" show-overflow-tooltip />
            <el-table-column prop="result" label="拜访结果" show-overflow-tooltip />
            <el-table-column prop="next_plan" label="下次计划" show-overflow-tooltip />
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="danger" @click="handleDeleteVisit(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="visitQuery.page"
            v-model:page-size="visitQuery.page_size"
            :total="visitTotal"
            layout="total, prev, pager, next"
            style="margin-top:16px;justify-content:flex-end"
            @current-change="loadVisits"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 联系人弹窗 -->
    <el-dialog v-model="contactDialogVisible" :title="contactForm.id ? '编辑联系人' : '新增联系人'" width="500px">
      <el-form :model="contactForm" label-width="100px">
        <el-form-item label="所属客户" required>
          <el-select v-model="contactForm.customer_id" placeholder="选择客户" filterable style="width:100%">
            <el-option
              v-for="c in customerList"
              :key="c.id"
              :label="c.name"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="姓名" required>
          <el-input v-model="contactForm.name" />
        </el-form-item>
        <el-form-item label="职位">
          <el-input v-model="contactForm.position" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="contactForm.phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="contactForm.email" />
        </el-form-item>
        <el-form-item label="主要联系人">
          <el-switch v-model="contactForm.is_primary" :active-value="1" :inactive-value="0" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="contactForm.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="contactDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveContact">保存</el-button>
      </template>
    </el-dialog>

    <!-- 拜访记录弹窗 -->
    <el-dialog v-model="visitDialogVisible" title="新增拜访记录" width="500px">
      <el-form :model="visitForm" label-width="100px">
        <el-form-item label="所属客户" required>
          <el-select v-model="visitForm.customer_id" placeholder="选择客户" filterable style="width:100%">
            <el-option
              v-for="c in customerList"
              :key="c.id"
              :label="c.name"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="拜访日期">
          <el-date-picker v-model="visitForm.visit_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="拜访内容">
          <el-input v-model="visitForm.content" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="拜访结果">
          <el-input v-model="visitForm.result" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="下次计划">
          <el-input v-model="visitForm.next_plan" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visitDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveVisit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getContacts, createContact, updateContact, deleteContact,
  getVisits, createVisit, deleteVisit,
  getCustomers
} from '../../api'

// 客户列表
const customerList = ref([])
const selectedCustomerId = ref(null)

// Tab
const activeTab = ref('contacts')

// ==================== 联系人 ====================
const contactList = ref([])
const contactTotal = ref(0)
const contactQuery = ref({ page: 1, page_size: 20 })
const contactDialogVisible = ref(false)
const contactForm = ref({})

const loadContacts = async () => {
  const params = { ...contactQuery.value }
  if (selectedCustomerId.value) {
    params.customer_id = selectedCustomerId.value
  }
  const res = await getContacts(params)
  contactList.value = res.data || []
  contactTotal.value = res.total || 0
}

const showContactDialog = (row) => {
  contactForm.value = row
    ? { ...row }
    : {
        customer_id: selectedCustomerId.value || null,
        name: '',
        position: '',
        phone: '',
        email: '',
        is_primary: 0,
        remark: '',
      }
  contactDialogVisible.value = true
}

const handleSaveContact = async () => {
  if (!contactForm.value.customer_id) {
    ElMessage.warning('请选择所属客户')
    return
  }
  if (!contactForm.value.name) {
    ElMessage.warning('请填写联系人姓名')
    return
  }
  if (contactForm.value.id) {
    await updateContact(contactForm.value.id, contactForm.value)
  } else {
    await createContact(contactForm.value)
  }
  ElMessage.success('保存成功')
  contactDialogVisible.value = false
  loadContacts()
}

const handleDeleteContact = async (row) => {
  await ElMessageBox.confirm('确定删除该联系人？', '提示', { type: 'warning' })
  await deleteContact(row.id)
  ElMessage.success('删除成功')
  loadContacts()
}

// ==================== 拜访记录 ====================
const visitList = ref([])
const visitTotal = ref(0)
const visitQuery = ref({ page: 1, page_size: 20 })
const visitDialogVisible = ref(false)
const visitForm = ref({})

const loadVisits = async () => {
  const params = { ...visitQuery.value }
  if (selectedCustomerId.value) {
    params.customer_id = selectedCustomerId.value
  }
  const res = await getVisits(params)
  visitList.value = res.data || []
  visitTotal.value = res.total || 0
}

const showVisitDialog = () => {
  visitForm.value = {
    customer_id: selectedCustomerId.value || null,
    visit_date: '',
    content: '',
    result: '',
    next_plan: '',
  }
  visitDialogVisible.value = true
}

const handleSaveVisit = async () => {
  if (!visitForm.value.customer_id) {
    ElMessage.warning('请选择所属客户')
    return
  }
  await createVisit(visitForm.value)
  ElMessage.success('保存成功')
  visitDialogVisible.value = false
  loadVisits()
}

const handleDeleteVisit = async (row) => {
  await ElMessageBox.confirm('确定删除该拜访记录？', '提示', { type: 'warning' })
  await deleteVisit(row.id)
  ElMessage.success('删除成功')
  loadVisits()
}

// ==================== 公共 ====================
const handleCustomerChange = () => {
  contactQuery.value.page = 1
  visitQuery.value.page = 1
  loadContacts()
  loadVisits()
}

const loadCustomers = async () => {
  const res = await getCustomers({ page: 1, page_size: 999 })
  customerList.value = res.data || []
}

onMounted(() => {
  loadCustomers()
  loadContacts()
  loadVisits()
})
</script>
