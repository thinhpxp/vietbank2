import { createApp } from 'vue';
import { createPinia } from 'pinia';
import '@/assets/tokens.scss';
import '@/assets/admin.css';
import '@/assets/common-ui.css';
import '@/assets/icons.css';
import App from './App.vue'
import router from './router'
import toastPlugin from './utils/toast'
import i18n from './utils/i18n'
import SvgIcon from './components/common/SvgIcon.vue'
import titleMixin from './mixins/titleMixin'
import { setupVxeTable } from './utils/vxe-table'

const app = createApp(App)
const pinia = createPinia()

// Suppress ResizeObserver loop limit exceeded error
window.addEventListener('error', e => {
    if (e.message === 'ResizeObserver loop completed with undelivered notifications.' ||
        e.message === 'ResizeObserver loop limit exceeded') {
        const resizeObserverErrDiv = document.getElementById('webpack-dev-server-client-overlay-div');
        const resizeObserverErr = document.getElementById('webpack-dev-server-client-overlay');
        if (resizeObserverErr) resizeObserverErr.setAttribute('style', 'display: none');
        if (resizeObserverErrDiv) resizeObserverErrDiv.setAttribute('style', 'display: none');
        e.stopImmediatePropagation();
    }
});

// Setup vxe-table
setupVxeTable(app)

// Register SvgIcon globally
app.component('SvgIcon', SvgIcon)

// Register Global Mixin for titles
app.mixin(titleMixin)

app.use(pinia)
app.use(router)
app.use(toastPlugin)
app.use(i18n)
app.mount('#app')