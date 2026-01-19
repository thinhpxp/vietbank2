<template>
    <div class="access-mgmt">
        <div class="mgmt-header">
            <div class="header-left">
                <h2>🛡️ Quản lý Truy cập & Hệ thống</h2>
            </div>
            <div class="mgmt-tabs">
                <button :class="{ active: activeMainTab === 'users' }" @click="activeMainTab = 'users'">👥 Người
                    dùng</button>
                <button :class="{ active: activeMainTab === 'groups' }" @click="activeMainTab = 'groups'">🔑 Nhóm &
                    Quyền</button>
                <button :class="{ active: activeMainTab === 'audit' }" @click="activeMainTab = 'audit'">📜 Nhật
                    ký</button>
            </div>
            <div class="admin-role-legend">
                <span class="admin-legend-item" title="Toàn quyền hệ thống, bỏ qua RBAC"><span
                        class="badge badge-superuser">ROOT</span> Siêu Quản Trị</span>
                <span class="admin-legend-item" title="Có quyền truy cập Dashboard Admin, quyền hạn theo Nhóm"><span
                        class="badge badge-admin">Admin</span> Quản trị</span>
                <span class="admin-legend-item" title="Người dùng nghiệp vụ, chỉ có quyền theo Nhóm"><span
                        class="badge badge-user">User</span> Nghiệp vụ</span>
            </div>
        </div>

        <!-- TAB 1: NGƯỜI DÙNG -->
        <div v-if="activeMainTab === 'users'" class="split-view" ref="userSplitView">
            <!-- LEFT: USER LIST -->
            <div class="pane pane-left" :style="{ width: userPaneWidth + '%' }">
                <div class="pane-header admin-row">
                    <div class="search-box flex-1">
                        <input type="text" v-model="userSearch" placeholder="Tìm kiếm user..."
                            class="admin-form-control" />
                    </div>
                    <button @click="createNewUser" class="btn-action btn-primary">
                        <SvgIcon name="plus" size="sm" /> Thêm
                    </button>
                </div>

                <div class="table-container scrollable">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Username</th>
                                <th>Họ tên</th>
                                <th>Trạng thái</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="u in filteredUsers" :key="u.id" :class="{ selected: selectedUser?.id === u.id }"
                                @click="selectUser(u)">
                                <td><strong>{{ u.username }}</strong></td>
                                <td>{{ u.full_name || '---' }}</td>
                                <td>
                                    <span :class="['badge', u.is_active ? 'badge-active' : 'badge-inactive']">
                                        {{ u.is_active ? 'Active' : 'Locked' }}
                                    </span>
                                    <span v-if="u.is_staff && !u.is_superuser" class="badge badge-admin">Admin</span>
                                    <span v-if="u.is_superuser" class="badge badge-superuser"
                                        title="Tài khoản Hệ thống">ROOT</span>
                                    <span v-if="!u.is_staff && !u.is_superuser" class="badge badge-user">User</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="divider" @mousedown="startResize('user')"></div>

            <!-- RIGHT: USER EDITOR -->
            <div class="pane pane-right" :style="{ width: (100 - userPaneWidth) + '%' }">
                <div v-if="selectedUser" class="editor-container">
                    <div class="pane-header admin-row">
                        <h3 class="flex-1">Chi tiết: {{ selectedUser.username }}</h3>
                        <div class="actions">
                            <span v-if="selectedUser.is_superuser" class="superuser-warning">
                                🛡️ Tài khoản Hệ thống (Bypass mọi quyền)
                            </span>
                            <button @click="saveUser" class="btn-success"
                                :disabled="isSaving || (selectedUser.is_superuser && !auth.isSuperuser)">
                                Lưu thay đổi
                            </button>
                        </div>
                    </div>

                    <div class="editor-content scrollable">
                        <div class="admin-form-grid">
                            <section class="admin-form-section">
                                <h4>Thông tin Tài khoản</h4>
                                <div class="admin-field">
                                    <label>Username</label>
                                    <input type="text" v-model="selectedUser.username" class="admin-form-control"
                                        disabled title="Username là định danh duy nhất và không thể thay đổi." />
                                </div>
                                <div class="admin-field">
                                    <label>Email</label>
                                    <input type="email" v-model="selectedUser.email" class="admin-form-control" />
                                </div>
                                <div class="field-row">
                                    <label class="admin-checkbox-label">
                                        <input type="checkbox" v-model="selectedUser.is_active" /> Hoạt động
                                    </label>
                                    <label class="admin-checkbox-label"
                                        :class="{ disabled: selectedUser.is_superuser && !auth.isSuperuser }">
                                        <input type="checkbox" v-model="selectedUser.is_staff"
                                            :disabled="selectedUser.is_superuser && !auth.isSuperuser" /> Quyền Admin
                                    </label>
                                    <label v-if="auth.isSuperuser" class="admin-checkbox-label">
                                        <input type="checkbox" v-model="selectedUser.is_superuser" /> Quyền Root
                                    </label>
                                </div>
                            </section>

                            <section class="admin-form-section">
                                <h4>Thông tin Cá nhân</h4>
                                <div class="admin-field">
                                    <label>Họ và tên</label>
                                    <input type="text" v-model="selectedUser.full_name" class="admin-form-control" />
                                </div>
                                <div class="admin-field">
                                    <label>Số điện thoại</label>
                                    <input type="text" v-model="selectedUser.phone" class="admin-form-control" />
                                </div>
                                <div class="admin-field">
                                    <label>Nơi làm việc</label>
                                    <input type="text" v-model="selectedUser.workplace" class="admin-form-control" />
                                </div>
                                <div class="admin-field">
                                    <label>Phòng ban</label>
                                    <input type="text" v-model="selectedUser.department" class="admin-form-control" />
                                </div>
                            </section>
                        </div>

                        <section class="admin-form-section">
                            <h4>Ghi chú quản trị</h4>
                            <div class="admin-field">
                                <textarea v-model="selectedUser.note" class="admin-form-control" rows="3"
                                    placeholder="Nhập ghi chú chi tiết về người dùng này..."></textarea>
                            </div>
                        </section>

                        <section class="admin-form-section">
                            <h4>Nhóm quyền</h4>
                            <div class="admin-group-picker">
                                <label v-for="g in groups" :key="g.id" class="admin-group-chip"
                                    :class="{ selected: selectedUser.groups.includes(g.id) }">
                                    <input type="checkbox" :value="g.id" v-model="selectedUser.groups" />
                                    {{ g.name }}
                                </label>
                            </div>
                        </section>

                        <section class="admin-form-section">
                            <h4>Quyền hạn thực tế</h4>
                            <div class="admin-effective-permissions">
                                <div v-if="selectedUser.is_superuser" class="all-permissions-banner">
                                    🔥 <strong>TOÀN QUYỀN HỆ THỐNG</strong> - Người dùng này có quyền thực hiện mọi hành
                                    động mà không cần gán nhóm.
                                </div>
                                <div v-else-if="selectedUser.permissions && selectedUser.permissions.length"
                                    class="admin-perm-tags">
                                    <span v-for="p in selectedUser.permissions" :key="p" class="admin-perm-tag">{{ p
                                    }}</span>
                                </div>
                                <div v-else class="empty-permissions">
                                    ⚠️ Tài khoản này hiện chưa có bất kỳ quyền hạn nào.
                                </div>
                            </div>
                        </section>

                        <section class="admin-form-section danger-zone">
                            <h4>Vùng nguy hiểm</h4>
                            <div class="action-row">
                                <button @click="confirmResetPassword" class="btn-warning"
                                    :disabled="selectedUser.is_superuser && !auth.isSuperuser">🔄 Reset mật
                                    khẩu</button>
                                <button @click="confirmDeleteUser" class="btn-danger"
                                    :disabled="selectedUser.is_superuser && !auth.isSuperuser">
                                    <SvgIcon name="trash" size="sm" /> Xóa tài
                                    khoản
                                </button>
                            </div>
                        </section>
                    </div>
                </div>
                <div v-else class="empty-state">
                    <i class="icon">👤</i>
                    <p>Chọn một người dùng để chỉnh sửa thông tin</p>
                </div>
            </div>
        </div>

        <!-- TAB 2: NHÓM & QUYỀN -->
        <div v-if="activeMainTab === 'groups'" class="split-view" ref="groupSplitView">
            <!-- LEFT: GROUP LIST -->
            <div class="pane pane-left" :style="{ width: groupPaneWidth + '%' }">
                <div class="pane-header">
                    <h3>Danh sách Nhóm</h3>
                    <button @click="createNewGroup" class="btn-primary">
                        <SvgIcon name="plus" size="sm" /> Tạo Nhóm
                    </button>
                </div>
                <div class="table-container scrollable">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Tên nhóm</th>
                                <th>Số quyền</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="g in groups" :key="g.id" :class="{ selected: selectedGroup?.id === g.id }"
                                @click="selectGroup(g)">
                                <td><strong>{{ g.name }}</strong></td>
                                <td>{{ g.permissions?.length || 0 }} quyền</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="divider" @mousedown="startResize('group')"></div>

            <!-- RIGHT: GROUP EDITOR -->
            <div class="pane pane-right" :style="{ width: (100 - groupPaneWidth) + '%' }">
                <div v-if="selectedGroup" class="editor-container">
                    <div class="pane-header admin-row">
                        <input type="text" v-model="selectedGroup.name" class="admin-form-control h3-input flex-1"
                            placeholder="Tên nhóm..." />
                        <div class="actions">
                            <button @click="saveGroup" class="btn-success" :disabled="isSaving">Lưu Nhóm</button>
                            <button @click="confirmDeleteGroup" class="btn-icon danger">
                                <SvgIcon name="trash" size="sm" />
                            </button>
                        </div>
                    </div>

                    <div class="permission-manager">
                        <div class="perm-header">
                            <h4>Phân quyền chi tiết</h4>
                            <div class="perm-search">
                                <input type="text" v-model="permSearch" placeholder="Tìm nhanh quyền..."
                                    class="admin-form-control" />
                            </div>
                        </div>

                        <div class="perm-list scrollable">
                            <div v-for="(perms, category) in groupedPermissions" :key="category" class="perm-category">
                                <h5 class="category-title">{{ category }}</h5>
                                <div class="perm-grid">
                                    <label v-for="p in perms" :key="p.id" class="perm-item"
                                        :class="{ checked: selectedGroup.permissions.includes(p.id) }">
                                        <input type="checkbox" :value="p.id" v-model="selectedGroup.permissions" />
                                        <div class="perm-info">
                                            <span class="p-name">{{ p.name }}</span>
                                            <code class="p-code">{{ p.codename }}</code>
                                        </div>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-else class="empty-state">
                    <i class="icon">🔑</i>
                    <p>Chọn hoặc tạo mới một nhóm để thiết lập quyền hạn</p>
                </div>
            </div>
        </div>

        <!-- TAB 3: AUDIT LOG -->
        <div v-if="activeMainTab === 'audit'" class="audit-view pane">
            <div class="pane-header admin-row">
                <h3 class="flex-1">Nhật ký hệ thống</h3>
                <div class="audit-filters">
                    <input type="text" v-model="auditSearch" placeholder="Tìm theo username, hành động..."
                        class="admin-form-control" />
                </div>
            </div>
            <div class="table-container scrollable">
                <table class="data-table audit-table">
                    <thead>
                        <tr>
                            <th>Thời gian</th>
                            <th>User</th>
                            <th>Hành động</th>
                            <th>Đối tượng</th>
                            <th>Ghi chú</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="log in filteredLogs" :key="log.id">
                            <td class="time">{{ formatTime(log.timestamp) }}</td>
                            <td><strong>{{ log.user_name }}</strong></td>
                            <td><span :class="['tag', 'tag-' + log.action]">{{ log.action }}</span></td>
                            <td>{{ log.target_model }}</td>
                            <td class="details">{{ log.details }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- MODAL RESET PASSWORD -->
        <div v-if="showResetModal" class="modal-overlay">
            <div class="modal-content">
                <h3>Reset Mật khẩu cho {{ selectedUser.username }}</h3>
                <div class="admin-field">
                    <label>Mật khẩu mới</label>
                    <input type="text" v-model="newPassword" class="admin-form-control" />
                    <p class="hint">Vui lòng cung cấp mật khẩu này cho nhân viên.</p>
                </div>
                <div class="modal-actions">
                    <button @click="showResetModal = false" class="btn-secondary">Hủy</button>
                    <button @click="executeResetPassword" class="btn-warning">Xác nhận Reset</button>
                </div>
            </div>
        </div>

        <!-- Delete User Confirm Modal -->
        <ConfirmModal v-if="selectedUser" :visible="showDeleteUserConfirm" type="warning" title="Xác nhận xóa tài khoản"
            :message="`Bạn có chắc chắn muốn XÓA tài khoản '${selectedUser.username}'? Hành động này không thể hoàn tác.`"
            confirmText="Xóa" @confirm="handleDeleteUser" @cancel="showDeleteUserConfirm = false" />

        <!-- Create Group Input Modal -->
        <InputModal :visible="showCreateGroupInput" title="Tạo nhóm mới" label="Tên nhóm:" confirmText="Tạo"
            @confirm="handleCreateGroup" @cancel="showCreateGroupInput = false" />

        <!-- Delete Group Confirm Modal -->
        <ConfirmModal v-if="selectedGroup" :visible="showDeleteGroupConfirm" type="warning" title="Xác nhận xóa nhóm"
            :message="`Bạn có chắc chắn muốn xóa nhóm '${selectedGroup.name}'?`" confirmText="Xóa"
            @confirm="handleDeleteGroup" @cancel="showDeleteGroupConfirm = false" />

        <!-- Error Modal (from mixin) -->
        <ConfirmModal :visible="showErrorModal" type="error" mode="alert" :title="errorModalTitle"
            :message="errorModalMessage" :errorCode="errorModalCode" :details="errorModalDetails" :showTimestamp="true"
            confirmText="Đóng" @confirm="showErrorModal = false" @cancel="showErrorModal = false" />
    </div>
</template>

<script>
import axios from 'axios';
import auth from '@/store/auth';
import { errorHandlingMixin } from '@/utils/errorHandler';
import ConfirmModal from '@/components/ConfirmModal.vue';
import InputModal from '@/components/InputModal.vue';

const API_BASE = 'http://localhost:8000/api';

export default {
    name: 'AdminAccessManagement',
    components: { ConfirmModal, InputModal },
    mixins: [errorHandlingMixin],
    data() {
        return {
            activeMainTab: 'users',
            userPaneWidth: 35,
            groupPaneWidth: 35,

            // Data
            users: [],
            groups: [],
            permissions: [],
            auditLogs: [],

            // Selection
            selectedUser: null,
            selectedGroup: null,

            // Search
            userSearch: '',
            permSearch: '',
            auditSearch: '',

            // UI States
            isSaving: false,
            isResizing: false,
            resizeMode: '',
            showResetModal: false,
            newPassword: '',

            // Confirm/Input Modals
            showDeleteUserConfirm: false,
            showDeleteGroupConfirm: false,
            showCreateGroupInput: false,

            auth // Add to data for template use
        };
    },
    computed: {
        filteredUsers() {
            if (!this.userSearch) return this.users;
            const q = this.userSearch.toLowerCase();
            return this.users.filter(u =>
                u.username.toLowerCase().includes(q) ||
                u.full_name?.toLowerCase().includes(q)
            );
        },
        groupedPermissions() {
            const grouped = {};
            const q = this.permSearch.toLowerCase();
            const filtered = this.permissions.filter(p =>
                p.name.toLowerCase().includes(q) ||
                p.codename.toLowerCase().includes(q)
            );

            filtered.forEach(p => {
                const cat = p.content_type || 'System';
                if (!grouped[cat]) grouped[cat] = [];
                grouped[cat].push(p);
            });
            return grouped;
        },
        filteredLogs() {
            if (!this.auditSearch) return this.auditLogs;
            const q = this.auditSearch.toLowerCase();
            return this.auditLogs.filter(l =>
                l.user_name.toLowerCase().includes(q) ||
                l.action.toLowerCase().includes(q) ||
                l.details?.toLowerCase().includes(q)
            );
        }
    },
    async created() {
        await this.loadAllData();
    },
    methods: {
        async loadAllData() {
            try {
                const [uRes, gRes, pRes, aRes] = await Promise.all([
                    axios.get(`${API_BASE}/users/`),
                    axios.get(`${API_BASE}/user-groups/`),
                    axios.get(`${API_BASE}/user-permissions/`),
                    axios.get(`${API_BASE}/audit-logs/`)
                ]);
                this.users = uRes.data;
                this.groups = gRes.data;
                this.permissions = pRes.data;
                this.auditLogs = aRes.data;
            } catch (e) {
                this.$toast.error('Lỗi tải dữ liệu hệ thống.');
            }
        },

        // User Methods
        selectUser(u) {
            this.selectedUser = JSON.parse(JSON.stringify(u));
        },
        createNewUser() {
            this.$router.push('/register'); // Redirect to existing register page for now or create inline
        },
        async saveUser() {
            this.isSaving = true;
            try {
                const res = await axios.patch(`${API_BASE}/users/${this.selectedUser.id}/`, this.selectedUser);
                const idx = this.users.findIndex(u => u.id === res.data.id);
                if (idx !== -1) {
                    // Sử dụng splice để đảm bảo tính phản ứng (reactivity) trong Vue
                    this.users.splice(idx, 1, res.data);
                }
                // Cập nhật selectedUser bằng clone mới từ server
                this.selectedUser = JSON.parse(JSON.stringify(res.data));
                this.$toast.success('Đã cập nhật người dùng.');
            } catch (e) {
                this.$toast.error('Lỗi khi lưu người dùng.');
            } finally {
                this.isSaving = false;
            }
        },
        confirmResetPassword() {
            this.newPassword = Math.random().toString(36).slice(-8);
            this.showResetModal = true;
        },
        async executeResetPassword() {
            try {
                await axios.post(`${API_BASE}/users/${this.selectedUser.id}/reset-password/`, { password: this.newPassword });
                this.showResetModal = false;
                this.$toast.success('Đã đặt lại mật khẩu thành công.');
            } catch (e) {
                this.$toast.error('Lỗi khi reset mật khẩu.');
            }
        },
        async confirmDeleteUser() {
            this.showDeleteUserConfirm = true;
        },
        async handleDeleteUser() {
            this.showDeleteUserConfirm = false;
            try {
                await axios.delete(`${API_BASE}/users/${this.selectedUser.id}/`);
                this.users = this.users.filter(u => u.id !== this.selectedUser.id);
                this.selectedUser = null;
                this.$toast.success('Đã xóa tài khoản.');
            } catch (e) {
                this.$toast.error('Lỗi khi xóa.');
            }
        },

        // Group Methods
        selectGroup(g) {
            this.selectedGroup = JSON.parse(JSON.stringify(g));
        },
        async createNewGroup() {
            this.showCreateGroupInput = true;
        },
        async handleCreateGroup(name) {
            this.showCreateGroupInput = false;
            if (!name) return;
            try {
                const res = await axios.post(`${API_BASE}/user-groups/`, { name, permissions: [] });
                this.groups.push(res.data);
                this.$toast.success('Đã tạo nhóm mới.');
            } catch (e) {
                this.$toast.error('Lỗi khi tạo nhóm.');
            }
        },
        async saveGroup() {
            this.isSaving = true;
            try {
                const res = await axios.put(`${API_BASE}/user-groups/${this.selectedGroup.id}/`, this.selectedGroup);
                const idx = this.groups.findIndex(g => g.id === res.data.id);
                if (idx !== -1) this.groups[idx] = res.data;
                this.$toast.success('Đã lưu cấu hình nhóm.');
            } catch (e) {
                this.$toast.error('Lỗi khi lưu.');
            } finally {
                this.isSaving = false;
            }
        },
        async confirmDeleteGroup() {
            this.showDeleteGroupConfirm = true;
        },
        async handleDeleteGroup() {
            this.showDeleteGroupConfirm = false;
            try {
                await axios.delete(`${API_BASE}/user-groups/${this.selectedGroup.id}/`);
                this.groups = this.groups.filter(g => g.id !== this.selectedGroup.id);
                this.selectedGroup = null;
                this.$toast.success('Đã xóa nhóm.');
            } catch (e) {
                this.$toast.error('Lỗi khi xóa nhóm.');
            }
        },

        // UI Helpers
        formatTime(ts) {
            return new Date(ts).toLocaleString('vi-VN');
        },
        startResize(mode) {
            this.isResizing = true;
            this.resizeMode = mode;
            document.addEventListener('mousemove', this.doResize);
            document.addEventListener('mouseup', this.stopResize);
            document.body.style.cursor = 'col-resize';
        },
        doResize(e) {
            if (!this.isResizing) return;
            const ref = this.resizeMode === 'user' ? this.$refs.userSplitView : this.$refs.groupSplitView;
            const rect = ref.getBoundingClientRect();
            const offset = ((e.clientX - rect.left) / rect.width) * 100;
            if (offset > 20 && offset < 70) {
                if (this.resizeMode === 'user') this.userPaneWidth = offset;
                else this.groupPaneWidth = offset;
            }
        },
        stopResize() {
            this.isResizing = false;
            document.removeEventListener('mousemove', this.doResize);
            document.removeEventListener('mouseup', this.stopResize);
            document.body.style.cursor = '';
        }
    }
};
</script>

<style scoped>
* {
    box-sizing: border-box;
}

.access-mgmt {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 40px);
    background: #f8fafc;
    overflow: hidden;
}

