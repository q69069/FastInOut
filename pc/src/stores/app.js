import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const loading = ref(false)
  const loadingText = ref('')

  function showLoading(text = '加载中...') {
    loading.value = true
    loadingText.value = text
  }

  function hideLoading() {
    loading.value = false
    loadingText.value = ''
  }

  return { loading, loadingText, showLoading, hideLoading }
})
