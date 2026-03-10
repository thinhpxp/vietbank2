<template>
    <div class="all-notifications-page">
        <div class="page-header">
            <h1>Tất cả thông báo</h1>
            <p class="subtitle">Xem và quản lý lịch sử thông báo của bạn</p>
        </div>

        <div class="content-container glass-effect">
            <div class="table-actions">
                <button @click="markAllAsRead" class="btn-secondary" :disabled="!hasUnread">
                    <SvgIcon name="check" size="sm" /> Đánh dấu tất cả đã đọc
                </button>
            </div>

            <vxe-table border round auto-resize :data="notifications" :loading="loading" :row-class-name="getRowClass"
                @cell-click="handleCellClick"
                :sort-config="{ remote: false, defaultSort: { field: 'created_at', order: 'desc' } }">
                <vxe-column width="60" align="center">
                    <template #default="{ row }">
                        <div :class="['status-dot', { unread: !row.is_read }]"></div>
                    </template>
                </vxe-column>

                <vxe-column field="type" title="Loại" width="120">
                    <template #default="{ row }">
                        <span class="type-tag" :class="row.type.toLowerCase()">
                            {{ getTypeLabel(row.type) }}
                        </span>
                    </template>
                </vxe-column>

                <vxe-column field="title" title="Tiêu đề" min-width="200">
                    <template #default="{ row }">
                        <div class="cell-title">{{ row.title }}</div>
                    </template>
                </vxe-column>

                <vxe-column field="content" title="Nội dung" min-width="300">
                    <template #default="{ row }">
                        <div class="cell-content">{{ row.content }}</div>
                    </template>
                </vxe-column>

                <vxe-column field="created_at" title="Thời gian" width="180" sortable>
                    <template #default="{ row }">
                        {{ formatDateTime(row.created_at) }}
                    </template>
                </vxe-column>
            </vxe-table>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import { API_URL } from '@/store/auth';
import SvgIcon from '@/components/common/SvgIcon.vue';

export default {
    name: 'AllNotifications',
    title: 'Tất cả thông báo',
    components: { SvgIcon },
    data() {
        return {
            notifications: [],
            loading: false
        };
    },
    computed: {
        hasUnread() {
            return this.notifications.some(n => !n.is_read);
        }
    },
    mounted() {
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
        async handleCellClick({ row }) {
            if (!row.is_read) {
                try {
                    await axios.post(`${API_URL}/notifications/${row.id}/mark_read/`);
                    row.is_read = true;
                } catch (err) {
                    console.error('Failed to mark as read', err);
                }
            }
        },
        async markAllAsRead() {
            const unreadIds = this.notifications.filter(n => !n.is_read).map(n => n.id);
            if (unreadIds.length === 0) return;

            try {
                // Assuming we don't have a bulk mark-as-read endpoint yet, 
                // we'll loop or just let the user click items. 
                // For a better UX, we'd want a bulk endpoint.
                // For now, let's simulate by marking all locally after individual calls if possible,
                // or just mark all locally if no bulk API exists.
                for (const id of unreadIds) {
                    await axios.post(`${API_URL}/notifications/${id}/mark_read/`);
                }
                this.notifications.forEach(n => n.is_read = true);
                this.$toast.success('Đã đánh dấu tất cả là đã đọc');
            } catch (err) {
                this.$toast.error('Có lỗi xảy ra khi thực hiện');
            }
        },
        getTypeLabel(type) {
            const labels = { 'INFO': 'Thông tin', 'WARN': 'Cảnh báo', 'DANGER': 'Khẩn cấp' };
            return labels[type] || type;
        },
        formatDateTime(val) {
            if (!val) return '';
            return new Date(val).toLocaleString('vi-VN');
        },
        getRowClass({ row }) {
            return row.is_read ? '' : 'row-unread';
        }
    }
};
</script>

<style scoped>
.all-notifications-page {
    padding: 30px;
    max-width: 1200px;
    margin: 0 auto;
}

.page-header {
    margin-bottom: 30px;
}

.page-header h1 {
    font-size: 1.8rem;
    color: #2c3e50;
    margin-bottom: 8px;
}

.subtitle {
    color: #7f8c8d;
    font-size: 1.1rem;
}

.content-container {
    background: white;
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
}

.table-actions {
    margin-bottom: 20px;
    display: flex;
    justify-content: flex-end;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: transparent;
    margin: 0 auto;
}

.status-dot.unread {
    background: #0366d6;
    box-shadow: 0 0 8px rgba(3, 102, 214, 0.5);
}

.type-tag {
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
}

.info {
    background: #e3f2fd;
    color: #1976d2;
}

.warn {
    background: #fff3e0;
    color: #f57c00;
}

.danger {
    background: #ffebee;
    color: #d32f2f;
}

.cell-title {
    font-weight: 600;
    color: #2c3e50;
}

.cell-content {
    color: #5d6d7e;
    font-size: 0.95rem;
}

.row-unread {
    background-color: rgba(3, 102, 214, 0.03);
}

.btn-secondary {
    padding: 8px 16px;
    border-radius: 8px;
    border: 1px solid #dcdfe6;
    background: white;
    color: #606266;
    cursor: pointer;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.2s;
}

.btn-secondary:hover:not(:disabled) {
    color: #0366d6;
    border-color: #0366d6;
    background: rgba(3, 102, 214, 0.05);
}

.btn-secondary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.glass-effect {
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}
</style>
