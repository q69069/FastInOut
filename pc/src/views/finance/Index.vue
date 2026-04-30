<template>
  <div>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="收款管理" name="receipts">
        <el-card>
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span>收款列表</span>
              <el-button type="primary" size="small" @click="showReceiptDialog()">新增收款</el-button>
            </div>
          </template>
          <el-table :data="receipts" border stripe>
            <el-table-column prop="code" label="单号" width="150" />
            <el-table-column prop="customer_name" label="客户" />
            <el-table-column prop="amount" label="金额" width="120" />
            <el-table-column prop="payment_method" label="方式" width="100" />
            <el-table-column prop="created_at" label="时间" width="180" />
          </el-table>
        </el-card>
      </el-tab-pane>
      <el-tab-pane label="付款管理" name="payments">
        <el-card>
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span>付款列表</span>
              <el-button type="primary" size="small" @click="showPaymentDialog()">新增付款</el-button>
            </div>
          </template>
          <el-table :data="payments" border stripe>
            <el-table-column prop="code" label="单号" width="150" />
            <el-table-column prop="supplier_name" label="供应商" />
            <el-table-column prop="amount" label="金额" width="120" />
            <el-table-column prop="payment_method" label="方式" width="100" />
            <el-table-column prop="created_at" label="时间" width="180" />
          </el-table>
        </el-card>
      </el-tab-pane>
      <el-tab-pane label="应收账款" name="receivables">
        <el-card>
          <template #header>应收账款汇总</template>
          <el-table :data="receivables" border stripe>
            <el-table-column prop="name" label="客户名称" />
            <el-table-column prop="balance" label="应收余额" width="150" />
            <el-table-column prop="contact" label="联系人" width="120" />
            <el-table-column prop="phone" label="电话" width="150" />
          </el-table>
        </el-card>
      </el-tab-pane>
      <el-tab-pane label="应付账款" name="payables">
        <el-card>
          <template #header>应付账款汇总</template>
          <el-table :data="payables" border stripe>
            <el-table-column prop="name" label="供应商名称" />
            <el-table-column prop="balance" label="应付余额" width="150" />
            <el-table-column prop="contact" label="联系人" width="120" />
            <el-table-column prop="phone" label="电话" width="150" />
          </el-table>
        </el-card>
      </el-tab-pane>
      <el-tab-pane label="收支流水" name="flow">
        <el-card>
          <template #header>收支流水</template>
          <el-table :data="flowList" border stripe>
            <el-table-column prop="code" label="单号" width="150" />
            <el-table-column prop="type" label="类型" width="80">
              <template #default="{ row }">
                <el-tag :type="row.type === 'income' ? 'success' : 'danger'">
                  {{ row.type === 'income' ? '收入' : '支出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" width="120" />
            <el-table-column prop="party_name" label="对方" />
            <el-table-column prop="payment_method" label="方式" width="100" />
            <el-table-column prop="created_at" label="时间" width="180" />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    <el-dialog v-model="receiptDialog" title="新增收款" width="500px">
      <el-form :model="receiptForm" label-width="80px">
        <el-form-item label="客户" required>
          <el-select v-model="receiptForm.customer_id" filterable>
            <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="金额" required>
          <el-input-number v-model="receiptForm.amount" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="方式">
          <el-select v-model="receiptForm.payment_method">
            <el-option label="现金" value="现金" />
            <el-option label="转账" value="转账" />
            <el-option label="微信" value="微信" />
            <el-option label="支付宝" value="支付宝" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="receiptForm.remark" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="receiptDialog = false">取消</el-button>
        <el-button type="primary" @click="handleReceipt">确定</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="paymentDialog" title="新增付款" width="500px">
      <el-form :model="paymentForm" label-width="80px">
        <el-form-item label="供应商" required>
          <el-select v-model="paymentForm.supplier_id" filterable>
            <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="金额" required>
          <el-input-number v-model="paymentForm.amount" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="方式">
          <el-select v-model="paymentForm.payment_method">
            <el-option label="现金" value="现金" />
            <el-option label="转账" value="转账" />
            <el-option label="微信" value="微信" />
            <el-option label="支付宝" value="支付宝" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="paymentForm.remark" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="paymentDialog = false">取消</el-button>
        <el-button type="primary" @click="handlePayment">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getReceipts, createReceipt, getPayments, createPayment, getReceivables, getPayables, getFinanceFlow, getCustomers, getSuppliers } from '../../api'

const activeTab = ref('receipts')
const receipts = ref([])
const payments = ref([])
const receivables = ref([])
const payables = ref([])
const flowList = ref([])
const customers = ref([])
const suppliers = ref([])
const receiptDialog = ref(false)
const paymentDialog = ref(false)
const receiptForm = ref({})
const paymentForm = ref({})

const loadData = async () => {
  const [r, p, rec, pay, f] = await Promise.all([
    getReceipts({ page_size: 100 }),
    getPayments({ page_size: 100 }),
    getReceivables(),
    getPayables(),
    getFinanceFlow({ page_size: 100 })
  ])
  receipts.value = r.data || []
  payments.value = p.data || []
  receivables.value = rec.data || []
  payables.value = pay.data || []
  flowList.value = f.data || []
}

const showReceiptDialog = () => {
  receiptForm.value = { customer_id: null, amount: 0, payment_method: '转账', remark: '' }
  receiptDialog.value = true
}

const showPaymentDialog = () => {
  paymentForm.value = { supplier_id: null, amount: 0, payment_method: '转账', remark: '' }
  paymentDialog.value = true
}

const handleReceipt = async () => {
  await createReceipt(receiptForm.value)
  ElMessage.success('收款成功')
  receiptDialog.value = false
  loadData()
}

const handlePayment = async () => {
  await createPayment(paymentForm.value)
  ElMessage.success('付款成功')
  paymentDialog.value = false
  loadData()
}

onMounted(async () => {
  const [c, s] = await Promise.all([
    getCustomers({ page_size: 100 }),
    getSuppliers({ page_size: 100 })
  ])
  customers.value = c.data || []
  suppliers.value = s.data || []
  loadData()
})
</script>
