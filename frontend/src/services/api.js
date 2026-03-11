import axios from 'axios';

export const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for API calls
apiClient.interceptors.request.use(
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

// Response interceptor for API calls
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const { status } = error.response || {};

        if (status === 401) {
            // Handle unauthorized access (e.g., redirect to login)
            // Note: We use dynamic import to avoid circular dependencies
            const { useAuthStore } = await import('../store/auth.store');
            const authStore = useAuthStore();
            const { showErrorDialog } = await import('../utils/errorHandler');

            showErrorDialog(null, "Phiên đăng nhập đã hết hạn. Bạn sẽ được chuyển về trang đăng nhập.", "Hết hạn phiên");

            setTimeout(() => {
                authStore.logout();
                window.location.href = '/login';
            }, 3000);
        } else if (status === 403) {
            const { showErrorDialog } = await import('../utils/errorHandler');
            showErrorDialog(null, error, "Truy cập bị từ chối");
        }

        return Promise.reject(error);
    }
);

export default apiClient;
