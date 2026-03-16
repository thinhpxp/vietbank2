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
                        <input v-model="form.username" type="text" class="admin-input" placeholder="Nhập username"
                            required />
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input v-model="form.email" type="email" class="admin-input" placeholder="Nhập email"
                            required />
                    </div>
                </div>

                <div class="form-group">
                    <label>Mật khẩu</label>
                    <input v-model="form.password" type="password" class="admin-input" placeholder="Nhập mật khẩu"
                        required />
                </div>

                <div class="form-group">
                    <label>Họ và tên</label>
                    <input v-model="form.full_name" type="text" class="admin-input" placeholder="Nguyễn Văn A"
                        required />
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>Số điện thoại</label>
                        <input v-model="form.phone" type="tel" class="admin-input" placeholder="090..." />
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>Nơi làm việc</label>
                        <input v-model="form.workplace" type="text" class="admin-input"
                            placeholder="Vietbank Chi nhánh..." />
                    </div>
                    <div class="form-group">
                        <label>Phòng ban/Chức danh</label>
                        <input v-model="form.department" type="text" class="admin-input"
                            placeholder="Phòng tín dụng..." />
                    </div>
                </div>

                <!-- Chọn Chi nhánh / Đơn vị -->
                <div class="form-group">
                    <label>🏢 Chi nhánh / Đơn vị công tác</label>
                    <vxe-select v-model="form.branch_id" class="admin-select-full" filterable clearable placeholder="-- Chọn chi nhánh / đơn vị --">
                        <vxe-option :value="null" label="-- Chưa chọn đơn vị (có thể cập nhật sau) --"></vxe-option>
                        <vxe-option v-for="b in branches" :key="b.id" :value="b.id" :label="b.display_name"></vxe-option>
                    </vxe-select>
                </div>

                <!-- DYNAMIC FIELDS FOR USER_EXT / THONG TIN BO SUNG THEO YEU CAU HE THONG-->
                <div v-if="hasDynamicFields" class="dynamic-extension mt-4 pt-4 border-t border-gray-100">
                    <DynamicForm v-if="dynamicGroups" :groups="dynamicGroups" :initial-values="dynamicValues"
                        mode="horizontal" @update:values="updateDynamicValues" />
                </div>

                <div v-if="error" class="error-message">
                    ⚠️ {{ error }}
                </div>

                <button type="submit" class="btn-action btn-primary btn-register-custom" :disabled="isLoading">
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
import { useAuthStore } from '@/store/auth.store';
import UserService from '@/services/user.service';
import MasterService from '@/services/master.service';
import DynamicForm from '@/components/DynamicForm.vue';

export default {
    name: 'RegisterPage',
    title: 'Đăng ký tài khoản',
    components: { DynamicForm },
    data() {
        return {
            form: {
                username: '',
                password: '',
                email: '',
                full_name: '',
                phone: '',
                workplace: '',
                department: '',
                branch_id: null
            },
            error: '',
            isLoading: false,
            dynamicGroups: {},
            dynamicValues: {},
            branches: [],
            authStore: useAuthStore()
        };
    },
    computed: {
        hasDynamicFields() {
            return Object.keys(this.dynamicGroups).length > 0;
        }
    },
    async mounted() {
        this.fetchDynamicFields();
        this.fetchBranches();
    },
    methods: {
        async fetchDynamicFields() {
            try {
                const res = await MasterService.getActiveFieldsGrouped('USER_EXT');
                this.dynamicGroups = res.data;
            } catch (e) {
                console.error('Error fetching dynamic fields for registration:', e);
            }
        },
        async fetchBranches() {
            try {
                const res = await MasterService.getBranches();
                this.branches = res.data || [];
            } catch (e) {
                console.warn('Không thể tải danh sách chi nhánh:', e);
            }
        },
        updateDynamicValues(values) {
            this.dynamicValues = { ...this.dynamicValues, ...values };
        },
        async handleRegister() {
            this.isLoading = true;
            this.error = '';
            try {
                // Chuẩn bị payload bao gồm cả trường động
                const registrationData = {
                    ...this.form,
                    field_values: this.dynamicValues
                };

                await UserService.register(registrationData);
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
    max-width: 800px;
}

.register-header {
    text-align: center;
    margin-bottom: 2rem;
}

.register-header h1 {
    font-size: 1.8rem;
    color: #1a2a6c;
    margin-bottom: 0.5rem;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1.2rem;
}

.form-group {
    margin-bottom: 1em;
    /* Handled by row gap or manual margins */
}

/* Fix for single-item rows */
.form-row:has(.form-group:only-child) {
    grid-template-columns: 1fr;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
    font-weight: 600;
    color: #555;
    text-align: left;
}

.divider {
    border: none;
    border-top: 1px solid #eee;
    margin: 1.5rem 0;
}

.btn-register-custom {
    width: 100%;
    margin-top: 1rem;
    font-size: 1rem;
    height: 42px !important;
    /* Slightly taller for primary action */
}

.error-message {
    color: #dc2626;
    background: #fee2e2;
    padding: 10px;
    border-radius: 6px;
    font-size: 0.9rem;
    margin-top: 1rem;
    text-align: left;
}

.register-footer {
    text-align: center;
    margin-top: 1.5rem;
    color: #666;
    font-size: 0.9rem;
}

.register-footer a {
    color: #42b983;
    font-weight: 600;
    text-decoration: none;
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

.admin-select-full {
    width: 100%;
}
</style>
