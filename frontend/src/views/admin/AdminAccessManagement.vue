<template>
    <div class="admin-page">
        <div class="mgmt-header">
            <div class="header-left">
                <h2>🛡️ Quản lý Truy cập & Hệ thống</h2>
            </div>
            <div class="admin-tabs">
                <button :class="{ active: activeMainTab === 'users' }" class="admin-tab-item"
                    @click="activeMainTab = 'users'">👥 Người dùng</button>
                <button :class="{ active: activeMainTab === 'groups' }" class="admin-tab-item"
                    @click="activeMainTab = 'groups'">🔑 Nhóm & Quyền</button>
            </div>
            <div class="admin-role-legend">
                <span class="admin-legend-item" title="Toàn quyền hệ thống, bỏ qua RBAC"><span
                        class="admin-badge badge-superuser">ROOT</span> Siêu Quản Trị</span>
                <span class="admin-legend-item" title="Có quyền truy cập Dashboard Admin, quyền hạn theo Nhóm"><span
                        class="admin-badge badge-admin">Admin</span> Quản trị</span>
                <span class="admin-legend-item" title="Người dùng nghiệp vụ, chỉ có quyền theo Nhóm"><span
                        class="admin-badge badge-user">User</span> Nghiệp vụ</span>
            </div>
        </div>

        <!-- TAB 1: NGƯỜI DÙNG -->
        <div v-if="activeMainTab === 'users'" class="admin-split-view" ref="userSplitView">
            <!-- LEFT: USER LIST -->
            <div class="admin-pane admin-pane-left" :style="{ width: userPaneWidth + '%' }">
                <div class="admin-pane-header admin-row">
                    <div class="search-box flex-1">
                        <input type="text" v-model="userSearch" placeholder="Tìm kiếm user..."
                            class="admin-form-control" />
                    </div>
                    <button @click="createNewUser" class="btn-action btn-create btn-icon-only"
                        title="Thêm Người dùng mới">
                        <SvgIcon name="plus" size="sm" />
                    </button>
                </div>

                <div class="data-table-vxe">
                    <vxe-table border round :data="filteredUsers" @cell-click="({ row }) => selectUser(row)"
                        :row-config="{ isHover: true, isCurrent: true }" :column-config="{ resizable: true }"
                        :sort-config="{ trigger: 'cell' }" height="auto" class="user-table">

                        <vxe-column field="username" title="Tài khoản" min-width="120" sortable>
                            <template #default="{ row }">
                                <strong>{{ row.username }}</strong>
                            </template>
                        </vxe-column>

                        <vxe-column field="full_name" title="Họ tên" min-width="150" sortable>
                            <template #default="{ row }">
                                {{ row.full_name }}
                            </template>
                        </vxe-column>

                        <vxe-column field="email" title="Email" min-width="150" sortable></vxe-column>

                        <vxe-column field="is_staff" title="Quyền" width="120" sortable>
                            <template #default="{ row }">
                                <span v-if="row.is_superuser" class="admin-badge badge-superuser">ROOT</span>
                                <span v-else-if="row.is_staff" class="admin-badge badge-warning">Quản trị</span>
                                <span v-else class="admin-badge badge-inactive">Người dùng</span>
                            </template>
                        </vxe-column>

                        <vxe-column field="is_active" title="Trạng thái" width="120" sortable>
                            <template #default="{ row }">
                                <span :class="row.is_active ? 'text-green' : 'text-red'">
                                    {{ row.is_active ? '● Hoạt động' : '○ Đang khóa' }}
                                </span>
                            </template>
                        </vxe-column>

                        <vxe-column title="Hành động" width="120" fixed="right">
                            <template #default="{ row }">
                                <button class="btn-action btn-edit btn-icon-only" @click.stop="editUser(row)"
                                    :disabled="!authStore.hasPermission('auth.change_user')"
                                    :title="authStore.hasPermission('auth.change_user') ? 'Sửa thông tin & Quyền' : 'Không có quyền sửa user'">
                                    <SvgIcon name="edit" size="sm" />
                                </button>
                            </template>
                        </vxe-column>
                    </vxe-table>
                </div>
            </div>

            <div class="divider" @mousedown="startResize('user')"></div>

            <!-- RIGHT: USER EDITOR -->
            <div class="admin-pane" :style="{ width: (100 - userPaneWidth) + '%' }">
                <div v-if="selectedUser" class="editor-container">
                    <div class="admin-pane-header admin-row">
                        <h3 class="flex-1">{{ isCreating ? 'Tạo người dùng mới' : `Chi tiết: ${selectedUser.username}`
                        }}</h3>
                        <div class="actions">
                            <span v-if="selectedUser.is_superuser" class="superuser-warning">
                                🛡️ Tài khoản Hệ thống (Bypass mọi quyền)
                            </span>
                            <button v-if="isCreating" @click="handleCreateUser" class="btn-action btn-create"
                                :disabled="isSaving">
                                <SvgIcon name="check" size="sm" /> Tạo người dùng
                            </button>
                            <button v-else @click="saveUser" class="btn-action btn-save flex items-center gap-2"
                                :disabled="isSaving || (selectedUser.is_superuser && !authStore.isSuperuser)"
                                title="Lưu thay đổi">
                                <SvgIcon name="save" size="sm" /> <span>Lưu thay đổi</span>
                            </button>
                            <button v-if="isCreating" @click="cancelCreate"
                                class="btn-action btn-secondary ml-2 btn-icon-only" title="Hủy bỏ">
                                <SvgIcon name="x" size="sm" />
                            </button>
                        </div>
                    </div>

                    <div class="editor-content scrollable">
                        <div class="admin-form-grid">
                            <section class="admin-form-section">
                                <h4>Thông tin Tài khoản</h4>
                                <div class="admin-field">
                                    <label>Username (*)</label>
                                    <input type="text" v-model="selectedUser.username" class="admin-form-control"
                                        :disabled="!isCreating"
                                        :title="isCreating ? 'Nhập tên đăng nhập duy nhất' : 'Username là định danh duy nhất và không thể thay đổi.'" />
                                </div>
                                <div class="admin-field" v-if="isCreating">
                                    <label>Mật khẩu (*)</label>
                                    <input type="password" v-model="selectedUser.password" class="admin-form-control"
                                        placeholder="Nhập mật khẩu cho user mới" />
                                </div>
                                <div class="admin-field">
                                    <label>Email</label>
                                    <input type="email" v-model="selectedUser.email" class="admin-form-control" />
                                </div>
                                <div class="field-row">
                                    <label class="admin-checkbox-label">
                                        <input type="checkbox" v-model="selectedUser.is_active" /> Hoạt động
                                    </label>
                                    <label v-if="authStore.isSuperuser" class="admin-checkbox-label"
                                        :class="{ disabled: selectedUser.is_superuser }"
                                        :title="selectedUser.is_superuser ? 'ROOT tự động có quyền quản trị' : 'Cho phép user này vào trang Admin và thao tác theo quyền nhóm'">
                                        <input type="checkbox" v-model="selectedUser.is_staff"
                                            :disabled="selectedUser.is_superuser" /> Quyền quản trị
                                    </label>
                                    <label v-if="authStore.isSuperuser" class="admin-checkbox-label">
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
                                    <label>Nơi công tác</label>
                                    <input type="text" v-model="selectedUser.workplace" class="admin-form-control" />
                                </div>
                                <div class="admin-field">
                                    <label>Phòng ban</label>
                                    <input type="text" v-model="selectedUser.department" class="admin-form-control" />
                                </div>
                            </section>

                            <!-- DYNAMIC FIELDS FOR USER_EXT - CÁC THÔNG TIN MỞ RỘNG CỦA USER HIỂN THỊ TẠI ĐÂY -->
                            <section v-if="hasDynamicFields" class="admin-form-section">
                                <div class="dynamic-editor-wrapper">
                                    <div v-if="loadingDynamic" class="loading-small">Đang tải cấu hình...</div>
                                    <DynamicForm v-else :groups="dynamicGroups"
                                        :initial-values="selectedUser.field_values || {}" mode="horizontal"
                                        @update:values="val => selectedUser.field_values = val" />
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
                                <button @click="confirmResetPassword" class="btn-action btn-warning"
                                    :disabled="(selectedUser.is_superuser && !authStore.isSuperuser) || !authStore.hasPermission('auth.change_user')"
                                    :title="!authStore.hasPermission('auth.change_user') ? 'Không có quyền' : 'Reset mật khẩu'">
                                    <SvgIcon name="refresh" size="sm" /> Reset mật khẩu
                                </button>
                                <button @click="confirmDeleteUser" class="btn-action btn-delete"
                                    :disabled="selectedUser.is_superuser && !authStore.isSuperuser">
                                    <SvgIcon name="trash" size="sm" /> Xóa tài khoản
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

        <!-- TAB 2: NHÓM (GROUPS) -->
        <div v-if="activeMainTab === 'groups'" class="admin-split-view" ref="groupSplitView">
            <!-- LEFT: GROUP LIST -->
            <div class="admin-pane admin-pane-left" :style="{ width: groupPaneWidth + '%' }">
                <div class="admin-pane-header admin-row">
                    <div class="flex-1 mr-4">
                        <input type="text" v-model="groupSearch" placeholder="Tìm kiếm nhóm..."
                            class="admin-input w-full" />
                    </div>
                    <button @click="createNewGroup" class="btn-action btn-create btn-icon-only" title="Tạo Nhóm mới">
                        <SvgIcon name="plus" size="sm" />
                    </button>
                </div>
                <div class="data-table-vxe">
                    <vxe-table border round :data="filteredGroups" @cell-click="({ row }) => selectGroup(row)"
                        :row-config="{ isHover: true, isCurrent: true }" :column-config="{ resizable: true }"
                        :sort-config="{ trigger: 'cell' }" height="auto" class="group-table">

                        <vxe-column field="name" title="Tên nhóm" min-width="150" sortable></vxe-column>


                        <vxe-column title="Hành động" width="120" fixed="right">
                            <template #default="{ row }">
                                <button class="btn-action btn-edit btn-icon-only" @click.stop="selectGroup(row)"
                                    title="Sửa nhóm">
                                    <SvgIcon name="edit" size="sm" />
                                </button>
                            </template>
                        </vxe-column>
                    </vxe-table>
                </div>
            </div>

            <div class="divider" @mousedown="startResize('group')"></div>

            <!-- RIGHT: GROUP EDITOR -->
            <div class="admin-pane" :style="{ width: (100 - groupPaneWidth) + '%' }">
                <div v-if="selectedGroup" class="editor-container">
                    <div class="admin-pane-header admin-row">
                        <input type="text" v-model="selectedGroup.name" class="admin-form-control h3-input flex-1"
                            placeholder="Tên nhóm..." />
                        <div class="actions flex items-center gap-2">
                            <button @click="saveGroup" class="btn-action btn-success flex items-center gap-2"
                                :disabled="isSaving" title="Lưu cấu hình Nhóm">
                                <SvgIcon name="save" size="sm" /> <span>Lưu Nhóm</span>
                            </button>
                            <button @click="confirmDeleteGroup" class="btn-action btn-danger btn-icon-only"
                                title="Xóa nhóm">
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

        <!-- TAB 3: CÀI ĐẶT HỆ THỐNG - MOVED TO SIDEBAR -->

        <!-- MODAL RESET PASSWORD -->
        <div v-if="showResetModal" class="modal-overlay">
            <div class="modal-content">
                <h3>Reset Mật khẩu cho {{ selectedUser.username }}</h3>
                <div class="admin-field">
                    <label>Mật khẩu mới</label>
                    <input type="text" v-model="newPassword" class="admin-form-control" />
                    <p class="hint">Vui lòng cung cấp mật khẩu này cho nhân viên.</p>
                </div>
                <div class="modal-footer">
                    <button @click="showResetModal = false" class="btn-action btn-secondary">Hủy</button>
                    <button @click="executeResetPassword" class="btn-action btn-warning">Xác nhận Reset</button>
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

    </div>
