<template>
    <div class="admin-page">
        <div class="page-header">
            <div class="header-title">
                <SvgIcon name="bell" size="lg" />
                <h2>Quản lý Thông báo</h2>
            </div>
            <button @click="openCreateModal" class="btn-action btn-create btn-icon-only" :disabled="!canCreate"
                :title="canCreate ? 'Tạo Thông báo mới' : 'Bạn không có quyền tạo'">
                <SvgIcon name="plus" size="sm" />
            </button>
        </div>

        <div class="data-table-vxe">
            <vxe-table border round auto-resize :data="notifications" :loading="loading"
                :column-config="{ resizable: true }"
                :sort-config="{ remote: false, defaultSort: { field: 'created_at', order: 'desc' } }">
                <vxe-column field="title" title="Tiêu đề" width="250"></vxe-column>
                <vxe-column field="type" title="Loại" width="120">
                    <template #default="{ row }">
                        <span :class="getTypeBadgeClass(row.type)">
                            {{ getTypeLabel(row.type) }}
                        </span>
                    </template>
                </vxe-column>
                <vxe-column field="is_active" title="Trạng thái" width="120" align="center">
                    <template #default="{ row }">
                        <vxe-switch v-model="row.is_active" open-label="Bật" close-label="Tắt" :disabled="!canEdit"
                            @change="toggleStatus(row)"></vxe-switch>
                    </template>
                </vxe-column>
                <vxe-column field="created_at" title="Ngày tạo" width="160" sortable>
                    <template #default="{ row }">
                        {{ formatDateTime(row.created_at) }}
                    </template>
                </vxe-column>
                <vxe-column field="expires_at" title="Hết hạn" width="160">
                    <template #default="{ row }">
                        {{ formatDateTime(row.expires_at) || 'Không giới hạn' }}
                    </template>
                </vxe-column>
                <vxe-column title="Hành động" width="120" fixed="right" align="center">
                    <template #default="{ row }">
                        <div class="flex gap-2 justify-center">
                            <button @click="editNotification(row)" class="btn-action btn-edit btn-icon-only"
                                :disabled="!canEdit" :title="canEdit ? 'Sửa' : 'Không có quyền sửa'">
                                <SvgIcon name="edit" size="sm" />
                            </button>
                            <button @click="deleteNotification(row)" class="btn-action btn-delete btn-icon-only"
                                :disabled="!canDelete" :title="canDelete ? 'Xóa' : 'Không có quyền xóa'">
                                <SvgIcon name="trash" size="sm" />
                            </button>
                        </div>
                    </template>
                </vxe-column>
            </vxe-table>
        </div>

        <NotificationEditModal v-if="showModal" :visible="showModal" :item="editingItem" @close="showModal = false"
            @saved="fetchNotifications" />

        <!-- Confirm Modal Xóa Thông báo -->
        <ConfirmModal
            :visible="showDeleteConfirm"
            title="Xóa Thông báo"
            message="Bạn có chắc chắn muốn xóa thông báo này? Hành động này không thể hoàn tác."
            confirmText="Xóa"
            type="error"
            mode="confirm"
            @confirm="handleDeleteConfirmed"
            @cancel="showDeleteConfirm = false"
        />
    </div>
</template>

<script>
import SystemService from '@/services/system.service';
import SvgIcon from '@/components/common/SvgIcon.vue';
import NotificationEditModal from './NotificationEditModal.vue';
import ConfirmModal from '@/components/ConfirmModal.vue';
import { useAuthStore } from '@/store/auth.store';

export default {
    name: 'AdminNotifications',
    title: 'Quản lý Thông báo Admin',
    components: { SvgIcon, NotificationEditModal, ConfirmModal },
    data() {
        return {
            notifications: [],
            loading: false,
            showModal: false,
            editingItem: null,
            showDeleteConfirm: false,
            pendingDeleteRow: null,
            authStore: useAuthStore()
        };
    },
    computed: {
        canCreate() { return this.authStore.hasPermission('document_automation.add_adminnotification'); },
        canEdit() { return this.authStore.hasPermission('document_automation.change_adminnotification'); },
        canDelete() { return this.authStore.hasPermission('document_automation.delete_adminnotification'); }
    },
    mounted() {
        if (!this.authStore.hasPermission('document_automation.view_adminnotification')) {
            this.$toast.error('Bạn không có quyền truy cập trang này');
            this.$router.push('/');
            return;
        }
        this.fetchNotifications();
    },
    methods: {
        async fetchNotifications() {
            this.loading = true;
            try {
                const res = await SystemService.getAdminNotifications();
                this.notifications = res.data;
            } catch (err) {
                this.$toast.error('Không thể tải danh sách thông báo');
            } finally {
                this.loading = false;
            }
        },
        getTypeLabel(type) {
            const labels = { 'INFO': 'Thông tin', 'WARN': 'Cảnh báo', 'DANGER': 'Khẩn cấp' };
            return labels[type] || type;
        },
        getTypeBadgeClass(type) {
            if (type === 'DANGER') return 'admin-badge badge-danger';
            if (type === 'WARN') return 'admin-badge badge-warning';
            return 'admin-badge badge-info';
        },
        formatDateTime(val) {
            if (!val) return '';
            return new Date(val).toLocaleString('vi-VN');
        },
        openCreateModal() {
            this.editingItem = null;
            this.showModal = true;
        },
        editNotification(row) {
            this.editingItem = { ...row };
            this.showModal = true;
        },
        async toggleStatus(row) {
            if (!this.canEdit) {
                this.$toast.error('Bạn không có quyền thay đổi trạng thái');
                row.is_active = !row.is_active;
                return;
            }
            try {
                await SystemService.updateAdminNotification(row.id, { is_active: row.is_active });
                this.$toast.success('Đã cập nhật trạng thái');
            } catch (err) {
                row.is_active = !row.is_active; // revert on error
                this.$toast.error('Lỗi khi cập nhật trạng thái');
            }
        },
        async deleteNotification(row) {
            if (!this.canDelete) {
                this.$toast.error('Bạn không có quyền xóa thông báo');
                return;
            }
            this.pendingDeleteRow = row;
            this.showDeleteConfirm = true;
        },
        async handleDeleteConfirmed() {
            this.showDeleteConfirm = false;
            if (!this.pendingDeleteRow) return;
            try {
                await SystemService.deleteAdminNotification(this.pendingDeleteRow.id);
                this.$toast.success('Đã xóa thông báo');
                this.fetchNotifications();
            } catch (err) {
                this.$toast.error('Lỗi khi xóa thông báo');
            } finally {
                this.pendingDeleteRow = null;
            }
        }
    }
};
</script>

<style scoped>
.data-table-vxe {
    margin-top: 10px;
}
</style>
