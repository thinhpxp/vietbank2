<template>
    <div class="admin-page page-container">
        <div class="page-header">
            <div class="header-title">
                <SvgIcon name="bell" size="lg" />
                <h2>Quản lý Thông báo</h2>
            </div>
            <button v-if="canCreate" @click="openCreateModal" class="btn-action btn-create btn-icon-only"
                title="Tạo Thông báo mới">
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
                        <span class="status-badge" :class="getTypeBadgeClass(row.type)">
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
                <vxe-column v-if="canEdit || canDelete" title="Hành động" width="120" fixed="right" align="center">
                    <template #default="{ row }">
                        <div class="flex gap-2 justify-center">
                            <button v-if="canEdit" @click="editNotification(row)"
                                class="btn-action btn-edit btn-icon-only" title="Sửa">
                                <SvgIcon name="edit" size="sm" />
                            </button>
                            <button v-if="canDelete" @click="deleteNotification(row)"
                                class="btn-action btn-delete btn-icon-only" title="Xóa">
                                <SvgIcon name="trash" size="sm" />
                            </button>
                        </div>
                    </template>
                </vxe-column>
            </vxe-table>
        </div>

        <NotificationEditModal v-if="showModal" :visible="showModal" :item="editingItem" @close="showModal = false"
            @saved="fetchNotifications" />
    </div>
</template>

<script>
import axios from 'axios';
import SvgIcon from '@/components/common/SvgIcon.vue';
import NotificationEditModal from './NotificationEditModal.vue';
import { API_URL } from '@/store/auth';
import auth from '@/store/auth';

export default {
    name: 'AdminNotifications',
    components: { SvgIcon, NotificationEditModal },
    data() {
        return {
            notifications: [],
            loading: false,
            showModal: false,
            editingItem: null
        };
    },
    computed: {
        canCreate() { return auth.hasPermission('document_automation.add_adminnotification'); },
        canEdit() { return auth.hasPermission('document_automation.change_adminnotification'); },
        canDelete() { return auth.hasPermission('document_automation.delete_adminnotification'); }
    },
    mounted() {
        if (!auth.hasPermission('document_automation.view_adminnotification')) {
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
                const res = await axios.get(`${API_URL}/notifications/`);
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
            if (type === 'DANGER') return 'badge-danger';
            if (type === 'WARN') return 'badge-warning';
            return 'badge-info';
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
                await axios.patch(`${API_URL}/notifications/${row.id}/`, { is_active: row.is_active });
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
            if (confirm('Bạn có chắc chắn muốn xóa thông báo này?')) {
                try {
                    await axios.delete(`${API_URL}/notifications/${row.id}/`);
                    this.$toast.success('Đã xóa thông báo');
                    this.fetchNotifications();
                } catch (err) {
                    this.$toast.error('Lỗi khi xóa thông báo');
                }
            }
        }
    }
};
</script>

<style scoped>
.data-table-vxe {
    margin-top: 10px;
}

.badge-info {
    background: #e0f2fe;
    color: #0369a1;
    border-color: #7dd3fc;
}

.badge-warning {
    background: #fffbeb;
    color: #92400e;
    border-color: #fcd34d;
}

.badge-danger {
    background: #fef2f2;
    color: #991b1b;
    border-color: #fecaca;
}
</style>
