const BASE_URL = 'http://127.0.0.1:8000/api'

export function request(url, options = {}) {
  const token = uni.getStorageSync('token')
  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json',
        ...options.header
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          uni.removeStorageSync('token')
          uni.redirectTo({ url: '/pages/login/login' })
          reject(new Error('未登录'))
        } else {
          uni.showToast({ title: res.data?.detail || '请求失败', icon: 'none' })
          reject(res)
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络错误', icon: 'none' })
        reject(err)
      }
    })
  })
}

export const api = {
  login: (data) => request('/auth/login', { method: 'POST', data }),
  getDashboard: () => request('/reports/dashboard'),
  getProducts: (params) => request('/products?' + new URLSearchParams(params)),
  getCustomers: (params) => request('/customers?' + new URLSearchParams(params)),
  getSalesOrders: (params) => request('/sales/orders?' + new URLSearchParams(params)),
  createSalesOrder: (data) => request('/sales/orders', { method: 'POST', data }),
  getInventory: (params) => request('/inventory?' + new URLSearchParams(params)),
  getReceipts: (params) => request('/finance/receipts?' + new URLSearchParams(params)),
  createReceipt: (data) => request('/finance/receipts', { method: 'POST', data }),
  getReceivables: () => request('/finance/receivables')
}
