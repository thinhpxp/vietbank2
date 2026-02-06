import { reactive, computed } from 'vue';
import axios from 'axios';

// API Configuration
export const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000/api';

// Cấu hình Axios Request Interceptor để tự động gắn Token vào mọi yêu cầu
axios.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Cấu hình Axios Response Interceptor để xử lý lỗi hết hạn phiên (401) và lỗi quyền (403)
axios.interceptors.response.use(
    (response) => response,
    (error) => {
        const { status } = error.response || {};

        if (status === 401) {
            // Hết hạn phiên hoặc Token không hợp lệ
            // Import động để tránh vòng lặp phụ thuộc (circular dependency)
            const { showErrorDialog } = require('../utils/errorHandler');
            showErrorDialog(null, "Phiên đăng nhập đã hết hạn. Bạn sẽ được chuyển về trang đăng nhập.", "Hết hạn phiên");

            setTimeout(() => {
                store.logout();
                window.location.href = '/login';
            }, 3000); // Đợi 3s để user kịp đọc thông báo
        }
        else if (status === 403) {
            // Không có quyền truy cập
            const { showErrorDialog } = require('../utils/errorHandler');
            showErrorDialog(null, error, "Truy cập bị từ chối");
        }

        return Promise.reject(error);
    }
);

const state = reactive({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
    permissions: JSON.parse(localStorage.getItem('permissions')) || [],
    isAuthenticated: !!localStorage.getItem('token'),
});

const store = {
    state,

    // Getters
    isAdmin: computed(() => {
        if (state.user?.is_staff || state.user?.is_superuser) return true;

        // Smart Access: Access if user has ANY "view_" permission for core admin modules
        const coreModules = [
            'user', 'group', 'permission',
            'field', 'fieldgroup', 'formview',
            'documenttemplate', 'role',
            'masterobjecttype', 'auditlog'
        ];

        // Check if any permission string contains "view_" + module OR just "view_user" etc.
        // Permissions usually come as "app_label.view_model" or just "view_model"
        return state.permissions.some(perm => {
            // Normalized check
            const p = perm.toLowerCase();
            return coreModules.some(mod => p.includes(`view_${mod}`) || p.includes(`change_${mod}`));
        });
    }),
    isSuperuser: computed(() => state.user?.is_superuser || false),
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
