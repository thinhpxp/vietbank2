/**
 * Error Handling Utility
 * Giúp xử lý và hiển thị lỗi một cách nhất quán với thông tin chi tiết
 */

/**
 * Format error object thành message string có cấu trúc
 * @param {Error|Object} error - Error object từ catch block
 * @returns {Object} - { message, errorCode, details }
 */
import { translate } from './i18n';
import eventBus, { EVENTS } from './eventBus';

/**
 * Format error object thành message string có cấu trúc
 * @param {Error|Object} error - Error object từ catch block
 * @returns {Object} - { message, errorCode, details }
 */
export function formatError(error) {
    let message = 'Đã xảy ra lỗi không xác định';
    let errorCode = '';
    let details = '';

    if (error.response) {
        // Lỗi từ API (Axios)
        const status = error.response.status;
        const data = error.response.data;

        // Message chính
        if (data && typeof data === 'object' && !data.message && !data.error) {
            // DRF field-specific errors: {"field": ["error message"]}
            const firstKey = Object.keys(data)[0];
            const firstError = data[firstKey];
            if (Array.isArray(firstError)) {
                message = firstError[0];
            } else if (typeof firstError === 'string') {
                message = firstError;
            } else {
                message = `Lỗi ${status}: ${error.response.statusText}`;
            }
        } else {
            message = data?.detail || data?.message || data?.error || `Lỗi ${status}: ${error.response.statusText}`;
        }

        // Tự động dịch message nếu có trong từ điển
        message = translate(message);

        // Error code
        errorCode = data?.code || `HTTP_${status}`;

        // Chi tiết kỹ thuật
        const detailsObj = {
            status: status,
            statusText: error.response.statusText,
            url: error.config?.url,
            method: error.config?.method?.toUpperCase(),
            data: data
        };

        details = JSON.stringify(detailsObj, null, 2);

    } else if (error.request) {
        // Request được gửi nhưng không nhận được response
        message = 'Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.';
        errorCode = 'NETWORK_ERROR';
        details = `Request URL: ${error.config?.url}\nMethod: ${error.config?.method}`;

    } else if (error.message) {
        // Lỗi khác (JavaScript error, validation error, etc.)
        message = error.message;
        errorCode = error.code || error.name || 'JS_ERROR';
        details = error.stack || '';

    } else if (typeof error === 'string') {
        // Lỗi dạng string đơn giản
        message = error;
    }

    return {
        message,
        errorCode,
        details
    };
}

let lastErrorTime = 0;
const ERROR_DEBOUNCE_MS = 500; // Không hiện 2 lỗi cùng loại trong 0.5s

/**
 * Hiển thị error dialog với thông tin chi tiết
 * Sử dụng trong component có ConfirmModal HOẶC Global Event Bus
 * 
 * @param {Object} vm - Vue component instance (this)
 * @param {Error|Object|String} error - Error object
 * @param {String} title - Tiêu đề dialog (optional)
 */
export function showErrorDialog(vm, error, title = 'Lỗi') {
    const now = Date.now();
    const { message, errorCode, details } = formatError(error);

    // Chống lặp thông báo (Debounce) cho cùng một lỗi trong thời gian ngắn
    if (now - lastErrorTime < ERROR_DEBOUNCE_MS) {
        return;
    }
    lastErrorTime = now;

    // 1. Emit to Global Event Bus (Ưu tiên số 1)
    // App.vue sẽ nhận và hiển thị Global Modal
    eventBus.emit(EVENTS.SHOW_GLOBAL_ERROR, { error, title });

    // 2. Fallback: Chỉ set local data nếu KHÔNG PHẢI lỗi 403/401 
    // (Vì 403/401 đã có Global Modal hoặc Interceptor xử lý riêng)
    const status = error.response?.status;
    const isAccessError = status === 403 || status === 401;

    if (vm && !isAccessError) {
        if (vm.errorModalTitle !== undefined) vm.errorModalTitle = title;
        if (vm.errorModalMessage !== undefined) vm.errorModalMessage = message;
        if (vm.errorModalCode !== undefined) vm.errorModalCode = errorCode;
        if (vm.errorModalDetails !== undefined) vm.errorModalDetails = details;
        if (vm.showErrorModal !== undefined) vm.showErrorModal = true;
    }
}

