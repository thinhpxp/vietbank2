<template>
    <div class="register-container">
        <div class="register-card">
            <div class="register-header">
                <h1>Tạo tài khoản</h1>
                <p>Vui lòng điền thông tin để đăng ký</p>
            </div>

            <form @submit.prevent="handleRegister" class="register-form">
                <div class="form-row">
                    <div class="form-group">
                        <label>Tên đăng nhập</label>
                        <input v-model="form.username" type="text" placeholder="Nhập username" required />
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input v-model="form.email" type="email" placeholder="Nhập email" required />
                    </div>
                </div>

                <div class="form-group">
                    <label>Mật khẩu</label>
                    <input v-model="form.password" type="password" placeholder="Nhập mật khẩu" required />
                </div>

                <hr class="divider" />

                <div class="form-group">
                    <label>Họ và tên</label>
                    <input v-model="form.full_name" type="text" placeholder="Nguyễn Văn A" required />
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>Số điện thoại</label>
                        <input v-model="form.phone" type="tel" placeholder="090..." />
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Nơi làm việc</label>
                            <input v-model="form.workplace" type="text" placeholder="Vietbank Chi nhánh..." />
                        </div>
                        <div class="form-group">
                            <label>Phòng ban</label>
                            <input v-model="form.department" type="text" placeholder="Phòng tín dụng..." />
                        </div>
                    </div>
                </div>

                <div v-if="error" class="error-message">
                    ⚠️ {{ error }}
                </div>

                <button type="submit" class="btn-register" :disabled="isLoading">
                    <span v-if="isLoading" class="loader"></span>
                    <span v-else>Đăng ký ngay</span>
                </button>

                <div class="register-footer">
                    <p>Đã có tài khoản? <router-link to="/login">Đăng nhập</router-link></p>
                </div>
            </form>
        </div>
    </div>
</template>

<script>
import auth from '@/store/auth';

export default {
    name: 'RegisterPage',
    data() {
        return {
            form: {
                username: '',
                password: '',
                email: '',
                full_name: '',
                phone: '',
                workplace: '',
                department: ''
            },
            error: '',
            isLoading: false
        };
    },
    methods: {
        async handleRegister() {
            this.isLoading = true;
            this.error = '';
            try {
                await auth.register(this.form);
                this.$toast.success('Đăng ký thành công! Vui lòng đăng nhập.');
                this.$router.push('/login');
            } catch (err) {
                if (err.response && err.response.data) {
                    const firstError = Object.values(err.response.data)[0];
                    this.error = Array.isArray(firstError) ? firstError[0] : firstError;
                } else {
                    this.error = 'Có lỗi xảy ra trong quá trình đăng ký.';
                }
            } finally {
                this.isLoading = false;
            }
        }
    }
};
</script>

<style scoped>
.register-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f4f6f9;
    padding: 2rem;
    font-family: 'Inter', sans-serif;
}

.register-card {
    background: white;
    padding: 2.5rem;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
    width: 100%;
    max-width: 550px;
}

.register-header {
    text-align: center;
    margin-bottom: 2rem;
}

.register-header h1 {
    font-size: 1.8rem;
    color: #1a2a6c;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.form-group {
    margin-bottom: 1.2rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    font-weight: 600;
    color: #555;
}

.form-group input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 0.95rem;
}

.divider {
    border: none;
    border-top: 1px solid #eee;
    margin: 1.5rem 0;
}

.btn-register {
    width: 100%;
    padding: 12px;
    background: #1a2a6c;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    margin-top: 1rem;
}

.error-message {
    color: #dc2626;
    background: #fee2e2;
    padding: 10px;
    border-radius: 6px;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.register-footer {
    text-align: center;
    margin-top: 1.5rem;
    color: #666;
}

.loader {
    width: 20px;
    height: 20px;
    border: 3px solid #FFF;
    border-bottom-color: transparent;
    border-radius: 50%;
    display: inline-block;
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