</template>

<script>
import SystemService from '@/services/system.service';
import MasterService from '@/services/master.service';
import { useAuthStore } from '@/store/auth.store';
import { errorHandlingMixin } from '@/utils/errorHandler';
import ConfirmModal from '@/components/ConfirmModal.vue';
import InputModal from '@/components/InputModal.vue';
import DynamicForm from '@/components/DynamicForm.vue';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';
import SvgIcon from '@/components/common/SvgIcon.vue';

export default {
    name: 'AdminAccessManagement',
    title: 'Quản trị Người dùng',
    components: { SvgIcon, ConfirmModal, InputModal, DynamicForm },
    mixins: [errorHandlingMixin, FilterableTableMixin],
    data() {
        return {
            activeMainTab: 'users',
            userPaneWidth: 35,
            groupPaneWidth: 35,

            // Data
            users: [],
            groups: [],
            permissions: [],

            // Selection
            selectedUser: null,
            selectedGroup: null,

            // Search
            userSearch: '',
            groupSearch: '',
            permSearch: '',

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
            isCreating: false,

            // USER_EXT data
            loadingDynamic: false,
            dynamicGroups: {},

            authStore: useAuthStore() // Pinia store
        };
    },
    computed: {
        filteredUsers() {
            return this.filterArray(this.users, { search: this.userSearch }, {
                search: { type: 'text', fields: ['username', 'full_name', 'email'] }
            });
        },
        filteredGroups() {
            return this.filterArray(this.groups, { search: this.groupSearch }, {
                search: { type: 'text', fields: ['name'] }
            });
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
        hasDynamicFields() {
            return Object.keys(this.dynamicGroups).length > 0;
        }
    },
    async created() {
        await this.loadAllData();
        await this.fetchDynamicConfig();
    },
    methods: {
        async loadAllData() {
            try {
                const [uRes, gRes, pRes] = await Promise.all([
                    SystemService.getUsers(),
                    SystemService.getUserGroups(),
                    SystemService.getUserPermissions()
                ]);
                this.users = uRes.data;
                this.groups = gRes.data;
                this.permissions = pRes.data;
            } catch (e) {
                this.showError(e, 'Lỗi tải dữ liệu hệ thống');
            }
        },

        async fetchDynamicConfig() {
            this.loadingDynamic = true;
            try {
                const res = await MasterService.getActiveFieldsGrouped('USER_EXT');
                this.dynamicGroups = res.data;
            } catch (e) {
                console.error('Lỗi tải cấu hình trường động:', e);
            } finally {
                this.loadingDynamic = false;
            }
        },

        // User Methods
        selectUser(u) {
            this.isCreating = false;
            this.selectedUser = JSON.parse(JSON.stringify(u));
        },
        editUser(u) {
            this.selectUser(u);
        },
        createNewUser() {
            this.isCreating = true;
            this.selectedUser = {
                username: '',
                password: '',
                email: '',
                is_active: true,
                is_staff: false,
                is_superuser: false,
                full_name: '',
                phone: '',
                workplace: '',
                department: '',
                note: '',
                groups: [],
                permissions: [],
                field_values: {}
            };
        },
        cancelCreate() {
            this.isCreating = false;
            this.selectedUser = null;
        },
        async handleCreateUser() {
            if (!this.selectedUser.username || !this.selectedUser.password) {
                this.$toast.warning('Vui lòng nhập Username và Mật khẩu!');
                return;
            }
            this.isSaving = true;
            try {
                const res = await SystemService.createUser(this.selectedUser);
                this.users.unshift(res.data);
                this.isCreating = false;
                this.selectedUser = JSON.parse(JSON.stringify(res.data));
                this.$toast.success(`Đã tạo người dùng '${res.data.username}' thành công!`);
            } catch (e) {
                this.showError(e, 'Lỗi khi tạo người dùng');
            } finally {
                this.isSaving = false;
            }
        },
        async saveUser() {
            this.isSaving = true;
            try {
                const res = await SystemService.updateUser(this.selectedUser.id, this.selectedUser);
                const idx = this.users.findIndex(u => u.id === res.data.id);
                if (idx !== -1) {
                    this.users.splice(idx, 1, res.data);
                }
                this.selectedUser = JSON.parse(JSON.stringify(res.data));
                this.$toast.success(`Cập nhật người dùng '${res.data.username}' thành công!`);
            } catch (e) {
                this.showError(e, 'Lỗi khi lưu người dùng');
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
                await SystemService.resetPassword(this.selectedUser.id, this.newPassword);
                this.showResetModal = false;
                this.$toast.success(`Đã đặt lại mật khẩu cho '${this.selectedUser.username}' thành công.`);
            } catch (e) {
                this.showResetModal = false;
                this.showError(e, 'Lỗi khi reset mật khẩu');
            }
        },
        async confirmDeleteUser() {
            this.showDeleteUserConfirm = true;
        },
        async handleDeleteUser() {
            this.showDeleteUserConfirm = false;
            try {
                await SystemService.deleteUser(this.selectedUser.id);
                const deletedName = this.selectedUser.username;
                this.users = this.users.filter(u => u.id !== this.selectedUser.id);
                this.selectedUser = null;
                this.$toast.success(`Đã xóa tài khoản '${deletedName}' thành công.`);
            } catch (e) {
                this.showError(e, 'Lỗi khi xóa tài khoản');
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
                const res = await SystemService.createUserGroup({ name, permissions: [] });
                this.groups.push(res.data);
                this.$toast.success(`Đã tạo nhóm '${name}' thành công.`);
            } catch (e) {
                this.showError(e, 'Lỗi khi tạo nhóm');
            }
        },
        async saveGroup() {
            this.isSaving = true;
            try {
                const res = await SystemService.updateUserGroup(this.selectedGroup.id, this.selectedGroup);
                const idx = this.groups.findIndex(g => g.id === res.data.id);
                if (idx !== -1) this.groups[idx] = res.data;
                this.$toast.success(`Đã lưu cấu hình nhóm '${res.data.name}'.`);
            } catch (e) {
                this.showError(e, 'Lỗi khi lưu cấu hình');
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
                await SystemService.deleteUserGroup(this.selectedGroup.id);
                const deletedName = this.selectedGroup.name;
                this.groups = this.groups.filter(g => g.id !== this.selectedGroup.id);
                this.selectedGroup = null;
                this.$toast.success(`Đã xóa nhóm '${deletedName}' thành công.`);
            } catch (e) {
                this.showError(e, 'Lỗi khi xóa nhóm');
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
        },
    }
};
</script>

<style scoped>
* {
    box-sizing: border-box;
}

.admin-page {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 64px - 40px);
    /* 64px Navbar + 40px Padding (Top+Bottom) of layout-main */
    background: #f8fafc;
    overflow: hidden;
    padding: 0 !important;
}

/* Custom Header specific to Access Mgmt */
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

.admin-tabs {
    background: #f1f5f9;
    padding: 4px;
    border-radius: 8px;
}

/* Pane & Split View Overrides (if any specific ones needed) */
.editor-container {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow: hidden;
    min-height: 0;
}

.editor-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--spacing-lg);
    max-width: 100%;
}

