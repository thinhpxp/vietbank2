import api from './api';

const UserService = {
    /**
     * Lấy thông tin cá nhân của người dùng hiện tại
     * (Bao gồm các trường profile cơ bản và field_values mở rộng)
     */
    getProfile() {
        return api.get('/me/');
    },

    /**
     * Cập nhật thông tin cá nhân
     */
    updateProfile(data) {
        return api.patch('/me/', data);
    },

    /**
     * Đăng ký tài khoản mới
     * (Bao gồm thông tin cơ bản và field_values mở rộng)
     */
    register(data) {
        return api.post('/register/', data);
    },

    /**
     * Đổi mật khẩu
     */
    changePassword(data) {
        return api.post('/change-password/', data);
    }
};

export default UserService;
