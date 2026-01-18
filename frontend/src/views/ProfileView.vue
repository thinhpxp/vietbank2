<template>
    <div class="page-container profile-page">
        <div class="page-header">
            <div class="header-title">
                <h2>👤 Quản lý tài khoản</h2>
            </div>
            <button class="btn-action btn-secondary" @click="$router.push('/')"> Quay lại</button>
        </div>

        <div v-if="loading" class="loading-state">Đang tải thông tin...</div>

        <div v-else class="profile-layout">
            <!-- CỘT TRÁI: THÔNG TIN CÁ NHÂN -->
            <div class="profile-section card">
                <h3>🏠 Thông tin cá nhân</h3>
                <p class="section-note">Cập nhật thông tin liên hệ và nơi công tác của bạn.</p>

                <form @submit.prevent="updateProfile" class="profile-form">
                    <div class="form-group">
                        <label>Tên đăng nhập (Username)</label>
                        <input :value="user.username" class="admin-input readonly" disabled
                            title="Username không thể thay đổi" />
                    </div>

                    <div class="form-group">
                        <label>Họ và tên</label>
                        <input v-model="profileForm.full_name" class="admin-input" placeholder="Nhập họ tên đầy đủ" />
                    </div>

                    <div class="form-group">
                        <label>Email</label>
                        <input v-model="profileForm.email" type="email" class="admin-input"
                            placeholder="example@vietbank.com.vn" />
                    </div>

                    <div class="form-group-row">
                        <div class="form-group">
                            <label>Số điện thoại</label>
                            <input v-model="profileForm.phone" class="admin-input" placeholder="0xxx.xxx.xxx" />
                        </div>
                    </div>

                    <div class="form-group-row">
                        <div class="form-group">
                            <label>Nơi công tác</label>
                            <input v-model="profileForm.workplace" class="admin-input"
                                placeholder="Ví dụ: Hội sở / Chi nhánh..." />
                        </div>
                        <div class="form-group">
                            <label>Phòng ban</label>
                            <input v-model="profileForm.department" class="admin-input"
                                placeholder="Phòng QLTD / Phòng Doanh nghiệp..." />
                        </div>
                    </div>

                    <div class="form-actions">
                        <button type="submit" class="btn-action btn-primary" :disabled="isUpdatingProfile">
                            {{ isUpdatingProfile ? 'Đang cập nhật...' : 'Lưu thay đổi' }}
                        </button>
                    </div>
                </form>
            </div>

            <!-- CỘT PHẢI: BẢO MẬT & QUYỀN HẠN -->
            <div class="profile-right">
                <!-- Đổi mật khẩu -->
                <div class="profile-section card security-card">
                    <h3>🔒 Đổi mật khẩu</h3>
                    <p class="section-note">Thay đổi mật khẩu định kỳ để bảo vệ tài khoản.</p>

                    <form @submit.prevent="changePassword" class="profile-form">
                        <div class="form-group">
                            <label>Mật khẩu hiện tại</label>
                            <input v-model="passwordForm.old_password" type="password" class="admin-input" required />
                        </div>
                        <div class="form-group">
                            <label>Mật khẩu mới</label>
                            <input v-model="passwordForm.new_password" type="password" class="admin-input" required />
                        </div>
                        <div class="form-group">
                            <label>Xác nhận mật khẩu mới</label>
                            <input v-model="passwordForm.confirm_password" type="password" class="admin-input"
                                required />
                        </div>
                        <div class="form-actions">
                            <button type="submit" class="btn-action btn-save" :disabled="isChangingPassword">
                                {{ isChangingPassword ? 'Đang xử lý...' : 'Cập nhật mật khẩu' }}
                            </button>
                        </div>
                    </form>
                </div>

                <!-- Quyền hạn (Read-only) -->
                <div class="profile-section card">
                    <h3>🛡️ Quyền hạn hiện tại</h3>
                    <div class="permissions-list">
                        <div class="perm-item" v-if="user.is_superuser">
                            <span class="badge-form">Quản trị viên hệ thống (Superuser)</span>
                        </div>
                        <div class="perm-item" v-else-if="user.is_staff">
                            <span class="badge-form">Nhân viên Admin (Staff)</span>
                        </div>
                        <div class="perm-item" v-else>
                            <span class="badge-form">Người dùng (End-user)</span>
                        </div>

                        <div v-if="user.groups_details && user.groups_details.length > 0" class="user-groups">
                            <p class="font-bold mb-2">Nhóm quyền:</p>
                            <div class="groups-flex">
                                <span v-for="g in user.groups_details" :key="g.id" class="status-badge draft">{{ g.name
                                    }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import auth from '@/store/auth';

export default {
    name: 'ProfileView',
    data() {
        return {
            loading: true,
            user: {},
            isUpdatingProfile: false,
            isChangingPassword: false,
            profileForm: {
                full_name: '',
                email: '',
                phone: '',
                workplace: '',
                department: ''
            },
            passwordForm: {
                old_password: '',
                new_password: '',
                confirm_password: ''
            }
        };
    },
    mounted() {
        this.fetchUserData();
    },
    methods: {
        async fetchUserData() {
            try {
                const res = await axios.get('http://localhost:8000/api/me/');
                this.user = res.data;
                // Map to form
                this.profileForm.full_name = this.user.full_name || '';
                this.profileForm.email = this.user.email || '';
                this.profileForm.phone = this.user.phone || '';
                this.profileForm.workplace = this.user.workplace || '';
                this.profileForm.department = this.user.department || '';
            } catch (e) {
                this.$toast.error('Không thể tải thông tin cá nhân');
            } finally {
                this.loading = false;
            }
        },
        async updateProfile() {
            this.isUpdatingProfile = true;
            try {
                await axios.patch('http://localhost:8000/api/me/', this.profileForm);
                this.$toast.success('Cập nhật thông tin thành công!');
                // Refresh auth state to update navbar name if changed
                auth.fetchProfile();
            } catch (e) {
                this.$toast.error('Lỗi cập nhật thông tin');
            } finally {
                this.isUpdatingProfile = false;
            }
        },
        async changePassword() {
            if (this.passwordForm.new_password !== this.passwordForm.confirm_password) {
                return this.$toast.error('Mật khẩu xác nhận không khớp');
            }

            this.isChangingPassword = true;
            try {
                await axios.post('http://localhost:8000/api/change-password/', {
                    old_password: this.passwordForm.old_password,
                    new_password: this.passwordForm.new_password
                });
                this.$toast.success('Đổi mật khẩu thành công!');
                // Reset form
                this.passwordForm = { old_password: '', new_password: '', confirm_password: '' };
            } catch (e) {
                const msg = e.response?.data?.old_password?.[0] || 'Lỗi đổi mật khẩu';
                this.$toast.error(msg);
            } finally {
                this.isChangingPassword = false;
            }
        }
    }
};
</script>

<style scoped>
.profile-page {
    max-width: 1000px;
    margin-top: 30px;
}

.profile-layout {
    display: flex;
    gap: 25px;
    text-align: left;
}

.profile-section {
    flex: 1;
}

.profile-right {
    width: 380px;
    display: flex;
    flex-direction: column;
    gap: 25px;
}

.card {
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    border: 1px solid #eee;
}

.card h3 {
    margin-top: 0;
    margin-bottom: 8px;
    color: #2c3e50;
    font-size: 1.2rem;
}

.section-note {
    font-size: 0.85rem;
    color: #7f8c8d;
    margin-bottom: 20px;
}

.profile-form {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 5px;
    flex: 1;
}

.form-group-row {
    display: flex;
    gap: 15px;
}

.form-group label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #34495e;
}

.readonly {
    background: #f8f9fa;
    cursor: not-allowed;
    color: #95a5a6;
}

.form-actions {
    margin-top: 10px;
    display: flex;
    justify-content: flex-end;
}

.permissions-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.groups-flex {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

@media (max-width: 1000px) {
    .profile-layout {
        flex-direction: column;
    }

    .profile-right {
        width: 100%;
    }
}
</style>
