<template>
    <div class="notification-panel" v-click-outside="close">
        <div class="bell-container" @click="toggle">
            <div class="bell-icon-wrapper">
                <SvgIcon name="bell" size="md" />
                <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
            </div>
        </div>

        <!-- Dropdown Panel -->
        <div v-if="isOpen" class="notification-dropdown glass-effect">
            <div class="dropdown-header">
                <h3>Thông báo</h3>
                <button v-if="unreadCount > 0" @click="markAllAsRead" class="btn-text">Đánh dấu tất cả đã đọc</button>
            </div>

            <div class="notification-list" ref="scrollContainer">
                <div v-if="notifications.length === 0" class="empty-state">
                    <SvgIcon name="info" size="lg" />
                    <p>Không có thông báo mới</p>
                </div>

                <div v-for="item in notifications" :key="item.id" class="notification-item"
                    :class="[item.type.toLowerCase(), { unread: !item.is_read }]" @click="handleItemClick(item)">
                    <div class="item-icon">
                        <SvgIcon :name="getIconName(item.type)" size="sm" />
                    </div>
                    <div class="item-content">
                        <div class="item-title">{{ item.title }}</div>
                        <div class="item-text">{{ truncate(item.content) }}</div>
                        <div class="item-time">{{ formatTime(item.created_at) }}</div>
                    </div>
                    <div v-if="!item.is_read" class="unread-dot"></div>
                </div>
            </div>

            <div class="dropdown-footer">
                <router-link to="/all-notifications" @click="close">Xem tất cả</router-link>
            </div>
        </div>
    </div>
</template>

<script>
import api from '@/services/api';
import SvgIcon from './SvgIcon.vue';

export default {
    name: 'NotificationPanel',
    components: { SvgIcon },
    directives: {
        'click-outside': {
            mounted(el, binding) {
                el.clickOutsideEvent = (event) => {
                    if (!(el === event.target || el.contains(event.target))) {
                        binding.value(event);
                    }
                };
                document.body.addEventListener('click', el.clickOutsideEvent);
            },
            unmounted(el) {
                document.body.removeEventListener('click', el.clickOutsideEvent);
            }
        }
    },
    data() {
        return {
            isOpen: false,
            notifications: [],
            unreadCount: 0,
            pollingInterval: null,
            lastFetchTime: 0
        };
    },
    mounted() {
        this.fetchUnreadCount();
        this.startPolling();
        // Re-fetch when tab becomes visible
        document.addEventListener('visibilitychange', this.handleVisibilityChange);
    },
    beforeUnmount() {
        this.stopPolling();
        document.removeEventListener('visibilitychange', this.handleVisibilityChange);
    },
    methods: {
        toggle() {
            this.isOpen = !this.isOpen;
            if (this.isOpen) {
                this.fetchNotifications();
            }
        },
        close() {
            this.isOpen = false;
        },
        async fetchUnreadCount() {
            try {
                const res = await api.get('/notifications/unread_count/');
                this.unreadCount = res.data.unread_count;
            } catch (err) {
                console.error('Failed to fetch unread count', err);
            }
        },
        async fetchNotifications() {
            try {
                const res = await api.get('/notifications/');
                this.notifications = res.data;
                this.lastFetchTime = Date.now();
            } catch (err) {
                console.error('Failed to fetch notifications', err);
            }
        },
        async handleItemClick(item) {
            if (!item.is_read) {
                try {
                    await api.post(`/notifications/${item.id}/mark_read/`);
                    item.is_read = true;
                    this.fetchUnreadCount();
                } catch (err) {
                    console.error('Failed to mark notification as read', err);
                }
            }
            // Optionally emit event or open modal
        },
        async markAllAsRead() {
            // In a real app, you might have a dedicated endpoint
            // For now, we'll mark all fetched unread items as read
            const unreadItems = this.notifications.filter(n => !n.is_read);
            for (const item of unreadItems) {
                await this.handleItemClick(item);
            }
        },
        getIconName(type) {
            switch (type) {
                case 'WARN': return 'alert';
                case 'DANGER': return 'alert';
                default: return 'info';
            }
        },
        formatTime(timestamp) {
            if (!timestamp) return '';
            const date = new Date(timestamp);
            return date.toLocaleString('vi-VN', {
                hour: '2-digit',
                minute: '2-digit',
                day: '2-digit',
                month: '2-digit'
            });
        },
        truncate(text, length = 100) {
            if (!text || text.length <= length) return text;
            return text.substring(0, length) + '...';
        },
        startPolling() {
            // Polling every 5 minutes (300,000 ms) as requested
            this.pollingInterval = setInterval(() => {
                this.fetchUnreadCount();
            }, 300000);
        },
        stopPolling() {
            if (this.pollingInterval) {
                clearInterval(this.pollingInterval);
            }
        },
        handleVisibilityChange() {
            if (document.visibilityState === 'visible') {
                // Only refresh if it's been more than 1 minute since last fetch
                if (Date.now() - this.lastFetchTime > 60000) {
                    this.fetchUnreadCount();
                    if (this.isOpen) this.fetchNotifications();
                }
            }
        }
    }
};
</script>