.divider {
    width: 4px;
    background: var(--slate-100);
    cursor: col-resize;
    transition: background 0.2s;
}

.divider:hover {
    background: var(--color-primary);
}

.pane-header h3 {
    margin: 0;
    font-size: var(--font-md);
    white-space: nowrap;
}

.pane-header input.h3-input {
    font-size: var(--font-lg);
    font-weight: bold;
    border: 1px solid var(--slate-200);
    padding: 6px 12px;
    border-radius: var(--radius-md);
    transition: all 0.2s;
    background: var(--slate-50);
    max-width: 400px;
}

.pane-header input.h3-input:hover,
.pane-header input.h3-input:focus {
    border-color: var(--slate-200);
    background: white;
    outline: none;
}

.data-table-vxe {
    margin-top: var(--spacing-sm);
    height: calc(100% - 60px);
}

/* Permission Manager */
.permission-manager {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow: hidden;
    border-top: 1px solid var(--slate-100);
    padding-top: var(--spacing-lg);
    min-height: 0;
}

.perm-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: var(--spacing-md);
    background: white;
    position: sticky;
    top: 0;
    z-index: 5;
    padding-bottom: var(--spacing-xs);
}

.perm-search {
    flex: 1;
    min-width: 200px;
}

.perm-list {
    flex: 1;
    border: 1px dashed var(--slate-200);
    padding: var(--spacing-lg);
    border-radius: var(--radius-md);
    overflow-y: auto;
}

