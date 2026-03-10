import apiClient, { API_URL } from '@/services/api';

export { API_URL };

// Quản lý Authentication Store
import { reactive, computed } from 'vue';

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
        return state.user?.is_staff || state.user?.is_superuser || false;
    }),
    isSuperuser: computed(() => state.user?.is_superuser || false),
    hasPermission: (perm) => {
        if (state.user?.is_superuser) return true;
        return state.permissions.includes(perm);
    },

    // Actions
    async login(username, password) {
        try {
            const response = await apiClient.post('/token/', { username, password });
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
    },

    async fetchProfile() {
        try {
            const response = await apiClient.get('/me/');
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
    },

    async register(data) {
        try {
            await apiClient.post('/register/', data);
            return true;
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    },

    initialize() {
        if (state.token) {
            this.fetchProfile();
        }
    }
};

export default store;
