import api from './api';

const SystemService = {
    getConfig() {
        return api.get('/system-config/');
    },

    updateConfig(payload) {
        return api.post('/system-config/', payload);
    },

    uploadLogo(formData) {
        return api.post('/upload-logo/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },

    // Users
    getUsers() {
        return api.get('/users/');
    },
    createUser(data) {
        return api.post('/users/', data);
    },
    updateUser(id, data) {
        return api.patch(`/users/${id}/`, data);
    },
    deleteUser(id) {
        return api.delete(`/users/${id}/`);
    },
    resetPassword(id, password) {
        return api.post(`/users/${id}/reset-password/`, { password });
    },

    // User Groups (Django Groups) & Permissions
    getUserGroups() {
        return api.get('/user-groups/');
    },
    createUserGroup(data) {
        return api.post('/user-groups/', data);
    },
    updateUserGroup(id, data) {
        return api.put(`/user-groups/${id}/`, data);
    },
    deleteUserGroup(id) {
        return api.delete(`/user-groups/${id}/`);
    },

    getUserPermissions() {
        return api.get('/user-permissions/');
    },

    getAuditLogs(params = {}) {
        return api.get('/audit-logs/', { params });
    },

    getAuditLogsByUrl(url) {
        return api.get(url);
    },

    getAdminNotifications() {
        return api.get('/notifications/');
    },
    createAdminNotification(data) {
        return api.post('/notifications/', data);
    },
    updateAdminNotification(id, data) {
        return api.patch(`/notifications/${id}/`, data);
    },
    deleteAdminNotification(id) {
        return api.delete(`/notifications/${id}/`);
    },

    getNotifications() {
        return api.get('/notifications/');
    },

    getUnreadCount() {
        return api.get('/notifications/unread_count/');
    },

    getUnreadNotificationsCount() {
        return api.get('/notifications/unread_count/');
    },

    markNotificationRead(id) {
        return api.post(`/notifications/${id}/mark_read/`);
    },

    markAllNotificationsRead() {
        return api.post('/notifications/mark_all_read/');
    }
};

export default SystemService;