/**
 * Hiển thị success dialog
 * @param {Object} vm - Vue component instance
 * @param {String} message - Thông báo thành công
 * @param {String} title - Tiêu đề (optional)
 */
export function showSuccessDialog(vm, message, title = 'Thành công') {
    vm.successModalTitle = title;
    vm.successModalMessage = message;
    vm.showSuccessModal = true;
}

/**
 * Hiển thị warning dialog
 * @param {Object} vm - Vue component instance
 * @param {String} message - Thông báo cảnh báo
 * @param {String} title - Tiêu đề (optional)
 */
export function showWarningDialog(vm, message, title = 'Cảnh báo') {
    vm.warningModalTitle = title;
    vm.warningModalMessage = message;
    vm.showWarningModal = true;
}

/**
 * Extract error message từ nhiều format khác nhau
 * @param {*} error - Error object
 * @returns {String} - Error message
 */
export function getErrorMessage(error) {
    if (typeof error === 'string') return error;
    if (error.response?.data?.message) return error.response.data.message;
    if (error.response?.data?.error) return error.response.data.error;
    if (error.message) return error.message;
    return 'Đã xảy ra lỗi không xác định';
}

/**
 * Log error với thông tin chi tiết (cho debugging)
 * @param {String} context - Context của lỗi (VD: "AdminUsers.createUser")
 * @param {*} error - Error object
 */
export function logError(context, error) {
    const { message, errorCode, details } = formatError(error);

    console.group(`🔴 Error in ${context}`);
    console.error('Message:', message);
    console.error('Code:', errorCode);
    console.error('Details:', details);
    console.error('Raw Error:', error);
    console.groupEnd();
}

/**
 * Mixin để dễ dàng sử dụng error handling trong components
 * 
 * @example
 * import { errorHandlingMixin } from '@/utils/errorHandler';
 * 
 * export default {
 *   mixins: [errorHandlingMixin],
 *   methods: {
 *     async saveData() {
 *       try {
 *         await axios.post('/api/data', this.formData);
 *         this.showSuccess('Lưu thành công!');
 *       } catch (error) {
 *         this.showError(error, 'Lỗi khi lưu dữ liệu');
 *       }
 *     }
 *   }
 * }
 */
export const errorHandlingMixin = {
    data() {
        return {
            // Error modal
            showErrorModal: false,
            errorModalTitle: 'Lỗi',
            errorModalMessage: '',
            errorModalCode: '',
            errorModalDetails: '',

            // Success modal
            showSuccessModal: false,
            successModalTitle: 'Thành công',
            successModalMessage: '',

            // Warning modal
            showWarningModal: false,
            warningModalTitle: 'Cảnh báo',
            warningModalMessage: ''
        };
    },
    methods: {
        /**
         * Hiển thị error dialog
         */
        showError(error, title = 'Lỗi') {
            showErrorDialog(this, error, title);
        },

        /**
         * Hiển thị success dialog
         */
        showSuccess(message, title = 'Thành công') {
            showSuccessDialog(this, message, title);
        },

        /**
         * Hiển thị warning dialog
         */
        showWarning(message, title = 'Cảnh báo') {
            showWarningDialog(this, message, title);
        },

        /**
         * Đóng tất cả modals
         */
        closeAllModals() {
            this.showErrorModal = false;
            this.showSuccessModal = false;
            this.showWarningModal = false;
        }
    }
};

export default {
    formatError,
    showErrorDialog,
    showSuccessDialog,
    showWarningDialog,
    getErrorMessage,
    logError,
    errorHandlingMixin
};
