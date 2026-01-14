import { reactive, computed } from 'vue';
import axios from 'axios';
import { toast } from '@/utils/toast';

// Cấu hình Axios Interceptor để xử lý lỗi hết hạn phiên (401)
axios.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            // Kiểm tra nếu là lỗi hết hạn token (thường backend trả về mã lỗi cụ thể hoặc message)
            const detail = error.response.data?.detail || '';
            if (detail.includes('expired') || detail.includes('valid')) {
                toast.warning('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.', 5000);
                store.logout();
                // Chuyển hướng người dùng về trang login nếu cần (Router guard sẽ xử lý việc này khi state thay đổi)
                window.location.href = '#/login';
            }
        }
        return Promise.reject(error);
    }
);

// API Configuration
const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000/api';

const state = reactive({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
    permissions: JSON.parse(localStorage.getItem('permissions')) || [],
    isAuthenticated: !!localStorage.getItem('token'),
});

const store = {
    state,

    // Getters
    isAdmin: computed(() => state.user?.is_staff || false),
    hasPermission: (perm) => {
        if (state.user?.is_superuser) return true;
        return state.permissions.includes(perm);
    },

    // Actions
    async login(username, password) {
        try {
            const response = await axios.post(`${API_URL}/token/`, { username, password });
            const { access } = response.data;

            this.setToken(access);
            await this.fetchProfile();
            return true;
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    },

    setToken(token) {
        state.token = token;
        state.isAuthenticated = true;
        localStorage.setItem('token', token);
        // Config axios for future requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    },

    async fetchProfile() {
        try {
            const response = await axios.get(`${API_URL}/me/`);
            const { permissions, ...userData } = response.data;
            state.user = userData;
            state.permissions = permissions || [];
            localStorage.setItem('user', JSON.stringify(userData));
            localStorage.setItem('permissions', JSON.stringify(state.permissions));
        } catch (error) {
            console.error('Fetch profile failed:', error);
            this.logout();
        }
    },

    logout() {
        state.token = null;
        state.user = null;
        state.permissions = [];
        state.isAuthenticated = false;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('permissions');
        delete axios.defaults.headers.common['Authorization'];
    },

    async register(data) {
        try {
            await axios.post(`${API_URL}/register/`, data);
            return true;
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    },

    initialize() {
        if (state.token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${state.token}`;
            this.fetchProfile();
        }
    }
};

export default store;
