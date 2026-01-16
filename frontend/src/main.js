import { createApp } from 'vue';
import '@/assets/tokens.scss';
import '@/assets/admin.css';
import App from './App.vue'
import router from './router' // <-- Import router
import toastPlugin from './utils/toast'
import auth from './store/auth' // Import auth store

const app = createApp(App)

// Khởi tạo trạng thái xác thực từ LocalStorage
auth.initialize()

app.use(router) // <-- Sử dụng router
app.use(toastPlugin)
app.mount('#app')