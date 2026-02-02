import { createApp } from 'vue';
import '@/assets/tokens.scss';
import '@/assets/admin.css';
import '@/assets/common-ui.css';
import '@/assets/icons.css';
import App from './App.vue'
import router from './router' // <-- Import router
import toastPlugin from './utils/toast'
import i18n from './utils/i18n'
import auth from './store/auth' // Import auth store
import SvgIcon from './components/common/SvgIcon.vue' // Import SvgIcon

const app = createApp(App)

// Khởi tạo trạng thái xác thực từ LocalStorage
auth.initialize()

// Register SvgIcon globally
app.component('SvgIcon', SvgIcon)

app.use(router) // <-- Sử dụng router
app.use(toastPlugin)
app.use(i18n)
app.mount('#app')