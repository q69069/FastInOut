import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Vant 按需引入样式
import 'vant/lib/index.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
