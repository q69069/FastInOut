/**
 * 单据页面共享工具函数
 */

/** 构建商品可用单位列表 */
export function buildAvailableUnits(p) {
  if (!p) return []
  const baseId = p.base_unit_id || p.id
  const units = [{ unit_id: baseId, unit_level: 'small', unit_name: p.small_unit_name || p.unit || '基本单位', conv_rate: 1 }]
  if (p.medium_unit_name) units.push({ unit_id: baseId, unit_level: 'medium', unit_name: p.medium_unit_name, conv_rate: p.medium_conv_rate || 1 })
  if (p.large_unit_name) units.push({ unit_id: baseId, unit_level: 'large', unit_name: p.large_unit_name, conv_rate: p.large_conv_rate || 1 })
  return units
}

/** 商品选择变化时，设置单价和可用单位 */
export function onProductChange(row, product, priceField = 'retail_price') {
  if (!product) return
  row._basePrice = product[priceField] || product.retail_price || 0
  row.price = row._basePrice
  row._availableUnits = buildAvailableUnits(product)
  if (row._availableUnits.length > 0) {
    const defaultUnit = row._availableUnits.find(u => u.unit_level === product.default_unit_level) || row._availableUnits[0]
    row.unit_id = defaultUnit.unit_id
    row._unitLevel = defaultUnit.unit_level
    row._unitConvRate = defaultUnit.conv_rate
    row.price = parseFloat((row._basePrice * defaultUnit.conv_rate).toFixed(2))
  }
  calcRowAmount(row)
}

/** 单位切换时，重新计算价格 */
export function onUnitChange(row, unitLevel) {
  const unit = row._availableUnits?.find(u => u.unit_level === unitLevel)
  if (unit && row._basePrice) {
    row._unitLevel = unit.unit_level
    row._unitConvRate = unit.conv_rate
    row.price = parseFloat((row._basePrice * unit.conv_rate).toFixed(2))
  }
  calcRowAmount(row)
}

/** 计算行金额 */
export function calcRowAmount(row) {
  row.amount = (row.quantity || 0) * (row.price || 0)
}

/** 复制行 */
export function copyRow(items, index) {
  const item = { ...items[index] }
  items.splice(index + 1, 0, item)
}

/** 日期格式化（表格 formatter 用） */
export function fmtDate(_r, _c, v) {
  return v ? String(v).replace('T', ' ').slice(0, 16) : ''
}

/** 日期格式化（直接传值用） */
export function fmtDateVal(v) {
  return v ? String(v).replace('T', ' ').slice(0, 16) : ''
}

/** 金额格式化 */
export function fmtMoney(v) {
  return Number(v || 0).toFixed(2)
}

/** 获取商品条码 */
export function getProductBarcode(products, productId) {
  const p = products.find(x => x.id === productId)
  return p?.barcode || '-'
}

/** 获取商品可用库存 */
export function getAvailableStock(products, productId, convRate) {
  const p = products.find(x => x.id === productId)
  const stock = p?.available_stock || p?.stock || 0
  const rate = convRate || 1
  return rate > 1 ? (stock / rate).toFixed(2) : stock.toFixed(2)
}

/** 获取商品占用库存 */
export function getOccupiedStock(products, productId) {
  const p = products.find(x => x.id === productId)
  return (p?.occupied_stock || 0).toFixed(2)
}

/** 创建空白行 */
export function createEmptyRow(overrides = {}) {
  return {
    product_id: null,
    quantity: 1,
    price: 0,
    amount: 0,
    remark: '',
    unit_id: null,
    _availableUnits: [],
    _basePrice: 0,
    ...overrides
  }
}

/** 创建 N 行空白行 */
export function createEmptyRows(count = 5, overrides = {}) {
  return Array.from({ length: count }, () => createEmptyRow(overrides))
}

/** 统一状态映射 - 采购订单/销售订单 */
export const orderStatusMap = {
  0: { label: '草稿', type: 'info' },
  1: { label: '已确认', type: 'warning' },
  2: { label: '已入库', type: 'success' },
  3: { label: '已冲红', type: 'danger' }
}

/** 统一状态映射 - 出库单/入库单 */
export const stockStatusMap = {
  0: { label: '草稿', type: 'info' },
  1: { label: '已确认', type: 'warning' },
  2: { label: '已出库', type: 'success' },
  3: { label: '已冲红', type: 'danger' }
}

/** 统一状态映射 - 退货订单 */
export const returnOrderStatusMap = {
  0: { label: '草稿', type: 'info' },
  1: { label: '已确认', type: 'warning' },
  2: { label: '已出库', type: 'success' },
  3: { label: '已冲红', type: 'danger' }
}

/** 统一状态映射 - 交货单/收货单 */
export const deliveryStatusMap = {
  pending: { label: '草稿', type: 'info' },
  confirmed: { label: '已确认', type: 'success' },
  settled: { label: '已结算', type: 'warning' },
  voided: { label: '已作废', type: 'info' },
  reversed: { label: '已冲红', type: 'danger' }
}

/** 统一状态映射 - 调拨 */
export const transferStatusMap = {
  0: { label: '草稿', type: 'info' },
  1: { label: '调拨中', type: 'warning' },
  2: { label: '已确认', type: 'success' },
  3: { label: '已取消', type: 'info' }
}

/** 统一状态映射 - 盘点 */
export const stocktakingStatusMap = {
  1: { label: '盘点中', type: 'info' },
  2: { label: '已审核', type: 'success' },
  3: { label: '已调整', type: 'warning' },
  4: { label: '已作废', type: 'danger' }
}

/** 统一状态映射 - 通用（字符串 key） */
export const genericStatusMap = {
  pending: { label: '草稿', type: 'warning' },
  approved: { label: '已通过', type: 'success' },
  confirmed: { label: '已确认', type: 'success' },
  audited: { label: '已审核', type: 'success' },
  adjusted: { label: '已调整', type: 'success' },
  rejected: { label: '已驳回', type: 'danger' },
  cancelled: { label: '已取消', type: 'info' },
  voided: { label: '已作废', type: 'info' },
  reversed: { label: '已冲红', type: 'info' },
  draft: { label: '草稿', type: 'info' },
  loaded: { label: '已装车', type: 'success' },
  returned: { label: '已退库', type: 'danger' }
}

/** 汇总计算方法（用于 el-table show-summary） */
export function makeSummaryMethod(amountField = 'amount') {
  return ({ columns, data }) => {
    const sums = []
    columns.forEach((col, idx) => {
      if (idx === 0) { sums[idx] = '合计'; return }
      if (col.property === amountField) {
        const total = data.reduce((s, row) => s + (row[amountField] || 0), 0)
        sums[idx] = `¥${total.toFixed(2)}`
      }
    })
    return sums
  }
}
