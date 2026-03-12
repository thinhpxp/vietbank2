<template>
    <div class="login-container">
        <div class="login-card">
            <div class="login-header">
                <div class="logo">🏦</div>
                <h1>Vietbank Contract</h1>
                <p>Hệ thống tự động hóa hồ sơ tín dụng</p>
            </div>

            <form @submit.prevent="handleLogin" class="login-form">
                <div class="form-group">
                    <label for="username">Tên đăng nhập</label>
                    <div class="input-wrapper">
                        <span class="icon">👤</span>
                        <input v-model="username" type="text" id="username" placeholder="Nhập tên đăng nhập" required
                            :disabled="isLoading" />
                    </div>
                </div>

                <div class="form-group">
                    <label for="password">Mật khẩu</label>
                    <div class="input-wrapper">
                        <span class="icon">🔒</span>
                        <input v-model="password" type="password" id="password" placeholder="Nhập mật khẩu" required
                            :disabled="isLoading" />
                    </div>
                </div>

                <div v-if="error" class="error-message">
                    ⚠️ {{ error }}
                </div>

                <button type="submit" class="btn-login" :disabled="isLoading">
                    <span v-if="isLoading" class="loader"></span>
                    <span v-else>Đăng nhập</span>
                </button>

                <div class="login-footer">
                    <p>Chưa có tài khoản? <router-link to="/register">Đăng ký ngay</router-link></p>
                </div>
            </form>
        </div>
    </div>
</template>

<script>
import { useAuthStore } from '@/store/auth.store';
import { getErrorMessage } from '@/utils/errorHandler';

export default {
    name: 'LoginPage',
    title: 'Đăng nhập',
    data() {
        return {
            username: '',
            password: '',
            error: '',
            isLoading: false,
            authStore: useAuthStore()
        };
    },
    methods: {
        async handleLogin() {
            this.isLoading = true;
            this.error = '';
            try {
                await this.authStore.login(this.username, this.password);
                this.$router.push('/');
            } catch (err) {
                // Sử dụng getErrorMessage thay vì hardcode
                this.error = getErrorMessage(err);
            } finally {
                this.isLoading = false;
            }
        }
    }
};
</script>

<style scoped>
.login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
    font-family: 'Inter', sans-serif;
}

.login-card {
    background: rgba(255, 255, 255, 0.95);
    padding: 2.5rem;
    border-radius: 20px;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
    width: 100%;
    max-width: 400px;
    backdrop-filter: blur(10px);
}

.login-header {
    text-align: center;
    margin-bottom: 2rem;
}

.logo {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.login-header h1 {
    font-size: 1.5rem;
    color: #333;
    margin-bottom: 0.5rem;
}

.login-header p {
    color: #666;
    font-size: 0.9rem;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #444;
}

.input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.input-wrapper .icon {
    position: absolute;
    left: 12px;
    font-size: 1.2rem;
}

.input-wrapper input {
    width: 100%;
    padding: 12px 12px 12px 40px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.3s, box-shadow 0.3s;
}

.input-wrapper input:focus {
    outline: none;
    border-color: #1a2a6c;
    box-shadow: 0 0 0 3px rgba(26, 42, 108, 0.1);
}

.btn-login {
    width: 100%;
    padding: 12px;
    background: #1a2a6c;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.3s;
}

.btn-login:hover {
    background: #0d1a4d;
}

.btn-login:disabled {
    background: #ccc;
    cursor: not-allowed;
}

.error-message {
    background: #fee2e2;
    color: #dc2626;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    font-size: 0.9rem;
    text-align: center;
}

.login-footer {
    text-align: center;
    margin-top: 1.5rem;
    font-size: 0.9rem;
    color: #666;
}

.login-footer a {
    color: #1a2a6c;
    text-decoration: none;
    font-weight: 600;
}

.loader {
    width: 20px;
    height: 20px;
    border: 3px solid #FFF;
    border-bottom-color: transparent;
    border-radius: 50%;
    display: inline-block;
    box-sizing: border-box;
    animation: rotation 1s linear infinite;
}

@keyframes rotation {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}
</style>