/* Header & Tabs */
.mgmt-header {
    padding: 1rem 1.5rem;
    background: #fff;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.mgmt-header h2 {
    font-size: 1.25rem;
    color: #1e293b;
    margin: 0;
}

.mgmt-tabs {
    display: flex;
    gap: 4px;
    background: #f1f5f9;
    padding: 4px;
    border-radius: 8px;
}

.mgmt-tabs button {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    background: transparent;
    color: #64748b;
    font-weight: 500;
    transition: all 0.2s;
}

.mgmt-tabs button.active {
    background: #fff;
    color: #2563eb;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* Layout */
.split-view {
    display: flex;
    flex: 1;
    overflow: hidden;
}

.pane {
    display: flex;
    flex-direction: column;
    padding: 1.25rem;
    background: #fff;
    overflow: hidden;
    /* Quan trọng để con không làm giãn cha */
    min-height: 0;
}

.editor-container {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow: hidden;
    /* Quan trọng để editor-content và permission-manager không giãn nở */
    min-height: 0;
    /* Fix flexbox growth in some browsers */
}

.editor-content {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    max-width: 100%;
}

.pane-left {
    border-right: 1px solid #f1f5f9;
}

.scrollable {
    overflow-y: auto;
    flex: 1;
}

.divider {
    width: 4px;
    background: #f1f5f9;
    cursor: col-resize;
    transition: background 0.2s;
}

.divider:hover {
    background: #3b82f6;
}

.pane-header {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    margin-bottom: 1rem;
    position: sticky;
    top: 0;
    background: #fff;
    z-index: 10;
    padding-bottom: 10px;
    /*border-bottom: 1px solid #f1f5f9;*/
    flex-wrap: wrap;
    gap: 10px;
    flex-shrink: 0;
    /* Đảm bảo header không bị co lại */
}

.pane-header h3 {
    margin: 0;
    font-size: 1rem;
    white-space: nowrap;
}

.pane-header input.h3-input {
    font-size: 1.1rem;
    font-weight: bold;
    border: 1px solid transparent;
    padding: 4px 8px;
    border-radius: 4px;
    transition: all 0.2s;
    background: transparent;
    width: 100%;
    min-width: 150px;
}

.pane-header input.form-control {
    width: 100%;
    min-width: 300px;
}

.pane-header input.h3-input:hover,
.pane-header input.h3-input:focus {
    border-color: #cbd5e1;
    background: #fff;
    outline: none;
}

/* Tables */
.table-container {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    white-space: nowrap;
    /* Prevent wrapping in cells */
}

.data-table th {
    background: #f8fafc;
    padding: 10px 12px;
    font-size: 0.75rem;
    text-transform: uppercase;
    color: #64748b;
    border-bottom: 1px solid #e2e8f0;
}

.data-table td {
    padding: 12px;
    border-bottom: 1px solid #f1f5f9;
    font-size: 0.9rem;
}

.data-table tr:hover {
    background: #f8fafc;
    cursor: pointer;
}

.data-table tr.selected {
    background: #eff6ff;
    border-left: 3px solid #2563eb;
}

/* Badges - Migrated to admin.css */

/* Legend - Migrated to admin.css */

/* Effective Permissions - Migrated to admin.css */

/* Forms - Migrated to admin.css */

/* Groups & Permissions - Migrated to admin.css */

.permission-manager {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow: hidden;
    /* Ràng buộc để con cuộn được */
    border-top: 1px solid #f1f5f9;
    padding-top: 1rem;
    min-height: 0;
}

.perm-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    /*margin-bottom: 1rem;*/
    flex-wrap: wrap;
    gap: 10px;
    background: #fff;
    position: sticky;
    top: 0;
    z-index: 5;
    padding-bottom: 5px;
}