.perm-category {
    margin-bottom: var(--spacing-xl);
}

.category-title {
    font-size: var(--font-xs);
    font-weight: bold;
    color: var(--slate-400);
    text-transform: uppercase;
    margin-bottom: 8px;
    background: var(--slate-50);
    padding: 4px 8px;
    border-radius: var(--radius-sm);
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
    border: 1px solid var(--slate-50);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all 0.2s;
}

.perm-item:hover {
    border-color: var(--color-primary);
    background: var(--color-info-light);
}

.perm-item.checked {
    border-color: var(--color-primary);
    background: var(--color-info-light);
}

.perm-info {
    display: flex;
    flex-direction: column;
}

.p-name {
    font-size: var(--font-sm);
    font-weight: 500;
}

.p-code {
    font-size: var(--font-xs);
    color: var(--slate-400);
}

.hint {
    font-size: var(--font-xs);
    color: var(--slate-500);
    margin-top: 8px;
}

.empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--slate-300);
}

.empty-state .icon {
    font-size: 4rem;
    opacity: 0.2;
    margin-bottom: var(--spacing-lg);
}

/* Audit Log specifics */
.audit-view {
    flex: 1;
}

.audit-table .time {
    color: var(--slate-500);
    font-size: var(--font-xs);
}
</style>
