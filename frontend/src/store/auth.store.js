import { defineStore } from 'pinia';
import apiClient from '@/services/api';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('token') || null,
        user: JSON.parse(localStorage.getItem('user')) || null,
        permissions: JSON.parse(localStorage.getItem('permissions')) || [],
        isAuthenticated: !!localStorage.getItem('token'),
    }),

    getters: {
        isAdmin: (state) => {
            return state.user?.is_staff || state.user?.is_superuser || false;
        },
        isSuperuser: (state) => state.user?.is_superuser || false,
        hasPermission: (state) => (perm) => {
            if (state.user?.is_superuser) return true;
            return state.permissions.includes(perm);
        },
    },

    actions: {
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
            this.token = token;
            this.isAuthenticated = true;
            localStorage.setItem('token', token);
        },

        async fetchProfile() {
            try {
                const response = await apiClient.get('/me/');
                const { permissions, ...userData } = response.data;
                this.user = userData;
                this.permissions = permissions || [];
                localStorage.setItem('user', JSON.stringify(userData));
                localStorage.setItem('permissions', JSON.stringify(this.permissions));
            } catch (error) {
                console.error('Fetch profile failed:', error);
                this.logout();
            }
        },

        logout() {
            this.token = null;
            this.user = null;
            this.permissions = [];
            this.isAuthenticated = false;
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
            if (this.token) {
                this.fetchProfile();
            }
        }
    }
});