<style scoped>
.notification-panel {
    position: relative;
    display: inline-block;
}

.bell-container {
    cursor: pointer;
    padding: 8px;
    border-radius: 50%;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
}

.bell-container:hover {
    background: rgba(255, 255, 255, 0.15);
}

.bell-icon-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.badge {
    position: absolute;
    top: -6px;
    right: -8px;
    background: #ff4d4f;
    color: white;
    border-radius: 10px;
    padding: 2px 6px;
    font-size: 10px;
    font-weight: bold;
    border: 1.5px solid #0366d6;
    min-width: 16px;
    text-align: center;
}

.notification-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    width: 380px;
    max-height: 500px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    display: flex;
    flex-direction: column;
    margin-top: 10px;
    overflow: hidden;
    border: 1px solid rgba(0, 0, 0, 0.08);
}

.dropdown-header {
    padding: 15px 20px;
    border-bottom: 1px solid #f0f0f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.dropdown-header h3 {
    margin: 0;
    font-size: 1.1rem;
    color: #333;
}

.btn-text {
    background: none;
    border: none;
    color: #0366d6;
    font-size: 0.85rem;
    cursor: pointer;
    padding: 0;
}

.btn-text:hover {
    text-decoration: underline;
}

.notification-list {
    overflow-y: auto;
    max-height: 380px;
}

.notification-item {
    padding: 15px 20px;
    border-bottom: 1px solid #f8f8f8;
    display: flex;
    gap: 15px;
    cursor: pointer;
    transition: background 0.2s;
    position: relative;
}

.notification-item:hover {
    background: #f9f9f9;
}

.notification-item.unread {
    background: #f0f7ff;
}

.notification-item.unread:hover {
    background: #e6f1ff;
}

.item-icon {
    flex-shrink: 0;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.info .item-icon {
    background: #e6f7ff;
    color: #1890ff;
}

.warn .item-icon {
    background: #fff7e6;
    color: #faad14;
}

.danger .item-icon {
    background: #fff1f0;
    color: #ff4d4f;
}

.item-content {
    flex-grow: 1;
}

.item-title {
    text-align: left;
    font-weight: 600;
    font-size: 0.95rem;
    margin-bottom: 4px;
    color: #262626;
}

.item-text {
    text-align: left;
    font-size: 0.9rem;
    color: #595959;
    line-height: 1.4;
    margin-bottom: 6px;
}

.item-time {
    text-align: right;
    font-size: 0.8rem;
    color: #8c8c8c;
}

.unread-dot {
    width: 8px;
    height: 8px;
    background: #1890ff;
    border-radius: 50%;
    position: absolute;
    top: 15px;
    right: 15px;
}

.empty-state {
    padding: 40px 20px;
    text-align: center;
    color: #bfbfbf;
}

.empty-state p {
    margin-top: 10px;
    font-size: 0.9rem;
}

.dropdown-footer {
    padding: 10px;
    text-align: center;
    border-top: 1px solid #f0f0f0;
    background: #fafafa;
}

.dropdown-footer a {
    color: #595959;
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 500;
}

.dropdown-footer a:hover {
    color: #0366d6;
}

.glass-effect {
    backdrop-filter: blur(10px);
    background: rgba(255, 255, 255, 0.95);
}
</style>