.perm-search {
    flex: 1;
    min-width: 200px;
}

.perm-list {
    flex: 1;
    border: 1px dashed #e2e8f0;
    padding: 1rem;
    border-radius: 8px;
    overflow-y: auto;
    /* Cuộn tại đây */
}

.perm-category {
    margin-bottom: 1.5rem;
}

.category-title {
    font-size: 0.8rem;
    font-weight: bold;
    color: #94a3b8;
    text-transform: uppercase;
    margin-bottom: 8px;
    background: #f8fafc;
    padding: 4px 8px;
    border-radius: 4px;
}

.perm-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 8px;
}

.perm-item {
    display: flex;
    gap: 10px;
    padding: 8px;
    border: 1px solid #f1f5f9;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
}

.perm-item:hover {
    border-color: #3b82f6;
    background: #f0f7ff;
}

.perm-item.checked {
    border-color: #2563eb;
    background: #eff6ff;
}

.perm-info {
    display: flex;
    flex-direction: column;
}

.p-name {
    font-size: 0.85rem;
    font-weight: 500;
}

.p-code {
    font-size: 0.7rem;
    color: #94a3b8;
}

/* Buttons */
.btn-primary {
    background: #2563eb;
    color: #fff;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
}

.btn-success {
    background: #10b981;
    color: #fff;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
}

.btn-warning {
    background: #f59e0b;
    color: #fff;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
}

.btn-danger {
    background: #ef4444;
    color: #fff;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
}

.btn-secondary {
    background: #f1f5f9;
    color: #475569;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
}

/* Modal */
.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
}

.modal-content {
    background: #fff;
    padding: 2rem;
    border-radius: 12px;
    width: 400px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 2rem;
}

.hint {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 8px;
}

.empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
}

.empty-state .icon {
    font-size: 4rem;
    opacity: 0.2;
    margin-bottom: 1rem;
}

/* Audit Log */
.audit-view {
    flex: 1;
}

.audit-table .time {
    color: #64748b;
    font-size: 0.8rem;
}

.tag {
    padding: 2px 6px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: bold;
}

.tag-LOGIN {
    background: #dcfce7;
    color: #166534;
}

.tag-CREATE {
    background: #dbeafe;
    color: #1e40af;
}

.tag-UPDATE {
    background: #fef3c7;
    color: #92400e;
}

.tag-DELETE {
    background: #fee2e2;
    color: #991b1b;
}

.admin-form-control {
    min-width: 30ch;
}
</style>
